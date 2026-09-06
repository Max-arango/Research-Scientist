"""Scientific Research Operating System — core (srmae).

Standard-library-only, reproducible (no datetime.now/random inside), append-only.
"""
from __future__ import annotations

from .storage import Store
from .ids import IdGen, VALID_PREFIXES
from .objects import Value, is_valid_value, new_object, VALUE_KINDS
from .epistemic import (
    LADDER, NEGATIVE, LEGAL, can_transition, transition, IllegalTransition,
)
from .evidence import EvidenceState, assess, suggested_state, confidence
from .provenance import Provenance, REL
from . import snapshots
from .loops import LoopEngine, PHASES, DECISIONS
from .hitl import HITL, Level, CHECKPOINTS
from .safety import SafetyClass, review
from .failures import log_failure, FAILURE_TYPES
from .disputes import Dispute, needs_human
from . import metrics
from . import events
from .validate import validate, SchemaError

__all__ = [
    "Store", "IdGen", "VALID_PREFIXES",
    "Value", "is_valid_value", "new_object", "VALUE_KINDS",
    "LADDER", "NEGATIVE", "LEGAL", "can_transition", "transition", "IllegalTransition",
    "EvidenceState", "assess", "suggested_state", "confidence",
    "Provenance", "REL",
    "snapshots",
    "LoopEngine", "PHASES", "DECISIONS",
    "HITL", "Level", "CHECKPOINTS",
    "SafetyClass", "review",
    "log_failure", "FAILURE_TYPES",
    "Dispute", "needs_human",
    "metrics", "events",
    "validate", "SchemaError",
]
