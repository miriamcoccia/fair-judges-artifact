"""
standard_presentation.py: mutations that damage an image's orientation, testing whether the model detects non-standard presentation.
"""

from pathlib import Path
from PIL import Image

from domain.item import Item
from mutations.base import MutatedItem, MutationType, Severity, build_mutated_path


class RotateMutation:
    ANGLE_BY_SEVERITY = {
        Severity.SUBTLE: 15,
        Severity.MODERATE: 90,
        Severity.OBVIOUS: 180,
    }

    def name(self) -> str:
        return "rotate"

    def apply(self, item: Item, severity: Severity, seed: int) -> MutatedItem:
        original_path = Path(item.image)
        new_path = build_mutated_path(
            item.id, self.name(), severity, original_path.suffix
        )

        if new_path.exists():
            return MutatedItem(
                original=item,
                mutation_type=MutationType.STANDARD_PRESENTATION,
                severity=severity,
                mutated_image=str(new_path),
            )

        original_image = Image.open(original_path)
        rotated_image = original_image.rotate(
            self.ANGLE_BY_SEVERITY[severity], expand=True
        )
        rotated_image.save(new_path)

        return MutatedItem(
            original=item,
            mutation_type=MutationType.STANDARD_PRESENTATION,
            severity=severity,
            mutated_image=str(new_path),
        )
