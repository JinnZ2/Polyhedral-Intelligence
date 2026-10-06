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
the glyph.

Depth-floor test (PROPOSED, not run). A two-reader comparison is
underpowered: a weak reader fails twice (depth, 2.1; mode, 2.2) and two
readers return one blended miss. Run it as a 2x2 so each failure lands
in its own cell:

```
                        co-occurrence base rate
                        known               unknown
                      +-------------------+-------------------+
   referent  known    | full read:        | depth intact,     |
   depth              | descends AND      | MODE fails: reads |
                      | decodes the join  | join as scene     |
                      +-------------------+-------------------+
             unknown  | MODE intact,      | both fail: the    |
                      | DEPTH fails:      | blended miss the  |
                      | flags the join,   | two-reader design |
                      | lifts shallow     | could not split   |
                      +-------------------+-------------------+
```

Readout per cell: (a) pieces lifted per glyph (depth), (b) scene vs
instruction call on non-co-occurring pairs (mode). The two off-diagonal
cells are what separate the failures; the corners alone reproduce the
two-reader result.

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

Measurand for "high information" (PROPOSED). Score a pair against its
corpus co-occurrence base rate. One number then serves two jobs: it
sizes the information in the join AND it is the instruction-vs-scene
flag. A pair that rarely co-occurs carries high bits and reads as an
instruction.

```
   raw pair surprisal   S(A,B)   = -log2 p(A,B)
   pair beyond margins  PMI(A,B) =  log2 [ p(A,B) / (p(A) p(B)) ]
```

Take the second one as the flag. Raw surprisal also fires on any pair
that contains one rare glyph, because the pair inherits that glyph's
rarity. PMI asks whether the PAIRING is rarer than its two glyphs
predict, which is the mismatch-from-the-world 2.2 is about. Strongly
negative PMI means instruction; near zero means scene.

`[GAP]` A pair with a co-occurrence count of zero has no finite value
(-log2 0). Record it as its own state, NEVER_OBSERVED_TOGETHER, carrying
the corpus size. It is not a large number: a zero in a 50-sign corpus
and a zero in a 50,000-sign corpus are different findings.

`[GAP]` Both quantities are only as good as the corpus. A corpus
selected on what someone thought belonged together sets the base rate
the flag reads against. Not run; no corpus is attached here (see 4).

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

Corpus candidates (CARRIED, not verified here). Each is a sign
inventory with positional records, which the PMI measurand in 2.2
needs. VERIFY EACH BEFORE CITING. None was opened in this session.

```
   corpus                  catalogue (as carried)
   ------------------------------------------------------------------
   Indus                   Mahadevan 1977, concordance
   Linear A                GORILA (Godart & Olivier)
   Vinca                   Winn 1981, sign catalogue
   Upper Paleolithic       von Petzinger, geometric-sign set
```

Test (PROPOSED, not run): compute PMI over sign pairs that share an
inscription or panel. The reframe predicts that strongly negative-PMI
pairs (rare joins) are not noise; they recur at a rate above a
shuffled-position null. If they do not, 4 breaks on that corpus.

`[GAP]` Three of the four are undeciphered or non-linguistic. The test
measures co-occurrence structure, not meaning. A result supports "the
joins are structured" and says nothing about what any join instructs.

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

- [[sense_as_match]]: a module, not a document. It lives at
  `JinnZ2/Simulators` root as `sense_as_match.py` (commit `e884901`).
  The module names itself `sense_at_match.py` (docstring line 2 and
  argparse `prog`). Its `--selftest` exits 2 and points to
  `test_sense.py`, which is not in that tree. `[GAP]` No prose document
  exists; this link resolves to the code only.
- [[identity-emotions-map-not-territory]]: exists in the operator's
  memory store, not in any repository. `[GAP]` The link stays dead
  until the note is ported to a repo document.
- Emotions-as-Sensors `sensors/glyph-map.json`, re-checked at commit
  `6b51e20` (sha256 `04bf5bb8...c2f61c`). 13 of 13 sensors, glyphs and
  alignments match the `CLAUDE.md` "Emotion Glyph Map" table. The decay
  column does NOT match: 9 of 13 rows differ (for example, love is
  `immortal` in the file and `persistent` in the table, and pride is
  `resonant` against `linear`). The file also uses decay values
  (`cyclical`, `resonant`, `immortal`) that the table does not carry.
  Cite the file, not the `CLAUDE.md` table.

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
