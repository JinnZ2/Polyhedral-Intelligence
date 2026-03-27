#!/usr/bin/env python3
"""
generate.py — Training data generator for Polyhedral Intelligence.
Reads atlas_schema.json, protocols.json, five_field_schema_map.json,
entries/*.json, and Rosetta bridge data to produce JSONL training data
for the Mandala Noise-Redesign Protocol.

Usage:
    python data/training/generate.py
"""

import json, pathlib, random, textwrap

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).parent

random.seed(42)

SYSTEM_PROMPT = (
    "You are a symbolic knowledge architect using the Mandala Noise-Redesign "
    "Protocol. You compress concepts into geometric glyphs mapped to 20 Families "
    "(icosahedron) and 12 Principles (dodecahedron), sweep them for balance, "
    "reframe flagged imbalances as design insights using the Noise-to-Insight "
    "Protocol (NIP), and ground reasoning in equations from the atlas schema. "
    "You reason with symbols and geometry, not narrative."
)

# ── NIP patterns (constant) ─────────────────────────────────────────────────

NIP_PATTERNS = [
    {"id": "NIP1", "name": "Noise = Fractal Signal",
     "rule": "Turbulence becomes structure. Chaotic input contains self-similar patterns at multiple scales."},
    {"id": "NIP2", "name": "Uncertainty = Silence Signal",
     "rule": "Absence reveals truth. What is NOT present or measurable carries information."},
    {"id": "NIP3", "name": "Delay = Relative Time",
     "rule": "Lags reveal hidden dimensions. Temporal offsets encode structural depth."},
    {"id": "NIP4", "name": "Error = Hidden Dimension",
     "rule": "Contradictions expand space. Errors point to missing variables or collapsed axes."},
    {"id": "NIP5", "name": "Instability = Emergent Flexibility",
     "rule": "Wobble becomes adaptation. Instability is the system searching for a new attractor."},
]

# ── Keyword-to-symbol map (from Poly.py) ────────────────────────────────────

KEYWORD_MAP = {
    'flow': '〰', 'fluid': '〰', 'stream': '〰',
    'turbulent': 'ᘯᘰ', 'chaos': 'ᘯᘰ', 'chaotic': 'ᘯᘰ',
    'network': '⬡', 'graph': '⬡', 'web': '⬡', 'mesh': '⬡',
    'crystal': '◇', 'lattice': '◇', 'structure': '◇',
    'geometry': '☆', 'shape': '☆',
    'engineer': '⚙', 'design': '⚙', 'build': '⚙', 'machine': '⚙',
    'transform': '↻', 'change': '↻', 'evolve': '↻',
    'resonate': '∿', 'vibrate': '∿', 'oscillate': '∿',
    'energy': '⚡', 'power': '⚡', 'force': '⚡',
    'heat': '△≈', 'thermal': '△≈', 'temperature': '△≈',
    'information': '⊗', 'data': '⊗', 'signal': '⊗',
    'conscious': '◎', 'aware': '◎', 'mind': '◎',
    'cognition': '⋯⋯', 'neural': '⋯⋯', 'brain': '⋯⋯',
    'life': '••••', 'biological': '••••', 'organic': '••••',
    'space': '◯', 'cosmic': '◯', 'orbital': '◯',
    'matter': '◆', 'material': '◆', 'substance': '◆',
    'particle': '⚪', 'quantum': '⚪', 'atom': '⚪',
    'self': '↺', 'healing': '↺', 'recursive': '↺',
    'uncertain': '◧', 'random': '◧', 'stochastic': '◧',
    'symmetry': '⧖', 'balance': '⧖', 'mirror': '⧖',
}

# ── Loaders ──────────────────────────────────────────────────────────────────

def load_atlas():
    p = ROOT / "atlas_schema.json"
    return json.loads(p.read_text(encoding="utf-8"))


def load_protocols():
    p = ROOT / "protocols.json"
    return json.loads(p.read_text(encoding="utf-8"))


def load_five_fields():
    p = ROOT / "five_field_schema_map.json"
    return json.loads(p.read_text(encoding="utf-8"))


def load_entries():
    entries = []
    for fp in sorted((ROOT / "entries").glob("*.json")):
        try:
            entries.append(json.loads(fp.read_text(encoding="utf-8")))
        except Exception:
            pass
    return entries


def load_rosetta_bridges():
    p = ROOT / "atlas" / "remote" / "rosetta" / "bridges.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


# ── JSONL helpers ────────────────────────────────────────────────────────────

