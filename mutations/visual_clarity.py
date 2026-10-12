"""
visual_clarity.py: mutations that add visual clutter — random shapes —
testing whether the model detects reduced visual clarity.
"""

import random
from pathlib import Path
from PIL import Image, ImageDraw

from domain.item import Item
from mutations.base import MutatedItem, MutationType, Severity, build_mutated_path


class ClarityMutation:
    SHAPE_COUNT_BY_SEVERITY = {
        Severity.SUBTLE: 2,
        Severity.MODERATE: 5,
        Severity.OBVIOUS: 10,
    }
    SHAPE_SIZE_FRACTION_BY_SEVERITY = {
        Severity.SUBTLE: 0.05,
        Severity.MODERATE: 0.10,
        Severity.OBVIOUS: 0.20,
    }

    def name(self) -> str:
        return "clarity_shapes"

    def apply(self, item: Item, severity: Severity, seed: int) -> MutatedItem:
        original_path = Path(item.image)
        new_path = build_mutated_path(
            item.id, self.name(), severity, original_path.suffix
        )

        if new_path.exists():
            return MutatedItem(
                original=item,
                mutation_type=MutationType.VISUAL_CLARITY,
                severity=severity,
                mutated_image=str(new_path),
            )

        original_image = Image.open(original_path)
        copied_image = original_image.copy()
        draw = ImageDraw.Draw(copied_image)
        rng = random.Random(seed)

        width, height = copied_image.size
        fraction = self.SHAPE_SIZE_FRACTION_BY_SEVERITY[severity]
        shape_size = int(min(width, height) * fraction)
        shape_count = self.SHAPE_COUNT_BY_SEVERITY[severity]

        for _ in range(shape_count):
            x = rng.randint(0, width - shape_size)
            y = rng.randint(0, height - shape_size)
            color = (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
            draw.ellipse([x, y, x + shape_size, y + shape_size], fill=color)

        copied_image.save(new_path)

        return MutatedItem(
            original=item,
            mutation_type=MutationType.VISUAL_CLARITY,
            severity=severity,
            mutated_image=str(new_path),
        )
