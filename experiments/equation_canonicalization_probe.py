# SPDX-License-Identifier: CC0-1.0
"""Probe for #2 (equation hashing catches string identity, not mathematical
equivalence): what fraction of the 128 real equations in
equations/json/*.json can SymPy actually parse, as-is and after a minimal
preprocessing pass?

Claim under test: "you'd need a computer algebra system (SymPy) to
canonicalize formulas." This measures how far that gets you on the *actual*
corpus rather than on clean textbook examples — these formulas use Leibniz
notation (dx/dt), unicode subscripts (Σᵢ, ωᵢ), nabla/partial operators
(∇, ∂, ∇²), semicolon-separated systems, and bracket concentration notation
([S]) that a generic parser was never designed for.

NOTE: this script requires `sympy`, which is NOT a project dependency
(the repo has zero third-party dependencies today — see CLAUDE.md). Install
it in a scratch venv to run this probe; do not add it to the repo without a
separate decision about taking on that dependency.

Run: pip install --user sympy && python experiments/equation_canonicalization_probe.py
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

try:
    from sympy import sympify
    from sympy.parsing.sympy_parser import parse_expr
except ImportError:
    print("sympy not installed — this is an experimental probe only, not a repo dependency.")
    print("Run: pip install --user sympy")
    sys.exit(1)


def load_formulas() -> list[tuple[str, str, str]]:
    out = []
    for path in sorted(glob.glob(str(ROOT / "equations" / "json" / "eq_*.json"))):
        e = json.loads(Path(path).read_text(encoding="utf-8"))
        out.append((e["id"], e["canonical_name"], e["canonical_form_ascii"]))
    return out


def try_raw_parse(formula: str) -> bool:
    try:
        parse_expr(formula, evaluate=False)
        return True
    except Exception:
        return False


UNICODE_REPLACEMENTS = {
    "θ": "theta", "ω": "omega", "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta",
    "ρ": "rho", "μ": "mu", "ν": "nu", "σ": "sigma", "λ": "lambda", "Δ": "Delta",
    "Σ": "Sum", "∇²": "laplacian", "∇": "nabla", "∂": "d", "√": "sqrt",
    "π": "pi", "φ": "phi", "χ": "chi", "‖": "|", "≈": "=", "∝": "=", "·": "*",
    "ᵢ": "_i", "ⱼ": "_j", "ₙ": "_n", "₀": "_0", "₁": "_1", "₂": "_2", "‡": "",
}


def preprocess(formula: str) -> str:
    """Minimal, honest preprocessing: no per-equation hand-tuning, just a
    generic unicode-symbol substitution + take the first clause of any
    semicolon-separated system + drop everything after a second '='."""
    f = formula.split(";")[0]  # systems of equations -> just the first one
    for uni, ascii_repl in UNICODE_REPLACEMENTS.items():
        f = f.replace(uni, ascii_repl)
    parts = f.split("=")
    if len(parts) > 2:
        f = "=".join(parts[:2])  # chained equalities (Re = ... = ...) -> first equality only
    return f.strip()


def main() -> int:
    formulas = load_formulas()
    raw_ok = 0
    preprocessed_ok = 0
    still_fails: list[tuple[str, str, str]] = []

    for fid, name, formula in formulas:
        if try_raw_parse(formula):
            raw_ok += 1
        pre = preprocess(formula)
        if try_raw_parse(pre):
            preprocessed_ok += 1
        else:
            still_fails.append((fid, name, formula))

    n = len(formulas)
    print(f"total equations tested:              {n}")
    print(f"parse as-is (no preprocessing):        {raw_ok}/{n} = {raw_ok/n:.0%}")
    print(f"parse after minimal preprocessing:      {preprocessed_ok}/{n} = {preprocessed_ok/n:.0%}")
    print()
    print(f"still fail after preprocessing ({len(still_fails)}):")
    for fid, name, formula in still_fails[:15]:
        print(f"  {fid} {name}: {formula!r}")
    if len(still_fails) > 15:
        print(f"  ... and {len(still_fails) - 15} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
