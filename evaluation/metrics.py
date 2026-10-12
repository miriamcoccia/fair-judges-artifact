"""
metrics.py: precision, recall, F1 for damage detection.
"""

from domain.verdict import Verdict
from domain.properties import QualityProperty


def ground_truth_property(mutation_type: str) -> QualityProperty:
    """
    Maps a saved result's mutation_type string to the QualityProperty it
    should be judged against. The fair_representation_control mutation
    doesn't damage anything, but it's still testing fair_representation
    specifically (on an undamaged image), so it maps to that same property.
    """
    if mutation_type == "fair_representation_control":
        return QualityProperty.FAIR_REPRESENTATION
    return QualityProperty(mutation_type)


def compute_confusion_counts(
    verdicts: list[Verdict], damaged_property: QualityProperty
) -> dict:
    """
    Compares model verdicts against ground truth (damaged_property should be
    passed=False, everything else should be passed=True).
    """
    tp = fp = fn = tn = 0

    for verdict in verdicts:
        is_damaged = verdict.property == damaged_property
        model_flagged_failure = not verdict.passed

        # your turn: based on is_damaged and model_flagged_failure,
        # increment the right counter
        if is_damaged and model_flagged_failure:
            tp += 1
        elif is_damaged and not model_flagged_failure:
            fn += 1
        elif not is_damaged and model_flagged_failure:
            fp += 1
        elif not is_damaged and not model_flagged_failure:
            tn += 1

    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def compute_metrics(counts: dict) -> dict:
    """
    Computes precision, recall, and F1 from TP/FP/FN counts.
    """
    tp = counts["tp"]
    fp = counts["fp"]
    fn = counts["fn"]

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    metrics = {"precision": precision, "recall": recall, "f1": f1}
    return metrics
