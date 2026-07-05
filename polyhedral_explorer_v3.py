#!/usr/bin/env python3
# polyhedral_explorer.py — CC0
# MRP + NIP engine with first‑class glyph algebra (compare, merge, conflict‑detect)
#
# Full 7‑step Mandala Redesign Protocol embedded as an explorable tree,
# plus glyph tokenization, similarity, merging, and conflict analysis.

import json, copy, os, uuid, random, math, sys
from typing import Any, Dict, List, Optional, Tuple, Set

# ----------------------------------------------------------------------
# 1. Load the atlas (add symbol->entity mapping)
# ----------------------------------------------------------------------
class PolyhedralMandala:
    def __init__(self, json_path: str):
        with open(json_path) as f:
            data = json.load(f)
        self.families = {f["id"]: f for f in data["families"]}
        self.principles = {p["id"]: p for p in data["principles"]}
        self.metadata = data.get("metadata", {})
        # Build tag index for entity comparison
        self.tag_index = {}
        self._build_tag_index()
        # Build symbol->entity mapping (longest match)
        self.symbol_to_entity = {}
        self._build_symbol_map()

    def _build_tag_index(self):
        self.tag_index = {}
        for fid, fam in self.families.items():
            for eq in fam["equations"]:
                for tag in eq.get("tags", []):
                    self.tag_index.setdefault(tag, []).append(("family", fid, eq["name"]))
        for pid, prin in self.principles.items():
            for eq in prin["equations"]:
                for tag in eq.get("tags", []):
                    self.tag_index.setdefault(tag, []).append(("principle", pid, eq["name"]))

    def _build_symbol_map(self):
        # For each family/principle, its "symbol" field is a string that may be multi‑character.
        # We'll map each unique symbol to the entity id. If multiple entities share a symbol, we keep the first.
        for fid, ent in self.families.items():
            sym = ent["symbol"]
            if sym not in self.symbol_to_entity:
                self.symbol_to_entity[sym] = ("family", fid)
        for pid, ent in self.principles.items():
            sym = ent["symbol"]
            if sym not in self.symbol_to_entity:
                self.symbol_to_entity[sym] = ("principle", pid)

    def entity_tags(self, typ: str, eid: str) -> Set[str]:
        """Return the set of all tags for a given entity (family/principle)."""
        ent = self.families[eid] if typ == "family" else self.principles[eid]
        tags = set()
        for eq in ent["equations"]:
            tags.update(eq.get("tags", []))
        return tags

