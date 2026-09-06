# Hypothesis Protocol (Hypothesis Generator)

Operating procedure for creating falsifiable HYPOTHESIS objects.

## Order of operations
1. Read the driving CLAIM(s), source context, and open questions.
2. Draft one or more competing hypotheses.
3. For each: write statement, rationale, assumptions, predictions, observable_variables,
   falsification_criteria, potential_confounders, expected_outcomes, alternative_explanations.
4. Verify each prediction is observable and tied to an observable variable.
5. Emit as a Value of kind HYPOTHESIS (never FACT).

## Checklist
- [ ] statement is a testable proposition, not an established fact.
- [ ] predictions[] non-empty and observable.
- [ ] falsification_criteria[] non-empty (else reject as non-scientific).
- [ ] potential_confounders[] listed.
- [ ] alternative_explanations[] listed.
- [ ] rationale cites CLM-/SRC- ids (or states UNKNOWN if speculative).
- [ ] not previously FALSIFIED and resubmitted as novel.

## Anti-hallucination rules
- A hypothesis is never presented as true or as a result.
- If the question is not falsifiable in principle, say so; do not smuggle in a fake proxy.
- Speculative basis → rationale UNCERTAIN, list missing inputs.
