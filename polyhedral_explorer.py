#!/usr/bin/env python3
# polyhedral_explorer.py — CC0
# MRP + NIP engine using polyhedral_bridge.py for accurate encoding.

import json, copy, os, uuid, random, math, sys
from typing import Any, Dict, List, Optional, Tuple, Set
from pathlib import Path

# Make the bridge importable (assume script is in repo root, or adjust)
BRIDGE_PATH = Path(__file__).resolve().parent
if str(BRIDGE_PATH) not in sys.path:
    sys.path.insert(0, str(BRIDGE_PATH))

try:
    from polyhedral_bridge import encode, generate_mandala_insight, PolyhedralEncoding
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False

# ----------------------------------------------------------------------
# 1. Load the atlas (unchanged)
# ----------------------------------------------------------------------
class PolyhedralMandala:
    def __init__(self, json_path: str):
        with open(json_path) as f:
            data = json.load(f)
        self.families = {f["id"]: f for f in data["families"]}
        self.principles = {p["id"]: p for p in data["principles"]}
        self.metadata = data.get("metadata", {})
        self.tag_index = {}
        self._build_tag_index()
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
        for fid, ent in self.families.items():
            sym = ent["symbol"]
            if sym not in self.symbol_to_entity:
                self.symbol_to_entity[sym] = ("family", fid)
        for pid, ent in self.principles.items():
            sym = ent["symbol"]
            if sym not in self.symbol_to_entity:
                self.symbol_to_entity[sym] = ("principle", pid)

    def entity_tags(self, typ: str, eid: str) -> Set[str]:
        ent = self.families[eid] if typ == "family" else self.principles[eid]
        tags = set()
        for eq in ent["equations"]:
            tags.update(eq.get("tags", []))
        return tags

# ----------------------------------------------------------------------
# 2. Glyph algebra (unchanged)
# ----------------------------------------------------------------------
class GlyphAlgebra:
    def __init__(self, mandala: PolyhedralMandala):
        self.mandala = mandala
        self.symbols_by_len = sorted(mandala.symbol_to_entity.keys(), key=len, reverse=True)

    def tokenize(self, glyph: str) -> List[Tuple[str, Optional[Tuple[str, str]]]]:
        tokens = []
        i = 0
        while i < len(glyph):
            if glyph[i] in ('➝', '⛓️', '→', ':', '-'):
                i += 1
                continue
            matched = False
            for sym in self.symbols_by_len:
                if glyph[i:].startswith(sym):
                    entity_info = self.mandala.symbol_to_entity.get(sym)
                    tokens.append((sym, entity_info))
                    i += len(sym)
                    matched = True
                    break
            if not matched:
                tokens.append((glyph[i], None))
                i += 1
        return tokens

    def entity_set(self, glyph: str) -> Set[Tuple[str, str]]:
        tokens = self.tokenize(glyph)
        entities = set()
        for _, entity_info in tokens:
            if entity_info is not None:
                entities.add(entity_info)
        return entities

    def similarity(self, glyph1: str, glyph2: str) -> float:
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
# 3. Tree state (unchanged, but now we store encoding data)
# ----------------------------------------------------------------------
class BranchState:
    def __init__(self):
        self.seed = ""
        self.family_resonance = {}
        self.principle_resonance = {}
        self.current_glyph = ""
        self.glyph_library: List[Tuple[str, str]] = []
        self.annotations: List[str] = []
        self.history: List[str] = []
        self.params: Dict[str, Any] = {}
        self.atlas_entry: Dict[str, Any] = {}
        self.encoding = None   # PolyhedralEncoding if bridge used
        self.bridge_draft: Optional[Dict[str, Any]] = None  # generate_mandala_insight() output, if run

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
        s.encoding = copy.deepcopy(self.encoding)
        s.bridge_draft = copy.deepcopy(self.bridge_draft)
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
# 4. Resonance vector function — uses bridge if available
# ----------------------------------------------------------------------
def resonance_vector(seed: str, mandala: PolyhedralMandala) -> Dict[str, Dict[str, float]]:
    if BRIDGE_AVAILABLE:
        try:
            enc = encode(seed)
            # Keys are canonical bridge ids ("FAM:RESONANCE", "PRIN:SYMMETRY"),
            # not the legacy ids ("F01", "P01") mandala.families/principles use.
            # See _load_glyph_maps() for the id-scheme translation used when
            # looking up a glyph symbol from these keys.
            return {
                "families": enc.family_amplitudes_l1,
                "principles": enc.principle_amplitudes_l1,
            }
        except Exception:
            pass
    # Fallback to tag overlap (keys are the legacy F01.../P01... ids)
    return {
        "families": _tag_overlap_resonance(seed, mandala, "family"),
        "principles": _tag_overlap_resonance(seed, mandala, "principle"),
    }


