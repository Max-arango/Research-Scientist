# Architecture Spec — scientific-research-mae (locked interfaces)

Coordination artifact authored by Orchestrator. Builders MUST honor these signatures so
parallel work integrates. Runtime: Python 3.14, **stdlib only**, tests via `unittest`.

## Deliverable layout
```
scientific-research-mae/
├── SKILL.md                      # skill entry (frontmatter + protocol)
├── README.md
├── docs/ARCHITECTURE.md
├── agents/                       # 10 markdown agent contracts
│   ├── orchestrator.md researcher.md verification.md hypothesis.md methodology.md
│   ├── fundamental_experimenter.md statistical_auditor.md adversary.md
│   └── communicator.md provenance.md   (+ safety_reviewer.md module)
├── schemas/*.json                # 12 JSON Schemas (draft-07 subset)
├── protocols/*.md                # source/hypothesis/experiment/verification/review protocols
├── core/                         # python package `srmae`
│   ├── __init__.py ids.py objects.py storage.py epistemic.py evidence.py
│   ├── provenance.py snapshots.py loops.py hitl.py safety.py failures.py
│   ├── disputes.py metrics.py events.py
├── examples/demo_research.py     # end-to-end synthetic run
└── tests/                        # unittest suite
```
Python package import root: `scientific-research-mae/core` → package name **`srmae`**.
Tests run with `cd scientific-research-mae && python3 -m unittest discover -s tests -q`.

## Scientific object model (the spine)
`SOURCE → CLAIM → HYPOTHESIS → PROTOCOL → EXPERIMENT → RESULT → ANALYSIS → CRITIQUE → VERDICT`
Every object: unique typed ID, `created_at`, `created_by` (agent id), `provenance` links.

### ID scheme (`ids.py`)
Prefixes: SRC CLM HYP PRO EXP RES ANL CRT VER SNP DSP FLR EVT. Zero-padded 5 digits.
```python
class IdGen:
    def __init__(self, store): ...          # reads counters from storage, persists
    def next(self, prefix: str) -> str      # e.g. next("CLM") -> "CLM-00001"
```
Counters persisted in storage so IDs never collide across process restarts (reproducibility).

### Value provenance (anti-hallucination, AC9)
Every scientifically-loaded value is wrapped, never a bare string/number:
```python
@dataclass
class Value:                     # objects.py
    kind: Literal["FACT","INFERENCE","HYPOTHESIS","RESULT","INTERPRETATION","OPINION",
                  "UNKNOWN","UNCERTAIN","CONTRADICTED"]
    content: Any
    support: list[str] = []      # ids of SOURCE/EXPERIMENT/etc backing it
    note: str = ""
```
Rule enforced by contracts + `evidence.py`: a value of kind RESULT/FACT with empty `support`
is INVALID. LLM assertions enter as kind INFERENCE/OPINION, never FACT.

## Core module APIs (LOCKED)

### storage.py — append-only JSON store
```python
class Store:
    def __init__(self, root: str|Path): ...      # root = storage/ dir
    def put(self, obj: dict) -> None             # writes objects/<ID>.json ; id in obj["id"]
    def get(self, id: str) -> dict
    def all(self, prefix: str|None=None) -> list[dict]
    def append_event(self, ev: dict) -> None     # events.jsonl (append-only)
    def counters(self) -> dict; def set_counter(self, prefix, n): ...
```
Objects are immutable once put with a given (id, version). Updates = new version via
`put` with incremented `obj["version"]`; store keeps history (never overwrite/delete).

### epistemic.py — state machine (AC5)
States (positive path): `UNVERIFIED → LITERATURE_SUPPORTED → EXPERIMENTALLY_TESTED →
REPRODUCED → ROBUST → ADVERSARIALLY_CHALLENGED → HUMAN_REVIEWED`.
Negative/terminal: `WEAK_EVIDENCE INCONCLUSIVE CONTRADICTED FAILED_REPLICATION FALSIFIED
BLOCKED`.
```python
LEGAL: dict[str, set[str]]                        # adjacency of allowed transitions
def can_transition(a: str, b: str) -> bool
def transition(obj: dict, to: str, *, evidence: list[str], by: str) -> dict
    # raises IllegalTransition if not in LEGAL or if evidence empty for a *strengthening* move
```
Invariant: any move UP the strength ladder REQUIRES non-empty `evidence`. Moves to negative
states allowed from anywhere (evidence of failure). No auto-jump skipping levels.

### evidence.py — evidence engine (AC8, non-simplistic)
Returns a multi-dimensional `EvidenceState`, NOT a single number:
```python
@dataclass
class EvidenceState:
    supporting_sources: int; contradicting_sources: int
    independent_replications: int; repetitions: int
    methodological_quality: str        # low|moderate|high  (+ reasoning)
    experimental_support: str          # none|weak|moderate|strong
    uncertainty: str                   # low|moderate|high
    falsification_status: str          # not_attempted|not_falsified|falsified
    reasoning: str                     # WHY — required, non-empty
def assess(claim: dict, sources: list[dict], experiments: list[dict]) -> EvidenceState
def suggested_state(es: EvidenceState) -> str   # maps to epistemic state, with caveats;
    # NEVER returns ROBUST on <2 independent replications; NEVER high confidence on 1 source
```
Guard: `assess` raises if asked to score with zero evidence. Confidence (0..1) MAY be derived
but is always paired with the dimensions above and `reasoning`.

