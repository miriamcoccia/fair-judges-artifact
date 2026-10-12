"""
item.py: defines what a question item is. For the scope of this project, it must contain an image.
"""
from dataclasses import dataclass
from typing import Tuple
from domain.errors import ItemError

@dataclass(frozen=True)
class Item:
    id: str
    question: str
    choices: Tuple[str, ...]
    answer: int
    hint: str
    image: str
    task: str
    grade: str
    subject: str
    topic: str
    category: str
    skill: str
    lecture: str
    solution: str
    split: str

    def __post_init__(self):
        if len(self.choices) == 0:
            raise ItemError("No multiple-choice options were provided.")
        if not (0 <= self.answer < len(self.choices)):
            raise ItemError("The answer should be chosen from one of the available options.")
        
