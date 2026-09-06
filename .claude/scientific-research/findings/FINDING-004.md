---
id: FINDING-004
title: Communicator has no machine-layer renderer
severity: LOW
status: ACCEPTED
discovered_by: orchestrator
discovered_at: 2026-09-03
task: TASK-001
---

# Finding

Spec §18 asks the Communicator to deliver loop summaries + a final report.
The agent contract `agents/communicator.md` defines the role and handoff format,
yet `srmae/` has no `communicator.py` to render those summaries to
`reports/communicator/*.md`. Output is purely an LLM-side artifact.

## Impact
- The Communicator can be invoked, but its output lives only in chat / handoff YAML.
- The Communicator summary that the spec §34 promises ("FINAL REPORT" file) is not persisted.

## Fix
- Add `srmae/communicator.py` with `render_loop_summary(store, loop_id)` and
  `render_final_report(store, verdict_id)` that produce markdown and write to
  `reports/communicator/`.

## Recommended
Acceptable as-is for the cognitive-only design; machine layer is for spine objects, not narrative.
The README states "agents/... (roles + boundaries + escalation)" — Communicator fits there.