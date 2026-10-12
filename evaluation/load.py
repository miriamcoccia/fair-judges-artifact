"""
load.py: reads saved run results from disk, into a form metrics.py can use.
"""

import json
from pathlib import Path
from dataclasses import dataclass

from domain.verdict import Verdict


@dataclass(frozen=True)
class LoadedResult:
    item_id: str
    mutation_type: str
    severity: str
    model: str
    strategy: str
    verdicts: list[Verdict]
    cost: float
    input_tokens: int
    output_tokens: int


def load_results(results_dir: Path) -> list[LoadedResult]:
    """
    Reads every saved result JSON file in results_dir, returns them as
    a list of LoadedResult objects.
    """
    results = []
    for file in results_dir.glob("*.json"):
        with open(file) as f:
            data = json.load(f)
            verdict_list = [Verdict(**v) for v in data["verdicts"]]
            result = LoadedResult(
                data["item_id"],
                data["mutation_type"],
                data["severity"],
                data["model"],
                data["strategy"],
                verdict_list,
                data["cost"],
                data["input_tokens"],
                data["output_tokens"],
            )
            results.append(result)
    return results
