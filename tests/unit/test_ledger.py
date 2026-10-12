"""
test_ledger.py: tests for Ledger.
"""

from pathlib import Path
from execution.ledger import Ledger


def test_add_batch(tmp_path):
    ledger_path = tmp_path / "ledger.txt"
    ledger = Ledger(ledger_path)
    ledger.add_batch("abc123")
    assert "abc123" in ledger.get_pending()


def test_remove_batch(tmp_path):
    ledger_path = tmp_path / "ledger.txt"
    ledger = Ledger(ledger_path)
    ledger.add_batch("abc123")
    ledger.remove_batch("abc123")
    assert "abc123" not in ledger.get_pending()


def test_ledger_persists_across_restart(tmp_path):
    ledger_path = tmp_path / "ledger.txt"
    ledger1 = Ledger(ledger_path)
    ledger1.add_batch("abc123")
    ledger2 = Ledger(ledger_path)  # simulates a fresh restart
    assert "abc123" in ledger2.get_pending()
