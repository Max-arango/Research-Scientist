```yaml
id: TASK-001
title: "Build scientific-research-mae skill from scratch"
description: >
  A Scientific Research Operating System: multi-agent, human-in-the-loop, evidence-driven.
  10 agents (orchestrator, researcher, verification, hypothesis, methodology, fundamental
  experimenter, statistical auditor, adversary/falsification, communicator, provenance),
  scientific object graph (SOURCE→CLAIM→HYPOTHESIS→PROTOCOL→EXPERIMENT→RESULT→ANALYSIS→
  CRITIQUE→VERDICT), epistemic state machine, evidence engine, provenance system, loop
  engine, HITL checkpoints, failure log, disagreement resolution, snapshot system, safety
  reviewer, JSON schemas, tests, end-to-end demo, docs.
status: IN_PROGRESS
priority: HIGH
classification:
  tipo: feature
  superficie: cli/lib
  riesgo: ninguno        # deliverable is a skill spec + stdlib python; no runtime attack surface
assigned_agent: orchestrator
dependencies: []
acceptance_criteria:
  - { id: AC1,  text: "SKILL.md exists, valid frontmatter, documents purpose/when-to-use/agents/workflow/HITL/evidence/failure/repro/examples", verify: "read + frontmatter check", met: false, evidence: null }
  - { id: AC2,  text: "10 agent contracts with ROLE/INPUTS/OUTPUTS/ALLOWED/FORBIDDEN/DECISION_BOUNDARIES/ESCALATION/ERROR_MODEL/EVIDENCE_REQUIREMENTS", verify: "count files + grep sections", met: false, evidence: null }
  - { id: AC3,  text: "JSON schemas for source,claim,hypothesis,protocol,experiment,result,critique,verdict,snapshot,dispute,failure", verify: "schema files parse as JSON", met: false, evidence: null }
  - { id: AC4,  text: "Core python: ids, storage, state machine, evidence engine, provenance graph, snapshots, validation", verify: "import + pytest", met: false, evidence: null }
  - { id: AC5,  text: "Epistemic state machine with legal transitions incl. negative states; illegal transitions rejected", verify: "unit test", met: false, evidence: null }
  - { id: AC6,  text: "Provenance graph reconstructs 'why this conclusion' for a verdict", verify: "unit test walks graph", met: false, evidence: null }
  - { id: AC7,  text: "HITL: 4 approval levels (AUTO/REVIEW/REQUIRE_APPROVAL/BLOCKED) + 5 checkpoints, enforced in code", verify: "unit test blocks unapproved", met: false, evidence: null }
  - { id: AC8,  text: "Evidence engine is non-simplistic (no '3 papers = 0.9'); multi-dimensional, justified", verify: "test asserts contextual output", met: false, evidence: null }
  - { id: AC9,  text: "Anti-hallucination: UNKNOWN/UNCERTAIN/CONTRADICTED handling; no fabricated sources/DOIs enforced by contract + a DOI/existence guard", verify: "test + contract grep", met: false, evidence: null }
  - { id: AC10, text: "Snapshot per loop; full research reconstructable from snapshots", verify: "roundtrip test", met: false, evidence: null }
  - { id: AC11, text: "Failure log taxonomy (11 types) + disagreement/dispute structure", verify: "schema + test", met: false, evidence: null }
  - { id: AC12, text: "Statistical auditor + adversary contracts distinguish SUPPORTED/NOT_FALSIFIED/STRONGLY_SUPPORTED/INCONCLUSIVE/FALSIFIED", verify: "grep contracts + verdict enum test", met: false, evidence: null }
  - { id: AC13, text: "End-to-end demo runs: question→...→verdict→snapshot→human review, using only synthetic/declared data", verify: "run demo script, exit 0", met: false, evidence: null }
  - { id: AC14, text: "All tests pass", verify: "pytest -q", met: false, evidence: null }
  - { id: AC15, text: "System metrics defined + at least computed in demo (traceability, falsification coverage, unsupported claim rate...)", verify: "demo prints metrics", met: false, evidence: null }
files: []
risks:
  - "Scope is very large; risk of shallow breadth. Mitigation: core must be real & tested, not stubs."
  - "Temptation to fake LLM outputs as evidence. Mitigation: contracts forbid; provenance tags every value by kind."
security_required: false
red_team_required: false
appsec_required: false   # AppSec-lite review of the in-deliverable safety reviewer module only
pipeline: [planner, builder, optimizer, qa, orchestrator]
iteration: 1
findings: []
created: 2026-09-02
updated: 2026-09-02
```
