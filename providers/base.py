"""
base.py: defines RawResponse (a normalized, provider-agnostic response)
and the BatchProvider protocol every provider must implement.
"""

from dataclasses import dataclass
from typing import Protocol
from enum import StrEnum


class BatchStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class RawResponse:
    custom_id: str
    content: str
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class PromptRequest:
    custom_id: str
    prompt: str
    endpoint: str
    image_path: str | None = None

    def __post_init__(self):
        if len(self.custom_id) == 0:
            raise ValueError("The field `custom_id` can't be empty.")
        if len(self.prompt) == 0:
            raise ValueError("The field `prompt` can't be empty.")


class BatchProvider(Protocol):

    def submit_batch(self, requests: list[PromptRequest]) -> str: ...
    def check_batch_status(self, batch_id: str) -> BatchStatus: ...
    def fetch_batch(self, batch_id: str) -> list[RawResponse]: ...
