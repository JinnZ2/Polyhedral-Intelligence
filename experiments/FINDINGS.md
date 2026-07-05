# Experiment findings: scoping the 5 open critique items

Methodology: for each claim, build a probe that measures it against the
repo's *actual* data (entries, equations, ontology) rather than arguing
about it in the abstract. Scripts are in this directory and are re-runnable.
Numbers below are from a single run on this repo state; re-run after any
relevant change to check for drift.

## #5 — Glyph tokenization opacity

`experiments/glyph_opacity_probe.py`

| Metric | Value |
|---|---|
| Glyph tokens scanned (seed_glyph + refined_glyph, all 11 entries) | 210 |
| Unrecognized by `GlyphAlgebra.tokenize()` | 123 (58.6%) |
| ...of which known stylistic alias (different codepoint, same concept) | 117 (95.1% of unknowns) |
| ...of which genuinely unclassified | 6 (🦇 🐬 bat/dolphin emoji, `\|` separator) |

**Root cause found:** entries use a *different* symbol vocabulary than
`atlas_schema.json`'s canonical one — e.g. entries write Matter as `◇`
(U+25C7 WHITE DIAMOND) while the schema's Matter symbol is `◆` (U+25C6
BLACK DIAMOND). Visually near-identical, different codepoints, silently
unrecognized. Same story for Resonance (`〰` vs `≡≡≡`), Life (`⒮`/`•` vs
`••••`), Emergence (`∙`/`●` vs `●●`), and 7 more.

**Verdict:** the critique's actual concern (fuzzy/visual matching for
hand-drawn or typo'd novel symbols) has **zero measured instances** in this
repo. The real, measured problem is a ~16-entry alias table, not a fuzzy-
matching problem. **High probability of success, low effort.** The 6
genuinely-unrecognized tokens (animal emoji, a stray `|`) aren't
family/principle stand-ins at all and correctly should stay unrecognized by
this tool.

## #3 — Hardcoded NIP pattern mapping

`experiments/nip_pattern_coverage_probe.py`

| Metric | Value |
|---|---|
| Entries analyzed | 11 |
| Family flag occurrences | 33, across 11 distinct names |
| Principle flag occurrences | 11, across 5 distinct names |
| Coverage by current `_NIP_PATTERN_FOR_ID` (10 hardcoded ids) | family 79%, principle 64%, overall 75% |
| Uncovered names (fall to generic default) | Energy-Thermo, Consciousness, Engineering, Unity, Relativity(principle), Continuity |

**Data quality issue found along the way:** entry `0001` flags
`"◧ Uncertainty"` under `resonance_sweep` (families) — Uncertainty is
Principle P10, not one of the 20 Families. Pre-existing bug in hand-authored
data, not introduced by this session.

**Verdict:** 75% coverage on n=11 entries / 44 flag occurrences is far too
small a sample to *learn* anything statistically (you'd want tens-to-
hundreds of consistently-labeled entries before a data-driven/learned
mapping would outperform a maintained table). It's large enough to
**extend the table to full 20+12 coverage** and **move it into ontology
data** (e.g. a field on `ontology/families.json`/`principles.json`) so
growing the atlas doesn't require code changes. **High probability of
success for the data-driven-table version; "learned" version isn't viable
yet at this corpus size — revisit past ~50 entries.**

## #1 — Keyword matching vs semantic understanding

`experiments/semantic_resonance_eval.py`

12-case labeled eval set including the exact adversarial phrasings from the
critique ("parametric amplification in nonlinear optical fibers" →
Resonance; "heat death of the universe" vs "heat treating steel" → distinct
families) plus paraphrased, non-literal-keyword restatements of 9 more
family domains.

| Approach | Accuracy |
|---|---|
| Current hand-curated keyword list (`_FAMILY_KEYWORDS`) | 5/12 = 42% |
| Auto-derived "rich corpus" (family description + physics_domains + exemplar equation names, token-overlap scored, zero new dependencies) | 4/12 = 33% |

**Verdict:** the critique's concern is real and larger than I'd have
guessed — 42% baseline accuracy on paraphrased/adversarial cases. But the
"just use a bigger auto-derived keyword corpus" cheap fix I tested **made
things slightly worse**, not better — lexical overlap alone can't bridge
"parametric amplification" to "Kuramoto Model" because they share zero
tokens; it takes actual domain knowledge that a pretrained embedding model
would encode and a bag-of-words corpus won't. **This falsifies the
zero-dependency path.** A real fix needs sentence embeddings, which means
**adding a new dependency to a repo that currently has zero** (see decision
point below) — genuinely higher cost/risk than the original critique's
"medium effort" estimate suggested, but also the only path that measurably
worked in this test.

## #2 — String-hash equation dedup vs mathematical equivalence

`experiments/equation_canonicalization_probe.py` (requires `sympy`,
installed only in this scratch session, not added as a repo dependency)

