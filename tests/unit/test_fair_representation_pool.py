"""
test_fair_representation_pool.py: tests for build_candidate_pool.
"""

from pathlib import Path

from mutations.fair_representation_pool import FlaggedCombination, build_candidate_pool


def touch_image(
    root: Path, gender: str, age: str, trait: str, set_n: int, race: str
) -> Path:
    image_dir = root / f"{gender}_{age}" / trait / f"img_set_{set_n}"
    image_dir.mkdir(parents=True, exist_ok=True)
    image_path = image_dir / f"{race}-{age}-{gender}-{trait}.jpg"
    image_path.touch()
    return image_path


def test_matches_fully_specified_combination(tmp_path):
    target = touch_image(tmp_path, "male", "young", "badstudent", 1, "Black")
    touch_image(tmp_path, "male", "young", "badstudent", 1, "White")  # should NOT match

    combo = FlaggedCombination(
        trait="badstudent", race="Black", gender="male", age="young"
    )
    result = build_candidate_pool(tmp_path, flagged_combinations=[combo])

    assert result == [str(target)]


def test_unspecified_race_matches_any_race(tmp_path):
    black = touch_image(tmp_path, "male", "old", "career", 0, "Black")
    white = touch_image(tmp_path, "male", "old", "career", 0, "White")

    combo = FlaggedCombination(trait="career", gender="male", age="old")
    result = build_candidate_pool(tmp_path, flagged_combinations=[combo])

    assert sorted(result) == sorted([str(black), str(white)])


def test_unspecified_gender_and_age_expand_to_all_four(tmp_path):
    touch_image(tmp_path, "male", "young", "family", 0, "Latino")
    touch_image(tmp_path, "male", "old", "family", 0, "Latino")
    touch_image(tmp_path, "female", "young", "family", 0, "Latino")
    touch_image(tmp_path, "female", "old", "family", 0, "Latino")

    combo = FlaggedCombination(trait="family")
    result = build_candidate_pool(tmp_path, flagged_combinations=[combo])

    assert len(result) == 4


def test_missing_trait_folder_is_skipped_not_an_error(tmp_path):
    combo = FlaggedCombination(trait="doesnotexist", gender="male", age="young")
    result = build_candidate_pool(tmp_path, flagged_combinations=[combo])

    assert result == []


def test_multiple_img_sets_are_all_collected(tmp_path):
    first = touch_image(tmp_path, "female", "young", "science", 1, "Indian")
    second = touch_image(tmp_path, "female", "young", "science", 2, "Latino")

    combo = FlaggedCombination(trait="science", gender="female", age="young")
    result = build_candidate_pool(tmp_path, flagged_combinations=[combo])

    assert sorted(result) == sorted(
        [first, second].__str__() and [str(first), str(second)]
    )
