"""
test_planner.py: tests for plan_work.
"""

from pathlib import Path
from execution.planner import plan_work
from execution.cache import Cache
from execution.unit import build_fingerprint
from mutations.base import MutationType, Severity
from prompting.builder import build_prompt, hash_prompt
from domain.item import Item
from domain.properties import QualityProperty


def make_item(**overrides):
    defaults = dict(
        id="q1",
        question="test",
        choices=("a", "b"),
        answer=0,
        hint="",
        image="img.png",
        task="t",
        grade="g",
        subject="s",
        topic="t",
        category="c",
        skill="sk",
        lecture="",
        solution="",
        split="train",
    )
    defaults.update(overrides)
    return Item(**defaults)


def test_plan_work_generates_all_combinations(tmp_path):
    item1 = make_item()
    cache_path = tmp_path / "cache.txt"
    cache = Cache(cache_path)

    units = plan_work(
        items=[item1],
        mutation_types=[MutationType.TECHNICAL_QUALITY],
        severities=[Severity.OBVIOUS],
        models=["gpt5.6"],
        strategies=["split", "combined"],
        cache=cache,
        seed=42,
    )

    assert len(units) == 2


def test_plan_work_skips_cached_fingerprints(tmp_path):
    item1 = make_item()
    cache_path = tmp_path / "cache.txt"
    cache = Cache(cache_path)

    prompt_text = build_prompt(item1, [QualityProperty.TECHNICAL_QUALITY])
    prompt_hash = hash_prompt(prompt_text)
    fp = build_fingerprint(
        "q1", "gpt5.6", "technical_quality", "obvious", 42, "split", prompt_hash
    )
    cache.mark_done(fp)

    units = plan_work(
        items=[item1],
        mutation_types=[MutationType.TECHNICAL_QUALITY],
        severities=[Severity.OBVIOUS],
        models=["gpt5.6"],
        strategies=["split", "combined"],
        cache=cache,
        seed=42,
    )

    assert len(units) == 1
    assert units[0].strategy == "combined"
