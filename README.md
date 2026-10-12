# MLLM: Multimodal Damage Detection Validators

Tests whether vision-language models (VLMs) can detect deliberately-injected
damage in image-based educational questions (ScienceQA). Damage is injected
programmatically (blur, rotation, clutter, and substitution mutations) at
three severity levels, and models are prompted to judge six quality
properties of each (possibly damaged) question.


---

## Research questions

1. **Split vs. combined prompting** — is it better (cheaper, more accurate)
   to ask a model about one quality property per call, or all six at once?
2. **Does detection improve with damage severity** — do models more reliably
   catch obvious damage than subtle damage?
3. **Does this hold across models** — do findings generalize beyond one VLM?

---

## Project layout

This project uses a **flat, root-level layout** (not `src/`). Imports are
root-relative, e.g. `from domain.item import Item`, `from config import
Secrets`. Run everything from the project root with `uv run python -m
<module>`, not `python <path>/file.py` — running a file directly changes
Python's module search path and breaks these imports.

```
domain/       Core vocabulary: Item, Verdict, QualityProperty. No
              dependencies on anything else in the project.
config.py     Secrets (.env), ModelConfig, ModelPricing, YAML loaders.
data/         ScienceQA loading, stratified sampling.
mutations/    Damage injection: blur, rotate, clarity-clutter, and two
              substitution mutations (functional relevance, text-image
              coherence). Fair Representation is NOT implemented — see
              Known limitations.
prompting/    Prompt template + JSON verdict schema (Pydantic).
providers/    Batch API clients. OpenAIProvider is the only one used in
              real runs. NebiusProvider exists and is unit-tested but was
              never pilot-validated (Nebius batch API was down) and is
              excluded from real runs.
tracking/     Cost calculation, MLflow logging, pass/fail summarization.
execution/    Orchestration: fingerprinting, caching, the crash-safe
              ledger, the manifest (config-drift guard), the planner, and
              runner.py which ties everything together.
evaluation/   Loading saved results, precision/recall/F1, severity/
              property/model breakdowns, cost aggregation, McNemar's
              test, bootstrap confidence intervals, LaTeX tables, figures.
cli.py        Typer CLI: sample / run / analyse.
tests/unit/   Full test suite, mirrors the folder structure above.
runs/         Gitignored. Cache, ledger, manifests, saved results, MLflow
              data, generated tables/figures.
data/         Gitignored (large files). ScienceQA CSVs and images live
              here locally, not in git.
```

---

## Setup

```bash
uv sync
cp .env.example .env   # fill in OPENAI_API_KEY etc.
```

Model definitions live in `configs/models/*.yaml`, one file per model:

```yaml
name: gpt5.6-luna       # internal identifier — used for fingerprinting,
                        # CLI --models values, and pricing.yaml keys
provider: openai
endpoint: gpt-5.6-luna  # exact string sent to the provider's API
```

**`name` and `endpoint` are deliberately separate.** `name` is your
internal, stable identifier; `endpoint` is whatever the provider's API
actually expects. Keep `name` consistent once you've used it in a real
run — it's baked into every fingerprint from that point on, and changing
it later makes historical results unrecoverable by the planner (this
happened once; see Known issues).

`configs/pricing.yaml` keys must match each model's `name` exactly.

---

## Running the pipeline

```bash
# 1. Build the Phase 1 stratified sample (10% by subject)
uv run python -m cli sample \
  --input-csv data/scienceqa/problems.csv \
  --output-csv data/scienceqa/phase1_sample.csv

# 2. Dry-run: see what would actually happen, incl. how much is cached
uv run python -m cli run \
  --items-csv data/scienceqa/phase1_sample.csv \
  --strategies split,combined \
  --models gpt5.6-luna \
  --dry-run

# 3. The real run — always under nohup, it can take hours
nohup uv run python -m cli run \
  --items-csv data/scienceqa/phase1_sample.csv \
  --strategies split,combined \
  --models gpt5.6-luna \
  --manifest-path runs/manifest_phase1.json \
  --max-per-batch 1788 \
  > runs/phase1_log.txt 2>&1 &

# 4. Analysis
uv run python -m evaluation.generate_full_summary
```