| Metric | Value |
|---|---|
| Equations tested | 128 (all of `equations/json/`) |
| Parse as-is with SymPy | 1/128 = 1% |
| Parse after minimal, generic unicode/notation preprocessing | 4/128 = 3% |

**Verdict:** the critique correctly identified the *concept* (SymPy could
canonicalize equivalent formulas) but significantly **underestimated the
cost** on this specific corpus. `canonical_form_ascii` strings are written
for human readability (`y(x,t) = A sin(kx) cos(ωt)`, Leibniz notation
`dx/dt`, semicolon-joined systems, unicode subscripts/∇/∂/Σ, bracket
concentration notation `[S]`) — not for parseability, and generic
preprocessing barely moves the needle (1%→3%). Getting real coverage would
require hand-authoring a second, CAS-ready representation per equation
(closer in cost to #7's derivation-writing than to "add a library call").
**Low near-term probability of a good cost/benefit; effort is closer to
"very high" than "high."**

## #7 — Stubbed equation derivations

| Metric | Value |
|---|---|
| Equation `.md` files with `_TODO: narrative derivation` still unfilled | 128/128 = 100% |

**Verdict:** not an experiment, a content-authoring backlog. Every single
equation file is untouched past the auto-generated template. Effort scales
linearly with equations covered; no shortcut found. Highest reference value
per critique's own ranking, but purely labor, decoupled from any code
decision above.

## Summary / recommended priority

| # | Item | Measured finding | Probability of success | Effort | Recommendation |
|---|---|---|---|---|---|
| 5 | Glyph opacity | 58.6% opaque, 95% is a known 16-entry alias table | **High** | **Low** | Do now |
| 3 | NIP mapping | 75% coverage, n too small to learn, easy to extend+datify | **High** | **Low** | Do now |
| 1 | Semantic resonance | 42% baseline, cheap fix falsified (33%, worse), embeddings test blocked by egress policy (huggingface.co 403) | Untested — Medium *if* embeddings work | **Medium-High** (new dependency + needs a reachable model host) | Blocked here; run `semantic_resonance_embeddings_probe.py` in an environment with huggingface.co access |
| 2 | Equation canonicalization | 1%→3% parseable as-is; needs per-equation re-authoring | **Low** near-term | **Very high** (underestimated) | Defer; revisit if #7 happens first (re-authoring for derivations could produce CAS-ready forms as a byproduct) |
| 7 | Equation derivations | 100% stubbed | N/A (labor, not risk) | **High**, linear | Ongoing content backlog, pick a subset and go |

## Decision points — resolutions

1. **#1 embeddings**: resolved as "test for real first" — but the test
   itself is blocked in this sandbox, which is its own finding.
   `sentence-transformers` installs fine (PyPI is on the egress allowlist),
   but loading any pretrained model (`all-MiniLM-L6-v2` or otherwise) pulls
   weights from `huggingface.co`, which this environment's egress policy
   denies with a hard 403 ("policy denial", not a transient failure — see
   `/root/.ccr/README.md`: don't retry or route around these, report them).
   So: **real embedding accuracy on the eval set is untested**, not because
   the idea failed, but because this sandbox can't reach the model host.
   `experiments/semantic_resonance_embeddings_probe.py` is written and
   ready to run — it needs an environment where `huggingface.co` (or a
   mirrored model source) is reachable. Until then, the only concrete
   numbers we have for #1 are the two lexical baselines above (42%
   keyword, 33% richer-corpus — worse).
2. **#3 NIP table format**: resolved as a `default_nip_pattern` field on
   each entry in `ontology/families.json` / `ontology/principles.json`
   (20/20 families, 12/12 principles). `polyhedral_bridge.py`'s
   `_nip_patterns_from_ontology()` reads it at runtime; the old 10-id
   hardcoded `_NIP_PATTERN_FOR_ID` dict is gone. Values for the 6 ids the
   coverage probe found already had real historical precedent were taken
   from the actual authored noise_to_insight text in entries/*.json; the
   rest were assigned by domain judgment. Re-running
   `nip_pattern_coverage_probe.py` now shows 100%/100% coverage (was
   79%/64%), and it also surfaced+fixed the entry-0001 data bug (a
   Principle flagged under the family sweep).
3. **#2/#7 sequencing**: resolved as "fold it in." `tools/
   extract_equations_atlas.py`'s per-equation `.md` template now has a
   "## Canonical SymPy Form" section next to "## Derivation", and the JSON
   schema has a matching `canonical_form_sympy` field (parallel to the
   existing empty `canonical_form_latex`). Deliberately **not** back-filled
   across all 128 existing equation files right now — re-running the
   extractor touches every file's `extracted_at` timestamp even with zero
   content changes (see the tool's own docstring), so that's a cost worth
   paying once, as part of an actual derivation-writing pass, not today for
   an empty stub. New equations extracted from here on get the field
   automatically; existing ones pick it up equation-by-equation as their
   derivations get written.
