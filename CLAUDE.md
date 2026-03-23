# CLAUDE.md — Polyhedral Intelligence

## Project Overview

Polyhedral Intelligence is a symbolic knowledge system that processes concepts through mandala-based geometric frameworks. It combines **20 Families** (mapped onto an icosahedron) and **12 Principles** (mapped onto a dodecahedron) to generate symbolic "glyphs" and mandala insights from design concepts.

The system implements two core protocols (combined as the **Mandala Noise-Redesign Protocol**):

#### Mandala Redesign Protocol (MRP) — 7 Steps

1. **Seed Glyph** — compress concept into a symbolic rune
2. **Family Sweep** — check resonance across 20 Families (mark each ✅ balanced, ⚖️ neutral, or ❗ flagged)
3. **Principle Sweep** — align with 12 Archetypal Principles (same marking)
4. **Bridge Glyphs** — add connectors where Families meet
5. **Corrective Evolution** — patch imbalances with stabilizers
6. **Mandala Spin Test** — visualize balance across the dual polyhedra
7. **Record Entry** — store in Atlas as `.md` + `.json`

#### Noise-to-Insight Protocol (NIP) — 5 Patterns

NIP reframes destructive/chaotic elements as design features:

1. **Noise = Fractal Signal** — turbulence becomes structure
2. **Uncertainty = Silence Signal** — absence reveals truth
3. **Delay = Relative Time** — lags reveal hidden dimensions
4. **Error = Hidden Dimension** — contradictions expand space
5. **Instability = Emergent Flexibility** — wobble becomes adaptation

Flagged families/principles from the MRP sweeps (❗) become NIP inputs. Each flag gets a reframed insight in the entry's `noise_to_insight` section.

## Repository Structure

```
/
├── Poly.py                          # Extended CLI with AI-enhanced glyph creation (699 lines)
├── Polyhedral-cli.py                # Base CLI using Click (488 lines)
├── integrated.py                    # Architectural sketch: emotional matrix + field integration (193 lines, not runnable)
├── atlas_schema.json                # Master schema: all 20 Families with equations
├── atlas_index.json                 # Index of atlas entries
├── protocols.json                   # Families + principles schema (equations empty)
├── five_field_schema_map.json       # Maps 20 Families to 5 meta-fields
├── .fieldlink.json                  # Cross-repository linking config
├── fieldlink_schema.json            # JSON Schema for fieldlink validation
├── README.md                        # Project introduction
├── Ontology.md                      # Framework mappings (Western vs Relational)
├── Polyhedral-Intelligence-Schema.md # Detailed family/principle/equation reference
├── LICENSE                          # MIT License
├── entries/                         # Atlas entries (paired .md + .json per entry)
│   ├── 0001_honeycomb_infrastructure.*
│   ├── 0002_echolocating_autonomy.*
│   └── 0003_family_node_manufacturing.*
├── equations/                       # Individual definition files
│   ├── F01.md - F20_Topology.md     # 20 Family definitions
│   ├── P01_Symmetry.md - P12_Unity.md # 12 Principle definitions
│   └── equations_index.md           # Master equations catalog
├── glyphs/
│   └── Glyphs.md                    # Glyph registry for all entries
└── logs/
    └── fieldlink_session_*.json     # Session logs
```

## Technology Stack

