"""Loop state snapshots (SNP-*) for rewind/restore."""
from __future__ import annotations

from .ids import IdGen

_SNAP_FIELDS = (
    "claims", "hyps", "experiments", "results", "failures",
    "agent_decisions", "human_decisions", "open_questions",
    "evidence_deltas", "next_actions",
)


def take(store, loop_id: str, state: dict) -> dict:
    """Write a SNP-* snapshot object capturing loop state. ts comes from state."""
    snap = {
        "id": IdGen(store).next("SNP"),
        "version": 1,
        "loop_id": loop_id,
        "ts": state.get("ts", "1970-01-01T00:00:00Z"),
        "created_at": state.get("ts", "1970-01-01T00:00:00Z"),
        "created_by": state.get("by", "system"),
        "provenance": [],
    }
    for f in _SNAP_FIELDS:
        snap[f] = state.get(f, [])
    store.put(snap)
    return snap


def restore(store, snapshot_id: str) -> dict:
    """Return the stored snapshot state dict."""
    return store.get(snapshot_id)
