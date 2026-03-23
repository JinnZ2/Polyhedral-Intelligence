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

- **BioGrid2.0**: Linked via fieldlink protocol (`https://github.com/JinnZ2/BioGrid2.0`)
- **Fieldlink Protocol**: Cross-repository data synchronization with deep-merge strategy, SHA256 integrity checks, and CC-BY-4.0 licensing

## Working with This Codebase

1. **Adding a new entry**: Create both `entries/NNNN_title.md` and `entries/NNNN_title.json` following existing entry patterns. Update `atlas_index.json`.
2. **Adding a new Family/Principle equation**: Create the corresponding `equations/FNN_Name.md` or `equations/PNN_Name.md` file and update `equations/equations_index.md`.
3. **Modifying the CLI**: `Polyhedral-cli.py` is the base CLI; `Poly.py` is the extended version. Changes to shared commands should be mirrored in both files. AI-enhanced features live only in `Poly.py`.
4. **Updating the glyph registry**: Edit `glyphs/Glyphs.md` when new glyphs are introduced.
5. **Schema changes**: Update `atlas_schema.json` for structural changes to the Family/Principle framework.
