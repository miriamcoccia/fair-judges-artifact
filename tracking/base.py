"""
base.py: defines the Tracker protocol every tracking backend must implement,
and NullTracker, the default no-op implementation.
"""

from typing import Protocol


class Tracker(Protocol):
    def log_run_start(self, params: dict) -> None: ...

    def log_metrics(self, metrics: dict) -> None: ...

    def log_run_end(self) -> None: ...


class NullTracker:
    def __init__(self): ...

    def log_run_start(self, params: dict) -> None:
        pass

    def log_metrics(self, metrics: dict) -> None:
        pass

    def log_run_end(self) -> None:
        pass
