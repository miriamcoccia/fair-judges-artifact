"""
test_figures.py: tests for plot_detection_by_severity.
"""

from pathlib import Path
from evaluation.figures import plot_detection_by_severity


def test_plot_creates_file(tmp_path):
    detection_rates = {
        "subtle": {"precision": 1.0, "recall": 0.5, "f1": 0.67},
        "obvious": {"precision": 1.0, "recall": 1.0, "f1": 1.0},
    }
    output_path = tmp_path / "chart.png"

    plot_detection_by_severity(detection_rates, output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
