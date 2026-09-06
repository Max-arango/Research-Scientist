"""Sequential zero-padded id generator persisted through the store."""
from __future__ import annotations

VALID_PREFIXES = {
    "SRC", "CLM", "HYP", "PRO", "EXP", "RES",
    "ANL", "CRT", "VER", "SNP", "DSP", "FLR", "EVT",
    "CHK",  # HITL checkpoints — distinct from verdicts (VER)
}


class IdGen:
    """Generates ids like 'CLM-00001'; counters persist via the store so a
    restart on the same root continues the sequence."""

    def __init__(self, store):
        self.store = store

    def next(self, prefix: str) -> str:
        if prefix not in VALID_PREFIXES:
            raise ValueError(f"unknown prefix {prefix!r}")
        n = self.store.counters().get(prefix, 0) + 1
        self.store.set_counter(prefix, n)
        return f"{prefix}-{n:05d}"
