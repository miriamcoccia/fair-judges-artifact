"""
generate_phase1_summary.py: computes and saves the complete Phase 1
analysis — detection rates, cost comparison, and significance tests.
"""

import json
from pathlib import Path

from evaluation.load import load_results
from evaluation.curves import detection_rate_by, total_cost_by_strategy
from evaluation.tables import strategy_severity_table_latex, save_table
from evaluation.significance import mcnemar_test, bootstrap_recall_ci

results = load_results(Path("runs/results"))

# detection rates
by_severity = detection_rate_by(results, group_by=["strategy", "severity"])
by_property = detection_rate_by(results, group_by=["strategy", "mutation_type"])

# cost
costs = total_cost_by_strategy(results)
split_scaled = costs["split"] * 6
combined_total = costs["combined"]

# significance
split_results = [r for r in results if r.strategy == "split"]
combined_results = [r for r in results if r.strategy == "combined"]
mcnemar_result = mcnemar_test(split_results, combined_results)
split_ci = bootstrap_recall_ci(split_results, n_bootstrap=1000)
combined_ci = bootstrap_recall_ci(combined_results, n_bootstrap=1000)

summary = {
    "detection_by_strategy_severity": {str(k): v for k, v in by_severity.items()},
    "detection_by_strategy_property": {str(k): v for k, v in by_property.items()},
    "cost": {
        "split_raw": costs["split"],
        "split_scaled_to_6x_coverage": split_scaled,
        "combined": combined_total,
    },
    "mcnemar_test": mcnemar_result,
    "bootstrap_recall_ci": {
        "split": split_ci,
        "combined": combined_ci,
    },
}

output_dir = Path("runs/phase1_summary")
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)

latex = strategy_severity_table_latex(by_severity)
save_table(latex, output_dir / "strategy_severity.tex")

print(f"Saved summary to {output_dir}")
