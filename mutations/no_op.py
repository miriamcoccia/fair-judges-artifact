"""
no_op.py: a control mutation that does NOT damage the image at all —
returns the original, unmutated image. Used to establish a baseline for
how often a model flags a property on genuinely undamaged content.
"""

from pathlib import Path

from domain.item import Item
from mutations.base import MutatedItem, MutationType, Severity


class NoOpMutation:
    def name(self) -> str:
        return "no_op_control"

    def apply(self, item: Item, severity: Severity, seed: int) -> MutatedItem:
        return MutatedItem(
            original=item,
            mutation_type=MutationType.FAIR_REPRESENTATION,
            severity=severity,
            mutated_image=item.image,
        )
