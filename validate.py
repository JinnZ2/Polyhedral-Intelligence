#!/usr/bin/env python3
"""
Validate all JSON files in Polyhedral-Intelligence.

Checks:
  1. JSON syntax (no smart quotes, trailing commas, etc.)
  2. Required top-level keys in atlas_schema.json
  3. Required top-level keys in protocols.json
  4. Entry JSON files have required fields
  5. atlas_index.json references match actual entry files

Run standalone:  python validate.py
Exit code 0 = all valid, 1 = errors found.
"""

import json
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent
ERRORS = []


def error(path, msg):
    ERRORS.append(f"  {path}: {msg}")


def check_json(path):
    """Parse a JSON file and check for smart quotes."""
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception as e:
        error(path, f"cannot read: {e}")
        return None

    # Check for smart quotes before parsing
    for i, ch in enumerate(raw):
        if ch in "\u201c\u201d\u2018\u2019":
            line = raw[:i].count("\n") + 1
            error(path, f"smart quote U+{ord(ch):04X} at line {line}")
            return None

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        error(path, f"invalid JSON: {e}")
        return None


def validate_atlas_schema(data, path):
    """Check atlas_schema.json has expected structure."""
    for key in ("families", "principles"):
        if key not in data:
            error(path, f"missing top-level key '{key}'")
            return

    families = data["families"]
    principles = data["principles"]

    if not isinstance(families, list) or len(families) != 20:
        error(path, f"expected 20 families, got {len(families) if isinstance(families, list) else type(families).__name__}")

    if not isinstance(principles, list) or len(principles) != 12:
        error(path, f"expected 12 principles, got {len(principles) if isinstance(principles, list) else type(principles).__name__}")

    for i, fam in enumerate(families):
        for field in ("id", "name", "symbol"):
            if field not in fam:
                error(path, f"family [{i}] missing '{field}'")


def validate_protocols(data, path):
    """Check protocols.json has expected structure."""
    for key in ("families", "principles"):
        if key not in data:
            error(path, f"missing top-level key '{key}'")


def validate_entry(data, path):
    """Check an atlas entry JSON has required fields."""
    for field in ("id", "title", "seed_glyph"):
        if field not in data:
            error(path, f"missing required field '{field}'")


def validate_atlas_index(data, path):
    """Check atlas_index.json entries reference real files."""
    if not isinstance(data, list):
        return

    entries_dir = ROOT / "entries"
    for item in data:
        if "file" in item:
            json_path = entries_dir / item["file"]
            if not json_path.exists():
                md_path = json_path.with_suffix(".md")
                if not json_path.exists():
                    error(path, f"references missing file: {item['file']}")


def validate_fieldlink(data, path):
    """Check .fieldlink.json structure."""
    if "fieldlink" not in data:
        error(path, "missing top-level 'fieldlink' key")
        return

    fl = data["fieldlink"]
    for key in ("version", "role"):
        if key not in fl:
            error(path, f"fieldlink missing '{key}'")


def main():
    print("Polyhedral-Intelligence JSON Validator")
    print("=" * 40)

    # 1. Validate all JSON files for syntax
    json_files = sorted(ROOT.glob("*.json")) + sorted(ROOT.glob("entries/*.json"))
    print(f"\nChecking {len(json_files)} JSON files...")

    parsed = {}
    for jf in json_files:
        data = check_json(jf)
        if data is not None:
            parsed[jf] = data

    # 2. Structural checks on key files
    atlas_path = ROOT / "atlas_schema.json"
    if atlas_path in parsed:
        validate_atlas_schema(parsed[atlas_path], atlas_path)

    protocols_path = ROOT / "protocols.json"
    if protocols_path in parsed:
        validate_protocols(parsed[protocols_path], protocols_path)

    fieldlink_path = ROOT / ".fieldlink.json"
    if fieldlink_path in parsed:
        validate_fieldlink(parsed[fieldlink_path], fieldlink_path)

    # 3. Entry file checks
    for jf in sorted(ROOT.glob("entries/*.json")):
        if jf in parsed:
            validate_entry(parsed[jf], jf)

    # 4. Atlas index cross-reference
    index_path = ROOT / "atlas_index.json"
    if index_path in parsed:
        validate_atlas_index(parsed[index_path], index_path)

    # 5. Also check nested JSON (protocols/connect.json, etc.)
    for extra in [ROOT / "protocols" / "connect.json"]:
        if extra.exists():
            check_json(extra)

    # Report
    print()
    if ERRORS:
        print(f"FAILED — {len(ERRORS)} error(s):")
        for e in ERRORS:
            print(e)
        return 1
    else:
        print(f"OK — {len(parsed)} files validated, no errors.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
