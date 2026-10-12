"""
test_unit.py: tests for build_fingerprint.
"""

from execution.unit import build_fingerprint


def test_same_inputs_produce_same_fingerprint():
    fp1 = build_fingerprint(
        "q1", "gpt5.6", "technical_quality", "obvious", 42, "split", "abc123"
    )
    fp2 = build_fingerprint(
        "q1", "gpt5.6", "technical_quality", "obvious", 42, "split", "abc123"
    )
    assert fp1 == fp2


def test_different_strategy_produces_different_fingerprint():
    fp1 = build_fingerprint(
        "q1", "gpt5.6", "technical_quality", "obvious", 42, "split", "abc123"
    )
    fp2 = build_fingerprint(
        "q1", "gpt5.6", "technical_quality", "obvious", 42, "combined", "abc123"
    )
    assert fp1 != fp2


def test_different_seed_produces_different_fingerprint():
    fp1 = build_fingerprint(
        "q1", "gpt5.6", "technical_quality", "obvious", 42, "split", "abc123"
    )
    fp2 = build_fingerprint(
        "q1", "gpt5.6", "technical_quality", "obvious", 99, "split", "abc123"
    )
    assert fp1 != fp2