### provenance.py — provenance graph (AC6)
```python
class Provenance:
    def __init__(self, store): ...
    def link(self, src_id: str, rel: str, dst_id: str) -> None    # rel in REL set
    def parents(self, id) -> list[tuple[str,str]]; def children(self, id): ...
    def why(self, id: str) -> dict          # full ancestry tree: sources, experiments,
                                            # audits, critiques, human decisions, seeds, envs
REL = {"SUPPORTS","CONTRADICTS","DERIVES","PRODUCES","TESTED_BY","CHALLENGED_BY",
       "IMPLEMENTED_BY","REPRODUCES","ANALYZED_BY","APPROVED_BY"}
```
`why(verdict_id)` must return enough to answer "why did the system conclude this".

### snapshots.py — per-loop snapshot (AC10)
```python
def take(store, loop_id: str, state: dict) -> dict     # writes SNP-*, returns snapshot
def restore(store, snapshot_id: str) -> dict           # reconstruct research state
```
Snapshot contains: loop id, ts, claims/hyps/experiments/results ids + statuses, failures,
agent decisions, human decisions, open questions, evidence deltas, next actions.

### loops.py — loop engine (§15)
```python
PHASES = ["INGEST","LITERATURE","VERIFY_CLAIMS","HYPOTHESIS","DESIGN","EXPERIMENT",
          "AUDIT","FALSIFY","VERDICT"]
class LoopEngine:
    def __init__(self, store, hitl, safety): ...
    def start_loop(self, phase: str) -> str
    def decide(self, signals: dict) -> str   # CONTINUE|REWIND|BRANCH|ESCALATE|TERMINATE
    def stalled(self, history: list[dict]) -> bool   # anti-infinite-loop
```
Not rigid: `decide` returns control action from signals (new confounder → REWIND, etc.).

### hitl.py — human-in-the-loop (AC7)
```python
class Level(str, Enum): AUTO; REVIEW; REQUIRE_APPROVAL; BLOCKED
CHECKPOINTS = ["RESEARCH_QUESTION","HYPOTHESIS","PROTOCOL","MAJOR_EXPERIMENT_BRANCH",
               "FINAL_CONCLUSION"]
class HITL:
    def classify(self, action: str) -> Level          # policy table
    def gate(self, checkpoint: str, payload: dict) -> "Pending|Approved"
    def approve(self, checkpoint_id: str, human: str, decision: bool, note: str) -> dict
```
`gate` on a REQUIRE_APPROVAL/BLOCKED action returns Pending and blocks progress until
`approve` recorded. Approvals are provenance nodes (APPROVED_BY). BLOCKED never proceeds.

### safety.py — safety/ethics reviewer (§22)
```python
class SafetyClass(str,Enum): SAFE_AUTONOMOUS; SUPERVISED; HUMAN_APPROVAL_REQUIRED; BLOCKED
def review(action: dict) -> tuple[SafetyClass, list[str]]   # (class, reasons)
```
Flags: physical/irreversible/regulated/bio-chem/cyber-offensive/human-subjects → escalate or
BLOCK. Can halt a workflow (LoopEngine consults safety before EXPERIMENT phase).

### failures.py (§20) & disputes.py (§21)
```python
FAILURE_TYPES = ["SCIENTIFIC","EXPERIMENTAL","REPRODUCIBILITY","STATISTICAL","TECHNICAL",
                 "TOOL","SOURCE","AGENT","COORDINATION","HUMAN_BLOCK","CAPABILITY_LIMITATION"]
def log_failure(store, **fields) -> str        # never deletes; failures are data
class Dispute: open(topic, agents, positions, evidence) -> id; resolve(id, how) -> None
```
Strong dispute (severity high) → triggers HITL.

### metrics.py (§31)
```python
def compute(store) -> dict   # source_quality, evidence_strength, replication_strength,
  # experimental_robustness, hypothesis_quality, methodological_quality,
  # falsification_coverage, reproducibility_score, traceability,
  # agent_disagreement_rate, human_intervention_rate, loop_efficiency,
  # false_confidence_rate, unsupported_claim_rate  — each {value, how, meaning}
```
`unsupported_claim_rate` = fraction of CLAIM/RESULT values with empty support (must be 0 in a
healthy run). `traceability` = fraction of verdicts whose `why()` reaches ≥1 SOURCE and ≥1
EXPERIMENT.

### events.py (§26)
Event constants (SOURCE_FOUND, CLAIM_CREATED, ... HUMAN_APPROVED, LOOP_STARTED/COMPLETED).
`emit(store, type, **payload)` → append to events.jsonl. Drives observability + metrics.

## Agent contract sections (AC2) — every agent file has all of:
ROLE · MISSION · INPUTS · OUTPUTS · ALLOWED_ACTIONS · FORBIDDEN_ACTIONS ·
DECISION_BOUNDARIES · ESCALATION_RULES · ERROR_MODEL · EVIDENCE_REQUIREMENTS · HANDOFF_FORMAT.
Capability boundaries (who may create what): Researcher→SOURCE/CLAIM(extract); Hypothesis→
HYPOTHESIS; Methodology→PROTOCOL; Verification/Fundamental→EXPERIMENT+RESULT; Auditor→ANALYSIS;
Adversary→CRITIQUE; Orchestrator→VERDICT(proposed)+workflow state; Human→approvals.
No agent approves its own work. No agent raises confidence without recorded evidence.

## Test matrix (AC14) — unittest
ids, storage roundtrip+history, epistemic legal/illegal, evidence non-simplistic+guards,
provenance why(), snapshots roundtrip, hitl gating+block, safety classification, failures
append-only, disputes→hitl, metrics, events, + integration (demo asserts).
