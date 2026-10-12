"""
cache.py: tracks which fingerprints have already been completed,
enabling crash-safe resume without duplicate API calls.
"""

from pathlib import Path


class Cache:
    def __init__(self, cache_path: Path):
        self.cache_path = cache_path
        self.completed: set[str] = set()
        if self.cache_path.exists():
            with open(self.cache_path) as f:
                for line in f:
                    self.completed.add(line.strip())

    def is_done(self, fingerprint: str) -> bool:
        return fingerprint in self.completed

    def mark_done(self, fingerprint: str) -> None:
        if fingerprint in self.completed:
            return
        self.completed.add(fingerprint)
        with open(self.cache_path, "a") as f:
            f.write(fingerprint + "\n")