def _load_glyph_maps() -> Tuple[Dict[str, str], Dict[str, str]]:
    """Build {id: glyph} maps covering both legacy ids (F01/P01, as used by
    atlas_schema.json / PolyhedralMandala) and canonical ids (FAM:*/PRIN:*,
    as returned by encode()), so a glyph lookup works regardless of which
    resonance_vector() path produced a given key."""
    fam_glyphs: Dict[str, str] = {}
    prin_glyphs: Dict[str, str] = {}
    ont_dir = BRIDGE_PATH / "ontology"
    fam_path = ont_dir / "families.json"
    prin_path = ont_dir / "principles.json"
    try:
        if fam_path.exists():
            with fam_path.open(encoding="utf-8") as f:
                for fam in json.load(f)["families"]:
                    fam_glyphs[fam["id"]] = fam["glyph"]
                    fam_glyphs[fam["legacy_id"]] = fam["glyph"]
        if prin_path.exists():
            with prin_path.open(encoding="utf-8") as f:
                for prin in json.load(f)["principles"]:
                    prin_glyphs[prin["id"]] = prin["glyph"]
                    prin_glyphs[prin["legacy_id"]] = prin["glyph"]
    except (KeyError, json.JSONDecodeError):
        pass
    return fam_glyphs, prin_glyphs

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

