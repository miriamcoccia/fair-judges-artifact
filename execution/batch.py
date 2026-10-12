"""
batch.py: splits a list of PromptRequests into properly-sized chunks
for submission, respecting provider request-count limits.
"""

from providers.base import PromptRequest


def chunk_requests(
    requests: list[PromptRequest], max_per_batch: int
) -> list[list[PromptRequest]]:
    """
    Splits requests into groups of at most max_per_batch each.
    """
    chunks = []
    for i in range(0, len(requests), max_per_batch):
        chunk = requests[i : i + max_per_batch]
        chunks.append(chunk)
    return chunks
