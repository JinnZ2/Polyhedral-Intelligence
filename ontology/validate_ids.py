# SPDX-License-Identifier: CC0-1.0
"""ID validator for ontology/families.json and ontology/principles.json.

Block A's equation index builder calls valid_family_ids() and valid_principle_ids()
to enforce that every equation.families[] / equation.principles[] binding resolves
to a known ID. Unknown IDs hard-error the build.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_FAMILIES_PATH = _HERE / "families.json"
_PRINCIPLES_PATH = _HERE / "principles.json"


@lru_cache(maxsize=1)
def _load_families() -> dict:
    with _FAMILIES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_principles() -> dict:
    with _PRINCIPLES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def valid_family_ids() -> frozenset[str]:
    return frozenset(item["id"] for item in _load_families()["families"])


def valid_principle_ids() -> frozenset[str]:
    return frozenset(item["id"] for item in _load_principles()["principles"])


def family_legacy_to_id() -> dict[str, str]:
    return {item["legacy_id"]: item["id"] for item in _load_families()["families"]}


def principle_legacy_to_id() -> dict[str, str]:
    return {item["legacy_id"]: item["id"] for item in _load_principles()["principles"]}


def validate_bindings(family_ids: list[str], principle_ids: list[str]) -> list[str]:
    """Return a list of error messages (empty if valid)."""
    errors = []
    fams = valid_family_ids()
    prins = valid_principle_ids()
    for fid in family_ids:
        if fid not in fams:
            errors.append(f"unknown family id: {fid!r}")
    for pid in principle_ids:
        if pid not in prins:
            errors.append(f"unknown principle id: {pid!r}")
    return errors


if __name__ == "__main__":
    fams = valid_family_ids()
    prins = valid_principle_ids()
    print(f"families:   {len(fams)}")
    print(f"principles: {len(prins)}")
    assert len(fams) == 20, f"expected 20 families, got {len(fams)}"
    assert len(prins) == 12, f"expected 12 principles, got {len(prins)}"
    print("OK")
