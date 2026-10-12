"""
test_text_image_coherence.py: tests for TextImageCoherence.
"""

import pytest
from PIL import Image
from pathlib import Path

from mutations.text_image_coherence import TextImageCoherenceMutation
from mutations.base import Severity, MutationType
from domain.item import Item


def make_item(image_path: str, item_id: str = "q1", **overrides):
    defaults = dict(
        id=item_id,
        question="Q",
        choices=("a", "b"),
        answer=0,
        hint="",
        image=image_path,
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


def make_test_image(path: Path, color: str) -> None:
    img = Image.new("RGB", (50, 50), color=color)
    img.save(path)


def test_relevance_produces_valid_mutated_item(tmp_path):
    image_1_path = tmp_path / "image1.png"
    make_test_image(image_1_path, "red")
    item_1 = make_item(str(image_1_path), item_id="tic_prod_1", topic="triangles")

    image_2_path = tmp_path / "image2.png"
    make_test_image(image_2_path, "blue")
    item_2 = make_item(str(image_2_path), item_id="tic_prod_2", topic="circles")

    mutation = TextImageCoherenceMutation(candidates=[item_1, item_2])
    result = mutation.apply(item_1, Severity.OBVIOUS, seed=42)

    assert result.mutation_type == MutationType.TEXT_IMAGE_COHERENCE
    assert result.severity == Severity.OBVIOUS
    assert Path(result.mutated_image).exists()


def test_relevance_substitutes_with_different_image(tmp_path):
    image_1_path = tmp_path / "image1.png"
    make_test_image(image_1_path, "red")
    item_1 = make_item(str(image_1_path), item_id="tic_sub_1", topic="triangles")

    image_2_path = tmp_path / "image2.png"
    make_test_image(image_2_path, "blue")
    item_2 = make_item(str(image_2_path), item_id="tic_sub_2", topic="circles")

    mutation = TextImageCoherenceMutation(candidates=[item_1, item_2])
    result = mutation.apply(item_1, Severity.OBVIOUS, seed=42)

    mutated_image = Image.open(result.mutated_image).convert("RGB")
    pixel = mutated_image.getpixel((0, 0))
    assert pixel == (0, 0, 255)


def test_relevance_never_substitutes_with_itself(tmp_path):
    image_1_path = tmp_path / "image1.png"
    make_test_image(image_1_path, "red")
    item_1 = make_item(str(image_1_path), item_id="tic_never_1", topic="triangles")

    image_2_path = tmp_path / "image2.png"
    make_test_image(image_2_path, "blue")
    item_2 = make_item(str(image_2_path), item_id="tic_never_2", topic="circles")

    image_3_path = tmp_path / "image3.png"
    make_test_image(image_3_path, "green")
    item_3 = make_item(str(image_3_path), item_id="tic_never_3", topic="squares")

    mutation = TextImageCoherenceMutation(candidates=[item_1, item_2, item_3])

    for seed in range(10):
        result = mutation.apply(item_1, Severity.OBVIOUS, seed=seed)
        mutated_image = Image.open(result.mutated_image).convert("RGB")
        pixel = mutated_image.getpixel((0, 0))
        assert pixel != (255, 0, 0)
