"""
test_builder.py: tests for build_prompt and hash_prompt
"""

from prompting.builder import build_prompt, hash_prompt
from domain.properties import QualityProperty
from domain.item import Item


def make_item(**overrides):
    defaults = dict(
        id="q1",
        question="What is 2+2?",
        choices=("3", "4", "5"),
        answer=1,
        hint="",
        image="img.png",
        task="t",
        grade="3",
        subject="math",
        topic="arithmetic",
        category="c",
        skill="sk",
        lecture="",
        solution="",
        split="train",
    )
    defaults.update(overrides)
    return Item(**defaults)


def test_build_prompt_includes_question():
    item = make_item()
    prompt = build_prompt(item, [QualityProperty.TECHNICAL_QUALITY])
    assert item.question in prompt


def test_build_prompt_split_includes_only_one_property():
    item = make_item()
    prompt = build_prompt(item, [QualityProperty.TECHNICAL_QUALITY])
    assert "technical_quality" in prompt
    assert "visual_clarity" not in prompt


def test_build_prompt_combined_includes_all_properties():
    item = make_item()
    prompt = build_prompt(item, list(QualityProperty))
    for prop in QualityProperty:
        assert prop.value in prompt


def test_hash_prompt_is_deterministic():
    assert hash_prompt("same text") == hash_prompt("same text")


def test_hash_prompt_differs_for_different_text():
    assert hash_prompt("text a") != hash_prompt("text b")
