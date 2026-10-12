"""
test_metrics.py: tests for compute_confusion_counts and compute_metrics.
"""

from evaluation.metrics import compute_confusion_counts, compute_metrics
from domain.verdict import Verdict
from domain.properties import QualityProperty


def test_compute_metrics_perfect_detection():
    counts = {"tp": 5, "fp": 0, "fn": 0, "tn": 5}
    result = compute_metrics(counts)
    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1"] == 1.0


def test_compute_metrics_no_positives_at_all():
    counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    result = compute_metrics(counts)
    assert result["precision"] == 0.0
    assert result["recall"] == 0.0
    assert result["f1"] == 0.0


def test_compute_metrics_partial():
    counts = {"tp": 2, "fp": 2, "fn": 3, "tn": 3}
    result = compute_metrics(counts)
    assert result["precision"] == 0.5
    assert result["recall"] == 0.4
    assert 0.43 < result["f1"] <= 0.45


def test_compute_metrics_zero_true_positives_and_false_positives():
    counts = {"tp": 0, "fp": 0, "fn": 3, "tn": 0}
    result = compute_metrics(counts)
    assert result == {"precision": 0.0, "recall": 0.0, "f1": 0.0}
