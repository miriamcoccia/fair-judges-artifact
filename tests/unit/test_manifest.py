"""
test_manifest.py: tests for Manifest, check_manifest, RunConfigDrift.
"""

import pytest
from pathlib import Path
from execution.manifest import Manifest, check_manifest, RunConfigDrift


def test_first_check_writes_manifest(tmp_path):
    path = tmp_path / "manifest.json"
    m = Manifest(git_commit="abc123", models=["gpt5.6"], seed=42)
    check_manifest(m, path)
    assert path.exists()


def test_matching_settings_passes_silently(tmp_path):
    path = tmp_path / "manifest.json"
    m = Manifest(git_commit="abc123", models=["gpt5.6"], seed=42)

    check_manifest(m, path)  # writes it
    check_manifest(m, path)  # writes it again with same settings, should not rise


def test_different_settings_raises_drift(tmp_path):
    path = tmp_path / "manifest.json"
    m1 = Manifest(git_commit="abc123", models=["gpt5.6"], seed=42)
    m2 = Manifest(git_commit="def456", models=["gpt5.5"], seed=99)
    check_manifest(m1, path)
    with pytest.raises(RunConfigDrift):
        check_manifest(m2, path)  # same path, different settings, it should raise
