"""
collateral_fp_analysis.py

Analyzes "collateral" false positives: cases where a mutation targeted ONE
property, but the judge model also flagged a DIFFERENT, untouched property
as failed.

Only considers results where strategy == "combined".
Produces separate tables for gpt5.6-luna and gpt5.6-terra.

Usage:
    uv run python collateral_fp_analysis.py runs/results
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

TARGET_MODELS = ["gpt5.6-luna", "gpt5.6-terra"]

ALL_PROPERTIES = [
    "functional_relevance",
    "visual_clarity",
    "technical_quality",
    "standard_presentation",
    "text_image_coherence",
    "fair_representation",
]


def load_results(results_dir: Path) -> list[dict]:
    """
    Reads every .json file in results_dir. Skips files that fail to parse,
    printing a warning instead of crashing the whole run.
    """
    results = []
    for path in results_dir.glob("*.json"):
        try:
            with open(path) as f:
                results.append(json.load(f))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: skipped unreadable file {path.name}: {e}")
    return results


def build_collateral_counts(results: list[dict], model: str) -> tuple[dict, dict]:
    """
    Returns two nested dicts, both keyed [mutation_type][property]:
    - fp_counts: number of times 'property' was wrongly flagged failed
    - total_counts: number of times 'property' was eligible to be counted
      (i.e. it wasn't the mutated property itself)
    """
    fp_counts = defaultdict(lambda: defaultdict(int))
    total_counts = defaultdict(lambda: defaultdict(int))

    for row in results:
        if row.get("strategy") != "combined":
            continue
        if row.get("model") != model:
            continue

        mutation_type = row.get("mutation_type")
        if mutation_type not in ALL_PROPERTIES:
            # unexpected/unknown mutation_type - skip rather than guess
            continue

        for verdict in row.get("verdicts", []):
            prop = verdict.get("property")
            if prop == mutation_type:
                # this is the property that was deliberately damaged,
                # not a collateral case
                continue
            if prop not in ALL_PROPERTIES:
                continue

            total_counts[mutation_type][prop] += 1
            if verdict.get("passed") is False:
                fp_counts[mutation_type][prop] += 1

    return fp_counts, total_counts


def print_table(model: str, fp_counts: dict, total_counts: dict) -> None:
    other_properties_header = ALL_PROPERTIES
    print(f"\n{'=' * 80}")
    print(f"Model: {model}")
    print(f"{'=' * 80}")

    header = f"{'mutation_type':<24}" + "".join(
        f"{p:<26}" for p in other_properties_header
    )
    print(header)

    for mutation_type in ALL_PROPERTIES:
        row_cells = []
        for prop in other_properties_header:
            if prop == mutation_type:
                row_cells.append(f"{'-- (mutated) --':<26}")
                continue
            fp = fp_counts[mutation_type].get(prop, 0)
            total = total_counts[mutation_type].get(prop, 0)
            pct = (fp / total * 100) if total > 0 else 0.0
            cell = f"{fp}/{total} ({pct:.1f}%)"
            row_cells.append(f"{cell:<26}")
        print(f"{mutation_type:<24}" + "".join(row_cells))


def write_csv(model: str, fp_counts: dict, total_counts: dict, out_path: Path) -> None:
    lines = ["mutation_type,property,fp_count,total_count,fp_percentage"]
    for mutation_type in ALL_PROPERTIES:
        for prop in ALL_PROPERTIES:
            if prop == mutation_type:
                continue
            fp = fp_counts[mutation_type].get(prop, 0)
            total = total_counts[mutation_type].get(prop, 0)
            pct = (fp / total * 100) if total > 0 else 0.0
            lines.append(f"{mutation_type},{prop},{fp},{total},{pct:.2f}")

    out_path.write_text("\n".join(lines))
    print(f"\nWrote {out_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run python collateral_fp_analysis.py /path/to/results")
        sys.exit(1)

    results_dir = Path(sys.argv[1])
    if not results_dir.is_dir():
        print(f"Not a directory: {results_dir}")
        sys.exit(1)

    print(f"Loading result files from {results_dir} ...")
    results = load_results(results_dir)
    print(f"Loaded {len(results)} result files total.")

    for model in TARGET_MODELS:
        fp_counts, total_counts = build_collateral_counts(results, model)
        print_table(model, fp_counts, total_counts)

        csv_name = f"collateral_fp_{model.replace('.', '_')}.csv"
        write_csv(model, fp_counts, total_counts, Path(csv_name))


if __name__ == "__main__":
    main()