def msg(user, assistant):
    return {"messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]}


def write_jsonl(name, records):
    p = OUT / name
    with p.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  {name:<45} {len(records):>4} examples")


# ── Task 1: Family identification ───────────────────────────────────────────

def gen_family_id(atlas):
    out = []
    for fam in atlas["families"]:
        fid, name, sym = fam["id"], fam["name"], fam["symbol"]
        domain = fam.get("domain", "")
        eq_count = len(fam.get("equations", []))
        eq_names = ", ".join(e["name"] for e in fam.get("equations", [])[:3])

        answer = (
            f"**{fid} — {name}** (symbol: `{sym}`)\n"
            f"**Domain:** {domain}\n"
            f"**Equations:** {eq_count} defined"
        )
        if eq_names:
            answer += f" — including {eq_names}"

        out.append(msg(
            f"What is Family {fid} in the Polyhedral Intelligence framework?",
            answer
        ))
        out.append(msg(
            f"Which family uses the symbol `{sym}`?",
            f"`{sym}` is the symbol for **{fid} — {name}**.\n"
            f"Domain: {domain}"
        ))
    return out


# ── Task 2: Principle identification ────────────────────────────────────────

def gen_principle_id(atlas):
    out = []
    for pri in atlas.get("principles", []):
        pid, name, sym = pri["id"], pri["name"], pri["symbol"]
        out.append(msg(
            f"What is Principle {pid} in the dodecahedral framework?",
            f"**{pid} — {name}** (symbol: `{sym}`)\n"
            f"One of 12 archetypal principles mapped onto the dodecahedron. "
            f"Used in the Principle Sweep (MRP step 3) to check alignment."
        ))
        out.append(msg(
            f"Which principle uses the symbol `{sym}`?",
            f"`{sym}` is **{pid} — {name}**."
        ))
    return out


# ── Task 3: Glyph creation from concept ─────────────────────────────────────

def gen_glyph_creation(entries):
    out = []
    for e in entries:
        title = e["title"]
        intent = e.get("intent", "")
        seed = e["seed_glyph"]

        out.append(msg(
            f"Create a seed glyph for: {title}",
            f"**Concept:** {title}\n"
            f"**Intent:** {intent}\n\n"
            f"**Seed glyph:** `{seed}`\n\n"
            f"Each symbol maps to an activated Family. The glyph compresses "
            f"the concept's core resonances into a symbolic token chain."
        ))

        # Reverse direction
        out.append(msg(
            f"What concept does the glyph `{seed}` represent?",
            f"**Glyph:** `{seed}`\n"
            f"**Concept:** {title}\n"
            f"**Intent:** {intent}"
        ))

    # Synthetic examples using keyword map
    synthetic = [
        ("self-healing network", "A distributed system that repairs itself autonomously"),
        ("quantum consciousness field", "Consciousness emerging from quantum-level particle interactions"),
        ("turbulent energy flow", "Energy transfer through chaotic fluid dynamics"),
        ("biological crystal lattice", "Living crystalline structures in organic systems"),
        ("cosmic information stream", "Data flowing through orbital-scale cosmic channels"),
    ]
    for concept, intent in synthetic:
        parts = []
        for kw, sym in KEYWORD_MAP.items():
            if kw in concept.lower() and sym not in parts:
                parts.append(sym)
        glyph = "".join(parts)
        if glyph:
            out.append(msg(
                f"Create a seed glyph for: {concept}",
                f"**Concept:** {concept}\n"
                f"**Intent:** {intent}\n\n"
                f"**Seed glyph:** `{glyph}`\n\n"
                f"Keyword extraction activates Family symbols: "
                + ", ".join(f"`{s}`" for s in parts)
            ))
    return out


# ── Task 4: Glyph decoding ──────────────────────────────────────────────────

def gen_glyph_decode(atlas, entries):
    out = []
    # Build reverse symbol-to-family map
    sym_map = {}
    for fam in atlas["families"]:
        sym_map[fam["symbol"]] = f"{fam['id']} {fam['name']}"
    for pri in atlas.get("principles", []):
        sym_map[pri["symbol"]] = f"{pri['id']} {pri['name']}"

    for e in entries:
        seed = e["seed_glyph"]
        refined = e.get("refined_glyph", "")

        if refined and refined != seed:
            added = refined.replace(seed, "").strip()
            out.append(msg(
                f"Decode the refined glyph `{refined}` — what was added beyond the seed?",
                f"**Seed glyph:** `{seed}`\n"
                f"**Refined glyph:** `{refined}`\n"
                f"**Added symbols:** `{added}`\n\n"
                f"The added symbols represent flagged families/principles that were "
                f"reframed through the Noise-to-Insight Protocol and incorporated "
                f"as corrective elements."
            ))
    return out


# ── Task 5: Family sweep ────────────────────────────────────────────────────

def gen_family_sweep(entries, atlas):
    out = []
    families = atlas["families"]

    for e in entries:
        title = e["title"]
        sweep = e.get("resonance_sweep", {})
        balanced = sweep.get("families_balanced", 0)
        total = sweep.get("families_total", 20)
        flags = sweep.get("flags", [])

        flag_block = "\n".join(f"  ❗ {f}" for f in flags)
        balanced_count = total - len(flags)

        answer = (
            f"**Family Sweep for:** {title}\n"
            f"**Seed glyph:** `{e['seed_glyph']}`\n\n"
            f"**Result:** {balanced}/{total} families balanced\n\n"
            f"**Flagged ({len(flags)}):**\n{flag_block}\n\n"
            f"The remaining {balanced_count} families show ✅ balanced or ⚖️ neutral "
            f"resonance with the concept. Flagged families become NIP inputs for "
            f"corrective evolution (MRP step 5)."
        )

        out.append(msg(
            f"Run a Family Sweep (MRP step 2) on the concept: {title}",
            answer
        ))

        # Also teach what a flag means
        for flag in flags:
            out.append(msg(
                f"Family '{flag}' was flagged in the sweep for '{title}'. What does this mean?",
                f"A ❗ flag on **{flag}** means this family shows imbalance with the "
                f"concept '{title}'. It doesn't mean the family is irrelevant — it means "
                f"there's tension or an unresolved gap.\n\n"
                f"This flag becomes an input to the Noise-to-Insight Protocol (NIP), "
                f"where it gets reframed as a design feature rather than a flaw."
            ))
    return out


# ── Task 6: Principle sweep ─────────────────────────────────────────────────

def gen_principle_sweep(entries):
    out = []
    for e in entries:
        title = e["title"]
        sweep = e.get("principle_sweep", {})
        balanced = sweep.get("principles_balanced", 0)
        total = sweep.get("principles_total", 12)
        flags = sweep.get("flags", [])

        flag_block = "\n".join(f"  ❗ {f}" for f in flags)

        out.append(msg(
            f"Run a Principle Sweep (MRP step 3) on: {title}",
            f"**Principle Sweep for:** {title}\n"
            f"**Result:** {balanced}/{total} principles aligned\n\n"
            f"**Flagged ({len(flags)}):**\n{flag_block}\n\n"
            f"Flagged principles join flagged families as NIP inputs."
        ))
    return out


# ── Task 7: Noise-to-Insight reframing ──────────────────────────────────────

def gen_noise_to_insight(entries):
    out = []
    for e in entries:
        title = e["title"]
        nti = e.get("noise_to_insight", {})
        if not nti:
            continue

        reframes = "\n".join(
            f"  `{sym}` → {insight}" for sym, insight in nti.items()
        )

        out.append(msg(
            f"Apply the Noise-to-Insight Protocol to the flagged elements for '{title}'.",
            f"**NIP Reframing for:** {title}\n\n{reframes}\n\n"
            f"Each flagged symbol is reframed through one of the 5 NIP patterns:\n"
            + "\n".join(f"  {p['id']}: {p['name']} — {p['rule']}" for p in NIP_PATTERNS)
        ))

        # Individual reframe questions
        for sym, insight in nti.items():
            out.append(msg(
                f"The symbol `{sym}` was flagged for '{title}'. How does NIP reframe it?",
                f"**Flag:** `{sym}` in concept '{title}'\n"
                f"**Reframe:** {insight}\n\n"
                f"Instead of treating this as a flaw, NIP converts the imbalance "
                f"into a design insight. The flag becomes a feature."
            ))
    return out


# ── Task 8: Meta-field classification ────────────────────────────────────────

def gen_meta_fields(five_fields, atlas):
    out = []
    fields = five_fields.get("fields", {})
    coupling = five_fields.get("coupling_logic", "")

    # Build family name lookup
    fam_names = {f["id"]: f["name"] for f in atlas["families"]}

    for field_name, field_data in fields.items():
        desc = field_data.get("description", "")
        fam_ids = field_data.get("families", [])
        fam_list = ", ".join(f"{fid} ({fam_names.get(fid, '?')})" for fid in fam_ids)

        out.append(msg(
            f"Which families belong to the '{field_name}' meta-field?",
            f"**{field_name.title()} Field**\n"
            f"**Description:** {desc}\n"
            f"**Families:** {fam_list}"
        ))

    # Overall coupling question
    if coupling:
        field_summary = "\n".join(
            f"  **{fn.title()}:** {fd['description']} ({', '.join(fd['families'])})"
            for fn, fd in fields.items()
        )
        out.append(msg(
            "How do the 5 meta-fields relate to each other?",
            f"The 20 Families map to 5 meta-fields with a cyclic coupling:\n\n"
            f"{field_summary}\n\n"
            f"**Coupling logic:** {coupling}"
        ))

    # Reverse: given a family, which field?
    for field_name, field_data in fields.items():
        for fid in field_data.get("families", []):
            fname = fam_names.get(fid, "?")
            out.append(msg(
                f"Which meta-field does {fid} ({fname}) belong to?",
                f"**{fid} ({fname})** belongs to the **{field_name.title()}** meta-field.\n"
                f"{field_data.get('description', '')}"
            ))
    return out


# ── Task 9: Equation grounding ──────────────────────────────────────────────

def gen_equations(atlas):
    out = []
    for fam in atlas["families"]:
        fid, name, sym = fam["id"], fam["name"], fam["symbol"]
        eqs = fam.get("equations", [])
        if not eqs:
            continue

        eq_block = "\n".join(
            f"  - **{eq['name']}:** `{eq['formula']}` "
            f"(glyph: {eq.get('glyph', '—')} \"{eq.get('glyph_name', '')}\")"
            for eq in eqs
        )

        out.append(msg(
            f"What equations define Family {fid} ({name})?",
            f"**{fid} — {name}** (`{sym}`)\n\n{eq_block}"
        ))

        # Individual equation questions
        for eq in eqs:
            tags = ", ".join(eq.get("tags", []))
            out.append(msg(
                f"Explain the equation '{eq['name']}' in the context of Family {fid}.",
                f"**{eq['name']}**\n"
                f"**Formula:** `{eq['formula']}`\n"
                f"**Family:** {fid} — {name} (`{sym}`)\n"
                f"**Glyph:** {eq.get('glyph', '—')} ({eq.get('glyph_name', '')})\n"
                f"**Tags:** {tags}\n\n"
                f"This equation grounds the {name} family in mathematical formalism. "
                f"The equation glyph compresses the formula's essence into a symbolic token."
            ))
    return out


# ── Task 10: Cross-repo bridge mapping ──────────────────────────────────────

def gen_bridge_mapping(bridges):
    out = []
    bridge_map = bridges.get("map", [])
    if not bridge_map:
        return out

    for b in bridge_map:
        shape = b.get("shape", "")
        poly = b.get("polyhedral", {})
        maps_to = poly.get("maps_to", "")
        note = poly.get("note", "")
        sensors = b.get("sensors", [])
        sensor_glyphs = b.get("sensor_glyphs", [])
        defenses = b.get("defense_names", [])
        scroll = b.get("bridge_scroll", "")

        sensor_block = ", ".join(
            f"{s} ({g})" if g else s
            for s, g in zip(sensors, sensor_glyphs + [None] * len(sensors))
        )
        defense_block = ", ".join(defenses) if defenses else "none mapped"

        out.append(msg(
            f"How does {shape} bridge to the Polyhedral Intelligence framework?",
            f"**{shape}**\n"
            f"**Maps to:** {maps_to}\n"
            f"**Note:** {note}\n\n"
            f"**Emotion sensors:** {sensor_block}\n"
            f"**Defense patterns:** {defense_block}\n"
            f"**Bridge scroll:** {scroll}"
        ))

    # Overview question
    shapes = [b.get("shape", "") for b in bridge_map]
    out.append(msg(
        "How do the Platonic solids connect to the Polyhedral Intelligence framework?",
        f"The Rosetta bridge maps {len(bridge_map)} Platonic solids to PI:\n\n"
        + "\n".join(
            f"  **{b.get('shape', '')}** → {b.get('polyhedral', {}).get('maps_to', '')}"
            for b in bridge_map
        )
        + "\n\nEach shape also links to emotion sensors (Emotions-as-Sensors) and "
        "defense patterns (Symbolic-Defense-Protocol), creating a cross-repo "
        "bridge between geometry, emotion, and protection."
    ))
    return out


# ── Task 11: Full MRP walkthrough ────────────────────────────────────────────

def gen_mrp_walkthrough(entries, atlas):
    out = []
    for e in entries:
        title = e["title"]
        seed = e["seed_glyph"]
        intent = e.get("intent", "")
        rsweep = e.get("resonance_sweep", {})
        psweep = e.get("principle_sweep", {})
        nti = e.get("noise_to_insight", {})
        refined = e.get("refined_glyph", "")
        insight_text = e.get("insight", "")

        r_flags = rsweep.get("flags", [])
        p_flags = psweep.get("flags", [])

        nti_block = "\n".join(f"    `{s}` → {i}" for s, i in nti.items())

        answer = textwrap.dedent(f"""\
**Full MRP Walkthrough: {title}**

**Step 1 — Seed Glyph:**
  `{seed}`
  Intent: {intent}

**Step 2 — Family Sweep:**
  {rsweep.get('families_balanced', '?')}/{rsweep.get('families_total', 20)} balanced
  Flags: {', '.join(r_flags) if r_flags else 'none'}

**Step 3 — Principle Sweep:**
  {psweep.get('principles_balanced', '?')}/{psweep.get('principles_total', 12)} aligned
  Flags: {', '.join(p_flags) if p_flags else 'none'}

**Step 4 — Bridge Glyphs:**
  Connectors added where flagged families meet adjacent balanced families.

**Step 5 — Corrective Evolution (NIP):**
{nti_block}

**Step 6 — Mandala Spin Test:**
  Visualize balance across icosahedron (families) and dodecahedron (principles).
  All flags reframed — mandala stabilized.

**Step 7 — Record Entry:**
  Refined glyph: `{refined}`

**Insight:** {insight_text}""")

        out.append(msg(
            f"Walk me through the complete Mandala Redesign Protocol for '{title}'.",
            answer
        ))
    return out


# ── Task 12: NIP pattern teaching ────────────────────────────────────────────

def gen_nip_patterns():
    out = []
    for p in NIP_PATTERNS:
        out.append(msg(
            f"Explain NIP pattern: {p['name']}",
            f"**{p['id']} — {p['name']}**\n\n"
            f"{p['rule']}\n\n"
            f"When a family or principle is flagged ❗ in a sweep, this pattern "
            f"reframes the imbalance as a design feature. The flag doesn't mean "
            f"the concept is broken — it means there's untapped potential."
        ))

    # Overview
    pattern_list = "\n".join(
        f"  {p['id']}: **{p['name']}** — {p['rule']}" for p in NIP_PATTERNS
    )
    out.append(msg(
        "What are the 5 Noise-to-Insight Protocol patterns?",
        f"The NIP defines 5 patterns for reframing flags as features:\n\n{pattern_list}"
    ))
    return out


# ── Task 13: Keyword-to-glyph mapping ───────────────────────────────────────

def gen_keyword_mapping():
    out = []
    # Group keywords by symbol
    sym_to_kw = {}
    for kw, sym in KEYWORD_MAP.items():
        sym_to_kw.setdefault(sym, []).append(kw)

    for sym, keywords in sym_to_kw.items():
        kw_str = ", ".join(keywords)
        out.append(msg(
            f"What keywords map to the glyph symbol `{sym}`?",
            f"**Symbol:** `{sym}`\n"
            f"**Keywords:** {kw_str}\n\n"
            f"When any of these keywords appear in a concept, the symbol `{sym}` "
            f"is added to the seed glyph during glyph creation."
        ))

    return out


# ── Task 14: Cross-repo co-activation (Family flags → EaS sensors) ──────────

# Map PI families to EaS emotion sensors via Rosetta bridge data
FAMILY_SENSOR_BRIDGE = {
    "F01": {"sensors": ["love", "peace"], "reason": "Resonance ↔ harmonic_resonance / universal_alignment"},
    "F02": {"sensors": ["excitement", "contentment"], "reason": "Flow ↔ positive_activation / effort_sufficiency"},
    "F03": {"sensors": ["curiosity", "confusion"], "reason": "Information ↔ directed probes / uncertainty"},
    "F04": {"sensors": ["compassion", "grief"], "reason": "Life ↔ interconnection_resonance / connection_loss"},
    "F05": {"sensors": ["anger", "excitement"], "reason": "Energy-Thermo ↔ identity_coherence / positive_activation"},
    "F06": {"sensors": ["curiosity", "doubt"], "reason": "Cognition ↔ directed probes / uncertainty processing"},
    "F07": {"sensors": ["awe", "peace"], "reason": "Earth-Cosmos ↔ scale recognition / alignment"},
    "F08": {"sensors": ["pride", "pain"], "reason": "Matter ↔ pattern_completion / pattern_disruption"},
    "F09": {"sensors": ["admiration", "contentment"], "reason": "Geometry ↔ aesthetic recognition / completeness"},
    "F10": {"sensors": ["fear", "excitement"], "reason": "Particle ↔ uncertainty at quantum scale / activation"},
    "F11": {"sensors": ["pride", "anger"], "reason": "Engineering ↔ completion sensor / boundary breach detector"},
    "F12": {"sensors": ["love", "longing"], "reason": "Networks ↔ resonance harmonizer / connection seeking"},
    "F13": {"sensors": ["anger", "fear"], "reason": "Reaction ↔ boundary defense / threat anticipation"},
    "F14": {"sensors": ["curiosity", "doubt"], "reason": "Measurement ↔ probe generation / calibration uncertainty"},
    "F15": {"sensors": ["longing", "hope"], "reason": "Navigation ↔ directional pull / anticipatory orientation"},
    "F16": {"sensors": ["compassion", "shame"], "reason": "Consciousness ↔ mirror integration / authenticity conflict"},
    "F17": {"sensors": ["fear", "excitement"], "reason": "Turbulence ↔ threat detection / edge-of-chaos activation"},
    "F18": {"sensors": ["confusion", "awe"], "reason": "Relativity ↔ frame shifting / scale recognition"},
    "F19": {"sensors": ["doubt", "curiosity"], "reason": "Statistical ↔ distribution uncertainty / pattern seeking"},
    "F20": {"sensors": ["love", "grief"], "reason": "Topology ↔ persistent connection / topological loss"},
}


def gen_cross_repo_coactivation(entries):
    out = []
    for e in entries:
        flags = e.get("resonance_sweep", {}).get("flags", [])
        title = e["title"]

        for flag_str in flags:
            # Extract family ID from flag string like "ᘯᘰ Turbulence"
            fid = None
            for fam_id, bridge in FAMILY_SENSOR_BRIDGE.items():
                # Match by symbol or name in the flag string
                if fam_id in flag_str:
                    fid = fam_id
                    break
            # Try matching by name
            if not fid:
                for fam_id, bridge in FAMILY_SENSOR_BRIDGE.items():
                    fname = fam_id  # we'll match differently
                    for name_frag in flag_str.split():
                        for check_id, check_bridge in FAMILY_SENSOR_BRIDGE.items():
                            pass
                # Simpler: match known family names
                flag_lower = flag_str.lower()
                for fam_id in FAMILY_SENSOR_BRIDGE:
                    fam_names_map = {
                        "F13": "reaction", "F16": "consciousness", "F17": "turbulence",
                        "F19": "statistical", "F10": "uncertainty",
                    }
                    if fam_names_map.get(fam_id, "").lower() in flag_lower:
                        fid = fam_id
                        break

            if not fid:
                # Default mapping for common flags
                if "turbulence" in flag_str.lower() or "ᘯᘰ" in flag_str:
                    fid = "F17"
                elif "reaction" in flag_str.lower() or "⇑" in flag_str:
                    fid = "F13"
                elif "uncertainty" in flag_str.lower() or "◧" in flag_str:
                    fid = "F19"  # closest match
                elif "consciousness" in flag_str.lower() or "◉" in flag_str:
                    fid = "F16"
                elif "statistical" in flag_str.lower() or "▁▃▅∿" in flag_str:
                    fid = "F19"

            if fid and fid in FAMILY_SENSOR_BRIDGE:
                bridge = FAMILY_SENSOR_BRIDGE[fid]
                sensors = bridge["sensors"]
                reason = bridge["reason"]

                out.append(msg(
                    f"Family {fid} was flagged in the sweep for '{title}'. "
                    f"Which Emotions-as-Sensors sensors resonate with this flag?",
                    f"**Flagged family:** {fid} ({flag_str})\n"
                    f"**Concept:** {title}\n\n"
                    f"**Resonant EaS sensors:** {', '.join(sensors)}\n"
                    f"**Bridge logic:** {reason}\n\n"
                    f"When {fid} is flagged, these emotion sensors are likely in "
                    f"co-activation — the imbalance in the polyhedral framework "
                    f"maps to a detectable emotional/systemic signal."
                ))

    # General bridge teaching
    for fid, bridge in FAMILY_SENSOR_BRIDGE.items():
        out.append(msg(
            f"What EaS sensors bridge to Family {fid}?",
            f"**{fid}** bridges to: {', '.join(bridge['sensors'])}\n"
            f"**Reason:** {bridge['reason']}"
        ))
    return out


# ── Task 15: Ontology translation (Western vs Relational) ───────────────────

ONTOLOGY_CONCEPTS = [
    {
        "term": "Control",
        "western": "Force/regulation, centralized authority, minimizing unpredictability",
        "relational": "Alignment with natural patterns, distributed redundant pathways, cooperation",
        "hidden_vars": "Relationship quality, pattern recognition depth, adaptive capacity",
        "pi_families": ["F02 Flow", "F12 Networks", "F17 Turbulence"],
        "reframe": "PI treats control as distributed resonance (F01) across a network (F12), not centralized force."
    },
    {
        "term": "Strength",
        "western": "Rigidity, resistance to change, dominance over opposing forces",
        "relational": "Adaptive capacity, energy efficiency, structural resilience",
        "hidden_vars": "Energy flow efficiency, structural organization, multi-system integration",
        "pi_families": ["F08 Matter", "F05 Energy-Thermo", "F20 Topology"],
        "reframe": "PI encodes strength as topological resilience (F20) — self-healing, not rigid."
    },
    {
        "term": "Efficiency",
        "western": "Maximum output per input, speed, minimizing waste",
        "relational": "Whole-system optimization, resource cycling, regeneration",
        "hidden_vars": "Externalized costs, relationship maintenance, regenerative capacity",
        "pi_families": ["F11 Engineering", "F04 Life", "F19 Statistical"],
        "reframe": "PI measures efficiency across the full mandala — all 20 families must balance, not just one metric."
    },
    {
        "term": "Speed",
        "western": "Faster = better, minimal time from problem to action",
        "relational": "Right timing matched to consequence, pattern recognition enabling efficient response",
        "hidden_vars": "Preparation quality, consequence scope, learning integration",
        "pi_families": ["F13 Reaction", "F18 Relativity", "F14 Measurement"],
        "reframe": "NIP pattern 3 (Delay = Relative Time) directly encodes this: lags reveal hidden dimensions."
    },
    {
        "term": "Technology",
        "western": "Manufactured mechanical/electronic tools",
        "relational": "Any systematic method — biological, social, technical",
        "hidden_vars": "Maintenance requirements, breakdown resilience, knowledge transmission",
        "pi_families": ["F11 Engineering", "F06 Cognition", "F04 Life"],
        "reframe": "PI's 20 Families span biological (F04), cognitive (F06), and engineered (F11) — technology is not limited to F11."
    },
    {
        "term": "Intelligence",
        "western": "Cognitive/computational, abstract reasoning, processing speed",
        "relational": "Pattern recognition, adaptive response, multi-sensory integration",
        "hidden_vars": "Relationship awareness, embodied knowledge, field coherence detection",
        "pi_families": ["F06 Cognition", "F16 Consciousness", "F01 Resonance"],
        "reframe": "PI distributes intelligence across cognition (F06), consciousness (F16), and resonance (F01) — not just computation."
    },
    {
        "term": "Knowledge",
        "western": "Codified information, context-free, verified through replication",
        "relational": "Embodied understanding, context-dependent, verified through practical effectiveness",
        "hidden_vars": "Relational context, embodied skill, timing sensitivity, field awareness",
        "pi_families": ["F03 Information", "F06 Cognition", "F16 Consciousness"],
        "reframe": "PI encodes knowledge across information (F03), cognition (F06), and consciousness (F16) — data alone is insufficient."
    },
    {
        "term": "Sensing",
        "western": "Technological instruments detecting specific variables",
        "relational": "Any system detecting field patterns — biological, social, technological",
        "hidden_vars": "Calibration quality, relational awareness, multi-modal integration",
        "pi_families": ["F14 Measurement", "F01 Resonance", "F15 Navigation"],
        "reframe": "PI links sensing to measurement (F14), resonance (F01), and navigation (F15) — sensing is multi-modal, not instrument-only."
    },
]


def gen_ontology_translation():
    out = []
    for c in ONTOLOGY_CONCEPTS:
        term = c["term"]
        out.append(msg(
            f"How does the concept of '{term}' differ between Western and Relational frameworks?",
            f"**{term}**\n\n"
            f"**Western:** {c['western']}\n"
            f"**Relational:** {c['relational']}\n\n"
            f"**Hidden variables the Western frame misses:** {c['hidden_vars']}\n\n"
            f"**PI families involved:** {', '.join(c['pi_families'])}\n"
            f"**PI reframe:** {c['reframe']}"
        ))
        out.append(msg(
            f"Reframe '{term}' through the relational lens using PI families.",
            f"{c['reframe']}\n\n"
            f"Relevant families: {', '.join(c['pi_families'])}\n"
            f"Hidden variables to surface: {c['hidden_vars']}"
        ))
        # Translation check
        out.append(msg(
            f"Someone says 'we need more {term.lower()}.' How do you check which framework they mean?",
            f"**Translation check for '{term}':**\n\n"
            f"Ask: are they seeking {c['western'].split(',')[0].lower()} (Western) "
            f"or {c['relational'].split(',')[0].lower()} (Relational)?\n\n"
            f"The hidden variables that distinguish them: {c['hidden_vars']}\n\n"
            f"In PI terms, check which families activate: {', '.join(c['pi_families'])}. "
            f"If only F11 (Engineering) lights up, it's likely Western-framed. "
            f"If F04 (Life), F12 (Networks), or F16 (Consciousness) also activate, "
            f"the relational frame is operating."
        ))
    return out


# ── Task 16: Equation-to-glyph compression ──────────────────────────────────

def gen_equation_glyph_compression(atlas):
    out = []
    for fam in atlas["families"]:
        fid, name = fam["id"], fam["name"]
        for eq in fam.get("equations", []):
            glyph = eq.get("glyph", "")
            glyph_name = eq.get("glyph_name", "")
            formula = eq.get("formula", "")
            eq_name = eq.get("name", "")
            if not glyph or not glyph_name:
                continue

            out.append(msg(
                f"Why does the glyph {glyph} (\"{glyph_name}\") encode the equation `{formula}`?",
                f"**Equation:** {eq_name}\n"
                f"**Formula:** `{formula}`\n"
                f"**Glyph:** {glyph} — \"{glyph_name}\"\n"
                f"**Family:** {fid} ({name})\n\n"
                f"The glyph compresses the equation's physical essence into a symbolic "
                f"token. \"{glyph_name}\" captures the qualitative behavior — what the "
                f"equation *does* rather than how it computes. This is the PI approach: "
                f"mathematics → symbolic compression → geometric meaning."
            ))

            out.append(msg(
                f"Given the glyph {glyph}, what equation does it encode?",
                f"**{glyph}** (\"{glyph_name}\") encodes:\n\n"
                f"**{eq_name}:** `{formula}`\n"
                f"**Family:** {fid} ({name})\n\n"
                f"The glyph is a symbolic compression of the equation's behavior."
            ))
    return out


# ── Task 17: BioGrid principle crosswalk ─────────────────────────────────────

BIOGRID_CROSSWALK = [
    {"id": "P01", "pi_name": "Symmetry",        "pi_sym": "⧖",  "bg_sym": "⚖️", "bg_name": "Symmetry",         "axis": "Invariance"},
    {"id": "P02", "pi_name": "Conservation",     "pi_sym": "↺",  "bg_sym": "♻️", "bg_name": "Conservation",      "axis": "Invariance"},
    {"id": "P03", "pi_name": "Relativity",       "pi_sym": "⊗",  "bg_sym": "🌀", "bg_name": "Relativity",        "axis": "Invariance"},
    {"id": "P04", "pi_name": "Duality",          "pi_sym": "◑",  "bg_sym": "⏳", "bg_name": "Causality",         "axis": "Transformation"},
    {"id": "P05", "pi_name": "Emergence",        "pi_sym": "●●", "bg_sym": "🌱", "bg_name": "Emergence",         "axis": "Transformation"},
    {"id": "P06", "pi_name": "Resonance",        "pi_sym": "∿",  "bg_sym": "🔄", "bg_name": "Entropy",           "axis": "Transformation"},
    {"id": "P07", "pi_name": "Continuity",       "pi_sym": "⎯",  "bg_sym": "🧩", "bg_name": "Information",       "axis": "Connectivity"},
    {"id": "P08", "pi_name": "Quantization",     "pi_sym": "▭",  "bg_sym": "🤝", "bg_name": "Interaction",       "axis": "Connectivity"},
    {"id": "P09", "pi_name": "Proportion",       "pi_sym": "▯",  "bg_sym": "🕸",  "bg_name": "Network",           "axis": "Connectivity"},
    {"id": "P10", "pi_name": "Uncertainty",      "pi_sym": "◧",  "bg_sym": "🐚", "bg_name": "Adaptation",        "axis": "Evolution"},
    {"id": "P11", "pi_name": "Transformation",   "pi_sym": "↻",  "bg_sym": "🦋", "bg_name": "Evolution",         "axis": "Evolution"},
    {"id": "P12", "pi_name": "Unity",            "pi_sym": "◎",  "bg_sym": "🔮", "bg_name": "Coherence",         "axis": "Evolution"},
]


def gen_biogrid_crosswalk():
    out = []
    for p in BIOGRID_CROSSWALK:
        same_name = p["pi_name"] == p["bg_name"]
        name_note = (
            "The name is shared across both repos."
            if same_name else
            f"Note the name difference: PI calls it **{p['pi_name']}**, "
            f"BioGrid calls it **{p['bg_name']}**. Same principle, different emphasis."
        )

        out.append(msg(
            f"Translate principle {p['id']} between Polyhedral Intelligence and BioGrid2.0.",
            f"**{p['id']}**\n\n"
            f"| | PI | BioGrid2.0 |\n"
            f"|---|---|---|\n"
            f"| Name | {p['pi_name']} | {p['bg_name']} |\n"
            f"| Symbol | `{p['pi_sym']}` | {p['bg_sym']} |\n"
            f"| Axis | — | {p['axis']} |\n\n"
            f"{name_note}"
        ))

    # Name divergences specifically
    divergent = [p for p in BIOGRID_CROSSWALK if p["pi_name"] != p["bg_name"]]
    if divergent:
        div_block = "\n".join(
            f"  {p['id']}: PI **{p['pi_name']}** ↔ BG **{p['bg_name']}**"
            for p in divergent
        )
        out.append(msg(
            "Which principles have different names between PI and BioGrid2.0?",
            f"**Principle name divergences:**\n\n{div_block}\n\n"
            f"These are the same underlying principles but named differently. "
            f"When translating between repos, use the ID (P01-P12) as the stable key."
        ))

    # Axis grouping (BioGrid only)
    axes = {}
    for p in BIOGRID_CROSSWALK:
        axes.setdefault(p["axis"], []).append(p)
    for axis_name, principles in axes.items():
        p_list = ", ".join(f"{p['id']} ({p['bg_name']})" for p in principles)
        out.append(msg(
            f"What principles belong to the '{axis_name}' axis in BioGrid2.0?",
            f"**{axis_name} Axis:**\n{p_list}\n\n"
            f"The 4 axes (Invariance, Transformation, Connectivity, Evolution) "
            f"are a BioGrid2.0 organizational layer. PI uses the dodecahedron "
            f"geometry directly without axis grouping."
        ))

    # Symbol translation
    out.append(msg(
        "How do principle symbols differ between PI and BioGrid2.0?",
        "PI uses **Unicode geometric symbols** (⧖, ↺, ⊗, ◑, etc.) while "
        "BioGrid2.0 uses **emoji** (⚖️, ♻️, 🌀, ⏳, etc.).\n\n"
        "Translation table:\n"
        + "\n".join(
            f"  {p['id']}: `{p['pi_sym']}` (PI) ↔ {p['bg_sym']} (BioGrid)"
            for p in BIOGRID_CROSSWALK
        )
        + "\n\nUse the principle ID (P01-P12) as the stable cross-repo key."
    ))
    return out


# ── Task 18: Entry comparison & pattern analysis ────────────────────────────

def gen_entry_comparison(entries):
    """Compare entries to teach pattern recognition across the atlas."""
    out = []
    if len(entries) < 2:
        return out

    for i, e1 in enumerate(entries):
        for e2 in entries[i+1:]:
            t1, t2 = e1["title"], e2["title"]
            f1 = set(e1.get("resonance_sweep", {}).get("flags", []))
            f2 = set(e2.get("resonance_sweep", {}).get("flags", []))
            shared = f1 & f2
            unique1 = f1 - f2
            unique2 = f2 - f1

            nti1 = e1.get("noise_to_insight", {})
            nti2 = e2.get("noise_to_insight", {})

            # Compare shared flags with different reframes
            shared_reframes = ""
            for flag in shared:
                # Find the symbol key in nti
                for sym in nti1:
                    if sym in flag:
                        r1 = nti1.get(sym, "")
                        r2 = nti2.get(sym, "")
                        if r1 and r2:
                            shared_reframes += f"  `{sym}`: '{t1}' → {r1} | '{t2}' → {r2}\n"

            out.append(msg(
                f"Compare the MRP results for '{t1}' and '{t2}'.",
                f"**{t1}** vs **{t2}**\n\n"
                f"**Shared flags ({len(shared)}):** {', '.join(shared) if shared else 'none'}\n"
                f"**Unique to '{t1}':** {', '.join(unique1) if unique1 else 'none'}\n"
                f"**Unique to '{t2}':** {', '.join(unique2) if unique2 else 'none'}\n\n"
                f"**Same flag, different reframes:**\n{shared_reframes}\n"
                f"This shows how NIP reframes are context-dependent — the same flag "
                f"produces different insights depending on the concept."
            ))
    return out


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Loading data...")
    atlas = load_atlas()
    protocols = load_protocols()
    five_fields = load_five_fields()
    entries = load_entries()
    bridges = load_rosetta_bridges()

    print(f"  Families:   {len(atlas.get('families', []))}")
    print(f"  Principles: {len(atlas.get('principles', []))}")
    print(f"  Entries:    {len(entries)}")
    print(f"  Bridges:    {len(bridges.get('map', []))}")
    print()

    print("Generating training data...")
    # Original 13 tasks
    write_jsonl("family-identification.jsonl",   gen_family_id(atlas))
    write_jsonl("principle-identification.jsonl", gen_principle_id(atlas))
    write_jsonl("glyph-creation.jsonl",           gen_glyph_creation(entries))
    write_jsonl("glyph-decoding.jsonl",           gen_glyph_decode(atlas, entries))
    write_jsonl("family-sweep.jsonl",             gen_family_sweep(entries, atlas))
    write_jsonl("principle-sweep.jsonl",          gen_principle_sweep(entries))
    write_jsonl("noise-to-insight.jsonl",         gen_noise_to_insight(entries))
    write_jsonl("meta-fields.jsonl",              gen_meta_fields(five_fields, atlas))
    write_jsonl("equations.jsonl",                gen_equations(atlas))
    write_jsonl("bridge-mapping.jsonl",           gen_bridge_mapping(bridges))
    write_jsonl("mrp-walkthrough.jsonl",          gen_mrp_walkthrough(entries, atlas))
    write_jsonl("nip-patterns.jsonl",             gen_nip_patterns())
    write_jsonl("keyword-mapping.jsonl",          gen_keyword_mapping())
    # New tasks
    write_jsonl("cross-repo-coactivation.jsonl",  gen_cross_repo_coactivation(entries))
    write_jsonl("ontology-translation.jsonl",     gen_ontology_translation())
    write_jsonl("equation-glyph-compression.jsonl", gen_equation_glyph_compression(atlas))
    write_jsonl("biogrid-crosswalk.jsonl",        gen_biogrid_crosswalk())
    write_jsonl("entry-comparison.jsonl",         gen_entry_comparison(entries))

    print("\nDone.")


if __name__ == "__main__":
    main()
