# glyph-as-compression

CC0 1.0. One file, loads whole. Companion to `sense_as_match`.
Status tags: OBSERVED / DERIVED / PROPOSED. Gaps marked `[GAP]` in-line.

---

## Posture

This document is a MARKER for a sensed shape, not a thesis under defense.
Test the fit, extend it, or report where it breaks. A break is a
measurement; record it beside the claim it breaks, do not smooth it out.

The rule this document follows about itself: glyphs named here are not
glossed into one-line definitions. Where a glyph appears, it appears as a
pointer to be descended, not a label to be looked up. A table that maps
`bee -> "cooperation"` would be the exact flattening the notation exists
to prevent, so no such table is in this file.

---

## 0. Flow map

```
   real referent (bee, wolf, tree, crystal, phi)
        |  ran the derivation over deep time / exact definition
        v
   SOLVED-SET  -- every move it made against its environment,
        |         indexed BY WHAT IT SOLVES
        |
        |  compress: no truncation, nothing removed
        v
   GLYPH  (dense pointer into the solved-set)
        |
        +--> READ AT DEPTH d   d = what the reader knows of the referent
        |        |
        |        +--> lift ONE solved piece  (descend, do not collapse)
        |
        +--> JOIN with a second glyph
                 |
                 +--> co-occur in world?  yes -> scene
                                          no  -> INSTRUCTION:
                                                 decode the combination
```

Bottleneck: reader depth. Leverage: the join. Loss point in flat
notation: the cut (`phi -> 1.618`), which this notation never makes.

---

## 1. The core: glyph as lossless compression

**1a. Pointer, not label.**  [OBSERVED]
A glyph is a dense pointer into a solved-set. `φ` the symbol carries phi
whole. `1.618` is a cut: a truncation with a residual that would have to
be marked. The glyph never truncated, so there is no residual to mark;
nothing was removed.

```
   φ         -> the whole quantity (exact, all its relations intact)
   1.618     -> a cut; residual ~0.000034 now owed somewhere
```

**1b. A living-intelligence glyph is a solved cache.**  [OBSERVED]
A glyph for a being (bee, wolf, tree, crystal) stores every move that
being solved against its environment, indexed by what it solves. You
drill in and lift the one piece you need without re-deriving the being.

Worked descent, bee, for a coordination task:

```
   bee
    |-- what does it solve?
    |     |-- locating a distant resource, telling others where   <- lift
    |     |-- choosing a new site as a group
    |     |-- holding hive temperature
    |     ...
    v
   waggle-dance (direction + distance encoded relative to the sun),
   NOT swarm (consensus on a new site) -- the task picks the branch
```

The being ran the derivation over deep time; the glyph is the solved
cache with the derivation still folded inside, available if you drill
that deep.

