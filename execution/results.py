"""
results.py: saves the full result of one completed unit of work to disk —
the source of truth for evaluation, separate from MLflow's summary mirror.
"""

import json
from pathlib import Path
from domain.verdict import Verdict

RESULTS_DIR = Path("runs/results")


def save_result(
    fingerprint: str,
    item_id: str,
    mutation_type: str,
    severity: str,
    model: str,
    strategy: str,
    verdicts: list[Verdict],
    cost: float,
    input_tokens: int,
    output_tokens: int,
) -> None:
    """
    Saves one completed unit's full result as a JSON file, named by fingerprint.
    """
    results_dict = {
        "item_id": item_id,
        "mutation_type": mutation_type,
        "severity": severity,
        "model": model,
        "strategy": strategy,
        "verdicts": [v.model_dump() for v in verdicts],
        "cost": float(cost),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    outpath = RESULTS_DIR / f"{fingerprint}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(results_dict, f)
