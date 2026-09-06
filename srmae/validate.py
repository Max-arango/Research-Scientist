"""Hand-rolled, stdlib-only schema validator for the spine objects.

Loads the Draft-07 JSON Schemas from `schemas/` and checks:
  - every key in `required[]` is present in `obj`
  - every enum constraint on a property is honored

It does NOT do full JSON Schema (no $ref resolution, no numeric ranges, no
pattern matching). The contracts are enforced in the cognitive layer; this
module is a sanity net for the machine layer.

Usage:
    from srmae.validate import validate
    validate(store.root, "CLM", obj)  # raises SchemaError if invalid

Or activate via `new_object(..., validate=True)`.
"""
from __future__ import annotations

import json
from pathlib import Path

# Map prefix -> filename in schemas/.
_PREFIX_TO_SCHEMA = {
    "SRC": "source.json",
    "CLM": "claim.json",
    "HYP": "hypothesis.json",
    "PRO": "protocol.json",
    "EXP": "experiment.json",
    "RES": "result.json",
    "ANL": "outcome.json",       # no ANALYSIS schema shipped yet
    "CRT": "critique.json",
    "VER": "verdict.json",
    "SNP": "snapshot.json",
    "DSP": "dispute.json",
    "FLR": "failure.json",
    "EVT": "loop.json",          # not a spine schema
    "CHK": "checkpoint.json",    # not a spine schema
}


class SchemaError(ValueError):
    """Raised when an object fails schema validation."""


def _schema_path(store_root: str, prefix: str) -> Path | None:
    name = _PREFIX_TO_SCHEMA.get(prefix)
    if name is None:
        return None
    # Schemas live one level above the srmae/ package: scientific-research-mae/schemas/
    candidates = [
        Path(store_root).parent.parent / "schemas" / name,
        Path(store_root).parent / "schemas" / name,
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _load_schema(store_root: str, prefix: str) -> dict | None:
    path = _schema_path(store_root, prefix)
    if path is None or not path.exists():  # noqa
        return None
    with path.open() as f:
        return json.load(f)


def validate(store_root: str, prefix: str, obj: dict) -> None:
    """Check obj against the spine schema for `prefix`. Raises SchemaError.

    Checks:
      - all keys in `required[]` are present in obj
      - enum constraints are honored (only when `additionalProperties: false`
        so the schema's `properties` block declares the field)

    No-op (silently returns) when no schema is registered for `prefix`. This
    keeps the validator backwards-compatible with brands like FLR that may
    grow schemas later without breaking today.
    """
    schema = _load_schema(store_root, prefix)
    if schema is None:
        return
    required = schema.get("required", []) or []
    properties = schema.get("properties", {}) or {}
    missing = [k for k in required if k not in obj]
    if missing:
        raise SchemaError(f"{prefix}: missing required keys {missing}")
    # Enum checks: only when the schema declared `additionalProperties: false`,
    # we can trust `properties` to be exhaustive. Schemas without that flag
    # allow extras, so we check enums on the keys that ARE present.
    for k, spec in properties.items():
        if "enum" not in spec:
            continue
        if k not in obj or obj[k] is None:
            continue
        v = obj[k]
        if isinstance(v, list):
            bad = [x for x in v if x not in spec["enum"]]
            if bad:
                raise SchemaError(
                    f"{prefix}.{k}: values {bad} not in {spec['enum']}")
        elif v not in spec["enum"]:
            raise SchemaError(
                f"{prefix}.{k}: {v!r} not in {spec['enum']}")