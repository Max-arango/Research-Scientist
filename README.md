# Research-Scientist — two multi-agent skills for Claude Code

Two complementary multi-agent skills that share one stdlib-only Python core:

- **`scientific-research-mae/`** — a *Scientific Research Operating System*: evidence-driven,
  human-in-the-loop, provenance-tracked research harness.
- **`multi-agent/`** — a general *software-engineering* multi-agent pipeline (plan → build →
  QA → security → decision), reusing the same core.

Both rest on one non-negotiable principle:

> **A claim is not true because an agent says so.** It grows stronger only when independent
> evidence survives attempts to falsify it. LLM output is never evidence; nothing is fabricated —
> no invented papers, DOIs, datasets, or measurements.

---

## Table of contents
- [Why this exists](#why-this-exists)
- [Architecture in one picture](#architecture-in-one-picture)
- [The two layers](#the-two-layers-cognitive--machine)
- [The scientific object spine](#the-scientific-object-spine)
- [The agents of `scientific-research-mae` (deep dive)](#the-agents-of-scientific-research-mae-deep-dive)
- [How a research loop actually runs](#how-a-research-loop-actually-runs)
- [The epistemic state machine](#the-epistemic-state-machine)
- [Human-in-the-loop](#human-in-the-loop-hitl)
- [The bundled literature tool](#the-bundled-literature-tool)
- [The agents of `multi-agent` (software engineering)](#the-agents-of-multi-agent-software-engineering)
- [Quick start](#quick-start)
- [Repository layout](#repository-layout)
- [Requirements & status](#requirements--status)

---

## Why this exists

An LLM asked to "research" will happily produce confident prose with invented citations. This
system refuses that failure mode by construction. Agents never chat their way to a conclusion;
they operate over **structured scientific objects** with unique IDs, and every strengthening of
a belief must be backed by recorded evidence the machine layer can check. The result is a
research process that is *reproducible, auditable, falsifiable, and human-governed*.

Every scientifically loaded value carries an epistemic **kind**, so the system can never blur
the line between what is known and what is guessed:

```
FACT · INFERENCE · HYPOTHESIS · RESULT · INTERPRETATION · OPINION
UNKNOWN (absent) · UNCERTAIN (in doubt) · CONTRADICTED (in conflict)
```

Absent information → `UNKNOWN`. Doubt → `UNCERTAIN`. Conflict → `CONTRADICTED`. A gap is never
filled with invented content.

---

## Architecture in one picture

```
                          ┌─────────────────────────────────────────────┐
                          │              ORCHESTRATOR (you)              │
                          │  decides who acts, integrates state,         │
                          │  proposes VERDICT, never self-approves       │
                          └───────────────┬─────────────────────────────┘
                                          │ delegates (Agent tool)
   ┌──────────┬──────────┬───────────┬────┴─────┬────────────┬───────────┬──────────┐
   ▼          ▼          ▼           ▼          ▼            ▼           ▼          ▼
Researcher Hypothesis Methodology Verification Fundamental Statistical Adversary Communicator
 SOURCE     HYPOTHESIS  PROTOCOL   EXPERIMENT   Experimenter  Auditor    CRITIQUE  summaries
 CLAIM                             RESULT       EXPERIMENT    ANALYSIS             to human
                                                RESULT
   │          │          │           │          │            │           │          │
   └──────────┴──────────┴───────────┴──────────┴────────────┴───────────┴──────────┘
                                          │  cross-cutting
                          ┌───────────────┴───────────────┐
                          ▼                               ▼
                    PROVENANCE                      SAFETY REVIEWER
             (why did we conclude this?)         (can BLOCK an experiment)
                                          │
                                          ▼
                              HUMAN  (approves at 5 checkpoints)
```

---

## The two layers (cognitive + machine)

| Layer | What it is | Why |
|---|---|---|
| **Cognitive** (markdown) | Agent contracts in `agents/*.md`, read by Claude subagents | Orchestration is genuinely done by an LLM reading a contract — modeling it as markdown is honest, not a fake engine. |
| **Machine** (`srmae/`, stdlib-only) | Storage, IDs, epistemic state machine, evidence engine, provenance graph, snapshots, HITL, safety, failures, disputes, metrics, validator | Reproducibility and auditability must be machine-checkable, not vibes. |

The cognitive layer **proposes**; the machine layer **records, constrains, and refuses illegal
epistemic moves**. An agent cannot mark a claim `ROBUST` in code without ≥2 independent
replications on file, no matter what its prose says.

---

## The scientific object spine

Every important element is a typed, versioned, append-only object with a unique ID:

```
SOURCE → CLAIM → HYPOTHESIS → PROTOCOL → EXPERIMENT → RESULT → ANALYSIS → CRITIQUE → VERDICT
```

IDs: `SRC · CLM · HYP · PRO · EXP · RES · ANL · CRT · VER · SNP · DSP · FLR` (+ `EVT`, `CHK`).
Objects are never overwritten; an update writes a new version. Failed experiments are kept.
Schemas live in `scientific-research-mae/schemas/*.json` (Draft-07) and can be enforced at
runtime via `new_object(..., validate=True)`.

---

## The agents of `scientific-research-mae` (deep dive)

Each agent is a **contract**: ROLE, MISSION, INPUTS, OUTPUTS, ALLOWED / FORBIDDEN actions,
decision boundaries, escalation rules, error model, evidence requirements, and a strict YAML
handoff format. Separation of function is absolute — **the agent that fixes is never the agent
that verifies, and no agent raises confidence without recorded evidence.**

### 🧭 Orchestrator — *"Is this really ready as a conclusion?"*
The principal agent (you, when the skill loads). Owns workflow state and the epistemic state of
every CLAIM and HYPOTHESIS.
- **Operates by**: selecting which agent acts next, opening/rewinding loops, integrating
  handoffs, applying epistemic transitions **only** through the legal ladder and **only** with
  recorded evidence, and proposing a VERDICT.
- **May create**: workflow state, SNAPSHOT, proposed VERDICT (`human_reviewed=false`).
- **Forbidden**: raising confidence without a cited object id; treating an agent statement as
  evidence; approving experiments it caused to run; approving its own verdict; reading
  `NOT_FALSIFIED` as "true".
- **Control actions each loop**: `CONTINUE · REWIND · BRANCH · ESCALATE · TERMINATE`.

### 📚 Internet Researcher — *"What does the literature say?"*
Finds real literature, creates `SOURCE` objects, extracts `CLAIM` objects.
- **Operates by**: calling the bundled `scripts/litsearch.py` tool (Crossref / OpenAlex / arXiv),
  **verifying every DOI (incl. retraction check)** before trusting it, then converting records to
  SOURCE via `srmae.source_from_record`.
- **Hard rule**: *accessibility ≠ quality*. Whether a paper can be opened (open-access, mirror,
  paywall) never feeds its credibility score. Sci-Hub is an access channel, never an authority.
- **May create**: SOURCE, CLAIM. **Forbidden**: fabricating papers/DOIs/authors; presenting a
  preprint as peer-reviewed; a quality score without a justified `{score, reasoning, evidence,
  uncertainty}` object; extracting a claim the source does not make.
- **On no retrievable identifier** → `retrievable=false`, value `UNKNOWN`, never invent a DOI.

### 💡 Hypothesis Generator — *"What could explain this?"*
Creative but rigor-bound source of testable, **falsifiable** HYPOTHESIS objects.
- **Operates by**: turning claims/gaps into hypotheses that carry `predictions[]`,
  `falsification_criteria[]`, `potential_confounders[]`, and `alternative_explanations[]` openly.
- **May create**: HYPOTHESIS. **Forbidden**: presenting a hypothesis as fact; emitting one with
  no falsification criteria (non-scientific → rejected); re-proposing an already-FALSIFIED idea
  as novel; omitting known confounders. A hypothesis always starts `UNVERIFIED`.

### 🔬 Methodology Designer — *"Does this experiment actually answer the question?"*
Authors the PROTOCOL **before any experiment runs** (protocol-before-experiment invariant).
- **Operates by**: defining independent/dependent/control variables, confounders, controls,
  metrics, sample size, baseline, and success/failure/**falsification** criteria — plus a written
  `inferential_justification` arguing the design can distinguish the hypothesis from its
  alternatives.
- **May create**: PROTOCOL. **Forbidden**: a protocol without controls or falsification criteria;
  a design whose measurements can't separate the hypothesis from confounders; running experiments.
- **Escalates** to the safety reviewer and to the human PROTOCOL checkpoint.

### 🧪 Verification Experimenter — *"Does the existing claim replicate?"*
Tests whether a **standing CLAIM** survives real scrutiny.
- **Operates by** the verification policy: **≥3 executions + baseline + positive & negative
  controls + parameter variation + independent/alternative conditions + a falsification attempt +
  a reproducibility analysis.** Three identical runs are *repetition*, not verification.
- **May create**: EXPERIMENT, RESULT (including failed runs). **Forbidden**: declaring "verified"
  from identical runs; hiding failures; raising the claim's state itself (that is the
  orchestrator's evidence-gated transition); verifying a claim it authored a fix for.
- `REPRODUCED` requires at least one *independent_replication*, not just repetitions.

### ⚗️ Fundamental Experimenter — *"What happens if we test the new hypothesis?"*
Implements and runs experiments for **new** hypotheses.
- **Operates by**: generating experiment code / simulations, running multiple methods and sweeps,
  and **saving every artifact** with seed, env, deps, versions, params, code_ref.
- **May create**: EXPERIMENT, RESULT, artifacts. **Forbidden**: deleting failed results;
  reporting a run that did not execute; fabricating metrics; authoring the analysis/critique/
  verdict of its own results; running a safety-flagged experiment without approval.

### 📊 Statistical Auditor — *"What do the numbers actually show?"*
Turns raw RESULTs into a rigorous ANALYSIS.
- **Operates by**: cleaning data **without touching originals** (`raw_ref` stays intact),
  quantifying uncertainty/robustness/sensitivity, checking sample size, correlation≠causation,
  overfitting; for simulations, checking convergence, discretization error, boundary conditions.
- **The signature rule**: every finding is tagged `OBSERVATION` (measured, with support) or
  `INTERPRETATION` (an inference, clearly labeled). **Forbidden**: reporting interpretation as
  observation; inferring causation from correlation without design support; creating CRITIQUE or
  VERDICT.

### ⚔️ Scientific Adversary — *"Can I destroy this conclusion?"* (MANDATORY gate)
Tries to falsify every conclusion before it becomes a verdict.
- **Operates by** running the full falsification arsenal: alternative explanations, uncontrolled
  confounders, proxy-vs-variable, method/instrument/code artifacts, chance/noise, cherry-picking,
  counterexamples, and *"what one experiment would most likely falsify this?"*.
- **May create**: CRITIQUE with `severity` and `falsification_status ∈ {not_attempted,
  not_falsified, falsified}`. **Enforces** the meaning of the verdict vocabulary and, above all,
  that **`NOT_FALSIFIED` ≠ "true"**. May open a DISPUTE against the auditor or orchestrator.

### 🗣️ Communicator — *"What happened and how sure are we?"*
Honest cognitive interface to the human.
- **Operates by**: summarizing each loop — which agents acted, evidence gathered, **failures**,
  uncertainties, technical limits, disputes, and the continue/stop reasoning.
- **Forbidden**: embellishing or rounding up confidence; hiding failures/uncertainty/dissent;
  presenting `NOT_FALSIFIED` as confirmation; creating or altering any spine object. Every stated
  conclusion cites the object ids behind it.

### 🧬 Provenance system — *"Why did we conclude this?"* (cross-cutting)
Makes every conclusion traceable.
- **Operates by**: recording, for each object, its actor, model+version, code commit, dataset,
  seeds, env, deps, timestamps, human decisions, tools — as **append-only** edges. Answers
  lineage queries like `why(VER-…)` back to raw evidence.
- **Blocks promotion**: a verdict cannot be final until its lineage back to SOURCE and EXPERIMENT
  is complete; missing fields are recorded as `UNKNOWN`, never invented.

### 🛡️ Safety Reviewer — *"Is this experiment safe to run autonomously?"* (can halt)
Classifies every planned action and can stop the workflow.
- **Classes**: `SAFE_AUTONOMOUS · SUPERVISED · HUMAN_APPROVAL_REQUIRED · BLOCKED`.
- **Operates by**: detecting dangerous / physical-irreversible / regulated / bio-chem /
  cyber-offensive / human-subjects signals. On doubt it escalates upward (never defaults to safe);
  a `BLOCKED` action never proceeds. It is a floor, not a substitute for an IRB.

> **Separation of function, restated:** QA-style verification, adversarial falsification,
> statistical audit, and the final production decision are four *different* agents. No agent
> approves its own work; only the human approves major decisions.

---

## How a research loop actually runs

Phases are a guide, not a rail — the orchestrator chooses the path:

```
INGEST → LITERATURE → VERIFY_CLAIMS → HYPOTHESIS → DESIGN → EXPERIMENT → AUDIT → FALSIFY → VERDICT
```

One loop, step by step (detail in `scientific-research-mae/reference/loop-engine.md`):

1. **Open** the loop in the run-log.
2. **Select** the acting agent(s) — not all every loop (literature loop → Researcher; verify loop
   → Verification + Auditor + Adversary, which may run in parallel).
3. **Delegate** → the agent returns a structured YAML handoff → persist objects + emit events.
4. **Recompute evidence** (`srmae.evidence.assess`) → attempt an epistemic **transition**
   (evidence-gated; illegal or unsupported-strengthening moves raise).
5. **Safety** review before any EXPERIMENT; **HITL** gate at the 5 checkpoints.
6. **Snapshot** the state (whole investigation is reconstructable).
7. **Decide**: `CONTINUE · REWIND · BRANCH · ESCALATE · TERMINATE`.
8. **Stall check** — same finding recurring, a fix reverting another, agents contradicting without
   arbitrable evidence, or N loops closing nothing → `LOOP_STALLED` → escalate to the human with
   the concrete history.

Example: falsification fails but surfaces a confounder → `REWIND → DESIGN` → redesign protocol →
new loop.

---

## The epistemic state machine

Claims and hypotheses climb a strength ladder, and **evidence is required to move up**:

```
UNVERIFIED → LITERATURE_SUPPORTED → EXPERIMENTALLY_TESTED → REPRODUCED → ROBUST
           → ADVERSARIALLY_CHALLENGED → HUMAN_REVIEWED

negative (reachable from anywhere):
  WEAK_EVIDENCE · INCONCLUSIVE · CONTRADICTED · FAILED_REPLICATION · FALSIFIED · BLOCKED
```

Knowledge is **never** a single confidence number. The evidence engine returns a
multi-dimensional `EvidenceState` (source quality, methodological quality, independence,
replication, consistency, uncertainty, experimental support, contradictory evidence,
falsification status). It refuses simplistic scoring ("3 papers = 0.9"), never reports `ROBUST`
without ≥2 independent replications, caps confidence at 0.9, and holds it ≤0.5 when uncertainty is
high — always paired with a written reason.

A **verdict** status is not a truth flag:
`SUPPORTED · NOT_FALSIFIED · STRONGLY_SUPPORTED · INCONCLUSIVE · FALSIFIED`. Every verdict cites
its evidence state and records any dissent.

---

## Human-in-the-loop (HITL)

The human is an explicit epistemic authority. Four risk levels —
`AUTO · REVIEW · REQUIRE_APPROVAL · BLOCKED` — and **five mandatory approval checkpoints**:

```
1 RESEARCH_QUESTION   2 HYPOTHESIS   3 PROTOCOL   4 MAJOR_EXPERIMENT_BRANCH   5 FINAL_CONCLUSION
```

Search a paper → AUTO. Run a simulation → AUTO. Change methodology → REVIEW.
External/irreversible action → REQUIRE_APPROVAL. Unsafe experiment → BLOCKED (never proceeds).

---

## The bundled literature tool

The Researcher **calls** `scientific-research-mae/scripts/litsearch.py` (it does not read the
source) — real retrieval, stdlib only, no fabrication:

| Command | What it does |
|---|---|
| `search "<q>" --source crossref\|openalex\|arxiv --rows N` | Multi-source search returning **real** DOIs / arXiv ids |
| `verify <DOI>` | Resolve a DOI + **retraction flag** (checks Crossref `update-to` *and* the `RETRACTED:` title prefix) |
| `expand <DOI> --direction refs\|citations` | Citation-graph walk (backward references / forward citations) via OpenAlex |
| `cite <DOI> --format bibtex\|csl` | Formatted reference (BibTeX or CSL-JSON) |

`srmae.source_from_record()` bridges a tool record into a validated SOURCE, stamping only the
facts the API returned — the quality appraisal is left to the agent. A record without a real
identifier becomes `retrievable=false`, never an invented DOI. Full playbook (which index for
which question, dedup, appraisal, retraction handling) is progressively disclosed in
`reference/search_strategy.md`.

---

## The agents of `multi-agent` (software engineering)

The general engineering skill reuses the same core and the same "no agent approves its own work"
discipline. Pipeline: **Planner → Builder → Optimizer → QA → (AppSec | Red Team) → Orchestrator**.

| Agent | Question it answers | May create | Key boundary |
|---|---|---|---|
| **Orchestrator** | *Is this really ready for production?* | workflow state, findings, Production Decision | cannot approve with CRITICAL / unmitigated HIGH findings |
| **Planner** | *What is the smallest correct plan?* | plan (files, phases, gates, risks, YAGNI notes) | no code; marks over-engineering |
| **Builder** | *Does the change work?* | code + the smallest failing-if-broken test | root-cause fix, not symptom; no out-of-scope edits |
| **Optimizer** | *Can this be simpler?* | minimal refactor diff | no new abstractions for one use site; no behavior change |
| **QA** | *Does it function?* | findings, QA report | no PASS without an executed test command; can't approve its own fix |
| **Red Team** | *Can I break it?* (defensive) | high/critical findings + PoC | authorized scope only; no destructive ops |
| **AppSec** | *Is it built securely?* | findings, AppSec report | reviews secure-by-construction; doesn't fix the code |

Gates required per task class are policy-driven (`multi-agent/config/policy.yml`): e.g. a bug fix
runs QA only; an auth change runs QA + AppSec + Red Team. Severity gates:
`CRITICAL → never to production`, `HIGH → never without explicit human override`, `MEDIUM →
mitigate or document`, `LOW → document`.

---

## Quick start

```bash
# --- Scientific Research OS ---
cd scientific-research-mae
python3 -m unittest discover -s tests -q          # 73 tests, stdlib only
python3 examples/demo_research.py                 # deterministic end-to-end synthetic run
python3 examples/demo_replication.py              # replication → REPRODUCED
python3 examples/demo_adversarial.py              # adversary falsifies → FALSIFIED
python3 examples/demo_failure_heavy.py            # 8 failure types, INCONCLUSIVE, dissent kept
python3 examples/demo_researcher_live.py "CRISPR off-target effects"   # real retrieval (self-skips offline)

# real literature calls
python3 scripts/litsearch.py search "intermittent fasting insulin" --source crossref --rows 5
python3 scripts/litsearch.py verify 10.1016/j.cell.2015.09.020

# --- General software-engineering MAE ---
cd ../multi-agent
python3 -m unittest tests.test_smoke -v           # 10 smoke tests

# --- Inside Claude Code, invoke the skills ---
# /scientific-research-mae run "Does intermittent fasting improve insulin sensitivity?"
# /multi-agent-engineering run "add a /health endpoint to the API"
```

---

## Repository layout

```
Research-Scientist/
├── README.md                        this file
├── scientific-research-mae/         Scientific Research OS
│   ├── SKILL.md                     orchestrator operating protocol
│   ├── agents/                      11 agent contracts
│   ├── schemas/                     13 Draft-07 JSON Schemas
│   ├── protocols/                   5 operating procedures
│   ├── srmae/                       stdlib core (storage, epistemic, evidence,
│   │                                provenance, snapshots, hitl, safety, failures,
│   │                                disputes, metrics, validate, sources, …)
│   ├── scripts/litsearch.py         bundled live literature tool
│   ├── reference/                   loop-engine + search-strategy (progressive disclosure)
│   ├── examples/                    5 deterministic / live demos
│   ├── tests/                       73 tests
│   └── docs/ARCHITECTURE.md         the map + known limitations
├── multi-agent/                     general software-engineering MAE
│   ├── SKILL.md · agents/ (7) · config/policy.yml · templates/
│   ├── core/                        vendored srmae core
│   └── tests/test_smoke.py
└── .claude/                         build audit trail (state · findings · decisions)
```

---

## Requirements & status

- **Python 3.11+**, standard library only. No external dependencies.
- **73 tests** in the research skill + **10** smoke tests in the engineering skill; **5** demos.
- **Known limits** (`scientific-research-mae/docs/ARCHITECTURE.md` §8): live retrieval needs
  network at runtime (the core is offline-deterministic; demos self-skip offline); the safety
  reviewer is a floor, not an IRB; the evidence engine structures judgment, it does not replace a
  statistician.

**License:** [MIT](LICENSE).
