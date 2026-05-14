# SPDX-License-Identifier: CC0-1.0
"""Smoke tests for polyhedral_bridge.encode().

Run with:
    python -m pytest tests/test_polyhedral_bridge.py
or:
    python tests/test_polyhedral_bridge.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import polyhedral_bridge  # noqa: E402
from polyhedral_bridge import PolyhedralEncoding, encode  # noqa: E402


def _l1_invariant(amps: dict[str, float]) -> bool:
    total = sum(amps.values())
    return abs(total - 1.0) < 1e-9 or total == 0.0


def test_text_input_networks_and_flow():
    """Hexagonal mesh under tidal load → expect FAM:NETWORKS and FAM:FLOW non-zero."""
    enc = encode("a hexagonal mesh under tidal load")
    assert isinstance(enc, PolyhedralEncoding)
    assert enc.family_amplitudes_l1["FAM:NETWORKS"] > 0
    assert enc.family_amplitudes_l1["FAM:FLOW"] > 0
    assert _l1_invariant(enc.family_amplitudes_l1)
    assert enc.provenance["input_type"] == "text"
    assert enc.provenance["amplitude_convention"] == "L1"


def test_dict_seed_input_deterministic():
    """Same dict seed payload → identical glyph signature across runs."""
    seed = {
        "intent": "self-healing crystalline lattice",
        "tags": ["FAM:MATTER", "FAM:NETWORKS"],
        "glyph": "◇⬡",
    }
    enc1 = encode(seed)
    enc2 = encode(seed)
    assert enc1.glyph_signature == enc2.glyph_signature
    assert enc1.family_amplitudes_l1 == enc2.family_amplitudes_l1
    assert enc1.principle_amplitudes_l1 == enc2.principle_amplitudes_l1
    # Tag bonus pushed FAM:MATTER and FAM:NETWORKS amplitudes up
    assert enc1.family_raw_counts["FAM:MATTER"] >= 1
    assert enc1.family_raw_counts["FAM:NETWORKS"] >= 1


def test_l1_invariants():
    """Family and principle amplitudes each sum to 1.0 when any signal is present."""
    enc = encode("turbulent flow with quantum uncertainty in the resonance frequency")
    assert _l1_invariant(enc.family_amplitudes_l1)
    assert _l1_invariant(enc.principle_amplitudes_l1)
    fam_v_sum = sum(enc.family_vector)
    prin_v_sum = sum(enc.principle_vector)
    assert abs(fam_v_sum - 1.0) < 1e-9 or fam_v_sum == 0.0
    assert abs(prin_v_sum - 1.0) < 1e-9 or prin_v_sum == 0.0


def test_empty_signal_does_not_crash():
    """A payload with no recognized keywords produces a fallback glyph and zero vectors."""
    enc = encode("xyzzy plugh foobar")
    assert sum(enc.family_amplitudes_l1.values()) == 0.0
    assert sum(enc.principle_amplitudes_l1.values()) == 0.0
    assert enc.glyph_signature == "◯"
    assert enc.equation_hashes == []


def test_missing_crf_fallback():
    """When metrology.constraint_recovery_framework is unavailable,
    duck-typed objects still encode and provenance.crf_available is False."""
    class FakeConstraint:
        name = "tidal energy harvest"
        description = "tidal flow on a hexagonal grid"
        tags = ["FAM:FLOW"]
        variables = ["v", "p"]

    enc = encode(FakeConstraint())
    assert enc.family_amplitudes_l1["FAM:FLOW"] > 0
    assert _l1_invariant(enc.family_amplitudes_l1)
    if not polyhedral_bridge._HAS_CRF:
        assert enc.provenance["crf_available"] is False


def test_equation_hashes_above_threshold():
    """Equation hashes for above-threshold families/principles are returned."""
    enc = encode("resonance and conservation of energy")
    assert isinstance(enc.equation_hashes, list)
    if enc.equation_hashes:
        for h in enc.equation_hashes:
            assert h.startswith("sha256:") and len(h) == 71  # "sha256:" + 64 hex


def test_glyph_signature_uses_top_three_then_top_two():
    """Composite glyph: up to 3 family glyphs ➝ up to 2 principle glyphs."""
    enc = encode("hexagonal mesh under turbulent flow with conservation of energy")
    assert "➝" in enc.glyph_signature
    parts = enc.glyph_signature.split("➝")
    assert 1 <= len(parts) <= 5


if __name__ == "__main__":
    tests = [
        test_text_input_networks_and_flow,
        test_dict_seed_input_deterministic,
        test_l1_invariants,
        test_empty_signal_does_not_crash,
        test_missing_crf_fallback,
        test_equation_hashes_above_threshold,
        test_glyph_signature_uses_top_three_then_top_two,
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
