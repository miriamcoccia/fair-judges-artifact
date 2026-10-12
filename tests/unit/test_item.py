"""
test_item.py: tests for the Item dataclass — construction, immutability,
and validation of the answer/choices relationship.
"""

import pytest
from domain.item import Item
from domain.errors import ItemError


def make_item(**overrides):
    """Builds a valid item where only the keyword args provided are replaced for testing purposes."""
    defaults = dict(
        id="q1",
        question="Q",
        choices=("a", "b", "c"),
        answer=1,
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


# happy path
def test_valid_item_builds():
    """A normal, correct Item should build without error."""
    item = make_item()
    assert item.answer == 1
    assert item.choices == ("a", "b", "c")


# immutability
def test_item_is_frozen():
    """
    Item is frozen=True. Trying to reassign a field after creation should raise, not silently succeed.
    """
    item = make_item()
    with pytest.raises(Exception):
        item.answer = 0


# edge cases
def test_answer_at_first_valid_index():
    """
    answer=0 is the smallest valid index and should not raise an error.
    """
    item = make_item(answer=0)
    assert item.answer == 0


def test_answer_at_last_valid_index():
    """
    choices has 3 items, so valid indices are 0, 1, 2.
    answer = 2 is the largest valid index and should not raise an error.
    """
    item = make_item(answer=2)
    assert item.answer == 2


def test_answer_one_past_last_index_raises():
    """
    One-off boundary should raise an error.
    """
    with pytest.raises(ItemError):
        make_item(answer=3)


# sad path
def test_negative_answer_raise():
    """
    answer indices can't be negative because choices are tuples and negative indexing doesn't work on tuples.
    """
    with pytest.raises(ItemError):
        make_item(answer=-1)


def test_empty_choices_raises():
    """
    An item must have choices, items with zero choices should raise an error before construction.
    """
    with pytest.raises(ItemError):
        make_item(choices=())
