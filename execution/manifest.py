"""
manifest.py: records the settings that produced a run's results,
and prevents accidentally reusing a folder with different settings.
"""

import json
import subprocess
from pathlib import Path
from dataclasses import dataclass, asdict


class RunConfigDrift(Exception):
    """Raised when a run folder's recorded settings don't match the current settings."""

    pass


def get_git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True
    )
    return result.stdout.strip()


@dataclass(frozen=True)
class Manifest:
    git_commit: str
    models: list[str]
    seed: int


def write_manifest(manifest: Manifest, path: Path) -> None:
    path.write_text(json.dumps(asdict(manifest), indent=2))


def check_manifest(manifest: Manifest, path: Path) -> None:
    """
    If a manifest already exists at this path, confirm it matches.
    If it doesn't match, raise RunConfigDrift.
    If nothing exists yet, write this one as the new record.
    """
    if not path.exists():
        write_manifest(manifest, path)
        return

    existing = json.loads(path.read_text())
    current = asdict(manifest)

    if existing != current:
        raise RunConfigDrift(
            f"Run settings changed. Existing: {existing}, current: {current}"
        )
