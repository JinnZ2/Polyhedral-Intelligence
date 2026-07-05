#!/usr/bin/env python3
# polyhedral_explorer.py — CC0
# MRP + NIP engine for the Polyhedral Intelligence Mandala.
#
# Full 7‑step Mandala Redesign Protocol embedded as an explorable tree.
# Noise‑to‑Insight mappings drive the corrective evolution step.
# Works with or without polyhedral_bridge.py (falls back to tag‑overlap).

import json, copy, os, uuid, random, math, sys
from typing import Any, Dict, List, Optional

# ----------------------------------------------------------------------
# 1. Load the atlas
# ----------------------------------------------------------------------
class PolyhedralMandala:
    def __init__(self, json_path: str):
        with open(json_path) as f:
            data = json.load(f)
        self.families = {f["id"]: f for f in data["families"]}
        self.principles = {p["id"]: p for p in data["principles"]}
        self.metadata = data.get("metadata", {})
        self.tag_index = {}
        for fid, fam in self.families.items():
            for eq in fam["equations"]:
                for tag in eq.get("tags", []):
                    self.tag_index.setdefault(tag, []).append(("family", fid, eq["name"]))
        for pid, prin in self.principles.items():
            for eq in prin["equations"]:
                for tag in eq.get("tags", []):
                    self.tag_index.setdefault(tag, []).append(("principle", pid, eq["name"]))

# ----------------------------------------------------------------------
# 2. Bridge encoder (optional real, always a tag‑overlap fallback)
# ----------------------------------------------------------------------
try:
    from polyhedral_bridge import encode_mandala_vector
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False

def _tag_overlap_resonance(entity_text: str, mandala: PolyhedralMandala, typ: str) -> Dict[str, float]:
    """Poor‑man's resonance: measure how many tags are mentioned in the text."""
    text_lower = entity_text.lower()
    scores = {}
    collection = mandala.families if typ == "family" else mandala.principles
    for eid, ent in collection.items():
        tags = set()
        for eq in ent["equations"]:
            tags.update(tag.lower() for tag in eq.get("tags", []))
        overlap = sum(1 for tag in tags if tag in text_lower)
        scores[eid] = overlap / (1 + len(tags))  # normalised
    return scores

def resonance_vector(seed: str, mandala: PolyhedralMandala) -> Dict[str, Dict[str, float]]:
    if BRIDGE_AVAILABLE:
        try:
            fam_vec, prin_vec = encode_mandala_vector(seed)
            # Assume encode_mandala_vector returns dicts {id: score} for families and principles
            return {"families": fam_vec, "principles": prin_vec}
        except Exception:
            pass
    return {
        "families": _tag_overlap_resonance(seed, mandala, "family"),
        "principles": _tag_overlap_resonance(seed, mandala, "principle"),
    }

# ----------------------------------------------------------------------
# 3. Tree data structures (same as before)
# ----------------------------------------------------------------------
class BranchState:
    def __init__(self):
        self.seed = ""              # original seed concept
        self.family_resonance = {}  # {Fxx: score}
        self.principle_resonance = {}
        self.current_glyph = ""     # evolving glyph string
        self.annotations: List[str] = []
        self.history: List[str] = []
        self.params: Dict[str, Any] = {}
        self.atlas_entry: Dict[str, Any] = {}  # final entry to save

    def clone(self):
        s = BranchState()
        s.seed = self.seed
        s.family_resonance = copy.deepcopy(self.family_resonance)
        s.principle_resonance = copy.deepcopy(self.principle_resonance)
        s.current_glyph = self.current_glyph
        s.annotations = self.annotations.copy()
        s.history = self.history.copy()
        s.params = copy.deepcopy(self.params)
        s.atlas_entry = copy.deepcopy(self.atlas_entry)
        return s

class TreeNode:
    def __init__(self, state: BranchState, choice="root", parent=None, entropy_cost=0.0):
        self.id = str(uuid.uuid4())[:8]
        self.state = state
        self.choice = choice
        self.parent = parent
        self.children: List[TreeNode] = []
        self.entropy_cost = entropy_cost

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def total_entropy_cost(self):
        return self.entropy_cost + (self.parent.total_entropy_cost() if self.parent else 0)

