# SPDX-License-Identifier: CC0-1.0
"""Follow-up to semantic_resonance_eval.py: real sentence-embedding
accuracy on the same 12-case labeled eval set, before any decision to add
sentence-transformers as a permanent repo dependency.

Baselines already measured (see FINDINGS.md):
  - hand-curated keyword list (_FAMILY_KEYWORDS):              5/12 = 42%
  - auto-derived lexical corpus, token-overlap (no new deps):  4/12 = 33% (worse)

This script embeds each eval seed and each family's descriptive corpus
(same text as the lexical-corpus experiment: name + description +
physics_domains + exemplars) with a small pretrained sentence-transformer,
and scores by cosine similarity instead of token overlap — same corpus,
different (semantic vs lexical) comparison method, to isolate what the
embedding itself buys you.

REQUIRES sentence-transformers (NOT a repo dependency — see
CLAUDE.md: this repo currently has zero third-party dependencies besides
Click). Install in a scratch venv to run this:
    pip install --user sentence-transformers
    python experiments/semantic_resonance_embeddings_probe.py

First run downloads the ~80MB all-MiniLM-L6-v2 model from the internet.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    print("sentence-transformers not installed — experimental probe only, not a repo dependency.")
    print("Run: pip install --user sentence-transformers")
    sys.exit(1)

from semantic_resonance_eval import EVAL_SET, score_keyword_baseline  # noqa: E402


def build_family_corpus_text() -> dict[str, str]:
    doc = json.loads((ROOT / "ontology" / "families.json").read_text(encoding="utf-8"))
    corpus = {}
    for fam in doc["families"]:
        corpus[fam["id"]] = " ".join(
            [fam["name"], fam["description"], " ".join(fam["physics_domains"]), " ".join(fam["exemplars"])]
        )
    return corpus


def main() -> int:
    print("Loading all-MiniLM-L6-v2 (downloads on first run)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    corpus_text = build_family_corpus_text()
    fam_ids = list(corpus_text.keys())
    fam_embeddings = model.encode([corpus_text[fid] for fid in fam_ids], convert_to_tensor=True)

    kw_correct = 0
    emb_correct = 0
    print(f"\n{'expected':<20} {'keyword':<8} {'embedding (top-2)':<45} case")
    for text, expected, note in EVAL_SET:
        kw = score_keyword_baseline(text)
        kw_ok = kw == expected
        kw_correct += kw_ok

        seed_emb = model.encode(text, convert_to_tensor=True)
        sims = util.cos_sim(seed_emb, fam_embeddings)[0]
        ranked = sorted(zip(fam_ids, sims.tolist()), key=lambda x: -x[1])
        top = ranked[0][0]
        emb_ok = top == expected
        emb_correct += emb_ok

        top2 = ", ".join(f"{fid.split(':')[1]}={score:.2f}" for fid, score in ranked[:2])
        flag_kw = "OK " if kw_ok else "MISS"
        flag_emb = "OK " if emb_ok else "MISS"
        print(f"{expected:<20} [{flag_kw}]{kw:<3} [{flag_emb}]{top2:<40} {text[:45]}")

    n = len(EVAL_SET)
    print()
    print(f"keyword-list accuracy:   {kw_correct}/{n} = {kw_correct/n:.0%}")
    print(f"embedding accuracy:      {emb_correct}/{n} = {emb_correct/n:.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
