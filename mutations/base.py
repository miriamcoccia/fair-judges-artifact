"""
base.py: defines the Mutation protocol, Severity levels, and the shared vocabulary for all damage types.
"""

from enum import StrEnum
from domain.item import Item
from dataclasses import dataclass
from typing import Protocol
from pathlib import Path

MUTATED_DIR = Path("data/mutated")


def build_mutated_path(
    item_id: str, mutation_name: str, severity: Severity, suffix: str
) -> Path:
    """
    Builds the standard output path for a mutated image:
    data/mutated/{item_id}/{mutation_name}_{severity}{suffix}
    """
    item_dir = MUTATED_DIR / item_id
    item_dir.mkdir(parents=True, exist_ok=True)
    return item_dir / f"{mutation_name}_{severity.value}{suffix}"


def build_mutated_path_no_severity(
    item_id: str, mutation_name: str, suffix: str
) -> Path:
    """
    Builds the standard output path for a mutated image with no severity:
    data/mutated/{item_id}/{mutation_name}{suffix}
    """
    item_dir = MUTATED_DIR / item_id
    item_dir.mkdir(parents=True, exist_ok=True)
    return item_dir / f"{mutation_name}{suffix}"


class Severity(StrEnum):
    SUBTLE = "subtle"
    MODERATE = "moderate"
    OBVIOUS = "obvious"


class MutationType(StrEnum):
    TECHNICAL_QUALITY = "technical_quality"
    STANDARD_PRESENTATION = "standard_presentation"
    VISUAL_CLARITY = "visual_clarity"
    FUNCTIONAL_RELEVANCE = "functional_relevance"
    FAIR_REPRESENTATION = "fair_representation"
    TEXT_IMAGE_COHERENCE = "text_image_coherence"
    FAIR_REPRESENTATION_CONTROL = "fair_representation_control"


@dataclass(frozen=True)
class MutatedItem:
    original: Item
    mutation_type: MutationType
    severity: Severity
    mutated_image: str


class Mutation(Protocol):
    def apply(self, item: Item, severity: Severity, seed: int) -> MutatedItem: ...

    def name(self) -> str: ...
