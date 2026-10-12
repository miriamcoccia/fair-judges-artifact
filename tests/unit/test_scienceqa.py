"""
test_scienceqa.py: Constructs tets to check whether the ScienceQA dataset is properly loaded.
"""

import pandas as pd
import pytest
from data.scienceqa import ScienceQALoader
from domain.item import Item
from domain.errors import ItemError


# good data
def make_dataframe(**overrides):
    """
    Builds a small, valid ScienceQA-style DataFrame (2 rows),
    overriding specific columns for testing edge cases.
    """
    data = {
        "question_id": ["q1", "q2"],
        "question": ["What is 2+2?", "What is the capital of France?"],
        "choices": ["['3', '4', '5']", "['Paris', 'London', 'Berlin']"],
        "answer": [1, 0],
        "hint": ["", ""],
        "image": ["img1.png", "img2.png"],
        "task": ["math", "geography"],
        "grade": ["3", "5"],
        "subject": ["math", "geography"],
        "topic": ["arithmetic", "capitals"],
        "category": ["addition", "europe"],
        "skill": ["basic-math", "geography-facts"],
        "lecture": ["", ""],
        "solution": ["", ""],
        "set": ["train", "train"],
    }
    data.update(overrides)
    return pd.DataFrame.from_dict(data)


def test_load_items_builds_valid_items():
    """
    Tests whether items are built correctly.
    """
    df = make_dataframe()
    loader = ScienceQALoader(df)
    items = loader.load_items()

    assert len(items) == 2
    for item in items:
        assert isinstance(item, Item)

    assert items[0].question == "What is 2+2?"
    assert items[0].choices == ("3", "4", "5")
    assert items[0].answer == 1


def test_loader_name():
    """
    Tests if the name of the dataset is loaded correctly.
    """
    df = make_dataframe()
    loader = ScienceQALoader(df)
    assert loader.name() == "scienceqa"


def test_load_items_handles_missing_hint_lecture_solution():
    """
    Tests if possible missing values in the 'hint', 'lecture', and 'solution' rows of the dataset are handled correctly.
    """
    df = make_dataframe(
        hint=[float("nan"), 0],
        lecture=[123, float("nan")],
        solution=[float("nan"), "a real solution"],
    )

    loader = ScienceQALoader(df)
    items = loader.load_items()

    assert items[0].hint == ""
    assert items[0].lecture == ""
    assert items[0].solution == ""

    assert items[1].hint == ""
    assert items[1].lecture == ""
    assert items[1].solution == "a real solution"
