"""Epistemic state ladder and legal transitions."""
from __future__ import annotations

# Positive ladder (strengthening moves go up this list, one step at a time).
LADDER = [
    "UNVERIFIED",
    "LITERATURE_SUPPORTED",
    "EXPERIMENTALLY_TESTED",
    "REPRODUCED",
    "ROBUST",
    "ADVERSARIALLY_CHALLENGED",
    "HUMAN_REVIEWED",
]

# Negative / terminal-ish states reachable from anywhere.
NEGATIVE = {
    "WEAK_EVIDENCE",
    "INCONCLUSIVE",
    "CONTRADICTED",
    "FAILED_REPLICATION",
    "FALSIFIED",
    "BLOCKED",
}

ALL_STATES = set(LADDER) | NEGATIVE


class IllegalTransition(Exception):
    """Raised when a state transition is not permitted."""


def _build_legal() -> dict[str, set[str]]:
    legal: dict[str, set[str]] = {}
    for i, s in enumerate(LADDER):
        nxt: set[str] = set()
        if i + 1 < len(LADDER):
            nxt.add(LADDER[i + 1])  # one step up the ladder
        nxt |= NEGATIVE            # any state -> any negative
        legal[s] = nxt
    for s in NEGATIVE:
        # negatives can only move sideways into other negatives (e.g. re-classify)
        legal[s] = set(NEGATIVE) - {s}
    return legal


LEGAL: dict[str, set[str]] = _build_legal()


def can_transition(a: str, b: str) -> bool:
    """True if moving from state a to state b is legal."""
    return b in LEGAL.get(a, set())


def _is_strengthening(a: str, b: str) -> bool:
    """True if b is strictly higher on the positive ladder than a."""
    if a in LADDER and b in LADDER:
        return LADDER.index(b) > LADDER.index(a)
    return False


def transition(obj: dict, to: str, *, evidence: list, by: str, ts: str) -> dict:
    """Transition obj to a new epistemic state, recording state_history.

    Raises IllegalTransition if the move is not legal, or if it is a
    strengthening (up-ladder) move with empty evidence.
    """
    frm = obj.get("state", "UNVERIFIED")
    if to not in ALL_STATES:
        raise IllegalTransition(f"unknown state {to!r}")
    if not can_transition(frm, to):
        raise IllegalTransition(f"illegal transition {frm} -> {to}")
    if _is_strengthening(frm, to) and not evidence:
        raise IllegalTransition(f"strengthening {frm} -> {to} requires evidence")
    obj.setdefault("state_history", []).append(
        {"from": frm, "to": to, "evidence": list(evidence), "by": by, "ts": ts}
    )
    obj["state"] = to
    return obj
