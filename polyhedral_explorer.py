#!/usr/bin/env python3
# polyhedral_explorer.py — CC0
# Explorer for the Polyhedral Intelligence Mandala (Families + Principles)
#
# Tree-based exploration with branching, backtracking, annotation,
# protocol application (MRP, NIP), and automated experiment suggestion.

import json
import copy
import uuid
import random
from typing import Any, Dict, List, Optional

# ----------------------------------------------------------------------
# Knowledge graph from JSON
# ----------------------------------------------------------------------
class PolyhedralMandala:
    def __init__(self, json_path: str):
        with open(json_path) as f:
            data = json.load(f)
        self.families = {f["id"]: f for f in data["families"]}
        self.principles = {p["id"]: p for p in data["principles"]}
        self.metadata = data.get("metadata", {})
        # Build tag index for cross-referencing
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
# Tree data structures (minimal, same as before)
# ----------------------------------------------------------------------
class BranchState:
    def __init__(self, focus_type: str = "", focus_id: str = ""):
        self.focus_type = focus_type    # "family", "principle", "equation", "none"
        self.focus_id = focus_id
        self.data: Any = None           # e.g. currently selected equation dict
        self.history: List[str] = []
        self.annotations: List[str] = []
        self.params: Dict[str, Any] = {}

    def clone(self):
        s = BranchState(self.focus_type, self.focus_id)
        s.data = copy.deepcopy(self.data)
        s.history = self.history.copy()
        s.annotations = self.annotations.copy()
        s.params = copy.deepcopy(self.params)
        return s

class TreeNode:
    def __init__(self, state: BranchState, choice: str = "root", parent=None, entropy_cost=0.0):
        self.id = str(uuid.uuid4())[:8]
        self.state = state
        self.choice = choice
        self.parent = parent
        self.children: List["TreeNode"] = []
        self.entropy_cost = entropy_cost

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def total_entropy_cost(self):
        return self.entropy_cost + (self.parent.total_entropy_cost() if self.parent else 0)

