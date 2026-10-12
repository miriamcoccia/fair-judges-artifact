"""
ledger.py: tracks batches that have been submitted but not yet fetched,
so a crash while waiting doesn't lose track of paid-for, in-flight batches.
"""

from pathlib import Path


class Ledger:
    def __init__(self, ledger_path: Path):
        self.ledger_path = ledger_path
        self.pending: set[str] = set()
        if self.ledger_path.exists():
            with open(self.ledger_path) as f:
                for line in f:
                    self.pending.add(line.strip())

    def add_batch(self, batch_id: str) -> None:
        self.pending.add(batch_id)
        with open(self.ledger_path, "a") as f:
            f.write(batch_id + "\n")

    def remove_batch(self, batch_id: str) -> None:
        self.pending.remove(batch_id)
        with open(self.ledger_path, "w") as f:
            for pending_id in self.pending:
                f.write(pending_id + "\n")

    def get_pending(self) -> set[str]:
        return self.pending
