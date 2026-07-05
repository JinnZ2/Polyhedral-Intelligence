# SPDX-License-Identifier: CC0-1.0
"""Smoke tests for polyhedral_explorer.MRPExplorer.

These exist because every prior revision of this file (polyhedral_explorer.py
v1-v3, polyhedral_bridge_v2.py) crashed on the first call to select() with
AttributeError: 'TreeNode' object has no attribute 'annotations' — none of
them had ever been executed before being committed. Running the full action
set here is the regression guard against that happening again silently.

Run with:
    python -m pytest tests/test_polyhedral_explorer.py
or:
    python tests/test_polyhedral_explorer.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from polyhedral_explorer import MRPExplorer  # noqa: E402

ATLAS = str(ROOT / "atlas_schema.json")


def _joined(exp: MRPExplorer) -> str:
    return "\n".join(exp.current.state.annotations)


def test_full_walkthrough_does_not_crash():
    """The full seed -> sweep -> glyph -> bridge-insight path runs end to end."""
    exp = MRPExplorer(ATLAS)
    exp.select("set_seed_concept:hexagonal mesh under tidal load")
    exp.select("run_family_sweep")
    exp.select("run_principle_sweep")
    exp.select("generate_seed_glyph")
    exp.select("run_bridge_insight")
    out = _joined(exp)
    assert "Seed: hexagonal mesh under tidal load" in out
    assert exp.current.state.current_glyph


def test_bridge_actually_used_not_silently_bypassed():
    """Family/principle resonance uses canonical FAM:*/PRIN:* bridge keys,
    not the crude tag-overlap fallback (regression guard for the
    fam_id_to_short KeyError that used to swallow the real encoding)."""
    exp = MRPExplorer(ATLAS)
    assert exp.bridge_used is True
    exp.select("set_seed_concept:hexagonal mesh under tidal load")
    exp.select("run_family_sweep")
    fam_res = exp.current.state.family_resonance
    assert any(k.startswith("FAM:") for k in fam_res)
    assert fam_res["FAM:NETWORKS"] > 0


def test_add_bridge_glyphs_resolves_symbols_from_canonical_ids():
    """add_bridge_glyphs must resolve glyph symbols even though
    family_resonance is keyed by canonical FAM:* ids, not the legacy
    F01-style ids mandala.families uses."""
    exp = MRPExplorer(ATLAS)
    exp.select("set_seed_concept:xyzzy plugh foobar")  # no keyword hits -> all-zero amplitudes
    exp.select("run_family_sweep")
    exp.select("run_principle_sweep")
    exp.select("generate_seed_glyph")
    before = exp.current.state.current_glyph
    exp.select("add_bridge_glyphs")
    out = _joined(exp)
    assert "No low" not in out or exp.current.state.current_glyph != before


def test_compare_and_merge_glyphs_are_wired_to_glyph_algebra():
    exp = MRPExplorer(ATLAS)
    exp.select("compare_glyphs:◇⚙:◇⇑")
    out = _joined(exp)
    assert "Similarity" in out
    assert "not implemented" not in out.lower()

    exp2 = MRPExplorer(ATLAS)
    exp2.select("merge_glyphs:◇⚙:⬡⇑")
    merged_out = _joined(exp2)
    assert "Merged:" in merged_out
    assert exp2.current.state.current_glyph.startswith("◇⚙")


def test_record_atlas_entry_stages_a_file():
    exp = MRPExplorer(ATLAS)
    exp.select("set_seed_concept:tidal resonance mesh")
    exp.select("run_family_sweep")
    exp.select("run_principle_sweep")
    exp.select("generate_seed_glyph")
    with tempfile.TemporaryDirectory() as tmp:
        import os
        os.environ["FIELDLINK_PATH"] = tmp
        exp.select("record_atlas_entry")
        staged = list(Path(tmp).glob("*.json"))
        assert len(staged) == 1


def test_save_branch_round_trips_annotations():
    exp = MRPExplorer(ATLAS)
    exp.select("set_seed_concept:test")
    exp.select("list_families")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        path = tmp.name
    try:
        exp.save_branch(path)
        import json
        with open(path, encoding="utf-8") as f:
            tree = json.load(f)
        assert tree["choice"] == "root"
        assert tree["children"]
    finally:
        Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    tests = [
        test_full_walkthrough_does_not_crash,
        test_bridge_actually_used_not_silently_bypassed,
        test_add_bridge_glyphs_resolves_symbols_from_canonical_ids,
        test_compare_and_merge_glyphs_are_wired_to_glyph_algebra,
        test_record_atlas_entry_stages_a_file,
        test_save_branch_round_trips_annotations,
    ]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
            failures += 1
        except Exception as e:
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            failures += 1
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(0 if failures == 0 else 1)
