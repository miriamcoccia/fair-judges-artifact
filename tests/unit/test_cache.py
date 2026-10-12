"""
test_cache.py: tests for Cache.
"""

from pathlib import Path
from execution.cache import Cache


def test_fresh_cache_has_nothing_done(tmp_path):
    cache_path = tmp_path / "cache.txt"
    cache = Cache(cache_path)
    assert cache.is_done("fp1") is False


def test_mark_done_updates_in_memory(tmp_path):
    cache_path = tmp_path / "cache.txt"
    cache = Cache(cache_path)
    cache.mark_done("fp1")
    assert cache.is_done("fp1") is True


def test_cache_persists_across_restart(tmp_path):
    cache_path = tmp_path / "cache.txt"

    cache1 = Cache(cache_path)
    cache1.mark_done("fp1")

    cache2 = Cache(cache_path)
    assert cache2.is_done("fp1") is True
    assert cache2.is_done("fp2") is False
