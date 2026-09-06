# scientific-research-mae

A **Scientific Research Operating System** for Claude Code: a multi-agent, human-in-the-loop,
evidence-driven harness that takes a research question through iterative loops of literature
research → claim extraction → evidence evaluation → hypothesis → methodological design →
verification & fundamental experiments → statistical audit → adversarial falsification →
verdict — with full provenance, reproducibility, and human approval gates.

It is **not** a chatbot that "helps you research". It is research *infrastructure*: agents
operate over structured scientific objects and a global, auditable research state.

## Core principle
> A claim is not true because an agent says so. A claim becomes stronger only when independent
> evidence survives attempts to falsify it.

LLM output is never evidence. Nothing is fabricated — no invented papers, DOIs, datasets, or
measurements. Absent → `UNKNOWN`, doubtful → `UNCERTAIN`, conflicting → `CONTRADICTED`.

## Quick start
```bash
# Invoke as a skill inside Claude Code:
/scientific-research-mae run "Does intermittent fasting improve insulin sensitivity in healthy adults?"

# Run the deterministic end-to-end demo (synthetic, offline):
cd scientific-research-mae
python3 examples/demo_research.py

# Run the test suite (stdlib unittest, no dependencies):
python3 -m unittest discover -s tests -q
```

## What's inside
```
SKILL.md              operating protocol (read by the orchestrator = you)
agents/               11 agent contracts (roles + boundaries + escalation)
schemas/              12 JSON Schemas for the scientific objects
protocols/            5 operating procedures (source/hypothesis/experiment/verify/review)
core/  (import srmae) stdlib-only engine: ids, storage, epistemic state machine, evidence,
                      provenance, snapshots, loops, hitl, safety, failures, disputes, metrics, events
docs/ARCHITECTURE.md  the map
examples/             end-to-end synthetic research run
tests/                unittest suite
reference/            loop-engine detail
```

## The agents
Orchestrator (decides) · Internet Researcher (SOURCE, CLAIM) · Hypothesis Generator
(HYPOTHESIS) · Methodology Designer (PROTOCOL) · Verification Experimenter & Fundamental
Experimenter (EXPERIMENT, RESULT) · Statistical Auditor (ANALYSIS) · Scientific Adversary
(CRITIQUE) · Communicator (summaries) · Provenance (cross-cutting) · Safety reviewer (can
halt). No agent approves its own work; the human approves major decisions.

## Human-in-the-loop
Five approval checkpoints — research question, hypothesis, protocol, major experiment branch,
final conclusion — over four risk levels: AUTO, REVIEW, REQUIRE_APPROVAL, BLOCKED. Unsafe or
irreversible actions are BLOCKED and never proceed.

## Reproducibility
Library functions take `ts`/`seed` explicitly (no hidden clock/RNG); IDs and counters persist;
`srmae.provenance.why(<verdict>)` reconstructs exactly why the system reached a conclusion;
snapshots reconstruct the whole investigation.

## Requirements
Python 3.11+ (developed on 3.14), standard library only. No external dependencies.

## Status & limitations
See `docs/ARCHITECTURE.md` §8. Live literature retrieval needs network tools at runtime; the
core is offline and deterministic. The safety reviewer is a floor, not an IRB.
