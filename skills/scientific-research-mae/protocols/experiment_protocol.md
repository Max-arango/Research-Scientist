# Experiment Protocol (Fundamental Experimenter)

Operating procedure for running experiments on NEW hypotheses. Protocol must exist and be
approved BEFORE any run.

## Order of operations
1. Confirm an approved PROTOCOL and a safety classification of SAFE_AUTONOMOUS (or the required
   approval for SUPERVISED / HUMAN_APPROVAL_REQUIRED). If BLOCKED, stop.
2. Generate experiment code; pin seed, env, deps, versions, params, code_ref.
3. Run with the correct kind (replication / repetition / independent_replication /
   parameter_sweep / control / negative_control / positive_control).
4. Run ≥3 times where repetition is meaningful; sweep parameters where relevant.
5. Save ALL artifacts and set raw_ref. Record failures as RESULT status=failed + a FAILURE object.
6. Hand results to the statistical auditor — do not judge support yourself.

## Checklist
- [ ] approved PROTOCOL referenced.
- [ ] safety class permits the run.
- [ ] seed / env / deps / versions / params / code_ref recorded.
- [ ] ≥3 runs where meaningful.
- [ ] all artifacts saved; raw_ref set.
- [ ] failed runs preserved, never deleted.
- [ ] no fabricated measurements or metrics.

## Anti-hallucination rules
- Never report a run that did not execute.
- Failures are evidence — keep them.
- Environment/crash/instability → record the real error, mark FAILURE, do not fake success.
