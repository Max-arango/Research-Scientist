"""Research loop engine: phases, decisions, and stall detection."""
from __future__ import annotations

from .ids import IdGen

PHASES = [
    "QUESTION",
    "LITERATURE",
    "HYPOTHESIS",
    "PROTOCOL",
    "EXPERIMENT",
    "ANALYSIS",
    "CRITIQUE",
    "VERDICT",
]

DECISIONS = ("CONTINUE", "REWIND", "BRANCH", "ESCALATE", "TERMINATE")

_STALL_THRESHOLD = 2


class LoopEngine:
    """Drives research loops and decides control-flow from signals."""

    def __init__(self, store, hitl, safety):
        self.store = store
        self.hitl = hitl
        self.safety = safety

    def start_loop(self, phase: str) -> str:
        """Register a persisted loop and return its id."""
        loop = {
            "id": IdGen(self.store).next("EVT"),
            "version": 1,
            "created_at": "1970-01-01T00:00:00Z",
            "created_by": "system",
            "provenance": [],
            "kind": "loop",
            "phase": phase,
            "status": "OPEN",
        }
        self.store.put(loop)
        return loop["id"]

    def decide(self, signals: dict) -> str:
        """Map loop signals to a control decision."""
        if signals.get("unsafe") or signals.get("unresolved_dispute"):
            return "ESCALATE"
        if signals.get("new_confounder"):
            return "REWIND"
        if signals.get("falsified"):
            # falsified hypothesis: rewind to try again unless nothing left.
            return "TERMINATE" if signals.get("exhausted") else "REWIND"
        if signals.get("new_subquestion"):
            return "BRANCH"
        if signals.get("all_criteria_met"):
            return "TERMINATE"
        return "CONTINUE"

    def stalled(self, history: list) -> bool:
        """True if the same finding signature repeats, or no progress is made,
        across at least stall_threshold entries."""
        if len(history) < _STALL_THRESHOLD:
            return False
        sigs = [h.get("signature") if isinstance(h, dict) else h for h in history]
        tail = sigs[-_STALL_THRESHOLD:]
        return all(s == tail[0] for s in tail)
