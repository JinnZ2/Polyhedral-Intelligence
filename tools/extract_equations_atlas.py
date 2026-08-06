# SPDX-License-Identifier: CC0-1.0
"""Block A pass 1: extract equations from atlas_schema.json into paired .json + .md files.

Walks atlas_schema.json families (F01..F20, 4 equations each) then principles
(P01..P12, 4 equations each). Deduplicates by SHA256 of the canonical form
(whitespace-normalized): the same formula appearing under multiple
families/principles becomes one equation with a merged bindings list, plus
aliases[] capturing the alternate names.

Each unique equation produces:
  equations/json/eq_NNN_<slug>.json   (canonical, hashable)
  equations/md/eq_NNN_<slug>.md       (narrative wrapper, derivation TODO)

Builds equations/json/equation_index.json.

EQ:NNN allocation: monotonic, in order of first appearance during the
families-then-principles walk. Stable across reruns when atlas_schema.json
is unchanged.

Idempotent: re-running with no atlas changes produces the same files.

Validation: every FAM:* / PRIN:* binding is checked against
ontology/validate_ids.py. Unknown IDs hard-fail the extraction.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "atlas_schema.json"
JSON_DIR = ROOT / "equations" / "json"
MD_DIR = ROOT / "equations" / "md"
INDEX_PATH = JSON_DIR / "equation_index.json"

sys.path.insert(0, str(ROOT / "ontology"))
from validate_ids import (  # noqa: E402
    family_legacy_to_id,
    principle_legacy_to_id,
    validate_bindings,
)


def slugify(name: str, max_len: int = 50) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    return s[:max_len]


def canonical_form_hash(formula: str) -> str:
    normalized = re.sub(r"\s+", " ", formula.strip())
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def md_template(eq: dict, filename_stem: str) -> str:
    fams = ", ".join(eq["families"]) if eq["families"] else "—"
    prins = ", ".join(eq["principles"]) if eq["principles"] else "—"
    tags = ", ".join(eq.get("tags", [])) if eq.get("tags") else "—"
    aliases = ", ".join(eq.get("aliases", [])) if eq.get("aliases") else "—"
    glyph = eq.get("glyph", "")
    glyph_name = eq.get("glyph_name", "")
    glyph_line = f"{glyph} *{glyph_name}*" if glyph and glyph_name else (glyph or "—")
    sources_line = "; ".join(
        f"{src['file']} (as `{src.get('context_name', eq['canonical_name'])}`)"
        for src in eq["extracted_from"]
    )

    return f"""# {eq["canonical_name"]}

**Equation ID:** `{eq["id"]}`
**Hash:** `{eq["hash"]}`
**License:** {eq["license"]}
**Sources:** {sources_line}

## Canonical Form

```
{eq["canonical_form_ascii"]}
```

## Bindings

- **Families:** {fams}
- **Principles:** {prins}
- **Aliases:** {aliases}
- **Atlas glyph:** {glyph_line}
- **Tags:** {tags}

## Derivation

> _TODO: narrative derivation. How is this equation constructed from first principles?_

## Canonical SymPy Form

> _TODO: a SymPy-parseable expression, filled in alongside the derivation
> above (not auto-extracted — see experiments/equation_canonicalization_probe.py:
> `canonical_form_ascii` is written for human readability, not parsing, and
> only ~3% of the corpus parses as-is even after generic preprocessing).
> Back-port into this equation's `canonical_form_sympy` field in
> `equations/json/{filename_stem}.json` once written, so mathematically
> equivalent equations can eventually be found by canonicalized-form
> comparison instead of string-hash identity._

## History

> _TODO: when and where this equation arose; key contributors; cultural context._

## Cross-cultural notes

> _TODO: any non-Western traditions in which this pattern appears, with attribution._

## Where it fails

> _TODO: regimes, assumptions, or domains where this equation breaks down._

---