# ----------------------------------------------------------------------
# 2. Glyph tokenizer and algebra
# ----------------------------------------------------------------------
class GlyphAlgebra:
    def __init__(self, mandala: PolyhedralMandala):
        self.mandala = mandala
        # Build a sorted list of known symbol strings by length descending for greedy matching
        self.symbols_by_len = sorted(mandala.symbol_to_entity.keys(), key=len, reverse=True)

    def tokenize(self, glyph: str) -> List[Tuple[str, Optional[Tuple[str, str]]]]:
        """
        Break a glyph string into a list of (symbol_str, entity_info) tokens.
        entity_info is (type, id) if recognized, else None.
        Delimiter characters like '➝', '⛓️' are treated as connectors and ignored.
        """
        tokens = []
        i = 0
        while i < len(glyph):
            # Skip connector chars
            if glyph[i] in ('➝', '⛓️', '→', ':', '-'):
                i += 1
                continue
            # Try longest known symbol
            matched = False
            for sym in self.symbols_by_len:
                if glyph[i:].startswith(sym):
                    entity_info = self.mandala.symbol_to_entity.get(sym)
                    tokens.append((sym, entity_info))
                    i += len(sym)
                    matched = True
                    break
            if not matched:
                # unknown character, keep as is
                tokens.append((glyph[i], None))
                i += 1
        return tokens

    def entity_set(self, glyph: str) -> Set[Tuple[str, str]]:
        """Return the set of unique (type, id) entities present in the glyph."""
        tokens = self.tokenize(glyph)
        entities = set()
        for _, entity_info in tokens:
            if entity_info is not None:
                entities.add(entity_info)
        return entities

    def similarity(self, glyph1: str, glyph2: str) -> float:
        """Jaccard similarity of entity sets."""
        set1 = self.entity_set(glyph1)
        set2 = self.entity_set(glyph2)
        if not set1 and not set2:
            return 1.0
        intersection = set1 & set2
        union = set1 | set2
        if not union:
            return 0.0
        return len(intersection) / len(union)

    def merge(self, glyph1: str, glyph2: str, bridge_connector: str = '⛓️') -> Tuple[str, List[str]]:
        """
        Merge two glyphs into a combined glyph.
        Returns (merged_glyph, conflict_list).
        Conflicts are detected as entity pairs (one from each glyph) that share zero tags.
        """
        merged = f"{glyph1}{bridge_connector}{glyph2}"
        set1 = self.entity_set(glyph1)
        set2 = self.entity_set(glyph2)
        conflicts = []
        for e1 in set1:
            tags1 = self.mandala.entity_tags(e1[0], e1[1])
            for e2 in set2:
                if e1 == e2:
                    continue
                tags2 = self.mandala.entity_tags(e2[0], e2[1])
                overlap = tags1 & tags2
                if not overlap:
                    conflicts.append(f"{e1[0][:4]}:{e1[1]} vs {e2[0][:4]}:{e2[1]} (zero tag overlap)")
        return merged, conflicts

    def detect_conflicts(self, glyph: str) -> List[str]:
        """Scan a single glyph for internal conflicts between any two entities."""
        entities = list(self.entity_set(glyph))
        conflicts = []
        for i in range(len(entities)):
            tags_i = self.mandala.entity_tags(entities[i][0], entities[i][1])
            for j in range(i + 1, len(entities)):
                tags_j = self.mandala.entity_tags(entities[j][0], entities[j][1])
                if not (tags_i & tags_j):
                    conflicts.append(f"{entities[i][0][:4]}:{entities[i][1]} vs {entities[j][0][:4]}:{entities[j][1]} (no shared tags)")
        return conflicts

# ----------------------------------------------------------------------
# 3. Tree state – extended with glyph library
# ----------------------------------------------------------------------
class BranchState:
    def __init__(self):
        self.seed = ""
        self.family_resonance = {}
        self.principle_resonance = {}
        self.current_glyph = ""
        self.glyph_library: List[Tuple[str, str]] = []  # (name, glyph_string)
        self.annotations: List[str] = []
        self.history: List[str] = []
        self.params: Dict[str, Any] = {}
        self.atlas_entry: Dict[str, Any] = {}

    def clone(self):
        s = BranchState()
        s.seed = self.seed
        s.family_resonance = copy.deepcopy(self.family_resonance)
        s.principle_resonance = copy.deepcopy(self.principle_resonance)
        s.current_glyph = self.current_glyph
        s.glyph_library = self.glyph_library.copy()
        s.annotations = self.annotations.copy()
        s.history = self.history.copy()
        s.params = copy.deepcopy(self.params)
        s.atlas_entry = copy.deepcopy(self.atlas_entry)
        return s

