"""
significance.py: statistical tests for comparing two strategies/models on
the same data — McNemar's test for paired detection comparisons, and
bootstrap confidence intervals for a single strategy's recall.
"""

import random
from statsmodels.stats.contingency_tables import mcnemar

from evaluation.load import LoadedResult
from evaluation.metrics import compute_confusion_counts, compute_metrics
from evaluation.metrics import (
    compute_confusion_counts,
    compute_metrics,
    ground_truth_property,
)


def did_catch_damage(result: LoadedResult) -> bool:
    """
    True if the model correctly flagged the actually-damaged property as failed.
    If the damaged property doesn't appear in the verdicts at all (a malformed
    or incomplete response), this counts as NOT caught — a missed detection,
    not a silent pass.
    """
    damaged_property = ground_truth_property(result.mutation_type)
    for verdict in result.verdicts:
        if verdict.property == damaged_property:
            return not verdict.passed
    return False


def match_paired_results(
    results_a: list[LoadedResult], results_b: list[LoadedResult]
) -> list[tuple[LoadedResult, LoadedResult]]:
    """
    Pairs up results from two strategies/models that evaluated the SAME
    underlying unit of work (same item, mutation, severity) — required for
    a valid paired comparison. Results that only exist on one side are dropped.
    """

    def key(r: LoadedResult):
        return (r.item_id, r.mutation_type, r.severity, r.model)

    lookup_b = {key(r): r for r in results_b}

    pairs = []
    for result_a in results_a:
        result_b = lookup_b.get(key(result_a))
        if result_b is not None:
            pairs.append((result_a, result_b))
    return pairs


def mcnemar_test(results_a: list[LoadedResult], results_b: list[LoadedResult]) -> dict:
    """
    Runs McNemar's test comparing detection rates between two strategies/models,
    on the same underlying items.
    """
    pairs = match_paired_results(results_a, results_b)

    b = 0  # A caught it, B missed it
    c = 0  # B caught it, A missed it

    for result_a, result_b in pairs:
        caught_a = did_catch_damage(result_a)
        caught_b = did_catch_damage(result_b)

        if caught_a and not caught_b:
            b += 1
        elif caught_b and not caught_a:
            c += 1

    table = [[0, b], [c, 0]]
    use_exact = (b + c) < 25
    test_result = mcnemar(table, exact=use_exact, correction=True)

    return {
        "b": b,
        "c": c,
        "n_pairs": len(pairs),
        "statistic": test_result.statistic,
        "p_value": test_result.pvalue,
    }


def bootstrap_recall_ci(
    results: list[LoadedResult],
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: int = 42,
) -> dict:
    """
    Estimates a confidence interval for the overall recall of `results`,
    by resampling with replacement many times and seeing how much the
    recall varies across resamples.
    """
    rng = random.Random(seed)
    n = len(results)

    point_counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    for result in results:
        damaged_property = ground_truth_property(result.mutation_type)
        counts = compute_confusion_counts(result.verdicts, damaged_property)
        for key in point_counts:
            point_counts[key] += counts[key]
    point_estimate = compute_metrics(point_counts)["recall"]

    bootstrap_recalls = []
    for _ in range(n_bootstrap):
        resample = [rng.choice(results) for _ in range(n)]

        counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
        for result in resample:
            damaged_property = ground_truth_property(result.mutation_type)
            result_counts = compute_confusion_counts(result.verdicts, damaged_property)
            for key in counts:
                counts[key] += result_counts[key]

        bootstrap_recalls.append(compute_metrics(counts)["recall"])

    bootstrap_recalls.sort()
    lower_idx = int((1 - confidence) / 2 * n_bootstrap)
    upper_idx = int((1 + confidence) / 2 * n_bootstrap) - 1

    return {
        "point_estimate": point_estimate,
        "lower": bootstrap_recalls[lower_idx],
        "upper": bootstrap_recalls[upper_idx],
        "confidence": confidence,
    }
