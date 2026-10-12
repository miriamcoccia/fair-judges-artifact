"""
test_experiment_sample.py: tests for build_phase1_sample.
"""

import pandas as pd
import numpy as np
from data.experiment_sample import build_phase1_sample


def make_fake_dataframe(n_rows=100, seed=0):
    np.random.seed(seed)
    subjects = np.random.choice(
        ["math", "science", "history"], size=n_rows, p=[0.5, 0.3, 0.2]
    )
    return pd.DataFrame(
        {
            "subject": subjects,
            "question": [f"question {i}" for i in range(n_rows)],
        }
    )


def test_phase1_sample_size():
    fake_df = make_fake_dataframe(100, 0)
    sample_df = build_phase1_sample(fake_df, 0.1, "subject", 0)

    assert 8 < len(sample_df) < 12


def test_phase1_sample_preserves_columns():
    fake_df = make_fake_dataframe(100, 0)
    sample_df = build_phase1_sample(fake_df, 0.1, "subject", 0)

    assert list(fake_df.columns) == list(sample_df.columns)


def test_phase1_sample_is_reproducible():
    fake_df = make_fake_dataframe(100, 0)
    sample_df1 = build_phase1_sample(fake_df, 0.1, "subject", 0)
    sample_df2 = build_phase1_sample(fake_df, 0.1, "subject", 0)
    assert sample_df1.equals(sample_df2)
