"""Core Value type and generic object factory."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

VALUE_KINDS = {
    "FACT", "INFERENCE", "HYPOTHESIS", "RESULT", "INTERPRETATION",
    "OPINION", "UNKNOWN", "UNCERTAIN", "CONTRADICTED",
}

_DEFAULT_TS = "1970-01-01T00:00:00Z"


@dataclass
class Value:
    """An epistemically-tagged value. FACT/RESULT with no support is invalid."""

    kind: str
    content: Any
    support: list[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict:
        return {"kind": self.kind, "content": self.content,
                "support": list(self.support), "note": self.note}


def is_valid_value(v: Value) -> bool:
    """A Value of kind RESULT or FACT with empty support is INVALID."""
    if v.kind not in VALUE_KINDS:
        return False
    if v.kind in ("RESULT", "FACT") and not v.support:
        return False
    return True


def new_object(store, idgen, prefix: str, by: str, ts: str = _DEFAULT_TS, **fields) -> dict:
    """Stamp and persist a new object. ts is passed in (never datetime.now)."""
    obj = {
        "id": idgen.next(prefix),
        "version": 1,
        "created_at": ts,
        "created_by": by,
        "provenance": [],
    }
    obj.update(fields)
    store.put(obj)
    return obj
