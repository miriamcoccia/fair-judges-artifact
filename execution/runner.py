"""
runner.py: orchestrates the full pipeline — plans work, applies mutations,
submits batches, polls for completion, fetches and records results.
"""

import json
import time
from pathlib import Path
import hashlib

from domain.item import Item
from domain.properties import QualityProperty
from mutations.base import Mutation, MutationType, Severity
from mutations.registry import get_mutation
from providers.base import BatchProvider, PromptRequest, BatchStatus, RawResponse
from execution.planner import plan_work, PlannedUnit
from execution.cache import Cache
from execution.ledger import Ledger
from execution.unit import build_fingerprint
from execution.batch import chunk_requests
from execution.planner import plan_work, PlannedUnit, unit_seed
from prompting.builder import build_prompt, hash_prompt
from prompting.schema import VerdictResponse
from tracking.base import Tracker
from tracking.pricing import calculate_cost
from tracking.registry import get_tracker
from tracking.summary import summarize_verdicts
from config import ModelPricing, ModelConfig
from execution.manifest import Manifest, get_git_commit, check_manifest
from execution.results import save_result


def build_mutations_by_type(
    items: list[Item], fair_representation_candidates: list[str] | None = None
) -> dict[MutationType, Mutation]:
    """
    Initializes one instance of each mutation type.

    * Relevance and coherence mutations use ScienceQA items as candidates.
    * Fair representation uses an optional external image pool.
    * Omitting the external pool safely excludes the fair representation mutation.
    """
    mutations_by_type = {
        MutationType.TECHNICAL_QUALITY: get_mutation("blur"),
        MutationType.STANDARD_PRESENTATION: get_mutation("rotate"),
        MutationType.VISUAL_CLARITY: get_mutation("clarity_shapes"),
        MutationType.FUNCTIONAL_RELEVANCE: get_mutation(
            "funct_relevance_substitution", candidates=items
        ),
        MutationType.TEXT_IMAGE_COHERENCE: get_mutation(
            "coherence_substitution", candidates=items
        ),
        MutationType.FAIR_REPRESENTATION_CONTROL: get_mutation("no_op_control"),
    }

    if fair_representation_candidates:
        mutations_by_type[MutationType.FAIR_REPRESENTATION] = get_mutation(
            "fair_repr_swap", candidates=fair_representation_candidates
        )

    return mutations_by_type


def build_request_for_unit(
    unit: PlannedUnit,
    seed: int,
    mutations_by_type: dict[MutationType, Mutation],
    model_configs: dict[str, ModelConfig],
) -> tuple[PromptRequest, str]:
    """
    Applies the correct mutation to get a damaged image, builds the actual
    PromptRequest to send, plus its fingerprint (used for cache/tracking).
    """
    mutation = mutations_by_type[unit.mutation_type]
    s = unit_seed(unit.mutation_type, unit.item.id, seed)
    mutated_item = mutation.apply(unit.item, unit.severity, s)

    if unit.strategy == "split":
        properties = [QualityProperty(unit.mutation_type.value)]
    else:
        properties = list(QualityProperty)

    prompt_text = build_prompt(unit.item, properties)
    prompt_hash = hash_prompt(prompt_text)

    fingerprint = build_fingerprint(
        unit.item.id,
        unit.model,
        unit.mutation_type.value,
        unit.severity.value,
        s,
        unit.strategy,
        prompt_hash,
    )

    endpoint = model_configs[unit.model].endpoint

    request = PromptRequest(
        custom_id=fingerprint,
        prompt=prompt_text,
        endpoint=endpoint,
        image_path=mutated_item.mutated_image,
    )

    return request, fingerprint


