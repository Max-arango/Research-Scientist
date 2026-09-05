# Reference — Research Loop Engine

Detail behind SKILL.md §"research loop engine". Load when a loop gets complicated (recurring
findings, stall, agent failure, rewind).

## Controls (defaults)
```
max_loops         : 8      # hard cap; on reach → HUMAN_REQUIRED
stall_threshold   : 2      # loops with no progress → LOOP_STALLED
min_executions    : 3      # verification policy floor (+ controls + falsification)
min_independent   : 2      # independent replications required for ROBUST
```
Budgets, not promises. Goal: finish earlier with evidence, or stop honestly.

## One loop, step by step
1. **Open** in run-log: `── LOOP K · <phase> ──`.
2. **Select the acting agent(s)** — not all every loop. Literature loop → Researcher; verify
   loop → Verification + Auditor + Adversary (gates may run in parallel).
3. **Delegate** → structured handoff back → persist objects + emit events.
4. **Recompute evidence** (`srmae.evidence.assess`) → attempt an epistemic transition
   (evidence-gated; illegal or unsupported-strengthening moves raise).
5. **Safety** review before any EXPERIMENT phase; **HITL** gate at the 5 checkpoints.
6. **Snapshot** the state.
7. **Decide** (`LoopEngine.decide(signals)`): CONTINUE | REWIND | BRANCH | ESCALATE | TERMINATE.
8. **Stall check** (`stalled(history)`) → escalate with the history that proves it.

## Control actions
- **CONTINUE** — next phase; evidence still accumulating.
- **REWIND** — go back a phase. Trigger: new confounder, failed design, falsified prediction.
  e.g. FALSIFY finds a confounder → `REWIND → DESIGN`.
- **BRANCH** — spawn a parallel line (alternative hypothesis/method) → needs HITL at
  MAJOR_EXPERIMENT_BRANCH.
- **ESCALATE** — hand to human. Trigger: unresolved dispute, safety BLOCK, ambiguity.
- **TERMINATE** — all criteria met (→ propose VERDICT) or FALSIFIED, or cap reached.

## Anti-infinite-loop (PROGRESS)
Progress = Δ(criteria met) + Δ(claims reaching a higher state) − (reopened findings) −
(reverting fixes). Stall signals: same finding signature recurs after a supposed fix; a fix
reverts a prior change (ping-pong); two agents contradict with no arbitrable evidence; a loop
closes nothing new. `no_progress ≥ stall_threshold → LOOP_STALLED →` escalate with the
concrete history ("HYP-002 re-falsified in loop 3 and 5 by the same critique"), not "stuck".

## Agent failure recovery
Register the error; decide if retryable (transient tool/ambiguous prompt → retry *differently*,
never identical); else change strategy (split, more context, fallback general-purpose) or
reassign; escalate if you still cannot continue. A failure never ends the pipeline silently.

## Termination
Loop terminates only in: proposed VERDICT after all acceptance criteria met with evidence
(→ HITL FINAL_CONCLUSION), FALSIFIED, HUMAN_REQUIRED, or MAX_LOOPS (→ escalate). Any other
state ⇒ keep looping.
