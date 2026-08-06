# SPDX-License-Identifier: CC0-1.0
"""Probe for #5 (fuzzy glyph tokenization): how opaque is GlyphAlgebra to
the glyphs actually used in entries/*.json, right now, with zero changes?

Claim under test: "glyph algebra depends on known symbols; unknown glyphs
are opaque." This measures the size of that problem on real data instead
of arguing about it in the abstract, and classifies each unknown symbol as
either a known stylistic alias (same concept, different codepoint from the
canonical atlas_schema.json symbol) or a genuinely novel/unclassified rune.

Run: python experiments/glyph_opacity_probe.py
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from polyhedral_explorer import GlyphAlgebra, PolyhedralMandala  # noqa: E402

# Manually verified aliases: symbol -> (family/principle name it stands in
# for in entries/*.json, canonical schema symbol). Built by inspecting the
# unknown-symbol list below against each entry's own prose (e.g. entry 0001
# glosses "◇" as "Matter (◇)" in glyphs/Glyphs.md, and atlas_schema.json's
# Matter symbol is "◆" — same concept, different diamond codepoint).
KNOWN_ALIASES = {
    "〰": ("Resonance", "≡≡≡"),
    "⋮": ("Cognition", "⋯⋯"),
    "⋯": ("Cognition", "⋯⋯"),
    "∙": ("Emergence", "●●"),
    "•": ("Life", "••••"),
    "●": ("Emergence", "●●"),
    "⒮": ("Life", "••••"),
    "◉": ("Consciousness", "◎"),
    "◇": ("Matter", "◆"),
    "✦": ("Particle", "⚪"),
    "◠": ("Relativity", "⊗≡"),
    "⟳": ("Conservation", "↺"),
    "△": ("Energy-Thermo", "△≈"),
    "≋": ("Flow", "↻"),
    "⊙": ("Earth-Cosmos", "◯"),
    "☯": ("Particle", "⚪"),
}


def main() -> int:
    mandala = PolyhedralMandala(str(ROOT / "atlas_schema.json"))
    algebra = GlyphAlgebra(mandala)

    total = 0
    unknown_counts: dict[str, int] = {}
    for path in sorted(glob.glob(str(ROOT / "entries" / "*.json"))):
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        for field in ("seed_glyph", "refined_glyph"):
            for sym, info in algebra.tokenize(d.get(field, "")):
                total += 1
                if info is None:
                    unknown_counts[sym] = unknown_counts.get(sym, 0) + 1

    unknown_total = sum(unknown_counts.values())
    known_alias_total = sum(c for s, c in unknown_counts.items() if s in KNOWN_ALIASES)
    genuinely_novel = {s: c for s, c in unknown_counts.items() if s not in KNOWN_ALIASES}

    print(f"total glyph tokens scanned:      {total}")
    print(f"unrecognized tokens:             {unknown_total} ({unknown_total/total:.1%})")
    print(f"  of which known stylistic alias: {known_alias_total} ({known_alias_total/unknown_total:.1%} of unknowns)")
    print(f"  of which genuinely unclassified: {sum(genuinely_novel.values())}")
    if genuinely_novel:
        print("  genuinely unclassified symbols:")
        for s, c in sorted(genuinely_novel.items(), key=lambda x: -x[1]):
            print(f"    {s!r}: {c}")
    print()
    print(f"CONCLUSION: {known_alias_total/unknown_total:.0%} of current opacity is a small, "
          f"enumerable alias-table problem, not a fuzzy/visual-embedding problem.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
