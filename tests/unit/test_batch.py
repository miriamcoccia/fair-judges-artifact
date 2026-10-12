"""
test_batch.py: tests for chunk_requests.
"""

from providers.base import PromptRequest
from execution.batch import chunk_requests


def test_chunk_requests_splits_evenly():
    requests = [
        PromptRequest(custom_id=f"q{i}", prompt="test", endpoint="test")
        for i in range(10)
    ]
    chunks = chunk_requests(requests, max_per_batch=5)
    assert len(chunks) == 2
    assert len(chunks[0]) == 5
    assert len(chunks[1]) == 5


def test_chunk_requests_handles_remainder():
    requests = [
        PromptRequest(custom_id=f"q{i}", prompt="test", endpoint="test")
        for i in range(12)
    ]
    chunks = chunk_requests(requests, max_per_batch=5)
    assert len(chunks) == 3
    assert len(chunks[0]) == 5
    assert len(chunks[1]) == 5
    assert len(chunks[2]) == 2


def test_chunk_requests_single_chunk_if_under_limit():
    requests = [
        PromptRequest(custom_id=f"q{i}", prompt="test", endpoint="test")
        for i in range(2)
    ]
    chunks = chunk_requests(requests, max_per_batch=5)
    assert len(chunks) == 1
    assert len(chunks[0]) == 2
