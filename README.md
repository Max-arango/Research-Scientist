# Research-Scientist — two Claude Code skills

Two complementary multi-agent skills for Claude Code, sharing a stdlib-only Python core.

## `scientific-research-mae/`
A **Scientific Research Operating System**: a multi-agent, human-in-the-loop, evidence-driven
research harness. Takes a research question through iterative loops — literature research →
claim extraction → evidence evaluation → hypothesis → methodological design → verification &
fundamental experiments → statistical audit → adversarial falsification → verdict — with full
provenance, reproducibility, and human approval gates.

- 11 agent contracts, 13 JSON Schemas, stdlib-only engine (`srmae/`)
- Bundled **live literature tool** (`scripts/litsearch.py`): real Crossref/OpenAlex/arXiv
  retrieval, DOI verify + retraction flag, citation-graph expand, BibTeX/CSL export — no fabrication
- 73 tests, 5 deterministic demos (incl. a live-retrieval demo that self-skips offline)

```bash
cd scientific-research-mae
python3 -m unittest discover -s tests -q      # 73 tests
python3 examples/demo_research.py             # end-to-end synthetic run
python3 scripts/litsearch.py search "CRISPR off-target effects" --source crossref
```

## `multi-agent/`
A **general software-engineering** multi-agent skill: Planner → Builder → Optimizer → QA →
(AppSec | Red Team) → Orchestrator, with policy-driven gates and a production decision. Reuses
the same `srmae` core (vendored as `multi-agent/core/`).

```bash
cd multi-agent
python3 -m unittest tests.test_smoke -v       # 10 smoke tests
```

## Core principle (both skills)
> A claim is not true because an agent says so. It grows stronger only when independent evidence
> survives attempts to falsify it. LLM output is never evidence; nothing is fabricated.

## Requirements
Python 3.11+, standard library only. No external dependencies.

## Status
See `scientific-research-mae/docs/ARCHITECTURE.md` §8 for known limitations. State/audit trail
for the build lives under `.claude/`.
