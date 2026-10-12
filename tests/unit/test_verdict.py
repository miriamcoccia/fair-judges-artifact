"""
test_verdict.py: tests for the Verdict dataclass.
"""

import pytest
from domain.verdict import Verdict
from domain.properties import QualityProperty
from domain.errors import VerdictError
from pydantic import ValidationError


# builds a valid verdict to be overridden with the data we are testing
def make_verdict(**overrides):
    """
    Builds a valid Verdict, overriding ony the fields being tested.
    """
    defaults = dict(
        property=QualityProperty.VISUAL_CLARITY,
        passed=True,
        reasoning="",
    )
    defaults.update(overrides)
    return Verdict(**defaults)


# happy path: valid verdict builds
def test_valid_verdict_builds():
    """
    A normal, correct Verdict should build without error.
    """
    verdict = make_verdict()
    assert verdict.property == QualityProperty.VISUAL_CLARITY
    assert verdict.passed == True
    assert verdict.reasoning == ""


# immutability
def test_verdict_is_frozen():
    """
    Verdicts should not be changed after they have been created. Doing so should raise, not pass silently.
    """
    verdict = make_verdict()
    with pytest.raises(ValidationError):
        verdict.passed = False


# sad path: invalid without explanation
def test_not_passed_needs_reasoning():
    """
    Quality properties that did not pass should always have a reasoninig. Empty strings in the reasoning field should fail.
    """
    with pytest.raises(VerdictError):
        make_verdict(passed=False, reasoning="")


def test_passed_has_no_reasoning():
    """
    Quality properties that pass should have empty strings as reasoning. Any other data in that field should raise.
    """
    with pytest.raises(VerdictError):
        make_verdict(passed=True, reasoning="The trait passed successfully.")