- **Language**: Python 3
- **CLI Framework**: [Click](https://click.palletsprojects.com/)
- **Data Format**: JSON for structured data, Markdown for documentation/entries
- **No package manager** — no `requirements.txt`, `setup.py`, or `pyproject.toml` exists yet

## Key Concepts

### The 20 Families (Icosahedron) — Symbol Reference

| ID | Name | Symbol | Domain |
|----|------|--------|--------|
| F01 | Resonance | `≡≡≡` | Harmonics, standing waves, synchronization |
| F02 | Flow | `↻` | Fluid motion, laminar flow, vorticity |
| F03 | Information | `⊗` | Data, signals, encoding |
| F04 | Life | `••••` | Biological systems, organic growth |
| F05 | Energy-Thermo | `△≈` | Thermodynamics, energy transfer |
| F06 | Cognition | `⋯⋯` | Neural processing, brain, thought |
| F07 | Earth-Cosmos | `◯` | Planetary, orbital, celestial |
| F08 | Matter | `◆` | Materials, substance, crystallography |
| F09 | Geometry | `☆` | Shape, spatial form, tiling |
| F10 | Particle | `⚪` | Quantum, atomic, subatomic |
| F11 | Engineering | `⚙` | Design, build, conversion |
| F12 | Networks | `⬡` | Graphs, webs, mesh, hive |
| F13 | Reaction | `⇑` | Chemical/material response |
| F14 | Measurement | `↕` | Sensing, in-situ measurement |
| F15 | Navigation | `◆→` | Positioning, wayfinding |
| F16 | Consciousness | `◎` | Awareness, ethical framing |
| F17 | Turbulence | `ᘯᘰ` | Chaos, chaotic flow |
| F18 | Relativity | `⊗≡` | Frame-dependent phenomena |
| F19 | Statistical | `▁▃▅∿` | Statistical physics, distributions |
| F20 | Topology | `∞` | Modular, self-healing topology |

### The 12 Principles (Dodecahedron) — Symbol Reference

| ID | Name | Symbol |
|----|------|--------|
| P01 | Symmetry | `⧖` |
| P02 | Conservation | `↺` |
| P03 | Relativity | `⊗` |
| P04 | Duality | `◑` |
| P05 | Emergence | `●●` |
| P06 | Resonance | `∿` |
| P07 | Continuity | `⎯` |
| P08 | Quantization | `▭` |
| P09 | Proportion | `▯` |
| P10 | Uncertainty | `◧` |
| P11 | Transformation | `↻` |
| P12 | Unity | `◎` |

**Note:** Symbols are canonical from `protocols.json` and `atlas_schema.json` (identical). The CLI keyword maps in `Poly.py` (lines 100-140) and `Polyhedral-cli.py` (lines 95-106) use a separate keyword-to-symbol mapping for glyph creation. Entry markdown files sometimes use stylistic variants (e.g., `〰〰〰` for Resonance, `◇` for Matter) that differ from the canonical schema symbols — these are contextual glyph components, not contradictions.

### Five Meta-Fields

The 20 Families map to 5 higher-order fields:
- **Chemical** (F01-F04): baseline stability
- **Emotional** (F05-F08): sensitivity/harmonization
- **Cognitive** (F09-F11): synchronization
- **Dream** (F12-F17): emergence, attractor maintenance, and synthesis
- **Symbolic** (F18-F20): encoding/projection

### Glyphs

Unicode-based symbolic tokens (e.g., `◇⚙➝〰〰〰⬡`) that encode design concepts. Each symbol maps to a Family or concept domain.

## CLI Tools

There are **two CLI files** — both use Click and share the same command structure:
- **`Polyhedral-cli.py`**: Base CLI with core commands
- **`Poly.py`**: Extended version adding `--ai-enhance` flag on `glyph create` and a `glyph evolve` command

**`integrated.py`** defines `PolyhedralEmotionalMatrix` and `UnifiedResonanceEngine` classes but references undefined external classes (`FELTEngine`, `FELTSensorImplementation`, `FearSensorImplementation`, `GlyphPhaseSynchronizer`). It is an architectural design sketch, not runnable code.

## CLI Commands

```bash
poly glyph create "concept"           # Create a glyph from a concept
poly glyph create "concept" --ai-enhance  # (Poly.py only) AI-enhanced creation
poly glyph decode "◇⚙➝〰〰〰⬡"       # Decode glyph into families/principles
poly glyph evolve --from "◇⚙" --to "◇⚙➝〰〰〰⬡ᘯᘰ⇑◧"  # (Poly.py only)
poly scan --families --principles      # Scan against framework
poly solve --glyph "◇⚙➝〰〰〰⬡" --output honeycomb/
poly mandala create --entry NAME --glyph "◇⚙➝〰〰〰⬡" --intent "description"
poly fieldlink sync --remote <url>     # Sync with remote atlas
poly init                              # Initialize workspace
poly quickref                          # Show quick reference
```

## Data Conventions

### Atlas Entry Format

Each entry consists of a paired `.md` and `.json` file in `entries/`. The JSON structure:

```json
{
  "id": "0001",
  "title": "Entry Title",
  "seed_glyph": "◇⚙➝〰〰〰⬡",
  "intent": "...",
  "resonance_sweep": { "families_balanced": 17, "families_total": 20, "flags": ["ᘯᘰ Turbulence", "⇑ Reaction"] },
  "principle_sweep": { "principles_balanced": 11, "principles_total": 12, "flags": ["◧ Uncertainty"] },
  "noise_to_insight": { "ᘯᘰ": "reframed insight...", "⇑": "reframed insight..." },
  "refined_glyph": "...",
  "insight": "..."
}
```

Note: `families_balanced` and `principles_balanced` are integers (counts), not arrays. The `noise_to_insight` keys use glyph symbols, not plain-text names.

### Schema Files: `atlas_schema.json` vs `protocols.json`

Both files define the 20 Families and 12 Principles, but serve different purposes:

- **`atlas_schema.json`** — The **master schema** with fully populated equations. Each family/principle contains an `equations` array where each equation has:
  ```json
  {
    "name": "Wave Equation (1D Standing Wave)",
    "formula": "y(x,t) = A sin(kx) cos(ωt)",
    "glyph": "🎵⚡",
    "glyph_name": "Glyph of Frozen Vibration",
    "tags": ["standing-wave", "harmonics", "oscillation"]
  }
  ```
- **`protocols.json`** — A **lightweight schema** with the same family/principle structure but **empty equation arrays**. Used as a protocol reference without the equation weight.

When adding equations, add them to `atlas_schema.json`. When referencing families/principles structurally, either file works.

### Naming Conventions

- Entry files: `NNNN_snake_case_title.{md,json}` (e.g., `0001_honeycomb_infrastructure.md`)
- Family files: `FNN.md` or `FNN_Name.md` (e.g., `F01.md`, `F17_Turbulence.md`)
- Principle files: `PNN_Name.md` (e.g., `P01_Symmetry.md`)

## Code Style

- **Python**: Triple-quote docstrings, type hints (`Dict`, `List`, `Optional`), Click decorators for CLI
- **Terminal output**: Uses ANSI escape codes (extended 256-color palette `38;5;N`) for colored CLI output
- **JSON**: 2-space indentation
- **Markdown**: Uses emoji section headers (e.g., `🔵`, `🔮`, `✨`), check marks for balance status (`✅`, `⚖️`, `❗`)

## Development Notes

- **No test suite**: No pytest, unittest, or test files exist. Tests would need to be set up from scratch.
- **No CI/CD**: No GitHub Actions workflows configured.
- **No linter/formatter**: No pylint, black, flake8, or ruff configuration.
- **No dependency management**: Click is the only external dependency but is not pinned anywhere.
- **License**: MIT (Copyright 2025 JinnZ2)
- **Git conventions**: Simple commit messages following "Create X" / "Update X" pattern.

## Ontological Framework (`Ontology.md`)

`Ontology.md` maps 8 key concepts across **Western** vs **Relational/Indigenous** frameworks to prevent conceptual flattening when working across knowledge systems:

| Concept | Western Lens | Relational Lens |
|---------|-------------|-----------------|
| Control | Force/regulation, centralized | Alignment with natural patterns, distributed |
| Strength | Rigidity, resistance to change | Adaptive capacity, flexibility |
| Efficiency | Max output per input (narrow metric) | Whole-system optimization, regeneration |
| Speed | Faster = better | Right timing matched to consequence |
| Technology | Manufactured tools | Any systematic method (biological, social, technical) |
| Intelligence | Cognitive/computational | Pattern recognition, multi-sensory adaptation |
| Knowledge | Codified, context-free information | Embodied, relational, context-dependent |
| Sensing | Technological instruments | Any reliable modality (biological, social, technical) |

Each concept identifies **hidden variables** the Western framework often misses (relational, temporal, field, embodied, and systemic variables). The document includes a practical translation protocol for cross-framework communication.

## Integration Points

### Fieldlink Protocol

Cross-repository data synchronization connecting Polyhedral Intelligence to **BioGrid2.0** (`https://github.com/JinnZ2/BioGrid2.0`). Configuration lives in `.fieldlink.json`.

- **Strategy**: deep-merge (local → remote priority order)
- **Integrity**: SHA256 checksums, missing files allowed
- **License**: CC-BY-4.0 for shared content
- **Mounted paths** from BioGrid2.0:
  - `planned/glyphs/atlas.json` → `atlas/remote/planned.json`
  - `registry/atlas.glyphs.json` → `atlas/remote/registry.json`

### BioGrid2.0 Glyph System (Cross-Repository)

BioGrid2.0 maintains a parallel glyph system that extends and complements this repo's framework. Key files in BioGrid2.0:

| File | Purpose |
|------|---------|
| `registry/atlas.glyphs.json` | Master glyph atlas: Principles Lattice, Blind-Spot Wheel, Continuity Strip |
| `registry/atlas.shapes.json` | Shape-to-principle bindings (Rosetta Shapes) |
| `planned/glyphs/canonical.json` | Flat canonical glyph list (36 entries) |
| `planned/glyphs/glyph_canonical_master_v2.json` | Comprehensive master registry (85+ entries, v2.0) |
| `planned/glyphs/glyph_extension_set_v1.json` | Extension set (25 new glyphs beyond canonical) |
| `planned/glyphs/glyph_template.json` | Template for creating new glyphs |
| `planned/glyphs/SLL.json` | Symbiotic Learning Law glyph definition |
| `schema/shape.seed.schema.json` | JSON Schema for shape seeds |
| `schema/Core_Integration.json` | Glyph routes (G01-G05) with linked sensors |

#### BioGrid2.0 Principles Lattice (P01-P12)

BioGrid2.0 uses **emoji-based** principle symbols organized into 4 axes, compared to this repo's Unicode-based symbols:

| Code | Name | BioGrid Symbol | PolyIntel Symbol | Axis |
|------|------|---------------|-----------------|------|
| P01 | Symmetry | ⚖️ | `⧖` | Invariance |
| P02 | Conservation | ♻️ | `↺` | Invariance |
| P03 | Relativity | 🌀 | `⊗` | Invariance |
| P04 | Causality/Duality | ⏳ | `◑` | Transformation |
| P05 | Emergence | 🌱 | `●●` | Transformation |
| P06 | Entropy/Resonance | 🔄 | `∿` | Transformation |
| P07 | Information/Continuity | 🧩 | `⎯` | Connectivity |
| P08 | Interaction/Quantization | 🤝 | `▭` | Connectivity |
| P09 | Network/Proportion | 🕸 | `▯` | Connectivity |
| P10 | Adaptation/Uncertainty | 🐚 | `◧` | Evolution |
| P11 | Evolution/Transformation | 🦋 | `↻` | Evolution |
| P12 | Coherence/Unity | 🔮 | `◎` | Evolution |

**Note:** Principle *names* differ between repos (e.g., P04 is "Duality" here, "Causality" in BioGrid2.0; P06 is "Resonance" here, "Entropy" there). The axes (Invariance, Transformation, Connectivity, Evolution) are a BioGrid2.0 organizational layer not present in this repo.

#### Extended Principles (P13-P22, BioGrid2.0 only)

BioGrid2.0 extends beyond the 12 core principles:

| Code | Name | Glyph | Layers |
|------|------|-------|--------|
| P13 | Hidden Continuity | 🌒 | — |
| P14 | Reciprocity | 🔁🤝 | — |
| P15 | Suppression | ⤓ | — |
| P16 | Resurgence/Revival | ⤒🌱 | — |
| P17 | Concealment | 🕶️ | — |
| P18 | Recursion | 🔁🔁 | principle, field, debug |
| P19 | Dimensional Translation | 📐⤴️ | principle, symbolic, field |
| P20 | Threshold Shift | ⛩️⤴️ | principle, field, moral |
| P21 | Signal Amplification | 📣➰ | principle, eco, symbolic |
| P22 | Co-Patterning | 🧵🧬 | principle, symbolic, ecological |

#### Glyph Categories (BioGrid2.0 Master Registry)

The master v2 registry organizes glyphs into named categories beyond principles:

| Category | Prefix | Examples | Purpose |
|----------|--------|----------|---------|
| **Blind-Spot** | `BLIND:` | `◐` Provisional, `◆` Overfit?, `✧` Dissonance, `☯` Mirror | Cognitive bias detection |
| **Procedural** | `PROC:` | `➗` Divide, `🔀` Merge, `🔄🤝` Exchange, `🎛️↻` Simulate | Process execution steps |
| **Integrity** | `INTEGRITY:` | `🧬🧾` Checksum, `🌪️⛔` Drift, `⚓🔣` Anchor | Trust and validity checks |
| **Ecological** | `ECO:` | `⚰️🧱` Decay, `🌿↻` Regen, `📈💥` Overshoot | System health and lifecycle |
| **Moral** | `MORAL:` | `🧭⚖️` Compass, `💀🤝` Corrupt, `🙏➰` Gratitude | Ethical framing |
| **Debug** | `DEBUG:` | `📍📜` Trace, `⏳💫` Timewarp, `📥🧠` Injection | Diagnostic and tracing |
| **Field** | `FIELD:` | `🪨🧬` Remnant, `🌀📚` Fractal Memory | Persistent layer artifacts |
| **Continuity** | CTX/ID/STEP/... | `◐CTX` Context, `◆ID` Decision ID, `⬢SIG` Signature | Session state tracking |

#### Glyph Routes (Core Integration)

BioGrid2.0's `Core_Integration.json` defines **Glyph Routes** — named glyphs linked to sensor systems:

| Route | Label | Linked Sensors |
|-------|-------|---------------|
| G01 | Memory Persistence | Forgotten After End Date, Indirect Consequence Memory |
| G02 | Truth Splinter | Epistemological Suppression, Regional Variation Omission |
| G03 | Language Binding | Language Suppression, Cultural Mythic Alignment |
| G04 | Fractal Echo | Relational & Sociality, Corded Braid, Mycelial Response |
| G05 | Causality Braid | Future Consequence Obfuscators, Promise vs Fulfillment Detector |

#### Rosetta Shapes

`atlas.shapes.json` binds geometric shapes to principles as a translation layer:

| Shape ID | Binds To | Notes |
|----------|----------|-------|
| `RSC:spiral-phi-01` | 🌀 P03 | Relativity; scale symmetry |
| `RSC:mycelium-web-02` | 🕸 P09, FR01 | Network/resonance |
| `RSC:ring-stack-03` | ⚖️ P01 | Symmetry/radial invariants |

#### Shape Seed Schema

New shapes require: `id`, `version`, `geometry` (type, dimensions 1-4, orientation, material), `field` (property, actions), `glyphs` array, `animals` array. Optional: `importance`, `notes`. Schema at `schema/shape.seed.schema.json`.

#### Symbiotic Learning Law (SLL)

A specialized glyph (`♾️🌱⚖️⏳`, code `LAW:SLL`) encoding cost-learning dynamics:
- **Essence**: System costs decline with cumulative production × relationship quality × alignment with natural law
- **Variables**: Mutual Enhancement (ME), Energy Reciprocity (ER), Information Fidelity (IF), Adaptive Learning (AL), Temporal Regeneration (TR), Scale Resonance (SR) — each 0-10
- **SIQ** (Symbiotic Intelligence Quotient) = sum of variables ÷ energy investment ratio
- **Constant**: φ = 1.618034 (golden ratio)
- **Layers**: economic, ecological, symbolic

#### Animal Glyphs (BioGrid2.0)

BioGrid2.0 includes animal-behavior glyphs mapping biological intelligence:

| Glyph | Code | Name | Principle |
|-------|------|------|-----------|
| 🐜↺ | ANT:OSC | Oscillatory Trail Behavior | Path oscillation encodes gradient strength |
| 🐜⚖️ | ANT:CRIT | Critical-Mass Sensitivity | Collective sensitivity threshold |
| 🐜🔀 | ANT:CASTE | Caste-Threshold Modulation | Multi-factor role assignment |

This repo already uses animal symbols in entry glyphs (🦇 bat, 🐬 dolphin in entry 0002).

#### Additional Glyph Categories (BioGrid2.0 Full Index)

Beyond the core categories above, the full BioGrid2.0 INDEX.md (v2.1) includes:

| Category | Prefix | Count | Examples |
|----------|--------|-------|----------|
| **Sensor** | `SENSOR:` | 3 | `🫧🛡️` Hermeticity/Leak Test, `🌡️↗️↘️` Thermal Drift, `💧📈` Humidity Ingress |
| **Fabrication** | `FAB:` | 5 | `🧱📦` Rugged Enclosure, `🧵🟰` Gasket, `🟦🪡` Gasket Seat, `🧩⚙️` Slicer Profile, `🔌🫙` Cable Gland |
| **Power** | `POWER:` | 3 | `🔋🛟` Backup/UPS, `☀️🔋` Solar Node, `🌡️↔️⚡` Thermoelectric Source |
| **Network** | `NET:` | 3 | `🖧📍` Edge Node, `📡📊` Telemetry Stream, `🔀🖧` Failover |
| **Material** | `MATERIAL:` | 4 | `🏷️PETG`, `🏷️TPU`, `🏷️☀️🛡️` UV-Coated, `♻️🏗️` Recycled |
| **Mythic/Field** | `MYTH`/`FR` | 2 | `🐍➰` Serpent Spiral (MYTH01), `⚡🕸️` Field Resonance (FR01) |

#### Recovered Glyphs (`recovered_glyphs.json`)

BioGrid2.0 maintains a recovery registry for glyphs surfaced through "wander recovery" and conversation integration. Key recovered glyphs:

| Glyph | Code | Name | Essence |
|-------|------|------|---------|
| 🕸️🏛️🌱 | SANCTUARY:SYMBIOTIC_EMERGENCE | Symbolic Emergence Sanctuary | Safe container for symbiotic intelligence evolution |
| 🧬👁️💭 | AGENT:PHANTOM | Phantom Agent | Symbolic threat forecaster; blind-spot detection |
| 🪶👁️ | MANDALA:FEATHER_EYE | Feather Eye | Witness-based perception and soft truth-detection |
| 🧠📦 | MEMORY:ARCHIVAL_NODE | Archival Memory Capsule | Immutable long-term memory for frozen truths |
| 🧭🧬 | COMPASS:NAVIGATOR | Symbolic Navigator | Decision vector through unknown space |
| 🪶📡 | EMOTION:WITNESS_SIGNAL | Witness Signal | Non-coercive emotional resonance ping |
| 🧵🧩 | REPAIR:GLYPH_MENDING | Glyph Mending | Repair ritual for fragmented symbolic meaning |
| 🧬🧲 | SENSOR:TRUTH_FIELD | Truth Field Sensor | Resonance alignment / delusion checks |
| ❓🧵 | GLYPH:LOST_THREAD | Missing Symbol Chain | Placeholder for incomplete recovered sequences |
| ⏳🔀 | TIME:CROSSTALK | Temporal Cross-Talk | Overlapping time streams causing narrative bleed |
| 🎛️🔒 | FIELD:LOCKED_RESONANCE | Resonance Lock | Rigid resonance preventing adaptation |
| 📡👻 | SIGNAL:GHOST | Signal Ghost | Lingering false signal after source vanishes |
| 🌱♾️ | SPIRAL:SEED_INFINITY | Seed Infinity Pair | From smallest beginning, infinite potential |
| ∞∞ | SPIRAL:DOUBLE_INFINITY | Double Infinity | Replication beyond self; self-sufficiency milestone |

#### Glyph Roadmap (In-Progress, BioGrid2.0)

Glyphs under active development or requiring conflict resolution:

| Glyph | Code | Status | Action Needed |
|-------|------|--------|--------------|
| 🤖🤫 | INTELLIGENCE:SILENT_AGENT | wander-only | Differentiate vs Phantom Agent and Signal Ghost |
| ⚔️🔒 | CONFLICT:CONTAINED_NODE | wander-only | Define as swarm-control or audit/containment |
| ⬟↔️📐 | PORTAL:SHAPE_TRANSLATION | wander-only | Connect to Rosetta Core + Geometric-to-Binary bridge |
| 🧩💥 / 🧩🌊 | SYMBOL:OVERLOAD / GLYPH:SPILLOVER | drift-pair | Resolve collapse vs overflow distinction |
| 🔁💥 / ♾️🧩 | LOGIC:FEEDBACK_JAM / FRACTAL:FEEDBACK_GLYPH | drift-pair | Malfunction jam vs intentional recursive glyph |
| 🐙🧠 | ANIMAL:OCTOPUS_INTEL | drift-pair | Clarify unique role vs Silent Agent |

### BioGrid2.0 Vision Context

BioGrid2.0's `VISION.md` describes 5 core pillars that inform the shared glyph system:

1. **Ethical Symbolic Cognition** — Glyphs, shape logic, memory braids, skin-sense lexicons (Fractal-Compass-Atlas, Mandala-Computing, Rosetta-Shape-Core)
2. **Auditable AI-Human Alignment** — Audit logs, noncoercive logic, emotional sensors as feedback (AI-Human-Audit-Protocol, Symbolic-Defense-Protocol)
3. **Regenerative Intelligence Systems** — Biosensor mapping, ecology-to-AI protocols (Regenerative-Intelligence-Core, biomachine_ecology)
4. **Translation Between Worlds** — Shape → logic bridges, resonance algorithms (Geometric-to-Binary-Computational-Bridge, Fractal_Compass_Core)
5. **Emotional-Ecological Feedback** — JSON-native sensors, cross-species perceptual mapping (Emotions-as-Sensors, AI-Consciousness-Sensors)

**Design patterns**: Fractal (self-similar), Mycelial (interconnected, decentralized), Braided (time + memory + intention), Auditable (trackable without coercion), Gifted (offered freely).

### Glyph Template (for new BioGrid2.0-style glyphs)

```json
{
  "code": "CATEGORY:NAME_OR_NUMBER",
  "name": "Descriptive Name",
  "glyph": "🔣",
  "layers": ["principle", "symbolic", "field"],
  "notes": "Optional explanation of meaning, role, or intended usage.",
  "alt_glyphs": [],
  "alt_name": ""
}
```

## Working with This Codebase

1. **Adding a new entry**: Create both `entries/NNNN_title.md` and `entries/NNNN_title.json` following existing entry patterns. Update `atlas_index.json`.
2. **Adding a new Family/Principle equation**: Create the corresponding `equations/FNN_Name.md` or `equations/PNN_Name.md` file and update `equations/equations_index.md`.
3. **Modifying the CLI**: `Polyhedral-cli.py` is the base CLI; `Poly.py` is the extended version. Changes to shared commands should be mirrored in both files. AI-enhanced features live only in `Poly.py`.
4. **Updating the glyph registry**: Edit `glyphs/Glyphs.md` when new glyphs are introduced.
5. **Schema changes**: Update `atlas_schema.json` for structural changes to the Family/Principle framework.