**`--manifest-path`**: give each distinct experiment configuration (different
model sets, different strategies) its own manifest file. The manifest
raises `RunConfigDrift` if you try to reuse a path with different settings
than last time — this is intentional, not a bug, and exists to stop
accidental silent mixing of incompatible results.

**`--max-per-batch`**: OpenAI's Batch API caps files at ~200MB. Since
images are sent as inline base64 (see below), this caps requests per
batch — 1788 is a safe default given this project's average image size
(~65KB → ~86KB base64). Recalculate if your images are a very different
size:

```python
safe_requests = int(150 * 1024 * 1024 / (avg_image_kb * 1024 * 1.33))
```

**Resuming after a crash**: just rerun the same command. The planner
consults the cache and only submits work that isn't already done —
this is the whole point of the fingerprint/cache system. Cost is not
duplicated.

---

## Architecture notes worth knowing

- **Images are sent as inline base64**, not via OpenAI's file-upload API.
  An earlier version uploaded each image once and referenced it by
  `file_id` — this failed at scale with `401: Unable to authorize file
  access` on a batch of 26,190 requests, for reasons never fully
  diagnosed. Base64 sidesteps the failure mode entirely and is also
  faster (no per-image network round-trip during batch construction).
- **A single OpenAI batch can only contain requests for one model.**
  `run_pipeline` groups requests by `endpoint` before chunking — do not
  remove this grouping if you touch `runner.py`.
- **Mutations are idempotent by file existence**: each `apply()` checks
  if the target mutated-image path already exists before regenerating
  it. Don't delete `data/mutated/` expecting a clean slate without
  understanding this — it will just silently skip regeneration for
  anything already present.
- **Split vs. combined precision is not directly comparable.** Split
  mode only ever asks about the one property that's actually damaged,
  so it structurally cannot produce a false positive — its precision of
  1.0 is a design artifact, not evidence it's a better judge. Compare
  strategies on **recall**, which both are equally exposed to.

---

## Known limitations

- **Fair Representation** is not implemented as a mutation. Injecting
  bias/stereotype content into images in a controlled way proved very
  hard, and LLM guardrails resist generating that content on request.
  A curated-examples approach was discussed but not pursued. Only 5 of
  6 quality properties have working mutations.
- **Nebius and Anthropic providers**: Nebius is built and unit-tested
  but was never pilot-validated (their batch API was unavailable) and
  is excluded from real runs. Anthropic was never built. All real data
  is OpenAI-only.
- **`test_runner.py`'s `FakeProvider` writes real files** into
  `runs/results/` (`save_result`'s output directory isn't mocked in
  those tests). Running the test suite pollutes real results with
  fake-model entries (`fake-model`, `model-a`, `model-b`, etc.) —
  `evaluation/generate_full_summary.py` filters to known real model
  names before analysis. Fix properly with `monkeypatch` before this
  causes a real problem.
- **Combined mode's precision is genuinely low** (~0.33–0.45), because
  it's evaluated against a ground truth that only credits one property
  per damaged image, while a single real defect can legitimately affect
  multiple properties at once. Worth discussing as a real limitation in
  the paper, not hiding it.

---

## Current results (summary)

- **~61,100 total results** across Phase 1 (194-item stratified sample,
  both strategies, one model) and Phase 2 (full 1,940-item dataset,
  combined-only, two models — `gpt5.6-luna`, `gpt5.6-terra`).
- **Detection improves with severity** for both strategies (recall
  ~0.71 → ~0.85 as damage goes subtle → obvious) — the core hypothesis
  holds.
- **Combined is significantly better at raw detection** than split
  (McNemar's test, p < 0.001) and **~2.5x cheaper** for equivalent
  property coverage.
- **Split's perfect precision is a structural artifact**, not a fair
  strategy comparison (see above).
- Full breakdowns, LaTeX tables, and figures: `runs/full_summary/`.

---

## Testing

```bash
uv run pytest tests/unit/ -v
```

Tests mirror the source layout 1:1. Fixtures use `tmp_path` for anything
touching the filesystem, `monkeypatch` for environment variables, and a
`FakeProvider`/`NullTracker` pattern for testing orchestration without
hitting real APIs or MLflow.