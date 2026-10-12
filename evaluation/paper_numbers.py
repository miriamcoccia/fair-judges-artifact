"""
paper_numbers.py: computes the numbers still missing from the SEIS draft,
with the model/phase filtering that generate_full_summary.py lacks.

Usage (from the project root):
    uv run python -m evaluation.paper_numbers
"""

import json
from collections import defaultdict
from pathlib import Path

from evaluation.curves import detection_rate_by
from evaluation.load import load_results
from evaluation.significance import did_catch_damage, mcnemar_test

REAL_MODELS = {"gpt5.6-luna", "gpt5.6-terra"}
PARAMETRIC = {"technical_quality", "standard_presentation", "visual_clarity"}
SUBSTITUTION = {"functional_relevance", "text_image_coherence"}
METAMORPHIC = PARAMETRIC | SUBSTITUTION
PHASE1_MODEL = "gpt5.6-luna"

results = [r for r in load_results(Path("runs/results")) if r.model in REAL_MODELS]
combined = [r for r in results if r.strategy == "combined"]
out = {}

# RQ1: recall per model x operator x severity (parametric operators only)
rq1 = detection_rate_by(
    [r for r in combined if r.mutation_type in PARAMETRIC],
    group_by=["model", "mutation_type", "severity"],
)
out["rq1_recall"] = {str(k): round(v["recall"], 3) for k, v in sorted(rq1.items())}

# RQ2: baseline flag rate per property on unmodified items (Phase 4 control)
flagged = defaultdict(int)
total = defaultdict(int)
for r in combined:
    if r.mutation_type != "fair_representation_control":
        continue
    for v in r.verdicts:
        total[(r.model, v.property.value)] += 1
        flagged[(r.model, v.property.value)] += not v.passed
out["rq2_baseline_flag_rate_pct"] = {
    str(k): round(100 * flagged[k] / total[k], 1) for k in sorted(total)
}
out["control_n_per_model"] = {
    m: sum(
        1
        for r in combined
        if r.model == m and r.mutation_type == "fair_representation_control"
    )
    for m in sorted(REAL_MODELS)
}

# RQ3: per-operator McNemar, Phase 1 model only (pairs on same model)
split_l = [r for r in results if r.strategy == "split" and r.model == PHASE1_MODEL]
comb_l = [
    r for r in combined if r.model == PHASE1_MODEL and r.mutation_type in METAMORPHIC
]
split_items = {r.item_id for r in split_l}
comb_l = [r for r in comb_l if r.item_id in split_items]
out["rq3_mcnemar_overall"] = mcnemar_test(split_l, comb_l)
out["rq3_mcnemar_by_operator"] = {
    op: mcnemar_test(
        [r for r in split_l if r.mutation_type == op],
        [r for r in comb_l if r.mutation_type == op],
    )
    for op in sorted(METAMORPHIC)
}

# Threats: run-to-run agreement on the three identical substitution inputs
by_unit = defaultdict(list)
for r in combined:
    if r.mutation_type in SUBSTITUTION:
        by_unit[(r.model, r.mutation_type, r.item_id)].append(did_catch_damage(r))
agree = defaultdict(lambda: [0, 0])
for (model, op, _), verdicts in by_unit.items():
    if len(verdicts) == 3:
        agree[(model, op)][0] += len(set(verdicts)) == 1
        agree[(model, op)][1] += 1
out["repeat_agreement_pct"] = {
    str(k): round(100 * a / n, 1) for k, (a, n) in sorted(agree.items())
}

Path("runs/paper_numbers.json").write_text(json.dumps(out, indent=2, default=float))
print(json.dumps(out, indent=2, default=float))
