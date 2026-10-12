"""
test_summary.py: tests for summarize_verdicts.
"""

from tracking.summary import summarize_verdicts
from domain.verdict import Verdict
from domain.properties import QualityProperty


def make_verdict(passed: bool, property=QualityProperty.TECHNICAL_QUALITY):
    reasoning = "" if passed else "some reason"
    return Verdict(property=property, passed=passed, reasoning=reasoning)


def test_summarize_mixed_verdicts():
    verdicts = [make_verdict(True), make_verdict(False), make_verdict(False)]
    result = summarize_verdicts(verdicts)
    assert result == {"passed_count": 1, "failed_count": 2}


def test_summarize_all_passed():
    verdicts = [make_verdict(True), make_verdict(True), make_verdict(True)]
    result = summarize_verdicts(verdicts)
    assert result == {"passed_count": 3, "failed_count": 0}


def test_summarize_empty_list():
    verdicts = []
    result = summarize_verdicts(verdicts)
    assert result == {"passed_count": 0, "failed_count": 0}
