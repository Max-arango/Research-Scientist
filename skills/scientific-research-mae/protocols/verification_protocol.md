# Verification Protocol (Verification Experimenter)

Operating procedure for verifying an EXISTING claim. Repetition alone never verifies.

## Verification policy (all required where possible)
- Minimum 3 executions.
- Baseline.
- Positive control AND negative control.
- Parameter variation.
- Independent / alternative conditions (different method or implementation).
- Explicit falsification attempt.
- Reproducibility analysis.

## Order of operations
1. Load the target CLAIM and its supporting evidence.
2. Confirm the PROTOCOL has controls and falsification criteria; else return to methodology.
3. Run repetitions, controls, and parameter sweeps; record seed/env/deps/params per experiment.
4. Attempt to falsify the claim directly.
5. Run at least one independent_replication before considering REPRODUCED.
6. Compute reproducibility (run count, variance, independent replication succeeded?).
7. Report evidence to the orchestrator; do not set the epistemic state yourself.

## Checklist
- [ ] ≥3 executions.
- [ ] baseline present.
- [ ] positive AND negative controls present.
- [ ] parameter variation performed.
- [ ] independent_replication attempted (required for REPRODUCED).
- [ ] falsification attempt recorded.
- [ ] failures preserved.

## Anti-hallucination rules
- "3 identical runs = verified" is FALSE and forbidden.
- Non-reproducible → FAILED_REPLICATION. Ambiguous spread → INCONCLUSIVE.
- The one who fixes a problem is not the one who verifies the fix.
