"""
generate_full_summary.py: computes and saves the complete analysis across
Phase 1-4 — detection rates, cost, significance, model comparison, and the
fair_representation mutation vs. control validation.
"""

import json
from pathlib import Path

from evaluation.load import load_results
from evaluation.curves import detection_rate_by, total_cost_by_strategy
from evaluation.tables import (
    strategy_severity_table_latex,
    two_dimension_table_latex,
    save_table,
    cost_summary_table_latex,
    fair_representation_validation_table_latex,
)
from evaluation.figures import plot_detection_by_severity
from evaluation.significance import mcnemar_test, bootstrap_recall_ci

results = load_results(Path("runs/results"))
print(f"Total results (before filtering): {len(results)}")

REAL_MODELS = {"gpt5.6-luna", "gpt5.6-terra"}
results = [r for r in results if r.model in REAL_MODELS]
print(f"Total results (after filtering test contamination): {len(results)}")

by_strategy_severity = detection_rate_by(results, group_by=["strategy", "severity"])
by_strategy_property = detection_rate_by(
    results, group_by=["strategy", "mutation_type"]
)
by_model_severity = detection_rate_by(results, group_by=["model", "severity"])
by_model_property = detection_rate_by(results, group_by=["model", "mutation_type"])

cost_by_strategy = total_cost_by_strategy(results)
cost_by_model = {}
for r in results:
    cost_by_model[r.model] = cost_by_model.get(r.model, 0.0) + r.cost

# --- RQ3: strategy comparison, restricted to the Phase 1 design ---
# Single-property prompting was run only with luna on the Phase 1 sample, so
# the combined results are restricted to the same model and the same units.
PHASE1_MODEL = "gpt5.6-luna"
split_results = [
    r for r in results if r.strategy == "split" and r.model == PHASE1_MODEL
]
split_keys = {(r.item_id, r.mutation_type, r.severity) for r in split_results}
combined_results = [
    r
    for r in results
    if r.strategy == "combined"
    and r.model == PHASE1_MODEL
    and (r.item_id, r.mutation_type, r.severity) in split_keys
]
mcnemar_result = mcnemar_test(split_results, combined_results)
split_ci = bootstrap_recall_ci(split_results, n_bootstrap=1000)
combined_ci = bootstrap_recall_ci(combined_results, n_bootstrap=1000)

# --- fair_representation validation: flag rate, computed directly ---
# (precision/recall don't apply to the control, since it has zero true
# positives by design — see the note in fair_representation_validation_table_latex)
mutated_fr = [r for r in results if r.mutation_type == "fair_representation"]
control_fr = [r for r in results if r.mutation_type == "fair_representation_control"]


def _flag_rate(rows) -> float:
    flagged = 0
    for r in rows:
        for v in r.verdicts:
            if v.property == "fair_representation" and not v.passed:
                flagged += 1
    return flagged / len(rows) if rows else 0.0


mutated_flag_rate = _flag_rate(mutated_fr)
control_fp_rate = _flag_rate(control_fr)

summary = {
    "total_results": len(results),
    "detection_by_strategy_severity": {
        str(k): v for k, v in by_strategy_severity.items()
    },
    "detection_by_strategy_property": {
        str(k): v for k, v in by_strategy_property.items()
    },
    "detection_by_model_severity": {str(k): v for k, v in by_model_severity.items()},
    "detection_by_model_property": {str(k): v for k, v in by_model_property.items()},
    "cost_by_strategy": cost_by_strategy,
    "cost_by_model": cost_by_model,
    "mcnemar_test": mcnemar_result,
    "bootstrap_recall_ci": {"split": split_ci, "combined": combined_ci},
    "fair_representation_validation": {
        "mutated_n": len(mutated_fr),
        "mutated_flag_rate": mutated_flag_rate,
        "control_n": len(control_fr),
        "control_false_positive_rate": control_fp_rate,
    },
}

output_dir = Path("runs/full_summary")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)

# --- tables ---
save_table(
    strategy_severity_table_latex(by_strategy_severity),
    output_dir / "strategy_severity.tex",
)

PROPERTIES_FOR_TABLE = [
    "technical_quality",
    "visual_clarity",
    "standard_presentation",
    "functional_relevance",
    "text_image_coherence",
    "fair_representation",
]
save_table(
    two_dimension_table_latex(
        by_model_severity,
        "Model",
        "Severity",
        ["gpt5.6-luna", "gpt5.6-terra"],
        ["subtle", "moderate", "obvious"],
        "Detection performance by model and damage severity.",
        "tab:model-severity",
    ),
    output_dir / "model_severity.tex",
)
save_table(
    cost_summary_table_latex(cost_by_model, len(results)),
    output_dir / "cost_summary.tex",
)
save_table(
    two_dimension_table_latex(
        by_model_property,
        "Model",
        "Property",
        ["gpt5.6-luna", "gpt5.6-terra"],
        PROPERTIES_FOR_TABLE,
        "Detection performance by model and evaluated property.",
        "tab:model-property",
    ),
    output_dir / "model_property.tex",
)
save_table(
    fair_representation_validation_table_latex(
        mutated_flag_rate, len(mutated_fr), control_fp_rate, len(control_fr)
    ),
    output_dir / "fair_representation_validation.tex",
)

# --- figure: overall detection by severity, combined strategy only ---
combined_by_severity = {
    sev: metrics
    for (strat, sev), metrics in by_strategy_severity.items()
    if strat == "combined"
}
plot_detection_by_severity(
    combined_by_severity, output_dir / "detection_by_severity.png"
)

print(f"Saved everything to {output_dir}/")
print(
    f"Fair representation: {mutated_flag_rate*100:.1f}% flagged (mutated, n={len(mutated_fr)})"
)
print(f"Control: {control_fp_rate*100:.1f}% flagged (unmodified, n={len(control_fr)})")
print(f"RQ3 pairs: split={len(split_results)}, combined={len(combined_results)}")
