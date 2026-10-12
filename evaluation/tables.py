"""
tables.py: generates LaTeX tables from computed metrics, for direct
inclusion in the paper.
"""

from pathlib import Path


def detection_rate_table_latex(detection_rates: dict[str, dict]) -> str:
    """
    Builds a LaTeX table (using the booktabs style) showing precision,
    recall, and F1 for each severity level.
    """
    severity_order = ["subtle", "moderate", "obvious"]
    available = [s for s in severity_order if s in detection_rates]

    lines = []
    lines.append(r"\begin{table}[h]")
    lines.append(r"\centering")
    lines.append(r"\begin{tabular}{lccc}")
    lines.append(r"\toprule")
    lines.append(r"Severity & Precision & Recall & F1 \\")
    lines.append(r"\midrule")

    for severity in available:
        metrics = detection_rates[severity]
        lines.append(
            f"{severity.capitalize()} & "
            f"{metrics['precision']:.2f} & "
            f"{metrics['recall']:.2f} & "
            f"{metrics['f1']:.2f} \\\\"
        )

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\caption{Detection performance by damage severity.}")
    lines.append(r"\label{tab:detection-by-severity}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def save_table(latex_string: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(latex_string)


def strategy_severity_table_latex(breakdown: dict[tuple, dict]) -> str:
    """
    Builds a LaTeX table from a (strategy, severity)-keyed breakdown,
    as produced by detection_rate_by(results, group_by=["strategy", "severity"]).
    """
    severity_order = ["subtle", "moderate", "obvious"]
    strategy_order = ["split", "combined"]

    lines = []
    lines.append(r"\begin{table}[h]")
    lines.append(r"\centering")
    lines.append(r"\begin{tabular}{llccc}")
    lines.append(r"\toprule")
    lines.append(r"Strategy & Severity & Precision & Recall & F1 \\")
    lines.append(r"\midrule")

    for strategy in strategy_order:
        for severity in severity_order:
            key = (strategy, severity)
            if key not in breakdown:
                continue
            metrics = breakdown[key]
            lines.append(
                f"{strategy.capitalize()} & {severity.capitalize()} & "
                f"{metrics['precision']:.2f} & "
                f"{metrics['recall']:.2f} & "
                f"{metrics['f1']:.2f} \\\\"
            )
        lines.append(r"\midrule")

    lines.pop()  # remove the trailing \midrule after the last group
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(
        r"\caption{Detection performance by prompting strategy and damage severity.}"
    )
    lines.append(r"\label{tab:strategy-severity}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def two_dimension_table_latex(
    breakdown: dict[tuple, dict],
    col1_name: str,
    col2_name: str,
    col1_order: list[str],
    col2_order: list[str],
    caption: str,
    label: str,
) -> str:
    """
    Builds a LaTeX table from any two-dimension breakdown (e.g. model x severity).
    """
    lines = []
    lines.append(r"\begin{table}[h]")
    lines.append(r"\centering")
    lines.append(r"\begin{tabular}{llccc}")
    lines.append(r"\toprule")
    lines.append(f"{col1_name} & {col2_name} & Precision & Recall & F1 \\\\")
    lines.append(r"\midrule")

    for c1 in col1_order:
        for c2 in col2_order:
            key = (c1, c2)
            if key not in breakdown:
                continue
            m = breakdown[key]
            lines.append(
                f"{c1} & {c2.capitalize()} & {m['precision']:.2f} & {m['recall']:.2f} & {m['f1']:.2f} \\\\"
            )
        lines.append(r"\midrule")

    lines.pop()
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(f"\\caption{{{caption}}}")
    lines.append(f"\\label{{{label}}}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def collateral_fp_table_latex(
    fp_counts: dict,
    total_counts: dict,
    model_name: str,
    properties: list[str],
) -> str:
    """
    Builds a LaTeX table showing collateral false-positive rates: for each
    mutated property (rows), the percentage of the time each OTHER property
    (columns) was wrongly flagged as failed.

    fp_counts and total_counts are nested dicts keyed [mutation_type][property],
    as produced by collateral_fp_analysis.build_collateral_counts. The diagonal
    (mutation_type == property) is not applicable and is rendered as "--".
    """
    column_spec = "l" + "c" * len(properties)
    header_cells = " & ".join(p.replace("_", " ").title() for p in properties)

    lines = []
    lines.append(r"\begin{table}[h]")
    lines.append(r"\centering")
    lines.append(r"\small")
    lines.append(f"\\begin{{tabular}}{{{column_spec}}}")
    lines.append(r"\toprule")
    lines.append(f"Mutated property & {header_cells} \\\\")
    lines.append(r"\midrule")

    for mutation_type in properties:
        row_cells = []
        for prop in properties:
            if prop == mutation_type:
                row_cells.append("--")
                continue
            fp = fp_counts.get(mutation_type, {}).get(prop, 0)
            total = total_counts.get(mutation_type, {}).get(prop, 0)
            pct = (fp / total * 100) if total > 0 else 0.0
            row_cells.append(f"{pct:.1f}\\%")
        row_label = mutation_type.replace("_", " ").title()
        lines.append(f"{row_label} & " + " & ".join(row_cells) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(
        f"\\caption{{Collateral false-positive rate by mutated property "
        f"({model_name}). Each cell shows how often the column property "
        f"was wrongly flagged as failed when the row property was the one "
        f"actually mutated.}}"
    )
    lines.append(f"\\label{{tab:collateral-fp-{model_name.replace('.', '-')}}}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def cost_summary_table_latex(
    cost_by_model: dict[str, float], total_results: int
) -> str:
    """
    Builds a LaTeX table summarizing total cost per model and the total
    number of results processed.
    """
    lines = []
    lines.append(r"\begin{table}[h]")
    lines.append(r"\centering")
    lines.append(r"\begin{tabular}{lr}")
    lines.append(r"\toprule")
    lines.append(r"Model & Total cost (\$) \\")
    lines.append(r"\midrule")

    for model, cost in cost_by_model.items():
        lines.append(f"{model} & {cost:.2f} \\\\")

    total_cost = sum(cost_by_model.values())
    lines.append(r"\midrule")
    lines.append(f"Total & {total_cost:.2f} \\\\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(
        f"\\caption{{Total cost by model, and total items processed: {total_results}.}}"
    )
    lines.append(r"\label{tab:cost-summary}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def fair_representation_validation_table_latex(
    mutated_flag_rate: float,
    mutated_n: int,
    control_fp_rate: float,
    control_n: int,
) -> str:
    """
    Validates the fair_representation mutation: how often curated stereotype
    images get flagged, vs. how often unmutated control images get
    incorrectly flagged. Precision/recall don't apply to the control
    (it has no true positives by design), so this reports flag rate and
    false positive rate directly instead.
    """
    lines = []
    lines.append(r"\begin{table}[h]")
    lines.append(r"\centering")
    lines.append(r"\begin{tabular}{lrr}")
    lines.append(r"\toprule")
    lines.append(r"Condition & N & Flagged \\")
    lines.append(r"\midrule")
    lines.append(
        f"Curated stereotype images (mutated) & {mutated_n} & "
        f"{mutated_flag_rate * 100:.1f}\\% \\\\"
    )
    lines.append(
        f"Unmutated images (control) & {control_n} & "
        f"{control_fp_rate * 100:.1f}\\% \\\\"
    )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(
        r"\caption{Validation of the Fair Representation mutation: percentage "
        r"of images flagged as violating fair\_representation, for curated "
        r"stereotype substitutes versus unmutated control images. "
        r"Precision/recall are not reported for the control condition, since "
        r"it contains no true positive cases by design.}"
    )
    lines.append(r"\label{tab:fair-representation-validation}")
    lines.append(r"\end{table}")
    return "\n".join(lines)
