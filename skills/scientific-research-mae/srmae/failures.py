"""Append-only failure log (FLR-*)."""
from __future__ import annotations

from .ids import IdGen

# Canonical 11-type taxonomy (design brief §20). Failures are data, not noise.
FAILURE_TYPES = [
    "SCIENTIFIC",            # a hypothesis/claim did not hold
    "EXPERIMENTAL",          # the experiment itself misbehaved
    "REPRODUCIBILITY",       # could not reproduce a prior result
    "STATISTICAL",           # invalid/insufficient statistical treatment
    "TECHNICAL",             # code/runtime error
    "TOOL",                  # an external tool failed
    "SOURCE",                # a source was unretrievable/unreliable
    "AGENT",                 # an agent produced unusable output
    "COORDINATION",          # orchestration/handoff breakdown
    "HUMAN_BLOCK",           # a human rejected/blocked progress
    "CAPABILITY_LIMITATION", # the system cannot do what was asked
]


def log_failure(store, *, type: str, what: str, why: str, impact: str,
                affected: list, resolution: str, reproducible: bool,
                changes_conclusions: bool, ts: str) -> str:
    """Persist a FLR-* failure record (never deleted). Validates type."""
    if type not in FAILURE_TYPES:
        raise ValueError(f"unknown failure type {type!r}")
    flr = {
        "id": IdGen(store).next("FLR"),
        "version": 1,
        "created_at": ts,
        "created_by": "system",
        "provenance": [],
        "type": type,
        "what": what,
        "why": why,
        "impact": impact,
        "affected": list(affected),
        "resolution": resolution,
        "reproducible": reproducible,
        "changes_conclusions": changes_conclusions,
    }
    store.put(flr)
    return flr["id"]
