# Review Protocol (Adversary + Auditor + Orchestrator gate)

Operating procedure for the mandatory adversarial review before any VERDICT is proposed.

## Order of operations
1. Auditor labels every finding OBSERVATION vs INTERPRETATION and quantifies uncertainty.
2. Adversary runs the full falsification list against the target:
   alternative explanations, confounders, proxy-vs-variable, artifact, chance, cherry-picking,
   counterexample, and the single most-likely falsifying experiment.
3. Adversary emits a CRITIQUE with severity and falsification_status (an actual attempt, not not_attempted).
4. Orchestrator maps evidence + critique to a verdict_status.
5. Provenance confirms complete lineage back to raw evidence.
6. Human reviews at the FINAL_CONCLUSION checkpoint; only then is the verdict final.

## Verdict mapping (enforced)
- FALSIFIED: a falsification criterion was met.
- NOT_FALSIFIED: survived attempts but evidence insufficient — NOT a claim of truth.
- INCONCLUSIVE: attempts neither supported nor falsified.
- SUPPORTED: positive evidence that also survived adversarial challenge.
- STRONGLY_SUPPORTED: SUPPORTED + independent replication + robustness + survived critique.

## Checklist
- [ ] observation vs interpretation labeled.
- [ ] uncertainty quantified.
- [ ] falsification actually attempted (status ≠ not_attempted at gate).
- [ ] counterexamples and alternative explanations recorded.
- [ ] lineage complete (provenance).
- [ ] confidence raised only with cited evidence.
- [ ] human review before final.

## Anti-hallucination rules
- NOT_FALSIFIED ≠ TRUE. Never present it as confirmation.
- No agent approves its own work; the fixer does not verify the fix.
- Missing data → UNKNOWN; doubt → UNCERTAIN; conflict → CONTRADICTED.
- Dissent is recorded on the verdict, never erased.
