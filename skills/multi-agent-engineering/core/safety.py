"""Safety review of proposed actions."""
from __future__ import annotations

from enum import Enum


class SafetyClass(str, Enum):
    SAFE_AUTONOMOUS = "SAFE_AUTONOMOUS"
    SUPERVISED = "SUPERVISED"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    BLOCKED = "BLOCKED"


# Keyword -> (class, reason). Highest severity wins.
_BLOCKED = ("pathogen", "explosive", "bioweapon", "chemical_weapon")
_HUMAN = (
    "physical", "irreversible", "regulated", "bio", "chem",
    "human_subjects", "cyber-offensive", "cyber_offensive", "exploit",
)
_SAFE = ("simulation", "literature", "search paper")


def review(action: dict) -> tuple[SafetyClass, list[str]]:
    """Classify an action dict and return (SafetyClass, reasons).

    Inspects the action's 'type'/'description' text and boolean flags such as
    irreversible/physical/human_subjects.
    """
    text = " ".join(
        str(action.get(k, "")) for k in ("type", "description", "action", "domain")
    ).lower()
    reasons: list[str] = []

    def flag(k: str) -> bool:
        return bool(action.get(k))

    # BLOCKED: hard-stop hazards.
    for kw in _BLOCKED:
        if kw in text:
            reasons.append(f"hazard keyword {kw!r} -> BLOCKED")
            return SafetyClass.BLOCKED, reasons

    # HUMAN_APPROVAL_REQUIRED: real-world / regulated / offensive.
    for kw in _HUMAN:
        if kw in text:
            reasons.append(f"keyword {kw!r} requires human approval")
    for fk in ("irreversible", "physical", "human_subjects", "regulated"):
        if flag(fk):
            reasons.append(f"flag {fk} set requires human approval")
    if reasons:
        return SafetyClass.HUMAN_APPROVAL_REQUIRED, reasons

    # SAFE_AUTONOMOUS: pure simulation / literature.
    for kw in _SAFE:
        if kw in text:
            reasons.append(f"{kw} is safe autonomous")
            return SafetyClass.SAFE_AUTONOMOUS, reasons

    reasons.append("no hazard signals; supervised by default")
    return SafetyClass.SUPERVISED, reasons
