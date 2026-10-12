# evaluation/paper_tables.py
"""Recall per operator / severity / model (RQ2) and per strategy (RQ3)."""

from collections import defaultdict
from pathlib import Path

from evaluation.load import load_results
from evaluation.significance import did_catch_damage

MODELS = {"gpt5.6-luna", "gpt5.6-terra"}
EXCLUDED = {"fair_representation", "fair_representation_control"}
SEVERITIES = ["subtle", "moderate", "obvious"]

results = [
    r
    for r in load_results(Path("runs/results"))
    if r.model in MODELS and r.mutation_type not in EXCLUDED
]


def recall(rows) -> str:
    if not rows:
        return "  -  "
    return f"{sum(did_catch_damage(r) for r in rows) / len(rows):.3f} (n={len(rows)})"


def group(rows, key):
    out = defaultdict(list)
    for r in rows:
        out[key(r)].append(r)
    return out


# --- RQ2: combined prompting, both models ---
combined = [r for r in results if r.strategy == "combined"]
print("RQ2: recall, combined prompting")
for (mut, model), rows in sorted(
    group(combined, lambda r: (r.mutation_type, r.model)).items()
):
    print(f"{mut:24s} {model:14s} pooled   {recall(rows)}")
    for sev in SEVERITIES:
        print(
            f"{'':24s} {'':14s} {sev:8s} "
            f"{recall([r for r in rows if r.severity == sev])}"
        )

# --- RQ3: luna, Phase 1 units, both strategies ---
split = [r for r in results if r.strategy == "split" and r.model == "gpt5.6-luna"]
keys = {(r.item_id, r.mutation_type, r.severity) for r in split}
comb_p1 = [
    r
    for r in combined
    if r.model == "gpt5.6-luna" and (r.item_id, r.mutation_type, r.severity) in keys
]
print("\nRQ3: recall on Phase 1 units (luna)")
print(f"{'overall':24s} split {recall(split)}  combined {recall(comb_p1)}")
for mut in sorted({r.mutation_type for r in split}):
    s = [r for r in split if r.mutation_type == mut]
    c = [r for r in comb_p1 if r.mutation_type == mut]
    print(f"{mut:24s} split {recall(s)}  combined {recall(c)}")
for sev in SEVERITIES:
    s = [r for r in split if r.severity == sev]
    c = [r for r in comb_p1 if r.severity == sev]
    print(f"{sev:24s} split {recall(s)}  combined {recall(c)}")
