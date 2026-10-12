"""
verdict.py: This file creates a Pydantic schema to handle the format of the model's response.
"""

from pydantic import BaseModel, ConfigDict, model_validator
from typing_extensions import Self
from domain.properties import QualityProperty
from domain.errors import VerdictError


class Verdict(BaseModel):
    model_config = ConfigDict(frozen=True)

    property: QualityProperty
    passed: bool
    reasoning: str

    @model_validator(mode="after")
    def check_reasoning_matches_verdict(self) -> Self:
        """
        The reasoning should only be provided if the verdict returns passed=False.
        """
        if self.passed and len(self.reasoning) > 0:
            raise VerdictError(
                "The reasoning should only be provided if a trait did not pass."
            )
        if not self.passed and len(self.reasoning) == 0:
            raise VerdictError(
                "The reasoning can't be empty if the trait did not pass."
            )
        return self
