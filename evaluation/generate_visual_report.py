"""
generate_visual_report.py: builds a set of clear charts from the saved
results, so patterns (like fair_representation's precision collapse)
are visible at a glance, not buried in JSON or LaTeX tables.

Usage:
    uv run python -m evaluation.generate_visual_report

Reads from: runs/results/ (the raw saved results, same source as
generate_full_summary.py)
Writes to:  runs/full_summary/charts/
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from evaluation.load import load_results
from evaluation.curves import detection_rate_by
from evaluation.significance import bootstrap_recall_ci

OUTPUT_DIR = Path("runs/full_summary/charts")
NAVY = "#2E5C8A"
CORAL = "#C0392B"
REAL_MODELS = {"gpt5.6-luna", "gpt5.6-terra"}

PROPERTY_ORDER = [
    "technical_quality",
    "visual_clarity",
    "standard_presentation",
    "functional_relevance",
    "text_image_coherence",
    "fair_representation",
]
SEVERITY_ORDER = ["subtle", "moderate", "obvious"]


def _setup_style():
    plt.style.use("seaborn-v0_8-whitegrid")


def _clean_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def chart_precision_recall_by_property(results: list, output_dir: Path) -> None:
    """
    Grouped bar chart: precision and recall side by side for each property,
    combined strategy only. This is the chart that makes fair_representation's
    precision collapse (and recall ceiling) visible at a glance.
    """
    combined = [r for r in results if r.strategy == "combined"]
    breakdown = detection_rate_by(combined, group_by=["mutation_type"])

    properties = [p for p in PROPERTY_ORDER if (p,) in breakdown]
    precisions = [breakdown[(p,)]["precision"] for p in properties]
    recalls = [breakdown[(p,)]["recall"] for p in properties]

    x = np.arange(len(properties))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width / 2, precisions, width, label="Precision", color=NAVY)
    ax.bar(x + width / 2, recalls, width, label="Recall", color=CORAL)

    ax.set_xticks(x)
    ax.set_xticklabels([p.replace("_", "\n") for p in properties], fontsize=9)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title(
        "Precision vs. Recall by Property (Combined Strategy)",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.legend(frameon=False, fontsize=10)
    _clean_axes(ax)

    fig.tight_layout()
    fig.savefig(output_dir / "precision_recall_by_property.png", dpi=200)
    plt.close(fig)


def chart_recall_by_severity_both_strategies(results: list, output_dir: Path) -> None:
    """
    Line chart: recall by severity, one line per strategy, on the same axes.
    Shows the severity trend AND the split-vs-combined gap together.
    """
    breakdown = detection_rate_by(results, group_by=["strategy", "severity"])

    fig, ax = plt.subplots(figsize=(7, 5))

    for strategy, color in [("split", NAVY), ("combined", CORAL)]:
        recalls = [
            breakdown[(strategy, sev)]["recall"]
            for sev in SEVERITY_ORDER
            if (strategy, sev) in breakdown
        ]
        ax.plot(
            SEVERITY_ORDER,
            recalls,
            marker="o",
            markersize=9,
            linewidth=2.5,
            label=strategy.capitalize(),
            color=color,
            markerfacecolor=color,
            markeredgecolor="white",
            markeredgewidth=1.5,
        )

    ax.set_ylim(0, 1.08)
    ax.set_xlabel("Damage Severity", fontsize=11)
    ax.set_ylabel("Detection Recall", fontsize=11)
    ax.set_title(
        "Recall by Severity: Split vs. Combined", fontsize=13, fontweight="bold", pad=15
    )
    ax.legend(frameon=False, fontsize=10)
    _clean_axes(ax)

    fig.tight_layout()
    fig.savefig(output_dir / "recall_by_severity_both_strategies.png", dpi=200)
    plt.close(fig)


def chart_cost_by_model(results: list, output_dir: Path) -> None:
    """
    Bar chart: total cost per model, in dollars.
    """
    cost_by_model: dict[str, float] = {}
    for r in results:
        cost_by_model[r.model] = cost_by_model.get(r.model, 0.0) + r.cost

    models = list(cost_by_model.keys())
    costs = [cost_by_model[m] for m in models]

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(models, costs, color=NAVY, width=0.5)

    for bar, cost in zip(bars, costs):
        ax.annotate(
            f"${cost:.2f}",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_ylabel("Total Cost ($)", fontsize=11)
    ax.set_title("Total Cost by Model", fontsize=13, fontweight="bold", pad=15)
    _clean_axes(ax)

    fig.tight_layout()
    fig.savefig(output_dir / "cost_by_model.png", dpi=200)
    plt.close(fig)


def chart_bootstrap_recall_comparison(results: list, output_dir: Path) -> None:
    """
    Error-bar chart: recall point estimate + 95% CI for split vs. combined,
    making the statistical significance visually obvious (do the bars overlap?).
    """
    split_results = [r for r in results if r.strategy == "split"]
    combined_results = [r for r in results if r.strategy == "combined"]

    split_ci = bootstrap_recall_ci(split_results, n_bootstrap=1000)
    combined_ci = bootstrap_recall_ci(combined_results, n_bootstrap=1000)

    labels = ["Split", "Combined"]
    points = [split_ci["point_estimate"], combined_ci["point_estimate"]]
    lower_err = [
        points[0] - split_ci["lower"],
        points[1] - combined_ci["lower"],
    ]
    upper_err = [
        split_ci["upper"] - points[0],
        combined_ci["upper"] - points[1],
    ]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.errorbar(
        labels,
        points,
        yerr=[lower_err, upper_err],
        fmt="o",
        markersize=12,
        capsize=8,
        capthick=2,
        elinewidth=2,
        color=NAVY,
        ecolor=CORAL,
    )

    ax.set_ylim(0.7, 0.85)
    ax.set_ylabel("Recall (95% bootstrap CI)", fontsize=11)
    ax.set_title(
        "Recall by Strategy, with Confidence Intervals",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    _clean_axes(ax)

    fig.tight_layout()
    fig.savefig(output_dir / "bootstrap_recall_comparison.png", dpi=200)
    plt.close(fig)


def main() -> None:
    _setup_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = load_results(Path("runs/results"))
    results = [r for r in results if r.model in REAL_MODELS]
    print(f"Loaded {len(results)} real results (test contamination filtered out).")

    chart_precision_recall_by_property(results, OUTPUT_DIR)
    chart_recall_by_severity_both_strategies(results, OUTPUT_DIR)
    chart_cost_by_model(results, OUTPUT_DIR)
    chart_bootstrap_recall_comparison(results, OUTPUT_DIR)

    print(f"Saved 4 charts to {OUTPUT_DIR}/")


def chart_fair_representation_validation(results: list, output_dir: Path) -> None:
    """
    Bar chart: flag rate for curated stereotype images vs. unmutated
    control images — the visual version of the validation table.
    """

    def _flag_rate(rows) -> float:
        flagged = 0
        for r in rows:
            for v in r.verdicts:
                if v.property == "fair_representation" and not v.passed:
                    flagged += 1
        return flagged / len(rows) if rows else 0.0

    mutated = [r for r in results if r.mutation_type == "fair_representation"]
    control = [r for r in results if r.mutation_type == "fair_representation_control"]

    labels = [
        f"Curated stereotypes\n(n={len(mutated)})",
        f"Unmutated control\n(n={len(control)})",
    ]
    rates = [_flag_rate(mutated) * 100, _flag_rate(control) * 100]

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(labels, rates, color=[CORAL, NAVY], width=0.5)

    for bar, rate in zip(bars, rates):
        ax.annotate(
            f"{rate:.1f}%",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=11,
            fontweight="bold",
        )

    ax.set_ylim(0, 108)
    ax.set_ylabel("% Flagged as Failed", fontsize=11)
    ax.set_title(
        "Fair Representation: Mutated vs. Control",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    _clean_axes(ax)

    fig.tight_layout()
    fig.savefig(output_dir / "fair_representation_validation.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