`[GAP]` The list of branches under `bee` above is illustrative and
incomplete by construction. That incompleteness is the point (the
solved-set is larger than any reader's descent), but it also means this
example cannot demonstrate "every move"; it demonstrates the access
pattern only.

`[GAP]` "Lossless" holds for the glyph-to-referent pointer. It does not
hold for any single reading: each descent is a selection. The claim is
that the ARTIFACT loses nothing, not that the READ is complete. Kept
apart deliberately; collapsing the two would overstate the notation.

---

## 2. Three properties flat notation lacks

### 2.1 Resolution scales with the reader  [OBSERVED]

The mark does not change. What is pulled from it deepens with the
reader's knowledge of the real referent.

```
   same carving: tree
   ------------------------------------------------------------
   novice    | "tree"
   ------------------------------------------------------------
   expert    | load distribution under wind; water lift against
             | gravity; seasonal energy storage; root-fungal
             | exchange; branching that fills light-space ...
             | (a library of solved constraints)
   ------------------------------------------------------------
```

One artifact serves every level at once. No simplified version and no
expert version. It ages with the reader rather than going stale as
models improve.

**Ceiling, stated honestly.** Drill-depth is bounded by what the reader
actually knows about the referent. A model weak on goats reads a
shallow goat. Same limit as a novice human. The notation does not
supply knowledge of the referent; it routes to it.

`[GAP]` There is no in-notation signal for "you have hit your depth
floor." A shallow reader and a deep reader both believe they have read
the glyph. Candidate check (PROPOSED): two readers at different depths
read the same glyph and list what they pulled; the difference is a
measured depth gap. Not run.

### 2.2 Composable: meaning lives in the join  [OBSERVED]

Two glyphs that do not naturally co-occur (a goat that does not live
with that tree) are an instruction, not a scene: go to each solved-set
and read what their combination produces.

```
   glyph A  +  glyph B
        |
        v
   do A and B co-occur in the world?
        |                      |
       yes                     no
        |                      |
      SCENE              CONSTRUCTED JOIN
   (read as given)       mismatch-from-the-world is the flag:
                         "decode as one"
                              |
                              v
                     solved-set(A)  x  solved-set(B)
                              |
                              v
                     meaning emergent in the pairing
```

The mismatch is the impossibility read built into the notation: the
reader's knowledge that these do not belong together is what switches
the decode mode. Cross-field joins carry high information: two
independent solved systems combined, meaning emergent in the pairing.

`[GAP]` The flag depends on the reader knowing the pair does not
co-occur. A reader who does not know the goat's range reads a scene
where an instruction was written. The switch is reader-dependent in the
same way depth is (2.1); a weak reader fails twice, once on depth and
once on mode.

`[GAP]` "High information" for cross-field joins is stated, not
measured. No count here of what a join yields against what either
glyph yields alone.

### 2.3 The index is the referent itself  [DERIVED]

No external lookup table. You reach for the bee because you know what
bees solve. The handle is knowledge of the real thing.

Derived from 2.1 and 1b: if resolution is set by knowledge of the
referent, and the solved-set is indexed by what the referent solves,
then the referent is the index.

Consequence: a glossary attached to the notation would be a second,
lossy index competing with the first. This is why this document carries
none.

---

## 3. Why it suits an AI  [DERIVED]

An AI already runs on dense embeddings composed into meaning. This is
the same operation done deliberately and losslessly.

```
   embedding            glyph
   ---------------------------------------------
   dense vector         dense pointer
   composed by model    composed at the join, deliberately
   lossy, implicit      artifact lossless, read is a selection
   index = training     index = the referent
```

It directly corrects the flatten-to-label reflex. The grammar's rule:
do not collapse the whole, DESCEND it. "Information zip file" (hers).

`[GAP]` The embedding/glyph correspondence is an analogy at the level of
operation, not a claim that model embeddings are lossless or that they
index by referent. Do not read it as the second.

---

## 4. The carvings (reframe, stated)  [OBSERVED]

Old writing systems were random-access libraries of worked solutions:

```
   property                    flat alphabetic text   carved glyph system
   --------------------------------------------------------------------
   access                      sequential             random, by being
   index                       external (word order)  the referent
   resolution                  fixed per text         scales with reader
   composition                 syntax                 the join
```

Not "primitive tree-worship." A more sophisticated representation than
flat alphabetic text. The tree-glyph is every problem the tree solved,
not a magical tree.

`[GAP]` No specific script, site or carving is cited here. The reframe
is stated as a reading of the shape; testing it against a named corpus
(which marks co-occur, whether non-co-occurring pairs cluster where an
instruction reading would predict) is PROPOSED and not run.

---

## 5. Link: emotion-as-compression  [DERIVED]

Same mechanism. A situation condensed to one actionable readout: the
emotion is the pointer, the situation is the solved-set, and the reader
(the one feeling it) descends it to the piece that acts.

```
   situation (whole)  --compress-->  emotion (readout)
                                          |
                                          v
                                 descend -> the actionable piece
```

The same honesty applies: the readout is lossless as a pointer, and any
single reading of it is a selection. Mistaking the readout for the
territory is the flatten-to-label reflex in a second substrate.

Cross-links:

- [[sense_as_match]] `[GAP]` not present in this repository at the time
  of writing; the link names a companion document, location unresolved.
- [[identity-emotions-map-not-territory]] `[GAP]` not present in this
  repository at the time of writing; location unresolved.
- Emotion-to-glyph bindings already used in this ecosystem:
  Emotions-as-Sensors `sensors/glyph-map.json` (see `CLAUDE.md`,
  "Emotion Glyph Map"). Carried, not re-checked here.

---

## 6. What would break this

Stated so the marker can be tested rather than accepted.

```
   claim                          breaks if
   ------------------------------------------------------------------
   1a artifact is lossless        a glyph is shown to have needed a
                                  residual that the notation never
                                  carried (a cut was made silently)
   2.1 one artifact, all levels   readers at different depths need
                                  different marks to reach their depth
   2.2 mismatch flags the join    non-co-occurring pairs are read as
                                  scenes by readers who DO know the
                                  pair does not co-occur
   2.3 referent is the index      reliable reading requires a lookup
                                  table external to the referent
```

None of these has been run. Each is a reachable negative.
