"""
test_tables.py: tests for detection_rate_table_latex and save_table.
"""

from pathlib import Path
from evaluation.tables import detection_rate_table_latex, save_table


def test_table_contains_all_severities():
    detection_rates = {
        "subtle": {"precision": 1.0, "recall": 0.5, "f1": 0.67},
        "obvious": {"precision": 1.0, "recall": 1.0, "f1": 1.0},
    }
    latex = detection_rate_table_latex(detection_rates)

    assert "Subtle" in latex
    assert "Obvious" in latex
    assert "0.50" in latex
    assert "1.00" in latex


def test_table_is_valid_latex_structure():
    detection_rates = {"subtle": {"precision": 1.0, "recall": 0.5, "f1": 0.67}}
    latex = detection_rate_table_latex(detection_rates)

    assert latex.startswith(r"\begin{table}")
    assert latex.endswith(r"\end{table}")
    assert r"\toprule" in latex
    assert r"\bottomrule" in latex


def test_save_table_writes_file(tmp_path):
    latex = r"\begin{table}test\end{table}"
    output_path = tmp_path / "test.tex"

    save_table(latex, output_path)

    assert output_path.exists()
    assert output_path.read_text() == latex
