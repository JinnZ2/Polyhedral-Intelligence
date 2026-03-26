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

    print("\nDone.")


if __name__ == "__main__":
    main()
