"""
integrity_checks.py: two checks needed before the paper numbers are final.

1. Batch alignment. runner.py pairs batch responses with requests by
   position (zip). This script downloads the input and output file of every
   batch found in the run logs and checks that the output custom_ids are in
   exactly the same order as the input custom_ids, and that no request failed.

2. RQ1 baseline. Recomputes the per-property flag rate on the unmodified
   control (fair_representation_control), per model, for Table RQ1 and the
   baseline row of the collateral table.

Usage:
    uv run python -m evaluation.integrity_checks runs/*.txt nohup.out
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from openai import OpenAI

from evaluation.load import load_results

BATCH_ID = re.compile(r"batch_[0-9a-f]{32}")
MODELS = {"gpt5.6-luna", "gpt5.6-terra"}


def batch_ids_from_logs(paths: list[str]) -> list[str]:
    ids = []
    for p in paths:
        for match in BATCH_ID.findall(Path(p).read_text(errors="ignore")):
            if match not in ids:
                ids.append(match)
    return ids


def custom_ids(client: OpenAI, file_id: str | None) -> list[str]:
    if file_id is None:
        return []
    text = client.files.content(file_id).text
    return [json.loads(line)["custom_id"] for line in text.splitlines() if line.strip()]


def check_batches(paths: list[str]) -> None:
    client = OpenAI()
    ids = batch_ids_from_logs(paths)
    print(f"Checking {len(ids)} batches")
    problems = 0
    for batch_id in ids:
        batch = client.batches.retrieve(batch_id)
        try:
            inputs = custom_ids(client, batch.input_file_id)
            outputs = custom_ids(client, batch.output_file_id)
            errors = custom_ids(client, batch.error_file_id)
        except Exception as e:
            print(f"{batch_id}  {batch.status:10s}  could not download files: {e}")
            problems += 1
            continue

        if inputs == outputs and not errors:
            status = "OK"
        elif sorted(inputs) == sorted(outputs) and not errors:
            status = "REORDERED"
        else:
            status = f"MISSING {len(inputs) - len(outputs)} (errors: {len(errors)})"
        if status != "OK":
            problems += 1
        print(
            f"{batch_id}  {batch.status:10s}  in={len(inputs):5d} out={len(outputs):5d}  {status}"
        )
    print(f"\n{problems} batch(es) need attention")


def baseline_rates() -> None:
    results = [
        r
        for r in load_results(Path("runs/results"))
        if r.model in MODELS and r.mutation_type == "fair_representation_control"
    ]
    flagged = defaultdict(int)
    totals = defaultdict(int)
    properties = set()
    for r in results:
        totals[r.model] += 1
        for v in r.verdicts:
            properties.add(str(v.property))
            if not v.passed:
                flagged[(r.model, str(v.property))] += 1

    print("\nRQ1 baseline flag rates (%), unmodified control")
    for model in sorted(totals):
        print(f"{model}  n={totals[model]}")
        for prop in sorted(properties):
            rate = 100 * flagged[(model, prop)] / totals[model]
            print(f"    {prop:24s} {rate:5.1f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python -m evaluation.integrity_checks <log files...>")
    check_batches(sys.argv[1:])
    baseline_rates()
