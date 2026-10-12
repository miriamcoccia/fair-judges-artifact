"""
test_schema.py: tests for VerdictResponse.
"""

import pytest
from prompting.schema import VerdictResponse
from domain.verdict import Verdict
from domain.properties import QualityProperty


def make_verdict(property: QualityProperty.VISUAL_CLARITY, passed=True, reasoning=""):
    return Verdict(property=property, passed=passed, reasoning=reasoning)


def test_valid_response_builds():
    response = VerdictResponse(
        verdicts=[make_verdict(property=QualityProperty.VISUAL_CLARITY)]
    )
    assert len(response.verdicts) == 1


def test_multiple_different_properties_builds():
    response = VerdictResponse(
        verdicts=[
            make_verdict(property=QualityProperty.VISUAL_CLARITY),
            make_verdict(property=QualityProperty.TECHNICAL_QUALITY),
        ]
    )
    assert len(response.verdicts) == 2


def test_duplicate_property_raises():
    with pytest.raises(ValueError):
        VerdictResponse(
            verdicts=[
                make_verdict(property=QualityProperty.VISUAL_CLARITY),
                make_verdict(property=QualityProperty.VISUAL_CLARITY),
            ]
        )
