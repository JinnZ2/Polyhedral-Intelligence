# Polyhedral Intelligence — Repository Review

Generated as a thorough, multi-faceted review of the repository as of commit `fc1db07` on `claude/new-repo-files-eymonl`. Every finding below was verified directly against the current files in this checkout (grep/read/run), not inferred. Where a section has no findings, that is stated explicitly rather than invented.

## Summary

| # | Section | Findings |
|---|---|---|
| 1 | Inconsistencies | 10 |
| 2 | Markdown Information Gaps | 11 |
| 3 | Code Audit | 10 |
| 4 | Organizational Structure Suggestions | 8 |
| 5 | Limitations Mitigation Checklist | 5 items, all partially addressed or missing (see caveat) |
| 6 | Discoverability & Crawler Optimization | 9 items checked, 6 missing / 3 partial |

---

## 1. Inconsistencies

### 1.1 `BridgeOrganize.md` is not Markdown — it's a runnable Python script

**File:** `BridgeOrganize.md` (repo root, 398 lines)

`file BridgeOrganize.md` reports `Python script, Unicode text, UTF-8 text executable`, and the full contents parse cleanly with `ast.parse()` — it's valid Python (imports `numpy`, `matplotlib.pyplot`, `matplotlib.gridspec`, `hashlib`, `json`, `datetime`, later `ipywidgets`/`IPython.display`), not prose. It defines its own `FAMILIES`/`PRINCIPLES` lists using **generic placeholder names** ("Adaptive", "Resilient", "Exploratory"...) that don't match the real 20 Families/12 Principles anywhere else in the repo.

**Fix:** rename to `BridgeOrganize.py` (or move into `experiments/` / an `archive/` dir — see §4.4), and add one line to `CLAUDE.md`/`README.md` noting it's an early, superseded sketch (it isn't referenced from `CLAUDE.md` at all today — see §2.10).

### 1.2 Three divergent keyword→glyph mappings for the same concept

- `polyhedral_bridge.py` (`_FAMILY_KEYWORDS`, `_PRINCIPLE_KEYWORDS`) — canonical `FAM:*`/`PRIN:*` ids, actively used by `encode()`, covered by tests.
- `Poly.py:102-142` (`keyword_map`, ~50 entries) **and separately** `Poly.py:186-207` (`family_keywords`, `F01`-`F20`) — a second, different mapping in the *same file*.
- `Polyhedral-cli.py:97-108` (`keyword_map`, only 10 entries) — a third, much sparser mapping.

None of these three are kept in sync. Concretely: `polyhedral_bridge.py`'s `FAM:RESONANCE` keyword list is `["resonate", "resonance", "harmonic", "vibrate", "oscillate", "frequency", "standing wave"]`, but `Poly.py:187`'s `'F01'` list is `['resonate', 'harmonic', 'vibrate', 'oscillate', 'frequency']` — missing `"resonance"` and `"standing wave"`. Verified reproduction:

```python
concept_lower = "resonance in a crystal lattice"
family_keywords_F01 = ['resonate', 'harmonic', 'vibrate', 'oscillate', 'frequency']
any(kw in concept_lower for kw in family_keywords_F01)  # -> False
```

Typing the literal word "resonance" into `poly glyph create "resonance in a crystal lattice"` does **not** activate Family F01 "Resonance" in `Poly.py`.

**Fix:** have both CLIs' `glyph create` call `polyhedral_bridge.encode()` (already exposed as `poly bridge encode` in `Poly.py:595-612`) instead of maintaining separate keyword tables.

### 1.3 `poly mandala create` writes entries in a format nothing else in the repo recognizes

**Files:** `Poly.py:465-539`, `Polyhedral-cli.py:321-396` (byte-identical)

This command creates `entries/<name>/<name>.md` and `entries/<name>/<name>.json` — a **subdirectory per entry** — with JSON keys `entry_id`, `seed_glyph`, `intent`, `created`, `status`, `families_activated`, `principles_activated`, `computational_outputs`.

The real convention, used by all 11 actual entries and documented in `CLAUDE.md`'s "Atlas Entry Format," is flat files `entries/NNNN_snake_case_title.{md,json}` with keys `id`, `title`, `seed_glyph`, `intent`, `resonance_sweep`, `principle_sweep`, `noise_to_insight`, `refined_glyph`, `insight`.

Running `poly mandala create` today produces an entry that:
- `validate.py`'s entry check (`ROOT.glob("entries/*.json")`, non-recursive) will never see, since it's one directory deeper.
- `atlas_index.json` won't reference.
- `glyphs/Glyphs.md` won't include.

