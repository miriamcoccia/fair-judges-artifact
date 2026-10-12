"""
mlflow_tracker.py: MLflow implementation of the Tracker protocol.
"""

import mlflow


class MLflowTracker:
    def __init__(self):
        self.active_run = None

    def log_run_start(self, params: dict) -> None:
        mlflow.start_run()
        mlflow.log_params(params)

    def log_metrics(self, metrics: dict) -> None:
        mlflow.log_metrics(metrics)

    def log_run_end(self) -> None:
        mlflow.end_run()