# ----------------------------------------------------------------------
# 5. MRP Explorer with bridge integration
# ----------------------------------------------------------------------
class MRPExplorer:
    def __init__(self, atlas_json_path: str):
        self.mandala = PolyhedralMandala(atlas_json_path)
        self.algebra = GlyphAlgebra(self.mandala)
        self.root = TreeNode(BranchState(), "root")
        self.current = self.root
        self.entropy_budget = 5.0
        self.bridge_used = BRIDGE_AVAILABLE
        self.fam_glyphs, self.prin_glyphs = _load_glyph_maps()

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
            options.append("add_bridge_glyphs")
            options.append("corrective_evolution")
            options.append("mandala_spin_test")
            options.append("record_atlas_entry")
            options.append("save_glyph_to_library")
            options.append("list_glyph_library")
            options.append("compare_glyphs")
            options.append("merge_glyphs")
            options.append("detect_glyph_conflicts")
        options.extend(["list_families", "list_principles", "entropy_event", "annotate"])
        if BRIDGE_AVAILABLE:
            options.append("run_bridge_insight")  # full MRP draft via bridge
        return options

    def select(self, choice_str: str):
        parts = choice_str.split(":", 1)
        action = parts[0]
        arg = parts[1] if len(parts) > 1 else None

        new_state = self.current.state.clone()
        new_state.history.append(choice_str)
        child = TreeNode(new_state, choice_str, parent=self.current, entropy_cost=0.05)

        if action == "set_seed_concept":
            new_state.seed = arg or "untitled"
            child.state.annotations.append(f"Seed: {new_state.seed}")

        elif action == "run_family_sweep":
            vec = resonance_vector(new_state.seed, self.mandala)
            new_state.family_resonance = vec["families"]
            top = sorted(vec["families"].items(), key=lambda x: x[1], reverse=True)[:5]
            child.state.annotations.append("Family Sweep (bridge used: {}):".format(self.bridge_used))
            for fid, score in top:
                child.state.annotations.append(f"  {fid}: {score:.3f}")

        elif action == "run_principle_sweep":
            vec = resonance_vector(new_state.seed, self.mandala)
            new_state.principle_resonance = vec["principles"]
            top = sorted(vec["principles"].items(), key=lambda x: x[1], reverse=True)[:5]
            child.state.annotations.append("Principle Sweep (bridge used: {}):".format(self.bridge_used))
            for pid, score in top:
                child.state.annotations.append(f"  {pid}: {score:.3f}")

        elif action == "generate_seed_glyph":
            if BRIDGE_AVAILABLE and not new_state.current_glyph:
                try:
                    enc = encode(new_state.seed)
                    glyph = enc.glyph_signature
                    new_state.current_glyph = glyph
                    new_state.encoding = enc.to_json() if hasattr(enc, 'to_json') else None
                    child.state.annotations.append(f"Bridge glyph: {glyph}")
                except Exception:
                    # fallback to manual construction
                    self._manual_seed_glyph(new_state, child)
            else:
                self._manual_seed_glyph(new_state, child)

        elif action == "add_bridge_glyphs":
            # Prefer the bridge's own flags (run_bridge_insight already
            # excludes the seed's core drivers from friction — see
            # generate_mandala_insight/_select_flags). Fall back to a raw
            # low-resonance-amplitude heuristic only if run_bridge_insight
            # hasn't been run yet, i.e. there's no bridge draft to accept.
            if new_state.bridge_draft:
                flags = new_state.bridge_draft["resonance_sweep"]["flags"]
                syms = [f.split(" ", 1)[0] for f in flags]
                source = "bridge flags"
            else:
                # low-resonance families, however resonance_vector() keyed them
                # (legacy "F01" or canonical "FAM:*") — try both id schemes.
                low_fam = [fid for fid, sc in new_state.family_resonance.items() if sc < 0.2]
                syms = []
                for fid in low_fam[:3]:
                    sym = self.fam_glyphs.get(fid) or self.mandala.families.get(fid, {}).get("symbol")
                    if sym:
                        syms.append(sym)
                source = "manual heuristic (no bridge draft — run run_bridge_insight to accept the bridge's flags instead)"
            if syms:
                bridge = "".join(syms)
                new_state.current_glyph += f"⛓️{bridge}"
                child.state.annotations.append(f"Bridge added [{source}]: {bridge}")
            else:
                child.state.annotations.append(f"No flagged families [{source}].")

        elif action == "corrective_evolution":
            # Prefer the bridge's own noise_to_insight reframes (accept
            # path). Fall back to the old fixed Turbulence/Uncertainty
            # threshold check (manual override path) only if no bridge
            # draft has been computed yet.
            if new_state.bridge_draft:
                n2i = new_state.bridge_draft.get("noise_to_insight", {})
                if n2i:
                    for sym, insight in n2i.items():
                        new_state.current_glyph += sym
                        child.state.annotations.append(f"Added noise‑glyph {sym} [bridge]: {insight}")
                else:
                    child.state.annotations.append("Bridge draft has no flags to correct.")
            else:
                flags = []
                if new_state.family_resonance.get("FAM:TURBULENCE", 0) < 0.2:
                    flags.append("ᘯᘰ")
                if new_state.principle_resonance.get("PRIN:UNCERTAINTY", 0) < 0.2:
                    flags.append("◧")
                for sym in flags:
                    new_state.current_glyph += sym
                    child.state.annotations.append(f"Added noise‑glyph {sym} [manual heuristic]")

        elif action == "mandala_spin_test":
            fam_ok = sum(1 for s in new_state.family_resonance.values() if s > 0.2)
            prin_ok = sum(1 for s in new_state.principle_resonance.values() if s > 0.2)
            child.state.annotations.append(f"Spin: Families {fam_ok}/{len(new_state.family_resonance)}, Principles {prin_ok}/{len(new_state.principle_resonance)}")

        elif action == "record_atlas_entry":
            entry = {
                "seed": new_state.seed,
                "glyph": new_state.current_glyph,
                "family_resonance": new_state.family_resonance,
                "principle_resonance": new_state.principle_resonance,
                "annotations": new_state.annotations,
            }
            if new_state.encoding:
                entry["bridge_encoding"] = new_state.encoding
            new_state.atlas_entry = entry
            fld = os.environ.get("FIELDLINK_PATH", "./fieldlink_staging")
            os.makedirs(fld, exist_ok=True)
            path = os.path.join(fld, f"{uuid.uuid4().hex[:8]}.json")
            with open(path, "w") as f:
                json.dump(entry, f, indent=2)
            child.state.annotations.append(f"Atlas entry staged: {path}")

        elif action == "run_bridge_insight":
            if BRIDGE_AVAILABLE:
                try:
                    entry = generate_mandala_insight(new_state.seed, name=new_state.seed)
                    # entry is a dict with resonance_sweep, flags, noise_to_insight, etc.
                    child.state.annotations.append("Bridge insight generated:")
                    child.state.annotations.append(json.dumps(entry, indent=2, ensure_ascii=False))
                    # Store it as the atlas entry directly, and keep the raw
                    # draft around so add_bridge_glyphs/corrective_evolution
                    # can act on the bridge's own flags instead of
                    # re-deriving their own heuristic.
                    new_state.atlas_entry = entry
                    new_state.bridge_draft = entry
                    new_state.current_glyph = entry.get("refined_glyph", new_state.current_glyph)
                except Exception as e:
                    child.state.annotations.append(f"Bridge insight failed: {e}")
            else:
                child.state.annotations.append("Bridge not available.")

        # Glyph algebra actions (unchanged)
        elif action == "save_glyph_to_library":
            if arg and ':' in arg:
                name, glyph = arg.split(':', 1)
                new_state.glyph_library.append((name.strip(), glyph.strip()))
            elif arg:
                new_state.glyph_library.append(("unnamed", arg.strip()))
            elif new_state.current_glyph:
                new_state.glyph_library.append(("current", new_state.current_glyph))
                child.state.annotations.append("Saved current glyph.")
        elif action == "list_glyph_library":
            lib = new_state.glyph_library
            if lib:
                child.state.annotations.append("Glyph Library:")
                for i, (n, g) in enumerate(lib):
                    child.state.annotations.append(f"  [{i}] {n}: {g}")
            else:
                child.state.annotations.append("Library empty.")
        elif action == "compare_glyphs":
            g1, g2 = self._two_glyphs(new_state, arg)
            if g1 and g2:
                sim = self.algebra.similarity(g1, g2)
                child.state.annotations.append(f"Similarity({g1}, {g2}) = {sim:.3f}")
            else:
                child.state.annotations.append(
                    "compare_glyphs needs 'glyph1:glyph2', or a single glyph to compare against current_glyph."
                )
        elif action == "merge_glyphs":
            g1, g2 = self._two_glyphs(new_state, arg)
            if g1 and g2:
                merged, conflicts = self.algebra.merge(g1, g2)
                new_state.current_glyph = merged
                child.state.annotations.append(f"Merged: {merged}")
                if conflicts:
                    child.state.annotations.append("Conflicts: " + "; ".join(conflicts))
            else:
                child.state.annotations.append(
                    "merge_glyphs needs 'glyph1:glyph2', or a single glyph to merge with current_glyph."
                )
        elif action == "detect_glyph_conflicts":
            glyph = new_state.current_glyph
            if glyph:
                conflicts = self.algebra.detect_conflicts(glyph)
                if conflicts:
                    child.state.annotations.append("Conflicts: " + "; ".join(conflicts))
                else:
                    child.state.annotations.append("No conflicts.")
            else:
                child.state.annotations.append("No glyph.")

        elif action == "list_families":
            fams = [f"{fid}: {self.mandala.families[fid]['name']}" for fid in self.mandala.families]
            child.state.annotations.append("Families:\n" + "\n".join(fams))
        elif action == "list_principles":
            prins = [f"{pid}: {self.mandala.principles[pid]['name']}" for pid in self.mandala.principles]
            child.state.annotations.append("Principles:\n" + "\n".join(prins))
        elif action == "entropy_event":
            added = float(arg) if arg else 0.2
            child.entropy_cost = added
            child.state.annotations.append(f"Entropy +{added}")
        elif action == "annotate":
            child.state.annotations.append(arg or "note")

        self.current.add_child(child)
        self.current = child

    def _two_glyphs(self, new_state, arg: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """Resolve a 'glyph1:glyph2' arg, or a single glyph compared against
        current_glyph, into a (glyph1, glyph2) pair (either may be None)."""
        if arg and ":" in arg:
            g1, g2 = arg.split(":", 1)
            return g1.strip(), g2.strip()
        if arg:
            return new_state.current_glyph or None, arg.strip()
        return None, None

    def _manual_seed_glyph(self, new_state, child):
        # fallback to top family/principle symbols
        top_fam = max(new_state.family_resonance, key=new_state.family_resonance.get, default="F01")
        top_prin = max(new_state.principle_resonance, key=new_state.principle_resonance.get, default="P01")
        fam_sym = self.mandala.families.get(top_fam, {}).get("symbol", "?")
        prin_sym = self.mandala.principles.get(top_prin, {}).get("symbol", "?")
        glyph = f"{fam_sym}➝{prin_sym}"
        new_state.current_glyph = glyph
        child.state.annotations.append(f"Manual Seed Glyph: {glyph}")

    def backtrack(self, steps=1):
        for _ in range(steps):
            if self.current.parent:
                self.current = self.current.parent

    def suggest_experiments(self):
        return ["Run full bridge insight", "Compare two seed concepts", "Inject entropy and re-test"]

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
# Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python polyhedral_explorer.py <atlas_schema.json> [seed]")
        sys.exit(1)
    exp = MRPExplorer(sys.argv[1])
    seed = sys.argv[2] if len(sys.argv) > 2 else "hexagonal mesh under tidal load"
    print("Bridge available:", exp.bridge_used)
    exp.select(f"set_seed_concept:{seed}")
    exp.select("run_family_sweep")
    exp.select("run_principle_sweep")
    exp.select("generate_seed_glyph")
    exp.select("run_bridge_insight")  # full MRP draft
    for ann in exp.current.state.annotations:
        print(" ", ann)
    exp.save_branch("polyhedral_tree.json")
