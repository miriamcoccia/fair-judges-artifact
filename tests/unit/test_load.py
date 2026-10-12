"""
test_load.py: tests for load_results.
"""

from pathlib import Path
from evaluation.load import load_results
from execution.results import save_result
from domain.verdict import Verdict
from domain.properties import QualityProperty


def test_load_results_reads_saved_files(tmp_path, monkeypatch):
    import execution.results

    monkeypatch.setattr(execution.results, "RESULTS_DIR", tmp_path)

    verdicts = [
        Verdict(
            property=QualityProperty.TECHNICAL_QUALITY, passed=False, reasoning="blurry"
        )
    ]
    save_result(
        fingerprint="fp1",
        item_id="q1",
        mutation_type="technical_quality",
        severity="obvious",
        model="gpt5.6",
        strategy="split",
        verdicts=verdicts,
        cost=0.0003,
        input_tokens=1000,
        output_tokens=50,
    )

    results = load_results(tmp_path)
    assert len(results) == 1
    assert results[0].item_id == "q1"
    assert results[0].verdicts[0].property == QualityProperty.TECHNICAL_QUALITY
