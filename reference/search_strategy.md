# Reference — Literature Search Strategy (load on demand)

Detail behind the RESEARCHER's `scripts/litsearch.py` tool. Load when a search gets
non-trivial (which index, dedup, appraisal, citation-graph). Not needed for a single
lookup.

## Which index for which question
| Question shape | Start with | Why |
|---|---|---|
| Biomedical / clinical | `--source crossref` then PubMed (manual) | DOI + MeSH coverage |
| CS / ML / physics / math | `--source arxiv` then `--source openalex` | preprints + citation graph |
| Cross-domain / unsure | `--source openalex` | widest coverage, one call |
| Need the canonical DOI record | `--source crossref` | authoritative metadata |

## The pipeline (search → verify → stamp → appraise → claim → expand)
1. `search "<q>" --source <idx> --rows 5-10` — get candidate records (real ids).
2. For EACH candidate: `verify <DOI>` — drop or flag `is_retracted`. Never skip.
3. `srmae.source_from_record(store, ids, record)` — stamp retrievable facts. This
   does NOT set a quality score.
4. **Appraise quality yourself**: add `quality_assessment` with each dimension a
   justified object `{score, reasoning, evidence, uncertainty}`:
   - `peer_review` (boolean FACT from venue, not inferred)
   - `methodological_quality`, `reproducibility`, `independence`, `overall`
5. Extract CLAIM(s) the source actually makes; cite `source_ids`.
6. `expand <DOI> --direction refs|citations` to widen when:
   - evidence base is thin (< 3 independent sources), or
   - you need to trace a claim's lineage, or
   - you suspect the literature is one-sided (look for contradicting citing work).

## Dedup
- Two records with the same DOI → one SOURCE. Prefer the crossref record for metadata.
- arXiv preprint + its published DOI → keep BOTH, link via provenance DERIVES; the
  published version's peer_review=true, the preprint's peer_review=false.

## Accessibility ≠ quality (hard rule)
`open_access`, `access_channel`, `full_text_available` go in the `accessibility` block.
They NEVER feed methodological_quality / reproducibility / independence / overall. A
mirror (Sci-Hub etc.) is an access channel only, never a credibility signal.

## Retraction handling
`verify` flags retraction two ways (Crossref `update-to` + `RETRACTED:` title prefix).
A retracted source is not silent support:
- If it was the basis of a CLAIM → mark that CLAIM `CONTRADICTED` and open a FAILURE
  (`type=SOURCE`, `changes_conclusions=true` if it flips a verdict).
- Record the retraction in `retraction_check` in the handoff.

## Reproducibility
Log every `litsearch` subcommand you ran in the handoff `tool_calls[]` so a reviewer
can replay the exact search. The script is deterministic given the same API state.

## Bibliography
`cite <DOI> --format bibtex|csl` at write-up time. Do not hand-format references.