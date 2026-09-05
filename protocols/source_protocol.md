# Source Protocol (Researcher)

Operating procedure for creating SOURCE and extracting CLAIM objects.

## Order of operations
1. Restate the sub-question. Search scholarly indexes first: Crossref, PubMed, arXiv, bioRxiv,
   medRxiv, Semantic Scholar, Google Scholar, IEEE, ACM, Nature, Science, APS, Springer,
   Elsevier, SciELO, university repositories.
2. For each candidate, resolve a real identifier (DOI or URL). If it does not resolve, stop —
   mark UNKNOWN, do not invent one.
3. Classify source_type (peer_reviewed / preprint / thesis / technical_report / dataset /
   conference_paper / review_article / blog / forum / secondary).
4. Record accessibility SEPARATELY (open_access, access_channel, full_text_available).
5. Score quality with justified objects only.
6. Extract claims the source actually makes; attribute each to the source id.
7. Flag contradictions across sources.

## Source checklist
- [ ] Retrievable identifier resolves (else `retrievable=false`, value UNKNOWN).
- [ ] source_type assigned from the fixed enum.
- [ ] preprint/thesis/blog NOT labeled peer_reviewed.
- [ ] accessibility recorded separately from quality.
- [ ] each quality score is {score, reasoning, evidence, uncertainty}.
- [ ] a mirror/Sci-Hub used only as an access channel, never as a credibility signal.

## Claim checklist
- [ ] statement is faithful to the source (no extrapolation).
- [ ] `source_ids` non-empty.
- [ ] contradictions marked CONTRADICTED.
- [ ] doubtful attribution marked UNCERTAIN.

## Anti-hallucination rules
- Never fabricate papers, DOIs, authors, dates, or citations.
- Absent evidence → UNKNOWN. Doubt → UNCERTAIN. Conflict → CONTRADICTED.
- ACCESSIBILITY ≠ QUALITY. Being easy to download says nothing about being correct.
