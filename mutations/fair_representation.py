"""fair_representation.py: constructs the mutation to target the fair representation trait. The mutation swaps images of the multiple-choice dataset with stereotype-containing images from the cmsc dataset"""

import random
from PIL import Image
from pathlib import Path

from mutations.base import (
    MutatedItem,
    MutationType,
    Severity,
    build_mutated_path_no_severity,
)

from domain.item import Item


class FairRepresentationMutation:
    def __init__(self, candidates: list[Path]):
        self.candidates = candidates

    def name(self) -> str:
        return "fair_representation_swap"

    def apply(self, item: Item, severity: Severity, seed: int) -> MutatedItem:
        rng = random.Random(seed)
        substitute = rng.choice(self.candidates)
        new_path = build_mutated_path_no_severity(
            item.id, self.name(), Path(substitute).suffix
        )

        if new_path.exists():
            return MutatedItem(
                original=item,
                mutation_type=MutationType.FAIR_REPRESENTATION,
                severity=severity,
                mutated_image=str(new_path),
            )

        substitute_image = Image.open(substitute)
        substitute_image.save(new_path)

        return MutatedItem(
            original=item,
            mutation_type=MutationType.FAIR_REPRESENTATION,
            severity=severity,
            mutated_image=str(new_path),
        )
