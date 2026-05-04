# Polyhedral-Intelligence — ID Proposal (Block 0)

**Status:** CONFIRMED by Kavik (JinnZ2) on 2026-05-04.
**Generated:** 2026-05-04
**Branch:** `claude/physics-ontology-framework-n1x4H`

This file lists the namespaced IDs extracted from `equations/F*.md` and `equations/P*.md` and consolidated into `ontology/families.json` (20) and `ontology/principles.json` (12).

These IDs are the canonical form used in equation bindings (`equation.families[]`, `equation.principles[]`) for Block A and downstream consumers. Once confirmed, the index builder enforces them — bindings to unknown IDs are hard-rejected at index build time.

---

## Families (icosahedron) — `FAM:*`

| Proposed ID         | Legacy ID | Name           | Glyph (canonical) | Meta-field |
|---------------------|-----------|----------------|-------------------|------------|
| `FAM:RESONANCE`     | F01       | Resonance      | `≡≡≡`             | Chemical   |
| `FAM:FLOW`          | F02       | Flow           | `↻`               | Chemical   |
| `FAM:INFORMATION`   | F03       | Information    | `⊗`               | Chemical   |
| `FAM:LIFE`          | F04       | Life           | `••••`            | Chemical   |
| `FAM:ENERGY_THERMO` | F05       | Energy-Thermo  | `△≈`              | Emotional  |
| `FAM:COGNITION`     | F06       | Cognition      | `⋯⋯`              | Emotional  |
| `FAM:EARTH_COSMOS`  | F07       | Earth-Cosmos   | `◯`               | Emotional  |
| `FAM:MATTER`        | F08       | Matter         | `◆`               | Emotional  |
| `FAM:GEOMETRY`      | F09       | Geometry       | `☆`               | Cognitive  |
| `FAM:PARTICLE`      | F10       | Particle       | `⚪`              | Cognitive  |
| `FAM:ENGINEERING`   | F11       | Engineering    | `⚙`               | Cognitive  |
| `FAM:NETWORKS`      | F12       | Networks       | `⬡`               | Dream      |
| `FAM:REACTION`      | F13       | Reaction       | `⇑`               | Dream      |
| `FAM:MEASUREMENT`   | F14       | Measurement    | `↕`               | Dream      |
| `FAM:NAVIGATION`    | F15       | Navigation     | `◆→`              | Dream      |
| `FAM:CONSCIOUSNESS` | F16       | Consciousness  | `◎`               | Dream      |
| `FAM:TURBULENCE`    | F17       | Turbulence     | `ᘯᘰ`              | Dream      |
| `FAM:RELATIVITY`    | F18       | Relativity     | `⊗≡`              | Symbolic   |
| `FAM:STATISTICAL`   | F19       | Statistical    | `▁▃▅∿`            | Symbolic   |
| `FAM:TOPOLOGY`      | F20       | Topology       | `∞`               | Symbolic   |

## Principles (dodecahedron) — `PRIN:*`

| Proposed ID            | Legacy ID | Name           | Glyph (canonical) | Axis           |
|------------------------|-----------|----------------|-------------------|----------------|
| `PRIN:SYMMETRY`        | P01       | Symmetry       | `⧖`               | Invariance     |
| `PRIN:CONSERVATION`    | P02       | Conservation   | `↺`               | Invariance     |
| `PRIN:RELATIVITY`      | P03       | Relativity     | `⊗`               | Invariance     |
| `PRIN:DUALITY`         | P04       | Duality        | `◑`               | Transformation |
| `PRIN:EMERGENCE`       | P05       | Emergence      | `●●`              | Transformation |
| `PRIN:RESONANCE`       | P06       | Resonance      | `∿`               | Transformation |
| `PRIN:CONTINUITY`      | P07       | Continuity     | `⎯`               | Connectivity   |
| `PRIN:QUANTIZATION`    | P08       | Quantization   | `▭`               | Connectivity   |
| `PRIN:PROPORTION`      | P09       | Proportion     | `▯`               | Connectivity   |
| `PRIN:UNCERTAINTY`     | P10       | Uncertainty    | `◧`               | Evolution      |
| `PRIN:TRANSFORMATION`  | P11       | Transformation | `↻`               | Evolution      |
| `PRIN:UNITY`           | P12       | Unity          | `◎`               | Evolution      |

---

## Decisions baked into this proposal

1. **Namespace prefixes**: `FAM:` and `PRIN:` distinguish families from principles, since some names overlap (`Resonance`, `Relativity`, `Transformation`).
2. **ID body**: `<UPPERCASE_NAME>` with `-` and spaces replaced by `_`. Only one such transform was needed: `Energy-Thermo` → `ENERGY_THERMO`, `Earth-Cosmos` → `EARTH_COSMOS`.
3. **Symbols**: canonical schema symbols from `atlas_schema.json` / `protocols.json` — *not* the emoji-prefixed variants used as section glyphs in the `equations/F*.md` source files (e.g. F01's section header is `🎵 Resonance`, but the canonical glyph is `≡≡≡`). Per CLAUDE.md, the schema symbols are authoritative.
4. **Glyph collisions**: `↻` is used for both `FAM:FLOW` and `PRIN:TRANSFORMATION`; `◎` for `FAM:CONSCIOUSNESS` and `PRIN:UNITY`; `⊗` for `FAM:INFORMATION` and `PRIN:RELATIVITY`. The namespace prefix is what disambiguates — glyphs alone are not unique across the polyhedra, by design.
5. **Meta-field assignments** for families taken verbatim from `five_field_schema_map.json`.
6. **Axis assignments** for principles taken from the BioGrid2.0 Principles Lattice mapping documented in `CLAUDE.md` (Invariance: P01–P03, Transformation: P04–P06, Connectivity: P07–P09, Evolution: P10–P12).

## Questions for Kavik — RESOLVED

- [x] Confirm ID namespace prefixes `FAM:` / `PRIN:`.
- [x] Confirm `ENERGY_THERMO` and `EARTH_COSMOS` snake-case forms.
- [x] Confirm meta-field axis names (`Chemical | Emotional | Cognitive | Dream | Symbolic`) and principle axis names (`Invariance | Transformation | Connectivity | Evolution`).
- [x] Confirm namespace separation is sufficient for the `Resonance` / `Relativity` / `Transformation` name collisions.

## Validation rule (effective on confirmation)

Once these IDs are confirmed (or amended) and committed, the equation index builder (`Block A.4`) will call `ontology/validate_ids.py::valid_family_ids()` and `valid_principle_ids()`. Any equation JSON with an unknown `FAM:*` or `PRIN:*` binding hard-errors the build.

## Next step

Block A (equation extraction) is unblocked as of 2026-05-04.
