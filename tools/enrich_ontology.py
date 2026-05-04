# SPDX-License-Identifier: CC0-1.0
"""Block C.1: enrich families.json and principles.json with equation_ids and
polyhedron neighbors.

Adds two fields to each family / principle entry:
  - equation_ids: list of EQ:* ids drawn from equation_index.json
  - neighbors:    list of FAM:* / PRIN:* ids that share an edge in the
                  icosahedron (for families) or dodecahedron (for principles)

Family-to-face mapping convention: legacy_id index, F01 → face 0,
F02 → face 1, ..., F20 → face 19. The 20 face indices are derived from a
standard icosahedron with vertices at the cyclic permutations of
(0, ±1, ±φ). Two faces are adjacent iff they share two vertices.

Principle-to-face mapping convention: same scheme on the dodecahedron.
Dodecahedron face adjacency is computed via duality — two dodecahedron
faces share an edge iff the corresponding icosahedron vertices share an
icosahedron edge (i.e. their distance equals the icosahedron edge length).
P01..P12 are mapped to icosahedron vertices 0..11 in vertex-list order.

These conventions are arbitrary placeholders. They give a deterministic,
reproducible adjacency — but the family/principle assignments to specific
faces have no semantic meaning yet. Override by editing the resulting
neighbors[] lists by hand if a meaningful assignment is decided later.
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ROOT / "ontology" / "families.json"
PRINCIPLES = ROOT / "ontology" / "principles.json"
INDEX = ROOT / "equations" / "json" / "equation_index.json"

PHI = (1 + math.sqrt(5)) / 2


def icosahedron_vertices() -> list[tuple[float, float, float]]:
    """12 vertices of a standard icosahedron, edge length 2."""
    return [
        (0,  1,  PHI),  # 0
        (0,  1, -PHI),  # 1
        (0, -1,  PHI),  # 2
        (0, -1, -PHI),  # 3
        (1,  PHI,  0),  # 4
        (1, -PHI,  0),  # 5
        (-1,  PHI,  0), # 6
        (-1, -PHI,  0), # 7
        (PHI,  0,  1),  # 8
        (PHI,  0, -1),  # 9
        (-PHI,  0,  1), # 10
        (-PHI,  0, -1), # 11
    ]


def dist_sq(a, b) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def icosahedron_faces(verts) -> list[tuple[int, int, int]]:
    """Find the 20 triangular faces (vertex triples at edge-length pairwise distance)."""
    edge_sq = 4.0  # for verts above, edge length is 2
    faces = []
    for i, j, k in itertools.combinations(range(len(verts)), 3):
        if (
            abs(dist_sq(verts[i], verts[j]) - edge_sq) < 1e-6
            and abs(dist_sq(verts[j], verts[k]) - edge_sq) < 1e-6
            and abs(dist_sq(verts[i], verts[k]) - edge_sq) < 1e-6
        ):
            faces.append(tuple(sorted((i, j, k))))
    if len(faces) != 20:
        raise SystemExit(f"icosahedron face count wrong: {len(faces)}")
    return faces


def icosa_face_adjacency(faces) -> dict[int, list[int]]:
    """Two faces are adjacent iff they share exactly 2 vertices (an edge)."""
    adj: dict[int, list[int]] = {i: [] for i in range(len(faces))}
    for i in range(len(faces)):
        for j in range(i + 1, len(faces)):
            if len(set(faces[i]) & set(faces[j])) == 2:
                adj[i].append(j)
                adj[j].append(i)
    for i in range(len(faces)):
        adj[i].sort()
        if len(adj[i]) != 3:
            raise SystemExit(f"face {i} has {len(adj[i])} neighbors, expected 3")
    return adj


def icosa_vertex_adjacency(verts) -> dict[int, list[int]]:
    """Two icosahedron vertices are adjacent iff their distance equals the edge length.

    Used as the dodecahedron face adjacency by duality.
    """
    edge_sq = 4.0
    adj: dict[int, list[int]] = {i: [] for i in range(len(verts))}
    for i in range(len(verts)):
        for j in range(i + 1, len(verts)):
            if abs(dist_sq(verts[i], verts[j]) - edge_sq) < 1e-6:
                adj[i].append(j)
                adj[j].append(i)
    for i in range(len(verts)):
        adj[i].sort()
        if len(adj[i]) != 5:
            raise SystemExit(f"vertex {i} has {len(adj[i])} neighbors, expected 5")
    return adj


def main() -> int:
    with INDEX.open("r", encoding="utf-8") as f:
        index = json.load(f)

    by_family = index.get("by_family", {})
    by_principle = index.get("by_principle", {})

    verts = icosahedron_vertices()
    faces = icosahedron_faces(verts)
    face_adj = icosa_face_adjacency(faces)
    vertex_adj = icosa_vertex_adjacency(verts)

    # Families
    with FAMILIES.open("r", encoding="utf-8") as f:
        fam_doc = json.load(f)

    fams = fam_doc["families"]
    if len(fams) != 20:
        raise SystemExit(f"expected 20 families, got {len(fams)}")
    legacy_to_face = {fams[i]["legacy_id"]: i for i in range(20)}
    face_to_id = {i: fams[i]["id"] for i in range(20)}

    for i, fam in enumerate(fams):
        fid = fam["id"]
        fam["equation_ids"] = list(by_family.get(fid, []))
        fam["neighbors_on_icosahedron"] = [face_to_id[n] for n in face_adj[i]]

    fam_doc["meta"]["enriched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fam_doc["meta"]["face_assignment"] = "legacy_id index → icosahedron face index (F01→face 0, ..., F20→face 19); arbitrary placeholder convention."
    fam_doc["meta"]["adjacency_source"] = "computed from standard icosahedron at vertices ±(0,1,φ) cyclic; faces are vertex triples at edge length 2 pairwise; two faces adjacent iff they share 2 vertices."

    # Principles
    with PRINCIPLES.open("r", encoding="utf-8") as f:
        prin_doc = json.load(f)

    prins = prin_doc["principles"]
    if len(prins) != 12:
        raise SystemExit(f"expected 12 principles, got {len(prins)}")
    pidx_to_id = {i: prins[i]["id"] for i in range(12)}

    for i, prin in enumerate(prins):
        pid = prin["id"]
        prin["equation_ids"] = list(by_principle.get(pid, []))
        prin["neighbors_on_dodecahedron"] = [pidx_to_id[n] for n in vertex_adj[i]]

    prin_doc["meta"]["enriched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    prin_doc["meta"]["face_assignment"] = "legacy_id index → dodecahedron face index (P01→face 0, ..., P12→face 11); arbitrary placeholder convention."
    prin_doc["meta"]["adjacency_source"] = "computed via icosahedron-dodecahedron duality: dodecahedron face i corresponds to icosahedron vertex i; two dodec faces adjacent iff their dual icosa vertices share an edge."

    fam_text = json.dumps(fam_doc, ensure_ascii=False, indent=2) + "\n"
    prin_text = json.dumps(prin_doc, ensure_ascii=False, indent=2) + "\n"
    FAMILIES.write_text(fam_text, encoding="utf-8")
    PRINCIPLES.write_text(prin_text, encoding="utf-8")

    fam_with_eqs = sum(1 for f in fams if f["equation_ids"])
    prin_with_eqs = sum(1 for p in prins if p["equation_ids"])
    print(f"families enriched:   {len(fams)}")
    print(f"  with equations:    {fam_with_eqs} / {len(fams)}")
    print(f"  total bindings:    {sum(len(f['equation_ids']) for f in fams)}")
    print(f"principles enriched: {len(prins)}")
    print(f"  with equations:    {prin_with_eqs} / {len(prins)}")
    print(f"  total bindings:    {sum(len(p['equation_ids']) for p in prins)}")
    print(f"icosa face adjacency: 20 faces × 3 neighbors each")
    print(f"dodec face adjacency: 12 faces × 5 neighbors each")
    return 0


if __name__ == "__main__":
    sys.exit(main())