class TreeNode:
    def __init__(self, state, choice="root", parent=None, entropy_cost=0.0):
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
# 4. MRP Explorer with glyph algebra
# ----------------------------------------------------------------------
class MRPExplorer:
    def __init__(self, atlas_json_path: str):
        self.mandala = PolyhedralMandala(atlas_json_path)
        self.algebra = GlyphAlgebra(self.mandala)
        self.root = TreeNode(BranchState(), "root")
        self.current = self.root
        self.entropy_budget = 5.0

    def choices(self) -> List[str]:
        state = self.current.state
        options = []
        if not state.seed:
            options.append("set_seed_concept")
        elif not state.family_resonance:
            options.append("run_family_sweep")
        elif not state.principle_resonance:
            options.append("run_principle_sweep")
        elif not state.current_glyph:
            options.append("generate_seed_glyph")
        else:
            # MRP steps
            options.append("add_bridge_glyphs")
            options.append("corrective_evolution")
            options.append("mandala_spin_test")
            options.append("record_atlas_entry")
            # Glyph algebra actions
            options.append("save_glyph_to_library")
            options.append("list_glyph_library")
            options.append("compare_glyphs")
            options.append("merge_glyphs")
            options.append("detect_glyph_conflicts")
        # Always available
        options.extend(["list_families", "list_principles", "entropy_event", "annotate"])
        return options

    def select(self, choice_str: str):
        parts = choice_str.split(":", 1)
        action = parts[0]
        arg = parts[1] if len(parts) > 1 else None

        new_state = self.current.state.clone()
        new_state.history.append(choice_str)
        child = TreeNode(new_state, choice_str, parent=self.current, entropy_cost=0.05)

        # ---- Core MRP steps ----
        if action == "set_seed_concept":
            new_state.seed = arg or "untitled"
            child.annotations.append(f"Seed: {new_state.seed}")

        elif action == "run_family_sweep":
            vec = resonance_vector(new_state.seed, self.mandala)
            new_state.family_resonance = vec["families"]
            top = sorted(vec["families"].items(), key=lambda x: x[1], reverse=True)[:5]
            child.annotations.append("Family Sweep (top 5):")
            for fid, score in top:
                child.annotations.append(f"  {fid} {self.mandala.families[fid]['name']}: {score:.3f}")

        elif action == "run_principle_sweep":
            vec = resonance_vector(new_state.seed, self.mandala)
            new_state.principle_resonance = vec["principles"]
            top = sorted(vec["principles"].items(), key=lambda x: x[1], reverse=True)[:5]
            child.annotations.append("Principle Sweep (top 5):")
            for pid, score in top:
                child.annotations.append(f"  {pid} {self.mandala.principles[pid]['name']}: {score:.3f}")

        elif action == "generate_seed_glyph":
            top_fam = max(new_state.family_resonance, key=new_state.family_resonance.get, default="F01")
            top_prin = max(new_state.principle_resonance, key=new_state.principle_resonance.get, default="P01")
            fam_sym = self.mandala.families[top_fam]["symbol"]
            prin_sym = self.mandala.principles[top_prin]["symbol"]
            glyph = f"{fam_sym}➝{prin_sym}"
            new_state.current_glyph = glyph
            child.annotations.append(f"Seed Glyph: {glyph}")

        elif action == "add_bridge_glyphs":
            low_fam = [fid for fid, sc in new_state.family_resonance.items() if sc < 0.2]
            syms = [self.mandala.families[fid]["symbol"] for fid in low_fam[:3]]
            if syms:
                bridge = "".join(syms)
                new_state.current_glyph += f"⛓️{bridge}"
                child.annotations.append(f"Bridge added: {bridge}")
            else:
                child.annotations.append("No low‑resonance families.")

        elif action == "corrective_evolution":
            flags = []
            if new_state.family_resonance.get("F17", 0) < 0.2:
                flags.append(("Turbulence", "ᘯᘰ"))
            if new_state.principle_resonance.get("P10", 0) < 0.2:
                flags.append(("Uncertainty", "◧"))
            for name, sym in flags:
                new_state.current_glyph += sym
                child.annotations.append(f"Added {name} noise‑glyph {sym}")

        elif action == "mandala_spin_test":
            fam_ok = sum(1 for s in new_state.family_resonance.values() if s > 0.2)
            prin_ok = sum(1 for s in new_state.principle_resonance.values() if s > 0.2)
            child.annotations.append(f"Spin: Families {fam_ok}/20, Principles {prin_ok}/12")

        elif action == "record_atlas_entry":
            entry = {
                "seed": new_state.seed,
                "glyph": new_state.current_glyph,
                "family_resonance": new_state.family_resonance,
                "principle_resonance": new_state.principle_resonance,
                "annotations": new_state.annotations,
            }
            new_state.atlas_entry = entry
            fld = os.environ.get("FIELDLINK_PATH", "./fieldlink_staging")
            os.makedirs(fld, exist_ok=True)
            path = os.path.join(fld, f"{uuid.uuid4().hex[:8]}.json")
            with open(path, "w") as f:
                json.dump(entry, f, indent=2)
            child.annotations.append(f"Atlas entry staged: {path}")

        # ---- Glyph algebra actions ----
        elif action == "save_glyph_to_library":
            # arg = name:glyph_string (e.g., "test:◇⚙➝〰〰〰⬡")
            if arg and ':' in arg:
                name, glyph = arg.split(':', 1)
                new_state.glyph_library.append((name.strip(), glyph.strip()))
                child.annotations.append(f"Saved '{name}' to library.")
            elif arg:
                new_state.glyph_library.append(("unnamed", arg.strip()))
                child.annotations.append("Saved unnamed glyph.")
            else:
                # save current glyph with default name
                if new_state.current_glyph:
                    new_state.glyph_library.append(("current", new_state.current_glyph))
                    child.annotations.append("Saved current glyph as 'current'.")

        elif action == "list_glyph_library":
            lib = new_state.glyph_library
            if lib:
                child.annotations.append("Glyph Library:")
                for i, (name, g) in enumerate(lib):
                    child.annotations.append(f"  [{i}] {name}: {g}")
            else:
                child.annotations.append("Library empty.")

        elif action == "compare_glyphs":
            # arg can be "0,1" to compare library indices, or two glyph strings separated by ';'
            if arg:
                try:
                    if ',' in arg:
                        i, j = map(int, arg.split(','))
                        g1 = new_state.glyph_library[i][1]
                        g2 = new_state.glyph_library[j][1]
                    elif ';' in arg:
                        g1, g2 = arg.split(';', 1)
                    else:
                        raise ValueError
                    sim = self.algebra.similarity(g1, g2)
                    child.annotations.append(f"Similarity: {sim:.3f}")
                    child.annotations.append(f"Glyph 1: {g1}")
                    child.annotations.append(f"Glyph 2: {g2}")
                except:
                    child.annotations.append("Usage: compare_glyphs:0,1 or compare_glyphs:glyph1;glyph2")
            else:
                # compare current glyph with first library entry if available
                if new_state.glyph_library and new_state.current_glyph:
                    g1 = new_state.current_glyph
                    g2 = new_state.glyph_library[0][1]
                    sim = self.algebra.similarity(g1, g2)
                    child.annotations.append(f"Current vs library[0]: {sim:.3f}")
                else:
                    child.annotations.append("Need two glyphs to compare.")

        elif action == "merge_glyphs":
            if arg:
                try:
                    if ',' in arg:
                        i, j = map(int, arg.split(','))
                        g1 = new_state.glyph_library[i][1]
                        g2 = new_state.glyph_library[j][1]
                    elif ';' in arg:
                        g1, g2 = arg.split(';', 1)
                    else:
                        raise ValueError
                    merged, conflicts = self.algebra.merge(g1, g2)
                    child.annotations.append(f"Merged: {merged}")
                    if conflicts:
                        child.annotations.append("Conflicts:")
                        for c in conflicts:
                            child.annotations.append(f"  {c}")
                    # store merged as current glyph
                    new_state.current_glyph = merged
                except:
                    child.annotations.append("Usage: merge_glyphs:0,1 or merge_glyphs:glyph1;glyph2")
            else:
                child.annotations.append("Provide two glyphs to merge.")

        elif action == "detect_glyph_conflicts":
            glyph = new_state.current_glyph
            if glyph:
                conflicts = self.algebra.detect_conflicts(glyph)
                if conflicts:
                    child.annotations.append("Internal conflicts detected:")
                    for c in conflicts:
                        child.annotations.append(f"  {c}")
                else:
                    child.annotations.append("No internal conflicts found.")
            else:
                child.annotations.append("No glyph to analyze.")

        # ---- Meta ----
        elif action == "list_families":
            fams = [f"{fid}: {self.mandala.families[fid]['name']}" for fid in self.mandala.families]
            child.annotations.append("Families:\n" + "\n".join(fams))
        elif action == "list_principles":
            prins = [f"{pid}: {self.mandala.principles[pid]['name']}" for pid in self.mandala.principles]
            child.annotations.append("Principles:\n" + "\n".join(prins))
        elif action == "entropy_event":
            added = float(arg) if arg else 0.2
            child.entropy_cost = added
            child.annotations.append(f"Entropy +{added}")
        elif action == "annotate":
            child.annotations.append(arg or "note")

        self.current.add_child(child)
        self.current = child

    def backtrack(self, steps=1):
        for _ in range(steps):
            if self.current.parent:
                self.current = self.current.parent

    def suggest_experiments(self):
        return [
            "Merge two glyphs from the library",
            "Compare glyph similarity",
            "Detect conflicts in a complex glyph",
            "Run full MRP on a new seed",
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
# Resonance helper (tag overlap fallback)
# ----------------------------------------------------------------------
def _tag_overlap_resonance(text: str, mandala: PolyhedralMandala, typ: str) -> Dict[str, float]:
    text = text.lower()
    scores = {}
    collection = mandala.families if typ == "family" else mandala.principles
    for eid, ent in collection.items():
        tags = set()
        for eq in ent["equations"]:
            tags.update(tag.lower() for tag in eq.get("tags", []))
        overlap = sum(1 for tag in tags if tag in text)
        scores[eid] = overlap / (1 + len(tags)) if tags else 0.0
    return scores

def resonance_vector(seed: str, mandala: PolyhedralMandala) -> Dict[str, Dict[str, float]]:
    # try real bridge if available, else fallback
    try:
        from polyhedral_bridge import encode_mandala_vector
        fam, prin = encode_mandala_vector(seed)
        return {"families": fam, "principles": prin}
    except:
        return {
            "families": _tag_overlap_resonance(seed, mandala, "family"),
            "principles": _tag_overlap_resonance(seed, mandala, "principle")
        }

# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python polyhedral_explorer.py <atlas_index.json> [seed]")
        sys.exit(1)
    exp = MRPExplorer(sys.argv[1])
    seed = sys.argv[2] if len(sys.argv) > 2 else "hexagonal mesh under tidal load"
    print("Seed:", seed)
    exp.select(f"set_seed_concept:{seed}")
    exp.select("run_family_sweep")
    exp.select("run_principle_sweep")
    exp.select("generate_seed_glyph")
    exp.select("add_bridge_glyphs")
    exp.select("corrective_evolution")
    exp.select("mandala_spin_test")
    print("Glyph:", exp.current.state.current_glyph)
    # save to library
    exp.select("save_glyph_to_library:current")
    # create a second glyph manually and merge
    exp.select("set_seed_concept:turbulent plasma containment")
    exp.select("run_family_sweep")
    exp.select("run_principle_sweep")
    exp.select("generate_seed_glyph")
    exp.select("add_bridge_glyphs")
    exp.select("corrective_evolution")
    exp.select("save_glyph_to_library:plasma_test")
    # merge the two stored glyphs
    exp.select("merge_glyphs:0,1")
    print("Merged glyph:", exp.current.state.current_glyph)
    exp.select("detect_glyph_conflicts")
    for ann in exp.current.state.annotations:
        print(" ", ann)
    exp.save_branch("glyph_algebra_tree.json")
    print("Tree saved.")
