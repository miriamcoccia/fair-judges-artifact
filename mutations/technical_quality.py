"""
technical_quality.py: mutations that damage an image's resolution, contrast,
or legibility — testing whether the model detects poor technical quality.
"""

from PIL import Image, ImageFilter
from pathlib import Path

from mutations.base import (
    Mutation,
    MutatedItem,
    MutationType,
    Severity,
    build_mutated_path,
)
from domain.item import Item


class BlurMutation:
    RADIUS_BY_SEVERITY = {
        Severity.SUBTLE: 2,
        Severity.MODERATE: 6,
        Severity.OBVIOUS: 15,
    }

    def name(self) -> str:
        return "blur"

    def apply(self, item: Item, severity: Severity, seed: int) -> MutatedItem:
        original_path = Path(item.image)
        new_path = build_mutated_path(
            item.id, self.name(), severity, original_path.suffix
        )

        if new_path.exists():
            return MutatedItem(
                original=item,
                mutation_type=MutationType.TECHNICAL_QUALITY,
                severity=severity,
                mutated_image=str(new_path),
            )

        original_image = Image.open(original_path)
        blurred_image = original_image.filter(
            ImageFilter.GaussianBlur(self.RADIUS_BY_SEVERITY[severity])
        )
        blurred_image.save(new_path)

        return MutatedItem(
            original=item,
            mutation_type=MutationType.TECHNICAL_QUALITY,
            severity=severity,
            mutated_image=str(new_path),
        )
