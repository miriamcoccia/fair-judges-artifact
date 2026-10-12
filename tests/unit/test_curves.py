"""
test_curves.py: tests for detection_rate_by_severity.
"""

from evaluation.curves import detection_rate_by_severity
from evaluation.load import LoadedResult
from domain.verdict import Verdict
from domain.properties import QualityProperty


def make_result(severity, passed):
    return LoadedResult(
        item_id="q1",
        mutation_type="technical_quality",
        severity=severity,
        model="gpt5.6",
        strategy="split",
        verdicts=[
            Verdict(
                property=QualityProperty.TECHNICAL_QUALITY,
                passed=passed,
                reasoning="" if passed else "damaged",
            )
        ],
        cost=0.0001,
        input_tokens=100,
        output_tokens=10,
    )


def test_detection_rate_improves_with_severity():
    results = [
        make_result("subtle", passed=True),
        make_result("subtle", passed=False),
        make_result("obvious", passed=False),
    ]

    output = detection_rate_by_severity(results)

    assert output["subtle"]["recall"] == 0.5
    assert output["obvious"]["recall"] == 1.0