**Fix:** either delete this command (it predates `polyhedral_bridge.generate_mandala_insight()`, which already produces the correct schema — see `polyhedral_bridge.py:341-` and its CLI-facing use in `polyhedral_explorer.py`'s `run_bridge_insight`), or rewrite it to shell out to `generate_mandala_insight()` and write flat `entries/NNNN_*.{md,json}` files.

### 1.4 `poly init`'s directory list doesn't match the real repo layout

**Files:** `Poly.py:625`, `Polyhedral-cli.py:451`

```python
dirs = ['entries', 'glyphs', 'bridges', 'outputs']
```

Neither `bridges/` nor `outputs/` exists anywhere in this repo. The directories that actually matter for a working checkout — `equations/`, `ontology/`, `atlas/`, `data/`, `experiments/`, `tests/`, `logs/` — aren't created by `init` at all.

### 1.5 `poly solve` references files that don't exist anywhere in the repo

**Files:** `Poly.py:389-452`, `Polyhedral-cli.py:245-309` (byte-identical)

References `bridges/glyph-to-geometric.json` (no `bridges/` directory exists), and on success tells the user to run `python engine/geometric_solver.py` and open `viewer/index.html` — neither `engine/` nor `viewer/` exists anywhere. `FileNotFoundError` is handled gracefully (no crash), but the command is fully non-functional and its "next steps" point at infrastructure that was never built.

### 1.6 Inconsistent dict-access safety for the same field, even within one file

**Files:** `Poly.py:219,265,271,314,319` vs `Poly.py:354,358,368,372,688` and `Polyhedral-cli.py:172,178,210,214,224,228`

Some call sites use unsafe direct indexing (`fam['domain']`), others use `fam.get('domain', '')`. This isn't just cross-file drift between the two CLIs (`Polyhedral-cli.py` uses `.get()` everywhere) — `Poly.py` itself mixes both patterns for the identical field across its `create`/`decode`/`evolve`/`scan`/`quickref` commands. Every family/principle in `atlas_schema.json` happens to have a `domain` key today, so this hasn't crashed yet, but it's a live `KeyError` risk against `protocols.json` or any future atlas variant that omits `domain`.

### 1.7 Canonical glyph symbols vs. the symbols entries actually use

**Files:** `atlas_schema.json` (canonical symbols) vs. `entries/*.json` / `entries/*.md`

`atlas_schema.json`'s Matter symbol is `◆` (U+25C6 BLACK DIAMOND); entries consistently write Matter as `◇` (U+25C7 WHITE DIAMOND) — a different Unicode codepoint. Same pattern for Resonance (`≡≡≡` canonical vs. `〰〰〰` used in entries), Life (`••••` vs. `⒮`), Emergence (`●●` vs. `∙∙●`/`●●●`), and others. `CLAUDE.md` calls this out as intentional ("stylistic variants, not contradictions"), which is a defensible editorial choice — but it has a measured, concrete cost: `experiments/glyph_opacity_probe.py` found **58.6%** of glyph tokens across `entries/*.json` are unrecognized by `polyhedral_explorer.GlyphAlgebra.tokenize()` as a direct result. See `experiments/FINDINGS.md` §5 for the full breakdown and the proposed alias-table fix (not yet implemented in the shipped code).

### 1.8 `CLAUDE.md` undercounts `Ontology.md`'s concepts (8 documented, 9 exist)

**Files:** `CLAUDE.md` "Ontological Framework" table vs. `Ontology.md` vs. `ontology/concepts/`

`CLAUDE.md`'s table lists 8 concepts: Control, Strength, Efficiency, Speed, Technology, Intelligence, Knowledge, Sensing. `Ontology.md` itself has 9 `##`-level concept sections (the same 8 plus **Scientific Rigor**), and `ontology/concepts/` has 9 matching JSON files including `scientific_rigor.json`. `CLAUDE.md`'s summary simply never mentions Scientific Rigor.

### 1.9 `validate.py`'s atlas-index cross-check never runs (see §3.1 for the code-level detail)

Counted here because it's a config/schema mismatch: `validate_atlas_index()` assumes `atlas_index.json` is a top-level JSON **array** of objects with a `"file"` key. The real file is `{"entries": [...]}`, and each entry has keys `id`/`title`/`glyph`/`tags` — no `"file"` key exists anywhere in it. The function's `isinstance(data, list)` guard returns immediately, so the check described in the script's own docstring ("5. atlas_index.json references match actual entry files") silently never executes.

### 1.10 Training data (`data/training/*.jsonl`) is stale relative to the atlas

All 17 `data/training/*.jsonl` files are dated `Jul 2 11:58`; `entries/0011_coral_reef_symbiotic_resonance.json` was added later the same day (`18:18`) and does not appear in any training file (`grep -l "0011\|coral" data/training/*.jsonl` returns nothing). `data/training/generate.py:87` globs `entries/*.json` dynamically, so this is a stale-artifact problem, not a hardcoded-count bug — it just needs a re-run: `python data/training/generate.py`.

---

## 2. Markdown Information Gaps

### 2.1 `README.md:100-102` references a script that doesn't exist

```
./fieldlink-pull.sh
```

No such file exists anywhere in the repository (`find . -iname "fieldlink-pull.sh"` finds nothing). Either the script needs to be added, or this section should be rewritten to describe the actual fieldlink workflow (`.fieldlink.json` + `fieldlink_schema.json`, consumed by `protocols/connect.json`'s exports/imports contract).

### 2.2 `README.md`'s "📂 Structure" section (lines 27-41) is drastically out of date

It lists only `entries/`, `glyphs/`, `README.md`, `atlas_index.json`. It doesn't mention `equations/`, `ontology/`, `atlas/`, `experiments/`, `tools/`, `tests/`, `data/`, `polyhedral_bridge.py`, `polyhedral_explorer.py`, `Poly.py`, `Polyhedral-cli.py`, `CLAUDE.md`, or any of the JSON schema files. A newcomer reading only `README.md` would have no idea the bridge encoder, the explorer, or the equation catalog exist.

### 2.3 `CLAUDE.md`'s own "Repository Structure" section is similarly behind current state

It documents `Poly.py`, `Polyhedral-cli.py`, `integrated.py`, the top-level JSON files, `entries/` (3 example files), `equations/`, `glyphs/`, `logs/` — but not `polyhedral_bridge.py`, `polyhedral_explorer.py`, `ontology/`, `atlas/`, `data/`, `experiments/`, `tests/`, `tools/`, `validate.py`, `PROJECTS.md`, `BridgeOrganize.md`, or `protocols/`. Since `CLAUDE.md` is the file most likely to be read first (by both humans and Claude Code sessions), this is the highest-value gap to close.

### 2.4 `CLAUDE.md`'s "Development Notes" directly contradicts the current repo

> "**No test suite**: No pytest, unittest, or test files exist. Tests would need to be set up from scratch."

`tests/test_polyhedral_bridge.py` and `tests/test_polyhedral_explorer.py` exist today, with 20 tests total, and both run standalone (`python tests/test_X.py`) or under pytest. This line was accurate when written but is now factually false. Ready fix:

```markdown
- **Test suite**: `tests/test_polyhedral_bridge.py` and `tests/test_polyhedral_explorer.py` (20 tests). Run with `python -m pytest tests/` or standalone (`python tests/test_polyhedral_bridge.py`). Poly.py, Polyhedral-cli.py, integrated.py, validate.py, and tools/*.py have no test coverage yet.
```

### 2.5 `glyphs/Glyphs.md` is missing 7 of 11 entries

**File:** `glyphs/Glyphs.md`

Only Entry 0001, 0002, 0003, and 0011 are documented (`grep -n "^## Entry"` confirms exactly these four headings). Entries 0004-0010 — Mycelial Computing, Tidal Energy Harvest, Quantum Navigation, Emotional Architecture, Fractal Governance, Symbiotic Materials, Temporal Cartography — are absent, despite `CLAUDE.md`'s own maintenance instruction: *"Updating the glyph registry: Edit `glyphs/Glyphs.md` when new glyphs are introduced."* The likely intent is a complete registry mirroring `entries/`; it has drifted since entry 0003.

### 2.6 `README.md` recommends a test command that isn't guaranteed to work out of the box

**File:** `README.md:109-113`

```markdown
### Tests
```bash
python -m pytest tests/
```
```

`pytest` is not installed in a stock environment for this repo (confirmed: `python3 -c "import pytest"` → `ModuleNotFoundError`) and there is no `requirements.txt`/`pyproject.toml` declaring it (consistent with `CLAUDE.md`'s own "No dependency management" note). The very next line does say the tests also run standalone without pytest, which is good — but leading with a command that will fail on a clean checkout is a rough first impression. Consider leading with the standalone command instead.

### 2.7 `README.md`'s test section doesn't mention `test_polyhedral_explorer.py`

**File:** `README.md:109-113` — only names `tests/test_polyhedral_bridge.py`.

### 2.8 Two parallel equation-documentation systems, uncross-referenced

`equations/F01.md` … `equations/F20_Topology.md` and `equations/P01_Symmetry.md` … `equations/P12_Unity.md` (family/principle-level summaries, referenced by `equations/equations_index.md`) coexist with the newer, more granular `equations/json/eq_NNN_*.json` + `equations/md/eq_NNN_*.md` (128 individual equation files with hashes, bindings, and — as of this session — a "Canonical SymPy Form" stub section, produced by `tools/extract_equations_atlas.py`). Neither system links to the other. A reader landing on `equations/F01.md` has no way to discover that `equations/json/eq_001_wave_equation_1d_standing_wave.json` (its underlying canonical, hashable form) exists.

### 2.9 `equations_index.md` doesn't mention the equation JSON/hash system at all

**File:** `equations/equations_index.md`

Describes itself as listing "all Families (20) and Principles (12) with their domains and example equations," pointing readers to `equations/FNN_Name.md` files — but never mentions `equation_index.json`, the `EQ:NNN` id scheme, or that formulas are also stored as structured, hashable JSON. Someone building tooling against equation data (as `polyhedral_bridge.py` itself does, via `equations/json/equation_index.json`) would not discover that from this index.

### 2.10 `CLAUDE.md` never mentions `BridgeOrganize.md`

Given finding 1.1 (it's actually Python, not Markdown, and uses a non-canonical Family/Principle vocabulary), a reader has no signal from `CLAUDE.md` about what this 16KB root-level file is, whether it's current, or how it relates to `polyhedral_bridge.py`.

### 2.11 `PROJECTS.md` claims "active fieldlink connections" that aren't verifiable from this repo alone

**File:** `PROJECTS.md`

Lists 6 "Core Integration Partners" with "active fieldlink connections," but `.fieldlink.json` only declares one source (`biogrid`, from BioGrid2.0) and no explicit connections to Rosetta-Shape-Core, Mandala-Computing, Regenerative-intelligence-core, or Emotions-as-Sensors are configured there. This may be accurate at the ecosystem level (those repos may declare the connection from their side), but as written in `PROJECTS.md` it reads as a claim this repo can't itself substantiate. Consider noting which direction each connection is declared from.

---

## 3. Code Audit

### 3.1 `validate.py`'s atlas-index cross-check is dead code

**File:** `validate.py:87-99`

```python
def validate_atlas_index(data, path):
    """Check atlas_index.json entries reference real files."""
    if not isinstance(data, list):
        return

    entries_dir = ROOT / "entries"
    for item in data:
        if "file" in item:
            json_path = entries_dir / item["file"]
            if not json_path.exists():
                md_path = json_path.with_suffix(".md")
                if not json_path.exists():
                    error(path, f"references missing file: {item['file']}")
```

Two independent bugs, either one alone would make this a no-op against the real `atlas_index.json`:
1. `atlas_index.json`'s top level is `{"entries": [...]}`, a **dict**, not a list — `isinstance(data, list)` is always `False`, so the function returns on line 90 before checking anything.
2. Even if that guard were fixed, entries have keys `id`/`title`/`glyph`/`tags` — no entry has ever had a `"file"` key, so the `if "file" in item` body would still never execute.
3. Independently, lines 96-98 compute `md_path = json_path.with_suffix(".md")` but then check `json_path.exists()` again instead of `md_path.exists()` — dead variable, redundant condition.

**Ready fix:**

```python
def validate_atlas_index(data, path):
    """Check atlas_index.json entries reference real entries/NNNN_*.{json,md} files."""
    entries = data.get("entries", []) if isinstance(data, dict) else data
    entries_dir = ROOT / "entries"
    for item in entries:
        entry_id = item.get("id")
        if not entry_id:
            continue
        matches = list(entries_dir.glob(f"{entry_id}_*.json"))
        if not matches:
            error(path, f"atlas_index entry {entry_id!r} has no matching entries/{entry_id}_*.json")
```

### 3.2 `Poly.py:187` — Resonance family keyword list doesn't contain "resonance"

Already covered in detail in §1.2; listed again here as its own code-audit item since it's a standalone, independently-fixable bug (add `"resonance"` and `"standing wave"` to the `'F01'` list, or better, delete the whole `family_keywords` dict and call `polyhedral_bridge.encode()`).

### 3.3 Zero test coverage outside `polyhedral_bridge.py` / `polyhedral_explorer.py`

`tests/` has exactly two files. `Poly.py` (716 lines), `Polyhedral-cli.py` (477 lines), `integrated.py` (194 lines), `validate.py` (169 lines), `ontology/validate_ids.py` (69 lines), `tools/extract_equations_atlas.py` (now 314 lines), `tools/enrich_ontology.py` (184 lines), and `data/training/generate.py` (989 lines) have none. Given `validate.py` has a confirmed dead-code bug (§3.1) that a single unit test would have caught, this is a concrete, not theoretical, gap.

### 3.4 Silent broad exception handling without logging

**Files:** `polyhedral_explorer.py:200-201`, `polyhedral_explorer.py:322-324`

```python
except Exception:
    pass
```
and
```python
except Exception:
    # fallback to manual construction
    self._manual_seed_glyph(new_state, child)
```

Both are legitimate fallback patterns (not silently discarding a needed result — they recover into a working alternate path), so this is a minor finding, not a crash risk. But swallowing the exception with no `repr(e)` recorded anywhere means a real bug in `encode()` (a typo in `ontology/families.json`, say) would silently downgrade every call to the weaker fallback path with zero visible signal during development. Consider at minimum appending `str(e)` to `child.state.annotations` in the second case, which already has an `annotations` list available.

### 3.5 `integrated.py` calls ~11 `self.*` methods that are never defined anywhere in the file

**File:** `integrated.py`

`CLAUDE.md` documents that `integrated.py` references 4 *external* undefined classes (`FELTEngine`, `FELTSensorImplementation`, `FearSensorImplementation`, `GlyphPhaseSynchronizer`). That's accurate but understates the gap — the following `self.*` methods are also called but never defined anywhere in `integrated.py` itself:

`load_polyhedral_atlas` (line 8), `get_families` (lines 12-16), `process_through_field` (lines 49, 56, 66, 79, 86), `detect_dishonesty_signals` / `detect_swarm_patterns` / `detect_resonance_mismatch` (lines 109, 113, 117), `update_chemical_constants` (line 93), `map_to_polyhedral_families` / `apply_principles` / `calculate_resonance_integrity` / `generate_recommendations` (lines 159, 165, 177, 192).

This doesn't change the file's documented status ("architectural design sketch, not runnable code" is accurate and sufficient), but if `CLAUDE.md`'s "Implementation Roadmap" for `integrated.py` is ever acted on, this fuller list of missing methods is what an implementer would actually need.

### 3.6 CLI file-path resolution is inconsistent across the codebase

**Files:** `Poly.py:49-60`, `Polyhedral-cli.py:49-60` vs. `polyhedral_bridge.py:32-35`, `polyhedral_explorer.py:10-12`

`polyhedral_bridge.py` and `polyhedral_explorer.py` both anchor their data-file paths to the script's own location (`ROOT = Path(__file__).resolve().parent`), so they work regardless of the caller's current working directory. `load_atlas()` in both CLI files does a bare `open(atlas_path, ...)` with a relative default (`"atlas_schema.json"`), which only resolves correctly when the CLI is invoked from the repo root. Running `python /path/to/Poly.py scan` from any other directory fails with the (reasonably handled, but avoidable) "Atlas not found" message.

### 3.7 `tools/extract_equations_atlas.py`'s ID scheme is unstable under mid-list insertion

**File:** `tools/extract_equations_atlas.py:16-20` (docstring) and the `EQ:NNN` assignment loop (~line 227 in the version before this session's fix)

The docstring claims: *"EQ:NNN allocation: monotonic, in order of first appearance... Stable across reruns when atlas_schema.json is unchanged."* That's true only when unchanged. Inserting a new equation anywhere in `atlas_schema.json` except at the very end of the very last principle's list shifts every subsequent equation's `EQ:NNN` id and filename on the next extraction run — and the script never deletes the old, now-orphaned `eq_NNN_*.{json,md}` files it leaves behind, so a rerun after a mid-list insertion produces duplicate/stale files under two different names for the same equation. (This was hit and worked around by hand during this session — see the commit adding `EQ:128` — rather than by running the tool.) Consider either an append-only mode that assigns new ids past the current max regardless of walk position, or a content-hash-derived id instead of a positional one.

### 3.8 `equations/json/eq_*.json`'s `variables` field is defined but never populated

**File:** `tools/extract_equations_atlas.py` (eq dict construction), confirmed empty (`[]`) in every one of the 128 files, e.g. `equations/json/eq_003_resonance_frequency.json`.

Not a bug — it's a documented placeholder — but worth flagging since it's exactly the kind of structured metadata a unit-checker (§5.2) would need, and it's already scaffolded, just unused.

### 3.9 `Polyhedral-cli.py` and `Poly.py` are ~70% byte-identical

`Colors` class, `print_glyph()`, `load_atlas()`, `cli()`, `scan()`, `solve()`, `fieldlink.sync()`, and `init()` are character-for-character the same in both files (diffed by inspection). `CLAUDE.md` acknowledges the risk ("Changes to shared commands should be mirrored in both files") but §1.6 and §1.2 show that mirroring has already lapsed in practice. See §4.1 for the structural fix.

### 3.10 No dependency manifest anywhere

Confirmed no `requirements.txt`, `setup.py`, `pyproject.toml`, or `Pipfile` exists. `click` is a hard runtime dependency of both CLIs (`import click` at the top of each, unguarded) but is declared nowhere machine-readable — a fresh clone's first `python Poly.py` will fail with `ModuleNotFoundError` unless the user already happens to have `click` installed. (`CLAUDE.md` documents this as a known state, not a surprise, but it's still worth fixing — see §4.8.)

---

## 4. Organizational Structure Suggestions

### 4.1 Extract the ~70% shared code between `Poly.py` and `Polyhedral-cli.py` into a common module

Given §3.9's finding, create `poly_common.py` (or `polyhedral_intelligence/cli_common.py` if §4.7 is adopted) holding `Colors`, `print_glyph()`, `load_atlas()`, and the identical `scan`/`solve`/`fieldlink`/`init` Click commands. Both CLI entry points import from it; `Poly.py` adds only the genuinely extended commands (`--ai-enhance`, `glyph evolve`, `bridge encode`, `quickref`). This directly prevents the class of drift documented in §1.6 (the `domain` access inconsistency) from recurring, because there would be exactly one copy of `decode()` instead of two.

### 4.2 Give `tests/` full-repository coverage, mirroring source filenames 1:1

The existing `tests/test_polyhedral_bridge.py` / `tests/test_polyhedral_explorer.py` naming is a good, worth-continuing pattern. Extend it: `tests/test_validate.py` (would have caught §3.1 immediately), `tests/test_cli.py` (using `click.testing.CliRunner` against both `Poly.py` and `Polyhedral-cli.py` — would have caught §1.3's schema mismatch and §3.2's keyword-matching bug), `tests/test_ontology_validate_ids.py`.

### 4.3 Keep `experiments/` and `tests/` separate — this is already correct, worth affirming

`experiments/` (falsifiable research probes, each measuring a specific claim, with `FINDINGS.md` as the durable record) and `tests/` (regression guards) serve genuinely different purposes and shouldn't be merged. No change recommended here — flagged only so this review's silence on `experiments/` isn't mistaken for an oversight.

### 4.4 Relocate and rename `BridgeOrganize.md`

Per §1.1: rename to `.py`, and move to either `experiments/` (if it's kept as a historical sketch worth preserving) or a new top-level `archive/` directory if the project wants a general home for superseded explorations. Either way, add a one-line pointer to `polyhedral_bridge.py`'s module docstring noting this was an earlier prototype.

### 4.5 Cross-link the two equation documentation systems (§2.8)

Cheapest fix: have `tools/extract_equations_atlas.py`'s `md_template()` (already producing `equations/md/eq_NNN_*.md`) include a `**Family/Principle summary:** equations/F01.md` line where applicable, and add a one-line note at the top of each `equations/FNN.md` pointing at its equations' `eq_NNN` files. A fuller fix would be to have `equations/equations_index.md` link both directions and to `equation_index.json` directly.

### 4.6 Document the `tools/` build order

`tools/extract_equations_atlas.py` must run before `tools/enrich_ontology.py` (the latter reads `equation_index.json`, which the former produces) — this is currently tribal knowledge, recoverable only by reading both scripts' source. A `tools/README.md` (or a two-line `tools/rebuild.sh`) stating the order would remove that friction, especially given §3.7's fragility around re-running the first step.

### 4.7 Consider a `src/`-style package layout (optional, not urgent for a solo maintainer)

The repo root currently holds 5 Python modules (`Poly.py`, `Polyhedral-cli.py`, `integrated.py`, `polyhedral_bridge.py`, `polyhedral_explorer.py`, `validate.py`) alongside ~10 top-level data/doc files. This is a legitimate, low-ceremony layout for the project's current size and isn't broken — flagging it only as a forward-looking option if the module count keeps growing: a `polyhedral_intelligence/` package (or `src/polyhedral_intelligence/`) would set up cleanly for eventual `pip install -e .` and make `import polyhedral_bridge` work from any directory without the `sys.path.insert()` gymnastics currently duplicated in `polyhedral_explorer.py:10-12` and every `tests/test_*.py`/`experiments/*.py` file.

### 4.8 Add a minimal dependency manifest

Per §3.10: a `requirements.txt` with just `click` (the one hard runtime dependency) resolves the fresh-clone failure mode directly. If §4.7's package layout is adopted, a `pyproject.toml` with an `[project.optional-dependencies]` `experiments = ["sympy", "sentence-transformers"]` extra would also make `experiments/`'s dependency-on-demand pattern (documented per-script today, e.g. `experiments/equation_canonicalization_probe.py`'s docstring) machine-installable: `pip install -e ".[experiments]"`.

---

## 5. Limitations Mitigation Checklist

**Caveat, stated up front rather than left implicit:** this checklist's framing (symbolic-subsymbolic grounding, falsifiability, formal verification) describes an **AI-grounding / claim-verification system**. Polyhedral Intelligence is not that — it's a symbolic *design* system that maps free-text concepts onto a 20-family/12-principle glyph vocabulary and a catalog of physics equations, for creative/architectural reframing (the Noise-to-Insight Protocol), not for verifying the truth of claims. The assessments below are an honest best-effort mapping of the checklist onto what the codebase actually does, not an argument that it should become a claim-verification system. Several of the "missing" items below are missing because they're out of the project's actual scope, not because of an oversight.

### 5.1 Symbolic–Subsymbolic Gap
*Is there explicit extraction of logical form? Connection to symbolic solvers?* — **Partially addressed.**

There is a real symbolic layer: 128 hashable equations (`equations/json/eq_*.json`) with stable `EQ:NNN` ids, bound to families/principles via `ontology/families.json`'s `equation_ids`. `polyhedral_bridge.encode()` associates free text with this symbolic layer via keyword matching + amplitude scoring, returning `equation_hashes` above a threshold. What's missing is anything *derivational*: no logical-form extraction (text is never parsed into predicates/FOL), and no connection to a symbolic solver (SAT/SMT/theorem prover). This session's `experiments/equation_canonicalization_probe.py` measured that even a purely mechanical bridge to a CAS (SymPy) would currently succeed on only 1-3% of the 128 formulas as written (see `experiments/FINDINGS.md` §2) — so the symbolic layer that exists today is a human-readable catalog, not yet a machine-manipulable one.

**Suggested next step (if this direction is wanted):** the `canonical_form_sympy` field added to the equation JSON schema this session (currently empty on all 128 equations, see `experiments/FINDINGS.md`'s decision-point 3) is the concrete hook for this — populate it equation-by-equation, then a real `sympy.parse_expr()`-based solver connection becomes possible.

### 5.2 Grounding Problem
*Are units/dimensions checked? Lower-layer constraints enforced? Meta-grounding flag for revolutionary claims?* — **Missing**, with one ready hook.

No dimensional-analysis or unit-consistency checking exists anywhere. The `variables` field on every equation JSON (§3.8) is present but always `[]` — it's the obvious place unit metadata would live, e.g.:

```json
"variables": [
  {"symbol": "F", "unit": "N", "dimension": "M L T^-2"},
  {"symbol": "G", "unit": "N m^2 kg^-2", "dimension": "M^-1 L^3 T^-2"}
]
```

No "meta-grounding flag for revolutionary claims" exists. `ontology/concepts/scientific_rigor.json` (and its `Ontology.md` counterpart) is the closest conceptual relative — it documents Western vs. relational definitions of rigor — but it's descriptive ontology, not an executable check that could flag e.g. an equation combination implying faster-than-light travel.

### 5.3 Semantic Ambiguity
*Are vague terms quantified? Is scope explicit? Is a reference class specified?* — **Partially addressed.**

`encode()`'s L1-normalized amplitude vectors are a genuine, if crude, quantification of "how strongly does this text resonate with each family/principle" (0.0-1.0, summing to 1.0 across all 20/12). `generate_mandala_insight()`'s `resonance_sweep`/`principle_sweep` gives explicit counts (e.g., "17/20 families balanced"). What's absent: no explicit temporal/spatial/ontological scope field on any entry or encoding, and no "reference class" concept (e.g., comparing a new seed's amplitude profile against a corpus of prior seeds — `experiments/`'s own analyses do this manually, per-experiment, but it isn't a first-class feature of `generate_mandala_insight()`).

### 5.4 Falsifiability Paradox
*Can the system enumerate a refutation-observation set? Escape-hatch detector? Falsifiable/unfalsifiable classifier?* — **Partially addressed — and this is the strongest-scoring item on the checklist.**

`experiments/` is, functionally, a falsification practice: each script states a specific, checkable claim and is designed so it *could* fail. Two of them did — `experiments/semantic_resonance_eval.py`'s "richer auto-derived corpus" hypothesis was measured at 33% accuracy against a 42% keyword-matching baseline, i.e. actively falsified rather than just "not tried" (see `experiments/FINDINGS.md` §1). This is genuinely good practice, uncommon to see documented this explicitly in a project of this size. What's missing to call this "addressed" rather than "partial": it's a manual research discipline invoked by a human running scripts, not a system capability — there's no `is_falsifiable(claim)` function, no automatic refutation-set enumeration wired into `generate_mandala_insight()` itself, and no hedge-word/"escape hatch" phrase detector (e.g., flagging "may in some cases suggest" as unfalsifiable framing) anywhere in `polyhedral_bridge.py`.

### 5.5 Formal Verification vs. Complexity
*Is formal proof scoped? Is background knowledge accessible? Probabilistic fallback with confidence?* — **Partially addressed.**

No formal-proof system exists (consistent with §5.1 — realistically out of scope given §5.1's 1-3% parseability finding). Background knowledge **is** accessible and well-structured: `ontology/families.json`/`principles.json` carry `exemplars`, `physics_domains`, `equation_ids`, `description`, and adjacency (`neighbors_on_icosahedron`/`neighbors_on_dodecahedron`) — a real, queryable graph, not just prose. A probabilistic-flavored fallback does exist in the form of the amplitude vectors, but it isn't framed or calibrated as "confidence" anywhere in the code or its output schema, and `experiments/semantic_resonance_eval.py`'s measured 42% accuracy on an adversarial eval set (§5.1/§5.3) means that if these amplitudes *were* read as calibrated confidence today, they'd currently be overconfident relative to that measurement.

---

## 6. Discoverability & Crawler Optimization

Checked against `README.md`, repo root, and the live GitHub repository metadata (`JinnZ2/Polyhedral-Intelligence`, fetched via the GitHub API during this review).

| Item | Status |
|---|---|
| Concise "What is this?" summary with high-signal keywords | Partially addressed |
| Repository topics set | **Missing** (confirmed via API — no topics returned) |
| `KEYWORDS.txt`/`.md` | **Missing** |
| `CITATION.cff` | **Missing** |
| "Why This Matters" / urgency statement | Partially addressed |
| Structured metadata (YAML frontmatter / JSON-LD) | **Missing** |
| Clear public API import example (one-liner) | Partially addressed |
| Open license clearly marked | Partially addressed (LICENSE file + GitHub metadata both correctly say CC0-1.0; `README.md` itself never mentions the license) |
| GitHub Pages / simple site | **Missing** (optional) |
| Anonymous feedback mechanism (issue templates) | **Missing** (`has_issues: true` but no `.github/ISSUE_TEMPLATE/`) |

### 6.1 Repository topics — not markdown, but the single highest-leverage fix here

GitHub topics are what search and many AI crawlers index first, and this repo has none set. Not fixable via a markdown snippet; run:

```bash
gh repo edit JinnZ2/Polyhedral-Intelligence --add-topic symbolic-ai --add-topic knowledge-representation --add-topic ontology --add-topic glyph --add-topic mandala --add-topic design-language --add-topic python
```

### 6.2 `KEYWORDS.md` — ready to paste as a new file

```markdown
# Keywords

symbolic AI, symbolic reasoning, knowledge representation, ontology,
mandala, glyph system, design language, icosahedron, dodecahedron,
platonic solids, families and principles, resonance sweep,
noise-to-insight, redesign protocol, physics equation catalog,
equation ontology, semantic bridge, text-to-glyph encoding,
polyhedral cognition, atlas of design, symbolic knowledge graph,
Python, CC0, open knowledge base
```

### 6.3 `CITATION.cff` — ready to paste as a new file

```yaml
cff-version: 1.2.0
message: "If you use this project, please cite it as below."
title: "Polyhedral Intelligence"
abstract: >-
  A mandala codex of families, principles, and glyphs — a living atlas
  of symbolic redesign using the Mandala Redesign Protocol and
  Noise-to-Insight Protocol.
authors:
  - name: "JinnZ2"
repository-code: "https://github.com/JinnZ2/Polyhedral-Intelligence"
license: CC0-1.0
```

### 6.4 YAML frontmatter for `README.md` — ready to paste at the very top of the file

```yaml
---
title: Polyhedral Intelligence
description: >-
  A symbolic knowledge system mapping concepts onto 20 Families
  (icosahedron) and 12 Principles (dodecahedron) via the Mandala
  Redesign Protocol and Noise-to-Insight Protocol.
keywords: [symbolic-ai, ontology, knowledge-representation, mandala, glyph-system]
license: CC0-1.0
language: Python
---
```

### 6.5 High-signal "What is this?" summary and API one-liner — ready to paste near the top of `README.md`, after the title

```markdown
**What is this?** Polyhedral Intelligence turns any text description of a
concept into a symbolic "glyph" — a short sequence of Unicode runes drawn
from 20 conceptual Families (mapped to an icosahedron) and 12 Principles
(mapped to a dodecahedron) — then sweeps it for imbalance and reframes any
flagged "noise" (turbulence, uncertainty, delay, error, instability) as a
design feature rather than a flaw. It's backed by a catalog of 128 named
physics/math equations bound to those Families and Principles.

```python
from polyhedral_bridge import encode
enc = encode("a hexagonal mesh under tidal load")
print(enc.glyph_signature)  # -> composite glyph, e.g. "⬡➝↻"
```
```

### 6.6 Minimal issue templates — ready to paste as `.github/ISSUE_TEMPLATE/config.yml` plus one template

`.github/ISSUE_TEMPLATE/config.yml`:
```yaml
blank_issues_enabled: true
contact_links:
  - name: Question or general feedback
    url: https://github.com/JinnZ2/Polyhedral-Intelligence/discussions
    about: Ask a question or share feedback — no template needed.
```

`.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug report
about: Something in the atlas, bridge, or CLI isn't behaving as documented
---

**What happened:**

**What you expected:**

**Steps to reproduce:**
```

### 6.7 License visibility in `README.md`

`README.md` never mentions the license at all today, despite `LICENSE` (CC0-1.0) being present and correctly set in GitHub's own repo metadata. Add near the bottom:

```markdown
## License
CC0-1.0 — public domain dedication. See [LICENSE](LICENSE).
```

---

## Confirmation

`REVIEW.md` has been created at the repository root with all six sections above.
