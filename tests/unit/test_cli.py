"""
test_cli.py: tests for the CLI commands.
"""

import pandas as pd
from typer.testing import CliRunner

from cli import app

runner = CliRunner()


def test_sample_command(tmp_path):
    input_csv = tmp_path / "input.csv"
    output_csv = tmp_path / "output.csv"

    df = pd.DataFrame(
        {
            "subject": ["math"] * 50 + ["science"] * 50,
            "question": [f"q{i}" for i in range(100)],
        }
    )
    df.to_csv(input_csv, index=False)

    result = runner.invoke(
        app,
        [
            "sample",
            "--input-csv",
            str(input_csv),
            "--output-csv",
            str(output_csv),
            "--fraction",
            "0.1",
        ],
    )

    assert result.exit_code == 0
    assert output_csv.exists()

    sample_df = pd.read_csv(output_csv)
    assert 8 <= len(sample_df) <= 12
