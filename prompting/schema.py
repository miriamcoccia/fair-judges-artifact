"""
schema.py: defines the expected shape of an AI model's response, covering both the split (single-property)
and combined (multi-property) strategies.
"""

from pydantic import BaseModel, ConfigDict, model_validator
from domain.verdict import Verdict


class VerdictResponse(BaseModel):
    """
    The AI's response to a prompt: one or more Verdicts,
    depending on whether the prompt was split or combined.
    """

    model_config = ConfigDict(extra="forbid")

    verdicts: list[Verdict]

    @model_validator(mode="after")
    def check_no_duplicate_properties(self) -> Self:
        properties = [v.property for v in self.verdicts]
        if len(properties) != len(set(properties)):
            raise ValueError("Duplicate QualityProperty found in verdicts.")
        return self
