"""
figures.py: generates the main severity-detection chart.
"""

import matplotlib.pyplot as plt
from pathlib import Path


def plot_detection_by_severity(
    detection_rates: dict[str, dict], output_path: Path
) -> None:
    """
    Plots recall by severity level (subtle -> moderate -> obvious), saves as PNG.
    """
    severity_order = ["subtle", "moderate", "obvious"]
    available = [s for s in severity_order if s in detection_rates]
    recalls = [detection_rates[s]["recall"] for s in available]

    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(6, 4))

    ax.plot(
        available,
        recalls,
        marker="o",
        markersize=9,
        linewidth=2.5,
        color="#2E5C8A",
        markerfacecolor="#2E5C8A",
        markeredgecolor="white",
        markeredgewidth=1.5,
        zorder=3,
    )

    ax.fill_between(available, recalls, alpha=0.08, color="#2E5C8A", zorder=1)

    for x, y in zip(available, recalls):
        ax.annotate(
            f"{y:.2f}",
            (x, y),
            textcoords="offset points",
            xytext=(0, 12),
            ha="center",
            fontsize=10,
            fontweight="bold",
            color="#2E5C8A",
        )

    ax.set_ylim(0, 1.08)
    ax.set_xlabel("Damage Severity", fontsize=11, labelpad=10)
    ax.set_ylabel("Detection Recall", fontsize=11, labelpad=10)
    ax.set_title(
        "Detection Rate by Damage Severity", fontsize=13, fontweight="bold", pad=15
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=10)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