def process_response(
    raw_response: RawResponse,
    unit: PlannedUnit,
    fingerprint: str,
    pricing: dict[str, ModelPricing],
    tracker: Tracker,
    cache: Cache,
) -> None:
    """
    Parses one raw response, saves it, logs it to the tracker, and marks
    its fingerprint done in the cache. Used both during a normal run and
    during manual recovery of a batch whose original run crashed.
    """
    try:
        verdicts_data = json.loads(raw_response.content)
        verdict_response = VerdictResponse(verdicts=verdicts_data)
    except Exception as e:
        print(f"Failed to parse response for {fingerprint}: {e}")
        return

    model_pricing = pricing[unit.model]
    cost = calculate_cost(
        model_pricing, raw_response.input_tokens, raw_response.output_tokens
    )
    summary = summarize_verdicts(verdict_response.verdicts)

    save_result(
        fingerprint=fingerprint,
        item_id=unit.item.id,
        mutation_type=unit.mutation_type.value,
        severity=unit.severity.value,
        model=unit.model,
        strategy=unit.strategy,
        verdicts=verdict_response.verdicts,
        cost=float(cost),
        input_tokens=raw_response.input_tokens,
        output_tokens=raw_response.output_tokens,
    )

    tracker.log_run_start(
        {
            "model": unit.model,
            "strategy": unit.strategy,
            "mutation_type": unit.mutation_type.value,
            "severity": unit.severity.value,
            "item_id": unit.item.id,
        }
    )
    tracker.log_metrics(
        {
            "cost": float(cost),
            "input_tokens": raw_response.input_tokens,
            "output_tokens": raw_response.output_tokens,
            **summary,
        }
    )
    tracker.log_run_end()

    cache.mark_done(fingerprint)


def run_pipeline(
    items: list[Item],
    mutation_types: list[MutationType],
    severities: list[Severity],
    models: list[str],
    strategies: list[str],
    provider: BatchProvider,
    cache: Cache,
    ledger: Ledger,
    tracker: Tracker,
    pricing: dict[str, ModelPricing],
    model_configs: dict[str, ModelConfig],
    seed: int,
    manifest_path: Path,
    max_per_batch: int = 50_000,
    poll_interval_seconds: int = 15,
    fair_representation_candidates: list[str] | None = None,
) -> None:
    """
    Runs the full pipeline: plans remaining work, applies mutations,
    submits it in batches, waits for completion, records results.
    """
    mutations_by_type = build_mutations_by_type(items, fair_representation_candidates)
    manifest = Manifest(git_commit=get_git_commit(), models=models, seed=seed)
    check_manifest(manifest, manifest_path)
    planned_units = plan_work(
        items, mutation_types, severities, models, strategies, cache, seed
    )

    if not planned_units:
        print("Nothing to do — all work already completed.")
        return

    # mutations_by_type = build_mutations_by_type(items)

    requests = []
    fingerprint_by_custom_id = {}
    unit_by_custom_id = {}

    for unit in planned_units:
        request, fingerprint = build_request_for_unit(
            unit, seed, mutations_by_type, model_configs
        )
        requests.append(request)
        fingerprint_by_custom_id[request.custom_id] = fingerprint
        unit_by_custom_id[request.custom_id] = unit

    requests_by_model = {}
    for request in requests:
        requests_by_model.setdefault(request.endpoint, []).append(request)

    chunks = []
    for model_endpoint, model_requests in requests_by_model.items():
        chunks.extend(chunk_requests(model_requests, max_per_batch))

    for chunk in chunks:
        batch_id = provider.submit_batch(chunk)
        ledger.add_batch(batch_id)
        print(f"Submitted batch {batch_id} with {len(chunk)} requests.")

        while True:
            status = provider.check_batch_status(batch_id)
            if status == BatchStatus.COMPLETED:
                break
            if status == BatchStatus.FAILED:
                raise RuntimeError(f"Batch {batch_id} failed.")
            time.sleep(poll_interval_seconds)

        raw_responses = provider.fetch_batch(batch_id)

        for raw_response, request in zip(raw_responses, chunk):
            custom_id = request.custom_id
            unit = unit_by_custom_id[custom_id]
            fingerprint = fingerprint_by_custom_id[custom_id]
            process_response(raw_response, unit, fingerprint, pricing, tracker, cache)

        ledger.remove_batch(batch_id)
        print(f"Batch {batch_id} fully processed and removed from ledger.")
