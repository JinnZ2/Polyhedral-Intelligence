# CLAUDE.md — Polyhedral Intelligence

## Project Overview

Polyhedral Intelligence is a symbolic knowledge system that processes concepts through mandala-based geometric frameworks. It combines **20 Families** (mapped onto an icosahedron) and **12 Principles** (mapped onto a dodecahedron) to generate symbolic "glyphs" and mandala insights from design concepts.

The system implements two core protocols:
- **Mandala Redesign Protocol (MRP)** — Generates mandala insights by sweeping concepts against all 20 Families and 12 Principles
- **Noise-to-Insight Protocol (NIP)** — Transforms noise (turbulence, uncertainty, error) into resilience insights

## Repository Structure

```
/
├── Poly.py                          # Extended CLI with AI-enhanced glyph creation (699 lines)
├── Polyhedral-cli.py                # Base CLI using Click (488 lines)
├── integrated.py                    # Architectural sketch: emotional matrix + field integration (193 lines, not runnable)
├── atlas_schema.json                # Master schema: all 20 Families with equations
├── atlas_index.json                 # Index of atlas entries
├── protocol.json / protocols.json   # Families + principles schema (identical duplicates, equations empty)
├── five_field_schema_map.json       # Maps 20 Families to 5 meta-fields
├── .fieldlink.json                  # Cross-repository linking config
├── fieldlink.schema.json            # JSON Schema for fieldlink validation
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

### The 20 Families (Icosahedron)

F01-Resonance, F02-Flow, F03-Information, F04-Life, F05-Energy/Thermo, F06-Cognition, F07-Earth/Cosmos, F08-Matter, F09-Geometry, F10-Particle, F11-Engineering, F12-Networks, F13-Reaction, F14-Measurement, F15-Navigation, F16-Consciousness, F17-Turbulence, F18-Relativity, F19-Statistical, F20-Topology

### The 12 Principles (Dodecahedron)

P01-Symmetry, P02-Conservation, P03-Relativity, P04-Duality, P05-Emergence, P06-Resonance, P07-Continuity, P08-Quantization, P09-Proportion, P10-Uncertainty, P11-Transformation, P12-Unity

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

## Integration Points

- **BioGrid2.0**: Linked via fieldlink protocol (`https://github.com/JinnZ2/BioGrid2.0`)
- **Fieldlink Protocol**: Cross-repository data synchronization with deep-merge strategy, SHA256 integrity checks, and CC-BY-4.0 licensing

## Working with This Codebase

1. **Adding a new entry**: Create both `entries/NNNN_title.md` and `entries/NNNN_title.json` following existing entry patterns. Update `atlas_index.json`.
2. **Adding a new Family/Principle equation**: Create the corresponding `equations/FNN_Name.md` or `equations/PNN_Name.md` file and update `equations/equations_index.md`.
3. **Modifying the CLI**: `Polyhedral-cli.py` is the base CLI; `Poly.py` is the extended version. Changes to shared commands should be mirrored in both files. AI-enhanced features live only in `Poly.py`.
4. **Updating the glyph registry**: Edit `glyphs/Glyphs.md` when new glyphs are introduced.
5. **Schema changes**: Update `atlas_schema.json` for structural changes to the Family/Principle framework.
