"""Multi-agent disputes (DSP-*)."""
from __future__ import annotations

from .ids import IdGen


class Dispute:
    """Opens and resolves disagreements between agents, persisted as DSP-*."""

    @staticmethod
    def open(store, topic: str, agents: list, positions: list,
             evidence: list, ts: str, severity: str = "normal") -> str:
        dsp = {
            "id": IdGen(store).next("DSP"),
            "version": 1,
            "created_at": ts,
            "created_by": "system",
            "provenance": [],
            "topic": topic,
            "agents": list(agents),
            "positions": list(positions),
            "evidence": list(evidence),
            "severity": severity,
            "status": "OPEN",
            "resolution": None,
        }
        store.put(dsp)
        return dsp["id"]

    @staticmethod
    def resolve(store, id: str, how: str, ts: str) -> dict:
        dsp = store.get(id)
        new = dict(dsp)
        new["version"] = dsp["version"] + 1
        new["status"] = "RESOLVED"
        new["resolution"] = how
        new["resolved_at"] = ts
        store.put(new)
        return new


def needs_human(dispute: dict) -> bool:
    """True if the dispute is high severity or asks for human review."""
    return dispute.get("severity") == "high" or dispute.get("resolution") == "human_review"
