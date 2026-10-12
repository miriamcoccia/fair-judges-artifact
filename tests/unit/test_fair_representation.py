"""
test_fair_representation.py: tests for FairRepresentationMutation.
"""

from pathlib import Path
from PIL import Image

from mutations.fair_representation import FairRepresentationMutation
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


def test_fair_representation_produces_valid_mutated_item(tmp_path):
    original_path = tmp_path / "original.png"
    make_test_image(original_path, "red")
    item = make_item(str(original_path), item_id="fr_prod_1")

    candidate_path = tmp_path / "candidate.png"
    make_test_image(candidate_path, "blue")

    mutation = FairRepresentationMutation(candidates=[candidate_path])
    result = mutation.apply(item, Severity.OBVIOUS, seed=42)

    assert result.mutation_type == MutationType.FAIR_REPRESENTATION
    assert result.severity == Severity.OBVIOUS
    assert Path(result.mutated_image).exists()


def test_fair_representation_substitutes_with_candidate_image(tmp_path):
    original_path = tmp_path / "original.png"
    make_test_image(original_path, "red")
    item = make_item(str(original_path), item_id="fr_sub_1")

    candidate_path = tmp_path / "candidate.png"
    make_test_image(candidate_path, "blue")

    mutation = FairRepresentationMutation(candidates=[candidate_path])
    result = mutation.apply(item, Severity.MODERATE, seed=42)

    mutated_image = Image.open(result.mutated_image).convert("RGB")
    pixel = mutated_image.getpixel((0, 0))
    assert pixel == (0, 0, 255)


def test_fair_representation_picks_randomly_from_candidates(tmp_path):
    original_path = tmp_path / "original.png"
    make_test_image(original_path, "red")
    item = make_item(str(original_path), item_id="fr_rand_1")

    candidate_1 = tmp_path / "candidate1.png"
    make_test_image(candidate_1, "blue")
    candidate_2 = tmp_path / "candidate2.png"
    make_test_image(candidate_2, "green")

    seen_pixels = set()
    for seed in range(10):
        # each seed needs its own item id, otherwise new_path collides
        # and idempotency stops the second call from writing anything
        seeded_item = make_item(str(original_path), item_id=f"fr_rand_{seed}")
        mutation = FairRepresentationMutation(candidates=[candidate_1, candidate_2])
        result = mutation.apply(seeded_item, Severity.SUBTLE, seed=seed)
        mutated_image = Image.open(result.mutated_image).convert("RGB")
        seen_pixels.add(mutated_image.getpixel((0, 0)))

    # over 10 different seeds, both candidates should show up at least once
    assert (0, 0, 255) in seen_pixels or (0, 255, 0) in seen_pixels
    assert len(seen_pixels) > 1


def test_fair_representation_is_idempotent(tmp_path):
    original_path = tmp_path / "original.png"
    make_test_image(original_path, "red")
    item = make_item(str(original_path), item_id="fr_idem_1")

    candidate_path = tmp_path / "candidate.png"
    make_test_image(candidate_path, "blue")

    mutation = FairRepresentationMutation(candidates=[candidate_path])
    first_result = mutation.apply(item, Severity.OBVIOUS, seed=1)
    first_mtime = Path(first_result.mutated_image).stat().st_mtime

    # second call, different seed on purpose: if idempotency works,
    # it must return early and never re-pick or re-save
    second_result = mutation.apply(item, Severity.OBVIOUS, seed=999)
    second_mtime = Path(second_result.mutated_image).stat().st_mtime

    assert first_result.mutated_image == second_result.mutated_image
    assert first_mtime == second_mtime


def test_fair_representation_same_file_across_all_severities(tmp_path):
    original_path = tmp_path / "original.png"
    make_test_image(original_path, "red")
    item = make_item(str(original_path), item_id="fr_sev_1")

    candidate_path = tmp_path / "candidate.png"
    make_test_image(candidate_path, "blue")

    mutation = FairRepresentationMutation(candidates=[candidate_path])

    subtle_result = mutation.apply(item, Severity.SUBTLE, seed=1)
    moderate_result = mutation.apply(item, Severity.MODERATE, seed=1)
    obvious_result = mutation.apply(item, Severity.OBVIOUS, seed=1)

    assert subtle_result.mutated_image == moderate_result.mutated_image
    assert moderate_result.mutated_image == obvious_result.mutated_image
