# SPDX-License-Identifier: CC0-1.0
"""Probe for #3 (hardcoded NIP mappings): how much of the *real* flagged-id
space does polyhedral_bridge._NIP_PATTERN_FOR_ID actually cover, measured
against every flag that has ever appeared in entries/*.json?

Claim under test: "the mapping is hand-assigned... it doesn't scale."
This measures the coverage gap on real data, and separately flags a data
quality issue found along the way (a family/principle name misfiled under
the wrong sweep in an existing entry) — you can't responsibly build a
learned model on top of a labeling bug you haven't found yet.

Run: python experiments/nip_pattern_coverage_probe.py
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from polyhedral_bridge import _NIP_PATTERN_FOR_ID  # noqa: E402

# The 20 canonical family names and 12 principle names, for the data-quality check.
FAMILY_NAMES = {
    "Resonance", "Flow", "Information", "Life", "Energy-Thermo", "Cognition",
    "Earth-Cosmos", "Matter", "Geometry", "Particle", "Engineering", "Networks",
    "Reaction", "Measurement", "Navigation", "Consciousness", "Turbulence",
    "Relativity", "Statistical", "Topology",
}
PRINCIPLE_NAMES = {
    "Symmetry", "Conservation", "Relativity", "Duality", "Emergence", "Resonance",
    "Continuity", "Quantization", "Proportion", "Uncertainty", "Transformation", "Unity",
}

# Reverse lookup: name -> canonical id, built from the hardcoded table's own
# keys plus the family/principle name lists (both "Relativity" ids exist,
# under FAM: and PRIN:, so this is deliberately kept separate per sweep).
_COVERED_FAM_NAMES = {k.split(":", 1)[1].replace("_", "-").title() for k in _NIP_PATTERN_FOR_ID if k.startswith("FAM:")}
_COVERED_PRIN_NAMES = {k.split(":", 1)[1].title() for k in _NIP_PATTERN_FOR_ID if k.startswith("PRIN:")}


def main() -> int:
    fam_flag_counts: dict[str, int] = {}
    prin_flag_counts: dict[str, int] = {}
    data_quality_issues: list[str] = []

    for path in sorted(glob.glob(str(ROOT / "entries" / "*.json"))):
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        for f in d["resonance_sweep"]["flags"]:
            name = f.split(" ", 1)[1]
            fam_flag_counts[name] = fam_flag_counts.get(name, 0) + 1
            if name not in FAMILY_NAMES:
                data_quality_issues.append(
                    f"{Path(path).name}: '{name}' flagged under resonance_sweep (families) "
                    f"but is not one of the 20 Family names"
                    + (" (it's a Principle)" if name in PRINCIPLE_NAMES else "")
                )
        for f in d["principle_sweep"]["flags"]:
            name = f.split(" ", 1)[1]
            prin_flag_counts[name] = prin_flag_counts.get(name, 0) + 1

    fam_covered = sum(c for n, c in fam_flag_counts.items() if n in _COVERED_FAM_NAMES)
    fam_total = sum(fam_flag_counts.values())
    prin_covered = sum(c for n, c in prin_flag_counts.items() if n in _COVERED_PRIN_NAMES)
    prin_total = sum(prin_flag_counts.values())

    print("=== data quality issues found in entries/*.json ===")
    for issue in data_quality_issues:
        print(f"  ! {issue}")
    if not data_quality_issues:
        print("  none")
    print()

    print(f"=== family flag coverage ===  ({fam_covered}/{fam_total} = {fam_covered/fam_total:.0%} of real occurrences)")
    for name, count in sorted(fam_flag_counts.items(), key=lambda x: -x[1]):
        mark = "covered" if name in _COVERED_FAM_NAMES else "-> falls to DEFAULT pattern"
        print(f"  {name:15s} {count}x  [{mark}]")
    print()

    print(f"=== principle flag coverage === ({prin_covered}/{prin_total} = {prin_covered/prin_total:.0%} of real occurrences)")
    for name, count in sorted(prin_flag_counts.items(), key=lambda x: -x[1]):
        mark = "covered" if name in _COVERED_PRIN_NAMES else "-> falls to DEFAULT pattern"
        print(f"  {name:15s} {count}x  [{mark}]")
    print()

    n_entries = len(glob.glob(str(ROOT / "entries" / "*.json")))
    print(f"CONCLUSION: n={n_entries} entries, {fam_total + prin_total} flag occurrences total. "
          f"Overall coverage {(fam_covered+prin_covered)/(fam_total+prin_total):.0%}. "
          f"Sample size is far too small to *learn* a mapping (that needs tens-to-hundreds "
          f"of consistently-labeled entries); it IS large enough to extend the hardcoded "
          f"table to full 20+12 coverage and move it into ontology data instead of code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
