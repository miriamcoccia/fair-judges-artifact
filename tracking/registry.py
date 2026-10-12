"""
registry.py: maps tracker names to their classes.
"""

from tracking.base import Tracker, NullTracker
from tracking.mlflow_tracker import MLflowTracker

TRACKERS: dict[str, type] = {"mlflow": MLflowTracker, "null": NullTracker}


def get_tracker(name: str, *args, **kwargs) -> Tracker:
    if name not in TRACKERS:
        raise ValueError(f"Unknown tracker: {name}")
    tracker_class = TRACKERS[name]
    return tracker_class(*args, **kwargs)
