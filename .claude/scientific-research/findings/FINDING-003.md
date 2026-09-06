---
id: FINDING-003
title: JSON Schemas not enforced by code; only by cognitive layer
severity: LOW
status: RESOLVED
discovered_by: orchestrator
discovered_at: 2026-09-03
resolved_by: orchestrator
resolved_at: 2026-09-05
task: TASK-001
---

# Finding (resolved)

Added `srmae/validate.py` — hand-rolled stdlib validator (no jsonschema dep).
`new_object(..., validate=True)` now runs validator before persisting.

## Evidence
- 5 new tests in `tests/test_validate.py`: ok, missing_required, bad_enum,
  unknown_prefix_no_crash, new_object_validate_true_rejects — all pass.
- Full suite 61/61. All 4 demos OK.
- Commit: `feat(schemas): hand-rolled stdlib validator + new_object(validate=True)`

## Fix
- validator checks required[] + enum constraints for the 13 spine schemas.
- CHK/EVT/ANL have no shipped schema → silently passes (backward-compat).
- No $ref, no pattern, no range — keeps it tiny and dependency-free.

## Note
Cognitive layer remains primary contract (agent .md files cite schemas).
Machine layer now has a safety net for opt-in validation.