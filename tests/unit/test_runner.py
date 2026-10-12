"""
test_runner.py: end-to-end test of run_pipeline using a fake provider.
"""

import json
from decimal import Decimal

from providers.base import RawResponse, BatchStatus
from execution.runner import run_pipeline
from execution.cache import Cache
from execution.ledger import Ledger
from tracking.base import NullTracker
from config import ModelPricing, ModelConfig
from mutations.base import MutationType, Severity
from domain.item import Item


class FakeProvider:
    def __init__(self):
        self.submitted_batches = {}

    def submit_batch(self, requests):
        batch_id = f"fake_batch_{len(self.submitted_batches)}"
        self.submitted_batches[batch_id] = requests
        return batch_id

    def check_batch_status(self, batch_id):
        return BatchStatus.COMPLETED

    def fetch_batch(self, batch_id):
        requests = self.submitted_batches[batch_id]
        fake_content = json.dumps(
            [{"property": "technical_quality", "passed": True, "reasoning": ""}]
        )
        return [
            RawResponse(
                custom_id=request.custom_id,
                content=fake_content,
                input_tokens=100,
                output_tokens=20,
            )
            for request in requests
        ]


def make_item(image_path: str, **overrides):
    defaults = dict(
        id="q1",
        question="What is 2+2?",
        choices=("3", "4", "5"),
        answer=1,
        hint="",
        image=image_path,
        task="t",
        grade="3",
        subject="math",
        topic="arithmetic",
        category="c",
        skill="sk",
        lecture="",
        solution="",
        split="train",
    )
    defaults.update(overrides)
    return Item(**defaults)


def make_test_image(path):
    from PIL import Image

    img = Image.new("RGB", (50, 50), color="red")
    img.save(path)


def test_run_pipeline_end_to_end(tmp_path):
    image_path = tmp_path / "original.png"
    make_test_image(image_path)
    item1 = make_item(str(image_path))

    cache = Cache(tmp_path / "cache.txt")
    ledger = Ledger(tmp_path / "ledger.txt")
    tracker = NullTracker()
    provider = FakeProvider()

    model_configs = {
        "fake-model": ModelConfig(
            name="fake-model",
            provider="openai",
            endpoint="fake-endpoint",
        )
    }
    pricing = {
        "fake-model": ModelPricing(
            input_per_million=Decimal("2.5"), output_per_million=Decimal("15.0")
        )
    }

    run_pipeline(
        items=[item1],
        mutation_types=[MutationType.TECHNICAL_QUALITY],
        severities=[Severity.OBVIOUS],
        models=["fake-model"],
        strategies=["split"],
        provider=provider,
        cache=cache,
        ledger=ledger,
        tracker=tracker,
        pricing=pricing,
        model_configs=model_configs,
        seed=42,
        manifest_path=tmp_path / "manifest.json",
    )

    assert len(cache.completed) == 1
    assert len(ledger.get_pending()) == 0


def test_run_pipeline_skips_completed_work(tmp_path):
    image_path = tmp_path / "original.png"
    make_test_image(image_path)
    item1 = make_item(str(image_path))

    cache = Cache(tmp_path / "cache.txt")
    ledger = Ledger(tmp_path / "ledger.txt")
    tracker = NullTracker()
    provider = FakeProvider()

    model_configs = {
        "fake-model": ModelConfig(
            name="fake-model",
            provider="openai",
            endpoint="fake-endpoint",
        )
    }
    pricing = {
        "fake-model": ModelPricing(
            input_per_million=Decimal("2.5"), output_per_million=Decimal("15.0")
        )
    }

    kwargs = dict(
        items=[item1],
        mutation_types=[MutationType.TECHNICAL_QUALITY],
        severities=[Severity.OBVIOUS],
        models=["fake-model"],
        strategies=["split"],
        provider=provider,
        cache=cache,
        ledger=ledger,
        tracker=tracker,
        pricing=pricing,
        model_configs=model_configs,
        seed=42,
        manifest_path=tmp_path / "manifest.json",
    )

    run_pipeline(**kwargs)
    assert len(provider.submitted_batches) == 1

    run_pipeline(**kwargs)
    assert len(provider.submitted_batches) == 1


def test_run_pipeline_separates_models_into_different_batches(tmp_path):
    image_path = tmp_path / "original.png"
    make_test_image(image_path)
    item1 = make_item(str(image_path))

    cache = Cache(tmp_path / "cache.txt")
    ledger = Ledger(tmp_path / "ledger.txt")
    tracker = NullTracker()
    provider = FakeProvider()

    pricing = {
        "model-a": ModelPricing(
            input_per_million=Decimal("2.5"), output_per_million=Decimal("15.0")
        ),
        "model-b": ModelPricing(
            input_per_million=Decimal("2.5"), output_per_million=Decimal("15.0")
        ),
    }
    model_configs = {
        "model-a": ModelConfig(
            name="model-a", provider="openai", endpoint="endpoint-a"
        ),
        "model-b": ModelConfig(
            name="model-b", provider="openai", endpoint="endpoint-b"
        ),
    }

    run_pipeline(
        items=[item1],
        mutation_types=[MutationType.TECHNICAL_QUALITY],
        severities=[Severity.OBVIOUS],
        models=["model-a", "model-b"],
        strategies=["split"],
        provider=provider,
        cache=cache,
        ledger=ledger,
        tracker=tracker,
        pricing=pricing,
        model_configs=model_configs,
        seed=42,
        manifest_path=tmp_path / "manifest.json",
    )

    # 1 item x 1 mutation x 1 severity x 2 models x 1 strategy = 2 total units,
    # but each model must be its own batch -> 2 separate batches submitted
    assert len(provider.submitted_batches) == 2
