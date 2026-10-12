"""
text_image_coherence.py: mutations that substitute the image with one from
the same subject but a different topic, testing whether the model detects
contradictions between the question text and the image.
"""

import random
from pathlib import Path
from PIL import Image

from domain.item import Item
from mutations.base import MutatedItem, MutationType, Severity, build_mutated_path


class TextImageCoherenceMutation:
    def __init__(self, candidates: list[Item]):
        self.candidates = candidates

    def name(self) -> str:
        return "coherence_substitution"

    def apply(self, item: Item, severity: Severity, seed: int) -> MutatedItem:
        original_path = Path(item.image)
        new_path = build_mutated_path(
            item.id, self.name(), severity, original_path.suffix
        )

        if new_path.exists():
            return MutatedItem(
                original=item,
                mutation_type=MutationType.TEXT_IMAGE_COHERENCE,
                severity=severity,
                mutated_image=str(new_path),
            )

        rng = random.Random(seed)
        possible_substitutes = [
            candidate
            for candidate in self.candidates
            if candidate.id != item.id
            and candidate.topic != item.topic
            and candidate.subject == item.subject
        ]
        substitute = rng.choice(possible_substitutes)
        substitute_path = Path(substitute.image)

        substitute_image = Image.open(substitute_path)
        substitute_image.save(new_path)

        return MutatedItem(
            original=item,
            mutation_type=MutationType.TEXT_IMAGE_COHERENCE,
            severity=severity,
            mutated_image=str(new_path),
        )
