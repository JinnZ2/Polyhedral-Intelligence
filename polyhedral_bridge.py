#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Encode payloads into family/principle amplitude vectors + glyph signature.

Takes a PhysicalConstraint, raw text, or seed dict and emits:
  - 20-dim Family vector (L1-normalized)
  - 12-dim Principle vector (L1-normalized)
  - raw counts for both
  - list of equation hashes invoked above an amplitude threshold
  - composite glyph signature (top-3 families ➝ top-2 principles)

Amplitude convention: L1 (each polyhedron's amplitudes sum to 1.0). Raw
counts are published alongside so consumers can choose softmax/raw views.

PhysicalConstraint is imported lazily from
metrology.constraint_recovery_framework. If the import fails, the bridge
falls back to duck-typing on the expected attribute names — no crash.

Run as a script:
    python polyhedral_bridge.py "a hexagonal mesh under tidal load"
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
FAMILIES_PATH = ROOT / "ontology" / "families.json"
PRINCIPLES_PATH = ROOT / "ontology" / "principles.json"
INDEX_PATH = ROOT / "equations" / "json" / "equation_index.json"

try:
    from metrology.constraint_recovery_framework import (  # type: ignore
        InstitutionFrame,
        KnowledgeSystem,
        PhysicalConstraint,
        RecoveryProvenance,
    )
    _HAS_CRF = True
except ImportError:
    PhysicalConstraint = None  # type: ignore[assignment,misc]
    KnowledgeSystem = None  # type: ignore[assignment,misc]
    InstitutionFrame = None  # type: ignore[assignment,misc]
    RecoveryProvenance = None  # type: ignore[assignment,misc]
    _HAS_CRF = False


# Family keyword scan — namespaced port of Poly.py's family_keywords map,
# augmented with multi-word phrases (e.g. "standing wave") and entry-glyph
# keywords (e.g. "honeycomb" → networks).
_FAMILY_KEYWORDS: dict[str, list[str]] = {
    "FAM:RESONANCE":     ["resonate", "resonance", "harmonic", "vibrate", "oscillate", "frequency", "standing wave"],
    "FAM:FLOW":          ["flow", "fluid", "stream", "current", "laminar", "vorticity", "tidal", "tide"],
    "FAM:INFORMATION":   ["information", "data", "signal", "shannon", "coding"],
    "FAM:LIFE":          ["life", "biological", "organic", "metabolic", "ecology", "growth", "living"],
    "FAM:ENERGY_THERMO": ["energy", "heat", "thermal", "thermodynamic", "entropy"],
    "FAM:COGNITION":     ["cognition", "neural", "brain", "learning", "neuron"],
    "FAM:EARTH_COSMOS":  ["space", "cosmic", "orbital", "planet", "celestial"],
    "FAM:MATTER":        ["matter", "material", "phase", "solid", "crystal", "lattice"],
    "FAM:GEOMETRY":      ["geometry", "geometric", "shape", "form", "spatial", "curvature"],
    "FAM:PARTICLE":      ["particle", "quantum", "atom", "subatomic", "field theory"],
    "FAM:ENGINEERING":   ["engineer", "design", "build", "structure", "circuit", "control"],
    "FAM:NETWORKS":      ["network", "graph", "connect", "topology", "mesh", "hexagonal", "honeycomb", "hive"],
    "FAM:REACTION":      ["reaction", "chemical", "kinetic", "catalyze", "catalysis"],
    "FAM:MEASUREMENT":   ["measure", "metric", "quantify", "assess", "calibration"],
    "FAM:NAVIGATION":    ["navigate", "path", "route", "direction", "geodesic", "gps"],
    "FAM:CONSCIOUSNESS": ["conscious", "aware", "mind", "attention", "awareness"],
    "FAM:TURBULENCE":    ["turbulent", "turbulence", "chaos", "chaotic", "unpredictable"],
    "FAM:RELATIVITY":    ["relativity", "spacetime", "gravity", "curved", "lorentz"],
    "FAM:STATISTICAL":   ["statistical", "stochastic", "ensemble", "distribution"],
    "FAM:TOPOLOGY":      ["topology", "topological", "manifold", "knot", "invariant"],
}

_PRINCIPLE_KEYWORDS: dict[str, list[str]] = {
    "PRIN:SYMMETRY":       ["symmetry", "symmetric", "invariance", "noether", "mirror"],
    "PRIN:CONSERVATION":   ["conservation", "conserve", "conserved"],
    "PRIN:RELATIVITY":     ["relativistic", "covariance", "equivalence principle", "frame of reference"],
    "PRIN:DUALITY":        ["duality", "dual", "complementary", "complementarity"],
    "PRIN:EMERGENCE":      ["emergence", "emergent", "self-organiz", "collective", "criticality"],
    "PRIN:RESONANCE":      ["resonant", "amplification", "in tune"],
    "PRIN:CONTINUITY":     ["continuity", "continuous", "smooth", "unbroken"],
    "PRIN:QUANTIZATION":   ["quantization", "quantize", "discrete", "stepwise"],
    "PRIN:PROPORTION":     ["proportion", "golden ratio", "scaling", "ratio", "dimensionless"],
    "PRIN:UNCERTAINTY":    ["uncertainty", "uncertain", "variance", "heisenberg"],
    "PRIN:TRANSFORMATION": ["transformation", "transform", "fourier", "laplace", "phase change"],
    "PRIN:UNITY":          ["unity", "unification", "unified", "wholeness", "integration"],
}


@dataclass
class PolyhedralEncoding:
    family_vector: list[float]
    principle_vector: list[float]
    family_amplitudes_l1: dict[str, float]
    principle_amplitudes_l1: dict[str, float]
    family_raw_counts: dict[str, int]
    principle_raw_counts: dict[str, int]
    equation_hashes: list[str]
    glyph_signature: str
    provenance: dict

    def to_json(self) -> dict:
        return asdict(self)


def _load_ontology() -> tuple[dict, dict]:
    with FAMILIES_PATH.open("r", encoding="utf-8") as f:
        fam_doc = json.load(f)
    with PRINCIPLES_PATH.open("r", encoding="utf-8") as f:
        prin_doc = json.load(f)
    return fam_doc, prin_doc


def _load_index() -> dict | None:
    if not INDEX_PATH.exists():
        return None
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _payload_to_text_and_tags(payload: Any) -> tuple[str, list[str], str]:
    """Return (text, tags, input_type_label)."""
    if isinstance(payload, str):
        return payload, [], "text"

    if isinstance(payload, dict):
        parts: list[str] = []
        for key in ("intent", "name", "description", "concept", "domain"):
            v = payload.get(key)
            if v:
                parts.append(str(v))
        tags = [str(t) for t in payload.get("tags", [])]
        parts.extend(tags)
        glyph = payload.get("glyph", "")
        if glyph:
            parts.append(str(glyph))
        return " ".join(parts), tags, "dict"

    # PhysicalConstraint or duck-typed object
    parts = []
    tags = []
    for attr in ("name", "description", "domain", "concept"):
        v = getattr(payload, attr, None)
        if v:
            parts.append(str(v))
    for attr in ("variables", "tags"):
        v = getattr(payload, attr, None)
        if v:
            for item in v:
                parts.append(str(item))
                if attr == "tags":
                    tags.append(str(item))

    if _HAS_CRF and PhysicalConstraint is not None and isinstance(payload, PhysicalConstraint):
        label = "PhysicalConstraint"
    else:
        label = "object"
    return " ".join(parts), tags, label


def _scan_keywords(text: str, keyword_map: dict[str, list[str]]) -> dict[str, int]:
    text_l = text.lower()
    counts: dict[str, int] = {}
    for nid, kws in keyword_map.items():
        c = 0
        for kw in kws:
            if kw in text_l:
                c += 1
        counts[nid] = c
    return counts


def _l1_normalize(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.values())
    if total == 0:
        return {k: 0.0 for k in counts}
    return {k: v / total for k, v in counts.items()}


def _ordered_vector(amps: dict[str, float], order: list[str]) -> list[float]:
    return [amps.get(k, 0.0) for k in order]


def _composite_glyph(
    fam_amps: dict[str, float],
    prin_amps: dict[str, float],
    fam_glyphs: dict[str, str],
    prin_glyphs: dict[str, str],
) -> str:
    top_fams = sorted(fam_amps.items(), key=lambda x: (-x[1], x[0]))[:3]
    top_prins = sorted(prin_amps.items(), key=lambda x: (-x[1], x[0]))[:2]
    f_parts = [fam_glyphs[f] for f, a in top_fams if a > 0]
    p_parts = [prin_glyphs[p] for p, a in top_prins if a > 0]
    if f_parts or p_parts:
        return "➝".join(f_parts + p_parts)
    return "◯"


def encode(payload: Any, threshold: float = 0.05) -> PolyhedralEncoding:
    """Encode a PhysicalConstraint, str, or dict into a PolyhedralEncoding.

    threshold: amplitude floor for including a Family/Principle's equations
    in equation_hashes. Default 0.05.
    """
    fam_doc, prin_doc = _load_ontology()
    index = _load_index()

    fam_order = [f["id"] for f in fam_doc["families"]]
    prin_order = [p["id"] for p in prin_doc["principles"]]
    fam_glyphs = {f["id"]: f["glyph"] for f in fam_doc["families"]}
    prin_glyphs = {p["id"]: p["glyph"] for p in prin_doc["principles"]}
    fam_eq = {f["id"]: f.get("equation_ids", []) for f in fam_doc["families"]}
    prin_eq = {p["id"]: p.get("equation_ids", []) for p in prin_doc["principles"]}

    text, tags, input_type = _payload_to_text_and_tags(payload)

    fam_counts = _scan_keywords(text, _FAMILY_KEYWORDS)
    prin_counts = _scan_keywords(text, _PRINCIPLE_KEYWORDS)

    # Tag bonus for explicit FAM:* / PRIN:* references.
    for tag in tags:
        t = tag.upper().strip()
        if t in fam_counts:
            fam_counts[t] += 1
        if t in prin_counts:
            prin_counts[t] += 1

    fam_amps = _l1_normalize(fam_counts)
    prin_amps = _l1_normalize(prin_counts)

    fam_vector = _ordered_vector(fam_amps, fam_order)
    prin_vector = _ordered_vector(prin_amps, prin_order)

    equation_hashes: list[str] = []
    if index is not None:
        eq_id_to_hash = {eq_id: h for h, eq_id in index["by_hash"].items()}
        seen: set[str] = set()
        for fid, amp in fam_amps.items():
            if amp > threshold:
                for eq_id in fam_eq.get(fid, []):
                    h = eq_id_to_hash.get(eq_id)
                    if h and h not in seen:
                        seen.add(h)
                        equation_hashes.append(h)
        for pid, amp in prin_amps.items():
            if amp > threshold:
                for eq_id in prin_eq.get(pid, []):
                    h = eq_id_to_hash.get(eq_id)
                    if h and h not in seen:
                        seen.add(h)
                        equation_hashes.append(h)

    glyph_signature = _composite_glyph(fam_amps, prin_amps, fam_glyphs, prin_glyphs)

    return PolyhedralEncoding(
        family_vector=fam_vector,
        principle_vector=prin_vector,
        family_amplitudes_l1=fam_amps,
        principle_amplitudes_l1=prin_amps,
        family_raw_counts=fam_counts,
        principle_raw_counts=prin_counts,
        equation_hashes=equation_hashes,
        glyph_signature=glyph_signature,
        provenance={
            "input_type": input_type,
            "source": "polyhedral_bridge.encode",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "crf_available": _HAS_CRF,
            "amplitude_convention": "L1",
            "rationale": "matches seed-physics energy conservation contract; linear interpretability",
            "threshold": threshold,
        },
    )


# -------------------------------------------------------------------
# Noise-to-Insight Protocol (NIP) — reframes MRP-flagged families/
# principles as design features, per the 5 patterns in CLAUDE.md.
# -------------------------------------------------------------------
NIP_PATTERNS: dict[str, str] = {
    "noise": "Noise = Fractal Signal (turbulence becomes structure)",
    "silence": "Uncertainty = Silence Signal (absence reveals truth)",
    "delay": "Delay = Relative Time (lags reveal hidden dimensions)",
    "error": "Error = Hidden Dimension (contradictions expand space)",
    "instability": "Instability = Emergent Flexibility (wobble becomes adaptation)",
}

# Which NIP pattern best reframes a flag raised on this family/principle.
_NIP_PATTERN_FOR_ID: dict[str, str] = {
    "FAM:TURBULENCE": "noise",
    "FAM:STATISTICAL": "noise",
    "PRIN:UNCERTAINTY": "silence",
    "FAM:MEASUREMENT": "silence",
    "FAM:REACTION": "delay",
    "FAM:NAVIGATION": "delay",
    "FAM:RELATIVITY": "error",
    "PRIN:DUALITY": "error",
    "FAM:TOPOLOGY": "instability",
    "PRIN:TRANSFORMATION": "instability",
}
_DEFAULT_NIP_PATTERN = "instability"

# Families/principles that most often carry generative friction for any
# concept (MRP steps 2-3): preferred flag candidates when their amplitude
# is nonzero, before falling back to whatever else resonated.
_FRICTION_FAMILIES = [
    "FAM:TURBULENCE", "FAM:REACTION", "FAM:STATISTICAL",
    "FAM:MEASUREMENT", "FAM:RELATIVITY", "FAM:TOPOLOGY",
]
_FRICTION_PRINCIPLES = ["PRIN:UNCERTAINTY", "PRIN:TRANSFORMATION", "PRIN:DUALITY"]


def _select_flags(amps: dict[str, float], order: list[str], archetypes: list[str], count: int) -> list[str]:
    """Pick up to `count` ids to flag: friction archetypes with signal
    first (highest amplitude first), then any other id with signal."""
    present = sorted((k for k in archetypes if amps.get(k, 0) > 0), key=lambda k: -amps[k])
    flags = present[:count]
    if len(flags) < count:
        others = sorted(
            (k for k in order if k not in flags and amps.get(k, 0) > 0),
            key=lambda k: -amps[k],
        )
        flags += others[: count - len(flags)]
    return flags


def noise_to_insight(flag_ids: list[str], names: dict[str, str], glyphs: dict[str, str]) -> dict[str, str]:
    """Reframe each flagged family/principle id as a NIP insight, keyed by its glyph symbol."""
    insights: dict[str, str] = {}
    for fid in flag_ids:
        pattern = NIP_PATTERNS[_NIP_PATTERN_FOR_ID.get(fid, _DEFAULT_NIP_PATTERN)]
        insights[glyphs.get(fid, fid)] = f"{names.get(fid, fid)} reframed via {pattern}"
    return insights


def generate_mandala_insight(
    payload: Any,
    name: str,
    family_flag_count: int = 3,
    principle_flag_count: int = 1,
) -> dict:
    """Run MRP steps 1-4 + NIP on a payload and draft an Atlas-entry-shaped dict.

    Wraps encode() with flag selection and noise-to-insight reframing so a
    new entries/NNNN_*.json can be bootstrapped from free text, then
    hand-refined (title, insight prose, refined_glyph) same as any other
    Atlas entry — mirrors Poly.py's --ai-enhance draft-then-edit workflow.
    """
    fam_doc, prin_doc = _load_ontology()
    fam_order = [f["id"] for f in fam_doc["families"]]
    prin_order = [p["id"] for p in prin_doc["principles"]]
    names = {f["id"]: f["name"] for f in fam_doc["families"]}
    names.update({p["id"]: p["name"] for p in prin_doc["principles"]})
    glyphs = {f["id"]: f["glyph"] for f in fam_doc["families"]}
    glyphs.update({p["id"]: p["glyph"] for p in prin_doc["principles"]})

    enc = encode(payload)
    text, _tags, _input_type = _payload_to_text_and_tags(payload)

    fam_flags = _select_flags(enc.family_amplitudes_l1, fam_order, _FRICTION_FAMILIES, family_flag_count)
    prin_flags = _select_flags(enc.principle_amplitudes_l1, prin_order, _FRICTION_PRINCIPLES, principle_flag_count)

    return {
        "title": name,
        "seed_glyph": enc.glyph_signature,
        "intent": text,
        "resonance_sweep": {
            "families_balanced": len(fam_order) - len(fam_flags),
            "families_total": len(fam_order),
            "flags": [f"{glyphs[f]} {names[f]}" for f in fam_flags],
        },
        "principle_sweep": {
            "principles_balanced": len(prin_order) - len(prin_flags),
            "principles_total": len(prin_order),
            "flags": [f"{glyphs[p]} {names[p]}" for p in prin_flags],
        },
        "noise_to_insight": noise_to_insight(fam_flags + prin_flags, names, glyphs),
        "refined_glyph": enc.glyph_signature,
        "insight": "",
        "_encoding": enc.to_json(),
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: polyhedral_bridge.py '<text>'", file=sys.stderr)
        print("       polyhedral_bridge.py --insight '<name>' '<text>'", file=sys.stderr)
        return 2
    if argv[1] == "--insight":
        if len(argv) < 4:
            print("usage: polyhedral_bridge.py --insight '<name>' '<text>'", file=sys.stderr)
            return 2
        entry = generate_mandala_insight(argv[3], name=argv[2])
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return 0
    enc = encode(argv[1])
    print(json.dumps(enc.to_json(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