# ----------------------------------------------------------------------
# Explorer for the Polyhedral Mandala
# ----------------------------------------------------------------------
class MandalaExplorer:
    def __init__(self, json_path: str):
        self.mandala = PolyhedralMandala(json_path)
        self.root = TreeNode(BranchState(), "root")
        self.current = self.root
        self.entropy_budget = 5.0

    def choices(self) -> List[str]:
        """Return possible next actions from the current state."""
        state = self.current.state
        options = []

        # If nothing focused, offer to browse families or principles
        if not state.focus_type:
            options.append("list_families")
            options.append("list_principles")
            options.append("list_protocols")
            options.append("entropy_event")
            options.append("annotate")
        elif state.focus_type in ("family", "principle"):
            # View equations of current focus
            entity = self._get_entity(state.focus_type, state.focus_id)
            for i, eq in enumerate(entity["equations"]):
                options.append(f"view_equation:{eq['name']}")
            options.append("compare_with_tag_overlap")
            options.append("apply_protocol:MRP")
            options.append("apply_protocol:NIP")
            options.append("back_to_root")
            options.append("annotate")
        elif state.focus_type == "equation":
            # Equation selected: view details, apply noise, compare
            options.append("show_details")
            options.append("apply_noise_to_equation")
            options.append("back_to_entity")
            options.append("annotate")
        return options

    def select(self, choice_str: str):
        parts = choice_str.split(":", 1)
        action = parts[0]
        arg = parts[1] if len(parts) > 1 else None

        new_state = self.current.state.clone()
        new_state.history.append(choice_str)
        child = TreeNode(new_state, choice_str, parent=self.current, entropy_cost=0.05)

        if action == "list_families":
            fams = [f"{fid}: {self.mandala.families[fid]['name']}" for fid in self.mandala.families]
            child.annotations.append("Families:\n" + "\n".join(fams))
        elif action == "list_principles":
            prins = [f"{pid}: {self.mandala.principles[pid]['name']}" for pid in self.mandala.principles]
            child.annotations.append("Principles:\n" + "\n".join(prins))
        elif action == "list_protocols":
            child.annotations.append("Protocols: MRP (Mandala Redesign Protocol), NIP (Noise-to-Insight Protocol)")

        elif action.startswith("select_"):
            # select_family:F01 or select_principle:P01
            if action == "select_family":
                if arg in self.mandala.families:
                    new_state.focus_type = "family"
                    new_state.focus_id = arg
                    child.annotations.append(f"Focused on family: {self.mandala.families[arg]['name']}")
            elif action == "select_principle":
                if arg in self.mandala.principles:
                    new_state.focus_type = "principle"
                    new_state.focus_id = arg
                    child.annotations.append(f"Focused on principle: {self.mandala.principles[arg]['name']}")

        elif action == "view_equation":
            # arg is equation name
            entity = self._get_entity(new_state.focus_type, new_state.focus_id)
            eq = next((e for e in entity["equations"] if e["name"] == arg), None)
            if eq:
                new_state.data = eq
                new_state.focus_type = "equation"
                new_state.focus_id = arg
                child.annotations.append(f"Selected equation: {eq['name']}")

        elif action == "show_details":
            if new_state.data:
                eq = new_state.data
                child.annotations.append(f"Name: {eq['name']}\nFormula: {eq['formula']}\nGlyph: {eq['glyph']} ({eq['glyph_name']})\nTags: {eq.get('tags', [])}")

        elif action == "compare_with_tag_overlap":
            # compare current entity with all others by tag overlap
            current_entity = self._get_entity(new_state.focus_type, new_state.focus_id)
            current_tags = set()
            for eq in current_entity["equations"]:
                current_tags.update(eq.get("tags", []))
            # score all other entities (families + principles)
            scores = []
            for other_type, other_dict in [("family", self.mandala.families), ("principle", self.mandala.principles)]:
                for oid, oent in other_dict.items():
                    if oid == new_state.focus_id and other_type == new_state.focus_type:
                        continue
                    other_tags = set()
                    for eq in oent["equations"]:
                        other_tags.update(eq.get("tags", []))
                    overlap = len(current_tags & other_tags)
                    if overlap > 0:
                        scores.append((overlap, other_type, oid, oent["name"]))
            scores.sort(reverse=True)
            if scores:
                lines = ["Tag overlap (most to least):"]
                for s in scores[:5]:
                    lines.append(f"  {s[1]}: {s[3]} ({s[0]} shared tags)")
                child.annotations.append("\n".join(lines))
            else:
                child.annotations.append("No tag overlap with any other entity.")

        elif action == "apply_protocol":
            if arg == "MRP":
                # Mandala Redesign Protocol: generate a synthetic fusion with the top overlapping entity
                current_entity = self._get_entity(new_state.focus_type, new_state.focus_id)
                # find best overlap
                best_overlap = None
                best_score = 0
                for other_type, other_dict in [("family", self.mandala.families), ("principle", self.mandala.principles)]:
                    for oid, oent in other_dict.items():
                        if oid == new_state.focus_id and other_type == new_state.focus_type:
                            continue
                        other_tags = set()
                        for eq in oent["equations"]:
                            other_tags.update(eq.get("tags", []))
                        current_tags = set()
                        for eq in current_entity["equations"]:
                            current_tags.update(eq.get("tags", []))
                        overlap = len(current_tags & other_tags)
                        if overlap > best_score:
                            best_score = overlap
                            best_overlap = (other_type, oid, oent)
                if best_overlap:
                    child.annotations.append(f"MRP: Fusing {current_entity['name']} with {best_overlap[2]['name']} (overlap {best_score} tags)")
                    # create a synthetic equation
                    child.annotations.append("New synthetic glyph: [FUSED_MANDALA]")
                else:
                    child.annotations.append("MRP: No suitable partner found for fusion.")
            elif arg == "NIP":
                # Noise-to-Insight Protocol: add noise to the current equation's parameters
                if new_state.data:
                    eq = new_state.data
                    # conceptual noise: scramble the formula string for insight
                    noisy_formula = eq["formula"] + " + η(t)"
                    child.annotations.append(f"NIP applied to {eq['name']}. Noisy insight: {noisy_formula}")
                else:
                    child.annotations.append("NIP: No equation selected.")

        elif action == "apply_noise_to_equation":
            if new_state.data:
                eq = new_state.data
                # simulate noise by swapping symbols
                noisy = eq["formula"].replace("=", "≈").replace("+", "⊕") + " + ε"
                child.annotations.append(f"Noise injected: {noisy}")
            else:
                child.annotations.append("No equation loaded.")

        elif action == "entropy_event":
            added = float(arg) if arg else 0.2
            child.entropy_cost = added
            child.annotations.append(f"Entropy increased by {added} (now {self.current.total_entropy_cost() + added:.2f})")

        elif action == "back_to_root":
            self.current = self.root
            return
        elif action == "back_to_entity":
            # go back to family/principle from equation
            new_state.focus_type = "family" if new_state.focus_type == "equation" else "principle"  # rough
            # need to know which family/principle we came from; we stored focus_id as equation name, lost entity id. Let's fix: store parent entity id in state.params
            # Instead, we'll just revert to the previous tree node's state.
            if self.current.parent:
                self.current = self.current.parent
                return
        elif action == "annotate":
            child.annotations.append(arg if arg else "manual note")

        self.current.add_child(child)
        self.current = child

    def _get_entity(self, typ, id_):
        if typ == "family":
            return self.mandala.families[id_]
        elif typ == "principle":
            return self.mandala.principles[id_]
        return None

    def backtrack(self, steps=1):
        for _ in range(steps):
            if self.current.parent:
                self.current = self.current.parent

    def annotate(self, text):
        self.current.state.annotations.append(text)

    def suggest_experiments(self) -> List[str]:
        # Propose next steps based on current focus
        state = self.current.state
        suggestions = []
        if state.focus_type in ("family", "principle"):
            suggestions.append("Compare with similar entities via tag overlap")
            suggestions.append("Apply Mandala Redesign Protocol")
        if state.focus_type == "equation":
            suggestions.append("Inject noise into this equation and observe")
        suggestions.append("List all families or principles")
        return suggestions

    def save_branch(self, filepath):
        # simplified serialisation
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
    import sys
    if len(sys.argv) < 2:
        print("Usage: python polyhedral_explorer.py <mandala.json>")
        sys.exit(1)
    exp = MandalaExplorer(sys.argv[1])
    print("Polyhedral Mandala Explorer ready.")
    print("Choices:", exp.choices())
    # Quick demo: select family F01, view an equation, apply NIP
    exp.select("select_family:F01")
    print(exp.choices())
    exp.select("view_equation:Wave Equation (1D Standing Wave)")
    print(exp.current.state.annotations)
    exp.select("apply_protocol:NIP")
    print(exp.current.state.annotations)
    exp.save_branch("polyhedral_tree.json")
    print("Tree saved.")
