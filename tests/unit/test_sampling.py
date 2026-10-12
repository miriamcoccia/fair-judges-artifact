"""
test_sampling.py: tests for stratidied_sample.
"""

import pandas as pd
import numpy as np
from data.sampling import stratified_sample


def make_stratified_dataframe(n_rows=100, seed=0):
    np.random.seed(seed)
    subjects = np.random.choice(["math", "geography"], size=n_rows, p=[0.7, 0.3])
    return pd.DataFrame(
        {
            "subject": subjects,
            "question": [f"question {i}" for i in range(n_rows)],
        }
    )


def test_stratified_sample_preserves_columns():
    df = make_stratified_dataframe()
    sample = stratified_sample(df, n=20, stratify_by="subject", seed=42)
    assert list(sample.columns) == ["subject", "question"]


def test_stratified_sample_returns_roughly_requested_size():
    df = make_stratified_dataframe()
    sample = stratified_sample(df, n=20, stratify_by="subject", seed=42)
    # rounding per group means exact size isn't guaranteed, but should be close
    assert 15 <= len(sample) <= 25


def test_stratified_sample_is_reproducible():
    df = make_stratified_dataframe()
    sample_1 = stratified_sample(df, n=20, stratify_by="subject", seed=42)
    sample_2 = stratified_sample(df, n=20, stratify_by="subject", seed=42)
    assert sample_1.equals(sample_2)
