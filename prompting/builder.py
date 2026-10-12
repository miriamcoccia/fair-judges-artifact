"""
builder.py: renders prompts from the Jinja template, given an item and
a list of quality properties to evaluate (1 for split, 6 for combined).
"""

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pathlib import Path
import hashlib

from domain.item import Item
from domain.properties import QualityProperty, rubric_for

TEMPLATE_DIR = Path(__file__).parent / "templates"

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    undefined=StrictUndefined,
)


def build_prompt(item: Item, properties: list[QualityProperty]) -> str:
    template = env.get_template("combined.jinja")

    prop_data = [
        {"name": prop.value, "definition": rubric_for(prop).definition}
        for prop in properties
    ]

    return template.render(
        characteristics=f"Grade: {item.grade}, Subject: {item.subject}, Topic: {item.topic}",
        question=item.question,
        properties=prop_data,
    )


def hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()
