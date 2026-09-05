"""Human-in-the-loop classification, gating, and approvals."""
from __future__ import annotations

from enum import Enum

from .ids import IdGen


class Level(str, Enum):
    AUTO = "AUTO"
    REVIEW = "REVIEW"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    BLOCKED = "BLOCKED"


# The five mandatory scientific approval checkpoints (SKILL.md / brief §14).
CHECKPOINTS = [
    "RESEARCH_QUESTION",
    "HYPOTHESIS",
    "PROTOCOL",
    "MAJOR_EXPERIMENT_BRANCH",
    "FINAL_CONCLUSION",
]

# action keyword -> Level
_POLICY = {
    "search paper": Level.AUTO,
    "search literature": Level.AUTO,
    "run simulation": Level.AUTO,
    "change methodology": Level.REVIEW,
    "external": Level.REQUIRE_APPROVAL,
    "irreversible": Level.REQUIRE_APPROVAL,
    "unsafe": Level.BLOCKED,
}


class HITL:
    """Classifies actions and manages approval gates persisted to the store."""

    def __init__(self, store):
        self.store = store

    def classify(self, action: str) -> Level:
        """Map an action string to a Level via the policy table (default REVIEW)."""
        a = action.lower()
        for key, level in _POLICY.items():
            if key in a:
                return level
        return Level.REVIEW

    def gate(self, checkpoint: str, payload: dict) -> dict:
        """Open a gate for a checkpoint. REQUIRE_APPROVAL/BLOCKED actions are
        PENDING (persisted, blocking); everything else auto-APPROVED."""
        action = payload.get("action", checkpoint)
        level = self.classify(action)
        status = "PENDING" if level in (Level.REQUIRE_APPROVAL, Level.BLOCKED) else "APPROVED"
        cp = {
            "id": IdGen(self.store).next("CHK"),
            "version": 1,
            "created_at": payload.get("ts", "1970-01-01T00:00:00Z"),
            "created_by": payload.get("by", "system"),
            "provenance": [],
            "kind": "checkpoint",
            "checkpoint": checkpoint,
            "action": action,
            "level": level.value,
            "status": status,
            "payload": payload,
        }
        self.store.put(cp)
        return {"status": status, "checkpoint_id": cp["id"]}

    def approve(self, checkpoint_id: str, human: str, decision: bool,
                note: str, ts: str) -> dict:
        """Record a human decision on a gate. A BLOCKED gate cannot proceed."""
        cp = self.store.get(checkpoint_id)
        if cp.get("level") == Level.BLOCKED.value:
            result = {"checkpoint_id": checkpoint_id, "status": "BLOCKED",
                      "human": human, "note": note}
            self._record(cp, result, ts)
            return result
        status = "APPROVED" if decision else "REJECTED"
        result = {"checkpoint_id": checkpoint_id, "status": status,
                  "human": human, "decision": decision, "note": note}
        self._record(cp, result, ts)
        return result

    def _record(self, cp: dict, result: dict, ts: str) -> None:
        """Persist the approval as a new version of the checkpoint object."""
        new = dict(cp)
        new["version"] = cp["version"] + 1
        new["status"] = result["status"]
        new["human_approval"] = {**result, "ts": ts}
        self.store.put(new)
