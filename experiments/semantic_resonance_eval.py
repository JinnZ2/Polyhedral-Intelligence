# SPDX-License-Identifier: CC0-1.0
"""Probe for #1 (keyword matching vs semantic understanding).

Claim under test: keyword matching misses semantic neighbors — e.g.
"parametric amplification in nonlinear optical fibers" should resonate
with FAM:RESONANCE even without the literal words "resonance"/"frequency",
and "heat death of the universe" vs "heat treating steel" should land in
different families despite sharing the word "heat".

This measures, on a labeled eval set (including the exact adversarial
cases from the critique), the accuracy of:
  (a) the current hand-curated keyword list (polyhedral_bridge._FAMILY_KEYWORDS)
  (b) a zero-new-dependency alternative: an auto-derived corpus per family
      from ontology/families.json's own description/physics_domains/
      exemplars fields, scored by token overlap instead of a fixed list.

(b) is NOT a semantic embedding — it's still lexical overlap — but it
tests whether a *broader, auto-derived* lexicon closes some of the gap
before reaching for a heavier dependency (sentence embeddings), which
needs its own follow-up experiment and a real dependency-addition
decision (this repo currently has zero third-party dependencies).

Run: python experiments/semantic_resonance_eval.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from polyhedral_bridge import _FAMILY_KEYWORDS, encode  # noqa: E402

# (seed text, expected top family, note). Includes the exact adversarial
# cases from the critique plus paraphrased (non-literal-keyword) restatements
# of several family domains, to probe recall beyond the curated list.
EVAL_SET: list[tuple[str, str, str]] = [
    # --- exact cases from the critique ---
    ("parametric amplification in nonlinear optical fibers", "FAM:RESONANCE",
     "critique case: a resonance phenomenon with no literal 'resonance'/'frequency' wording"),
    ("heat death of the universe", "FAM:ENERGY_THERMO",
     "critique case: thermodynamic, not engineering, despite similarity to next case"),
    ("heat treating steel", "FAM:ENGINEERING",
     "critique case: materials engineering, must NOT collapse onto the same answer as heat death"),
    # --- paraphrased, non-literal restatements of other family domains ---
    ("two pendulum clocks mounted on the same wall gradually fall into step", "FAM:RESONANCE",
     "Huygens synchronization, no literal resonance/harmonic keyword"),
    ("a river bending around a boulder leaves a trailing spiral of eddies", "FAM:FLOW",
     "vorticity described without the word 'vorticity' or 'turbulence'"),
    ("compressing a message so it takes the fewest bits to transmit", "FAM:INFORMATION",
     "entropy/coding without saying 'entropy' or 'shannon'"),
    ("a population of rabbits and foxes cycling between boom and bust", "FAM:LIFE",
     "Lotka-Volterra without 'ecology'/'population'/'growth'"),
    ("a satellite year on a distant moon", "FAM:EARTH_COSMOS",
     "orbital mechanics without 'orbit'/'gravity'/'planet'"),
    ("a crystal lattice that snaps between two stable arrangements under pressure", "FAM:MATTER",
     "phase transition without 'phase'/'material'/'solid'"),
    ("folding a flat sheet into a shape that tiles the plane with no gaps", "FAM:GEOMETRY",
     "tiling/tessellation without 'geometry'/'shape'/'spatial'"),
    ("a switching circuit that only ever holds one of two stable voltages", "FAM:ENGINEERING",
     "bistable circuit design without 'circuit'/'engineer'/'design' as the driving word"),
    ("friends of friends connecting a stranger to a celebrity in six steps", "FAM:NETWORKS",
     "small-world graph without 'network'/'graph'/'mesh'"),
]


def score_keyword_baseline(text: str) -> str:
    enc = encode(text)
    top = max(enc.family_amplitudes_l1.items(), key=lambda x: x[1])
    return top[0] if top[1] > 0 else "NONE"


def build_rich_corpus() -> dict[str, set[str]]:
    """Auto-derived per-family token set from ontology/families.json,
    zero curation, zero new dependencies."""
    doc = json.loads((ROOT / "ontology" / "families.json").read_text(encoding="utf-8"))
    corpus: dict[str, set[str]] = {}
    stop = {"the", "a", "an", "of", "and", "or", "in", "on", "to", "is", "are", "with"}
    for fam in doc["families"]:
        text = " ".join([fam["name"], fam["description"], " ".join(fam["physics_domains"]), " ".join(fam["exemplars"])])
        tokens = {t for t in re.findall(r"[a-z]+", text.lower()) if len(t) > 2 and t not in stop}
        corpus[fam["id"]] = tokens
    return corpus


def score_rich_corpus(text: str, corpus: dict[str, set[str]]) -> str:
    tokens = set(re.findall(r"[a-z]+", text.lower()))
    scores = {fid: len(tokens & toks) for fid, toks in corpus.items()}
    top = max(scores.items(), key=lambda x: x[1])
    return top[0] if top[1] > 0 else "NONE"


def main() -> int:
    corpus = build_rich_corpus()
    kw_correct = 0
    rich_correct = 0
    print(f"{'expected':<20} {'keyword-list':<20} {'rich-corpus':<20} case")
    for text, expected, note in EVAL_SET:
        kw = score_keyword_baseline(text)
        rich = score_rich_corpus(text, corpus)
        kw_ok = kw == expected
        rich_ok = rich == expected
        kw_correct += kw_ok
        rich_correct += rich_ok
        flag_kw = "OK " if kw_ok else "MISS"
        flag_rich = "OK " if rich_ok else "MISS"
        print(f"{expected:<20} [{flag_kw}]{kw:<15} [{flag_rich}]{rich:<15} {text[:50]}")
    n = len(EVAL_SET)
    print()
    print(f"keyword-list accuracy:  {kw_correct}/{n} = {kw_correct/n:.0%}")
    print(f"rich-corpus accuracy:   {rich_correct}/{n} = {rich_correct/n:.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