*Narrative wrapper for the canonical JSON at `equations/json/{filename_stem}.json`.*
"""


def write_files(eq: dict, json_path: Path, md_path: Path, filename_stem: str) -> tuple[bool, bool]:
    json_written = False
    md_written = False

    eq_for_disk = {k: v for k, v in eq.items() if not k.startswith("_")}
    new_json_text = json.dumps(eq_for_disk, ensure_ascii=False, indent=2) + "\n"
    if not json_path.exists() or json_path.read_text(encoding="utf-8") != new_json_text:
        json_path.write_text(new_json_text, encoding="utf-8")
        json_written = True

    new_md_text = md_template(eq, filename_stem)
    if not md_path.exists() or md_path.read_text(encoding="utf-8") != new_md_text:
        md_path.write_text(new_md_text, encoding="utf-8")
        md_written = True

    return json_written, md_written


def emit_atlas_walk(atlas: dict, fmap: dict, pmap: dict):
    """Yield (raw_eq, family_id_or_None, principle_id_or_None, context_label)."""
    for fam in atlas["families"]:
        legacy = fam["id"]
        if legacy not in fmap:
            raise SystemExit(f"atlas family {legacy!r} not in ontology/families.json")
        fid = fmap[legacy]
        for raw_eq in fam.get("equations", []):
            yield raw_eq, fid, None, f"{legacy} {fam['name']}"

    for prin in atlas["principles"]:
        legacy = prin["id"]
        if legacy not in pmap:
            raise SystemExit(f"atlas principle {legacy!r} not in ontology/principles.json")
        pid = pmap[legacy]
        for raw_eq in prin.get("equations", []):
            yield raw_eq, None, pid, f"{legacy} {prin['name']}"


def main() -> int:
    if not ATLAS.exists():
        print(f"atlas_schema.json not found at {ATLAS}", file=sys.stderr)
        return 1

    JSON_DIR.mkdir(parents=True, exist_ok=True)
    MD_DIR.mkdir(parents=True, exist_ok=True)

    fmap = family_legacy_to_id()
    pmap = principle_legacy_to_id()

    with ATLAS.open("r", encoding="utf-8") as f:
        atlas = json.load(f)

    extracted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    by_hash_eq: dict[str, dict] = {}
    order: list[str] = []  # hashes in first-appearance order

    merge_count = 0

    for raw_eq, fid, pid, ctx in emit_atlas_walk(atlas, fmap, pmap):
        name = raw_eq["name"]
        formula = raw_eq["formula"]
        h = canonical_form_hash(formula)

        if h in by_hash_eq:
            eq = by_hash_eq[h]
            if fid and fid not in eq["families"]:
                eq["families"].append(fid)
            if pid and pid not in eq["principles"]:
                eq["principles"].append(pid)
            if name != eq["canonical_name"] and name not in eq.get("aliases", []):
                eq.setdefault("aliases", []).append(name)
            for tag in raw_eq.get("tags", []):
                if tag not in eq["tags"]:
                    eq["tags"].append(tag)
            eq["extracted_from"].append({
                "file": ATLAS.name,
                "path": ctx,
                "extracted_at": extracted_at,
                "context_name": name,
            })
            merge_count += 1
        else:
            eq = {
                "id": "",  # assigned after walk
                "canonical_name": name,
                "canonical_form_latex": "",
                "canonical_form_ascii": formula,
                "canonical_form_sympy": "",  # filled by hand during derivation-writing, see md_template()
                "hash": h,
                "variables": [],
                "families": [fid] if fid else [],
                "principles": [pid] if pid else [],
                "source_provenance": [],
                "applies_in_repos": ["polyhedral-intelligence"],
                "version": "1.0",
                "license": "CC0-1.0",
                "tags": list(raw_eq.get("tags", [])),
                "aliases": [],
                "glyph": raw_eq.get("glyph", ""),
                "glyph_name": raw_eq.get("glyph_name", ""),
                "extracted_from": [{
                    "file": ATLAS.name,
                    "path": ctx,
                    "extracted_at": extracted_at,
                    "context_name": name,
                }],
            }
            by_hash_eq[h] = eq
            order.append(h)

    for i, h in enumerate(order, start=1):
        eq = by_hash_eq[h]
        eq["id"] = f"EQ:{i:03d}"
        eq["_filename_stem"] = f"eq_{i:03d}_{slugify(eq['canonical_name'])}"
        errors = validate_bindings(eq["families"], eq["principles"])
        if errors:
            raise SystemExit(f"binding validation failed for {eq['id']}: {errors}")

    json_writes = 0
    md_writes = 0

    for eq in by_hash_eq.values():
        stem = eq["_filename_stem"]
        json_path = JSON_DIR / f"{stem}.json"
        md_path = MD_DIR / f"{stem}.md"
        jw, mw = write_files(eq, json_path, md_path, stem)
        json_writes += int(jw)
        md_writes += int(mw)

    by_id: dict[str, str] = {}
    by_hash: dict[str, str] = {}
    by_family: dict[str, list[str]] = {}
    by_principle: dict[str, list[str]] = {}
    by_source: dict[str, list[str]] = {ATLAS.name: []}

    for eq in by_hash_eq.values():
        by_id[eq["id"]] = f"{eq['_filename_stem']}.json"
        by_hash[eq["hash"]] = eq["id"]
        for fid in eq["families"]:
            by_family.setdefault(fid, []).append(eq["id"])
        for pid in eq["principles"]:
            by_principle.setdefault(pid, []).append(eq["id"])
        by_source[ATLAS.name].append(eq["id"])

    index = {
        "version": "1.0",
        "generated": extracted_at,
        "count": len(by_hash_eq),
        "by_id": by_id,
        "by_hash": by_hash,
        "by_family": by_family,
        "by_principle": by_principle,
        "by_source": by_source,
    }

    new_index_text = json.dumps(index, ensure_ascii=False, indent=2) + "\n"
    if not INDEX_PATH.exists() or INDEX_PATH.read_text(encoding="utf-8") != new_index_text:
        INDEX_PATH.write_text(new_index_text, encoding="utf-8")
        index_written = True
    else:
        index_written = False

    print(f"unique equations:   {len(by_hash_eq)}")
    print(f"merged duplicates:  {merge_count}")
    print(f"json files written: {json_writes}")
    print(f"md files written:   {md_writes}")
    print(f"equation_index.json {'rewritten' if index_written else 'unchanged'}")
    print(f"families covered:   {len(by_family)} / 20")
    print(f"principles covered: {len(by_principle)} / 12")

    return 0


if __name__ == "__main__":
    sys.exit(main())