# ----------------------------------------------------------------------
# 4. MRP Explorer
# ----------------------------------------------------------------------
class MRPExplorer:
    def __init__(self, atlas_json_path: str):
        self.mandala = PolyhedralMandala(atlas_json_path)
        self.root = TreeNode(BranchState(), "root")
        self.current = self.root
        self.entropy_budget = 5.0

    def choices(self) -> List[str]:
        state = self.current.state
        options = []
        if not state.seed:
            options.append("set_seed_concept")
            options.append("list_families")
            options.append("list_principles")
            options.append("entropy_event")
            options.append("annotate")
        elif not state.family_resonance:
            options.append("run_family_sweep")
        elif not state.principle_resonance:
            options.append("run_principle_sweep")
        elif not state.current_glyph:
            options.append("generate_seed_glyph")
        else:
            # We have glyph and both sweeps; next steps:
            options.append("add_bridge_glyphs")
            options.append("corrective_evolution")
            options.append("mandala_spin_test")
            options.append("record_atlas_entry")
            options.append("apply_noise_insight")
            options.append("annotate")
        return options

    def select(self, choice_str: str):
        parts = choice_str.split(":", 1)
        action = parts[0]
        arg = parts[1] if len(parts) > 1 else None

        new_state = self.current.state.clone()
        new_state.history.append(choice_str)
        child = TreeNode(new_state, choice_str, parent=self.current, entropy_cost=0.05)

        if action == "set_seed_concept":
            # arg is the seed concept text; in interactive mode we'd prompt, here we use arg
            if arg:
                new_state.seed = arg
                child.annotations.append(f"Seed concept set: '{arg}'")
            else:
                child.annotations.append("Seed concept required. Use set_seed_concept:<text>")

        elif action == "run_family_sweep":
            if new_state.seed:
                vec = resonance_vector(new_state.seed, self.mandala)
                new_state.family_resonance = vec["families"]
                sorted_scores = sorted(vec["families"].items(), key=lambda x: x[1], reverse=True)
                top5 = sorted_scores[:5]
                child.annotations.append("Family Sweep (top 5):")
                for fid, score in top5:
                    child.annotations.append(f"  {fid} {self.mandala.families[fid]['name']}: {score:.3f}")
            else:
                child.annotations.append("No seed concept. Set one first.")

        elif action == "run_principle_sweep":
            if new_state.seed:
                vec = resonance_vector(new_state.seed, self.mandala)
                new_state.principle_resonance = vec["principles"]
                sorted_scores = sorted(vec["principles"].items(), key=lambda x: x[1], reverse=True)
                top5 = sorted_scores[:5]
                child.annotations.append("Principle Sweep (top 5):")
                for pid, score in top5:
                    child.annotations.append(f"  {pid} {self.mandala.principles[pid]['name']}: {score:.3f}")
            else:
                child.annotations.append("No seed concept. Set one first.")

        elif action == "generate_seed_glyph":
            # Build a glyph from the highest‑resonance family and principle symbols
            top_fam = max(new_state.family_resonance, key=lambda k: new_state.family_resonance[k], default="F01")
            top_prin = max(new_state.principle_resonance, key=lambda k: new_state.principle_resonance[k], default="P01")
            fam_symbol = self.mandala.families[top_fam]["symbol"]
            prin_symbol = self.mandala.principles[top_prin]["symbol"]
            glyph = f"{fam_symbol}➝{prin_symbol}"
            new_state.current_glyph = glyph
            child.annotations.append(f"Seed Glyph: {glyph}")

        elif action == "add_bridge_glyphs":
            # Find families with zero or low resonance and add bridge symbols
            low_families = [fid for fid, score in new_state.family_resonance.items() if score < 0.2]
            bridge_glyphs = [self.mandala.families[fid]["symbol"] for fid in low_families[:3]]
            if bridge_glyphs:
                bridge_str = "".join(bridge_glyphs)
                new_state.current_glyph += f"⛓️{bridge_str}"
                child.annotations.append(f"Bridge glyphs added: {bridge_str}")
            else:
                child.annotations.append("No low‑resonance families need bridging.")

        elif action == "corrective_evolution":
            # Apply NIP to turbulence/uncertainty flags
            # Scan for negative resonance in families associated with noise (turbulence F17, Uncertainty P10)
            flags = []
            if new_state.family_resonance.get("F17", 0) < 0.2:
                flags.append(("Turbulence", "ᘯᘰ"))
            if new_state.principle_resonance.get("P10", 0) < 0.2:
                flags.append(("Uncertainty", "◧"))
            if flags:
                # Add corrective glyphs
                for name, sym in flags:
                    new_state.current_glyph += sym
                    child.annotations.append(f"Corrective evolution: added {name} noise‑glyph {sym}")
            else:
                child.annotations.append("No instability flags detected. Glyph stable.")

        elif action == "mandala_spin_test":
            # Visualise balance across families and principles (text summary)
            fam_balanced = sum(1 for s in new_state.family_resonance.values() if s > 0.2)
            prin_balanced = sum(1 for s in new_state.principle_resonance.values() if s > 0.2)
            child.annotations.append(f"Mandala Spin Test: Families {fam_balanced}/20, Principles {prin_balanced}/12 balanced")
            child.annotations.append(f"Current Glyph: {new_state.current_glyph}")

        elif action == "record_atlas_entry":
            entry = {
                "seed": new_state.seed,
                "glyph": new_state.current_glyph,
                "family_resonance": new_state.family_resonance,
                "principle_resonance": new_state.principle_resonance,
                "annotations": new_state.annotations,
                "protocol_version": "1.0.0",
            }
            new_state.atlas_entry = entry
            child.annotations.append("Atlas entry recorded.")
            # Optionally stage for fieldlink
            fieldlink_dir = os.environ.get("FIELDlink_PATH", "./fieldlink_staging")
            os.makedirs(fieldlink_dir, exist_ok=True)
            entry_path = os.path.join(fieldlink_dir, f"{uuid.uuid4().hex[:8]}.json")
            with open(entry_path, "w") as f:
                json.dump(entry, f, indent=2)
            child.annotations.append(f"Staged for fieldlink at {entry_path}")

        elif action == "apply_noise_insight":
            # Convert known noise signatures into insight
            signatures = self.mandala.metadata.get("noise_signatures", [])
            if signatures:
                child.annotations.append("Noise‑to‑Insight applied:")
                for sig in signatures:
                    child.annotations.append(f"  {sig}")
            else:
                child.annotations.append("No noise signatures found in metadata.")

        elif action == "list_families":
            fams = [f"{fid}: {self.mandala.families[fid]['name']}" for fid in self.mandala.families]
            child.annotations.append("Families:\n" + "\n".join(fams))
        elif action == "list_principles":
            prins = [f"{pid}: {self.mandala.principles[pid]['name']}" for pid in self.mandala.principles]
            child.annotations.append("Principles:\n" + "\n".join(prins))
        elif action == "entropy_event":
            added = float(arg) if arg else 0.2
            child.entropy_cost = added
            child.annotations.append(f"Entropy increased by {added}.")
        elif action == "annotate":
            child.annotations.append(arg if arg else "manual note")

        self.current.add_child(child)
        self.current = child

    def backtrack(self, steps=1):
        for _ in range(steps):
            if self.current.parent:
                self.current = self.current.parent

    def suggest_experiments(self):
        return [
            "Run full MRP pipeline on a new seed concept",
            "Compare resonance of two seeds",
            "Inject entropy and re‑test spin balance",
        ]

    def save_branch(self, filepath):
        def node_to_dict(node):
            return {
                "id": node.id,
                "choice": node.choice,
                "annotations": node.state.annotations,
                "entropy_cost": node.entropy_cost,
                "children": [node_to_dict(c) for c in node.children]
            }
        with open(filepath, 'w') as f:
            json.dump(node_to_dict(self.root), f, indent=2)

# ----------------------------------------------------------------------
# Demo: run the full MRP pipeline on a seed concept
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python polyhedral_explorer.py <atlas_index.json> [seed concept]")
        sys.exit(1)
    explorer = MRPExplorer(sys.argv[1])
    seed = sys.argv[2] if len(sys.argv) > 2 else "hexagonal mesh under tidal load"
    print("Seed:", seed)
    explorer.select(f"set_seed_concept:{seed}")
    explorer.select("run_family_sweep")
    explorer.select("run_principle_sweep")
    explorer.select("generate_seed_glyph")
    explorer.select("add_bridge_glyphs")
    explorer.select("corrective_evolution")
    explorer.select("mandala_spin_test")
    explorer.select("record_atlas_entry")
    # Show full annotations
    for ann in explorer.current.state.annotations:
        print("  ", ann)
    explorer.save_branch("mrp_tree.json")
    print("MRP pipeline tree saved.")
