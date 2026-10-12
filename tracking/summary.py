"""
summary.py: aggregates Verdicts into summary metrics for tracking/logging.
"""

from domain.verdict import Verdict


def summarize_verdicts(verdicts: list[Verdict]) -> dict:
    """
    Summarizes a list of Verdicts into pass/fail counts, for logging.
    """
    passed_count = sum(v.passed for v in verdicts)
    failed_count = len(verdicts) - passed_count

    return {
        "passed_count": passed_count,
        "failed_count": failed_count,
    }
