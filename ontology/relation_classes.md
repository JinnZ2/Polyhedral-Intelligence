# relation classes

This is a distinct relational ontology. Its classes exist and are relevant
to the degree they are useful. It is declared as a frame, not asserted as
the only frame. Every record declares its frame; class values are
frame-indexed.  [STATED]

CC0 1.0. Co-authored: STATED = the operator's definitions, DERIVED = the
formalization, OPEN = not defined, do not invent.

---

## Two axes  [STATED 2026-10-07; schema relation_class/2]

```
   state_class      what the relation IS        persistence / decay axis
                    COUPLED | CONTINUOUS | REVISABLE | IMMORTAL
                    | CONSTITUTIVE (OPEN) | RESONANT (axis move PROPOSED)

   contact_pattern  how contact RECURS          observation channel
                    CYCLICAL {period, phase, env_index}
                    IRREGULAR {interval_set_by: self|other|mutual|environment}
                    CONSTANT                    near-continuous contact
                    NONE                        contact not possible
                                                (e.g. IMMORTAL across death)
```

Source: her long ties (best friend 17 yrs, father, mother) are CONTINUOUS,
with irregular contact and no decay. Her grown children are CONTINUOUS
when not cyclical; birthdays and holidays are a CYCLICAL pattern of
remembrance on top. One relation carries a state and a contact pattern at
once, so schema 1's single `class` field merged two things.

```
   grown child:  state_class CONTINUOUS
                 contact_pattern [CYCLICAL {P1Y, birthday, calendar},
                                  IRREGULAR {mutual}]

   contact P(t) may be periodic ──► the state follows state_class, not contact
```

- Both fields are required and neither has a default. A missing
  state_class is UNCLASSED and is never inferred from contact. A missing
  contact_pattern is INCOMPLETE.
- A relation may list more than one contact pattern. NONE beside a pattern
  that has contact is CONTRADICTS_CLASS.
- CYCLICAL moved axes. It is a contact pattern, not a state.
- RESONANT: a move to the interaction axis is PROPOSED, because it is
  measured by the interaction test and says nothing about decay. It is
  flagged for her confirmation and not finalized, so RESONANT stays a state
  member for now. `validate` adds the flag RESONANT_AXIS_PROPOSED.
- Migration from schema 1 is `migrate()`. A record with class CYCLICAL
  gets contact_pattern CYCLICAL and state_class UNCLASSED, which must be
  declared. Any other class is renamed to state_class.

Which axis each check reads:

```
   check                              keys on
   off-phase pre-filter               contact_pattern CYCLICAL
   decay value / CONTRADICTS_CLASS    state_class
   class switch, from / to            state_class (a contact pattern is UNRATIFIED there)
   IMMORTAL form-change drop          state_class
   fitted lambda, fitted_on=state     state_class: CONTINUOUS|COUPLED|IMMORTAL, lambda != 0
                                      -> ENV_DRIFT_IN_SAMPLE
   fitted lambda, fitted_on=contact   contact_pattern CYCLICAL|IRREGULAR, lambda != 0
                                      -> CONTACT_CHANNEL_ARTIFACT (any state)
```

E1 log (doc note, PROPOSED): each contact carries a `contact_type`,
either `ritual` (birthday, holiday) or `irregular`. The prediction is that
resumption latency is flat for both types, and flat against gap length.
No E1 log exists yet in this repository or in Simulators. The field is
specified in `proposed_tests.E1_CONTACT_TYPE` so the log carries it from
its first row.

---

## Where the truth lives

```
   ontology/relation_classes.json   the ONLY source of class definitions,
                                    models, verdicts and next actions
   ontology/relation_class.py       reads the JSON; validates records
   tests/test_relation_class.py     pins every rule
   this file                        how to read the above; copies nothing
```

The frame statement above is the one exception: it is mirrored from
`frame_statement` in the JSON, and a test fails if the two drift apart.

---

## Flow of a record

```
   record
     |
     +-- state_class absent ...................... UNCLASSED (never defaulted)
     +-- state_class not in set .................. UNRATIFIED (never coerced)
     +-- contact_pattern absent .................. INCOMPLETE (field: contact_pattern)
     +-- contact value not in set ................ UNRATIFIED
     +-- frame absent ............................ INCOMPLETE (field: frame)
     +-- reference not written before outcome .... UNRATED (L1)
     |
     v
   class rules (per class, from the JSON)
     |
     +-- value contradicts the class ............. CONTRADICTS_CLASS
     +-- question malformed for the referent ..... CATEGORY_ERROR
     +-- inside an uncertainty band .............. BOUNDARY_AMBIGUOUS
     |
     v
   history of one relation, one frame  (check_switch)
     |
     +-- pre-filter: drop readings in a CYCLICAL contact off-phase, and
     |   IMMORTAL form-change readings
     +-- gate: readings without a prior reference are UNRATED, not judged
     +-- class change, no declared rule ......... UNDECLARED_THRESHOLD
     +-- class change, reference unchanged ...... CONTRADICTS_CLASS
     +-- rule declared, readings diverge ........ per reading; relation-level
     |                                             only at >= min_n
     +-- history spans two frames ............... CONFLICT (frame clash only)
```

Every verdict has its own next action. The table is `result_states` in the
JSON; a test fails if two verdicts share an action.

---

## Reading the coupling  [STATED: L2; DERIVED: the form]

```
   R = (environment, precedence, chain of custody)     the reference
   c = c(R(t))         not c(t)
   dc/dt = (dc/dR) * (dR/dt)

   R unchanged  ->  c unchanged, however much time passes
```

Read the reference chain; `c` is not read directly. Readings carry
`reference = {env_terms, precedence, custody, written}`, written before
the outcome (L1). Which reference terms index `c` for a given relation
type is OPEN.

---

## Translation to the default frame  [DERIVED, PROPOSED; partial]

```
   this frame ──── project_to_default ────► default frame
     class, reference,                        class = REVISABLE (every row)
     lambda(R), driver R                      lambda = constant, driver = t
                       lossy: many → one

   default frame ── lift_to_frame ─────────► this frame
                    only with class + reference + frame SUPPLIED
                    (new information, not an inverse)
```

The default frame also MERGES the two axes: contact frequency is used as
the state proxy, so a contact gap reads as decay. That is the measurand
inversion: the moon in Earth's shadow, a scheduled loss of observation
read as a change of orbit (`translation_map.default_merges_axes`).

Lorentz maps are invertible; this one is not, so the cost is asymmetric:
the projection is free to compute and loses the reference, and the
return direction carries the whole cost. A default-frame fitted λ reads per class:
a nonzero fit on COUPLED, CONTINUOUS or IMMORTAL rows is
ENV_DRIFT_IN_SAMPLE (the sample's environment moved). A fit on contact
data from a CYCLICAL or IRREGULAR contact pattern is CONTACT_CHANNEL_ARTIFACT,
whatever the state. On REVISABLE rows a state fit holds only inside the
sample's environment range (`interpret_fitted_lambda`, which requires
`fitted_on` to be declared). Detail: `translation_map` in the
JSON. The per-class λ correspondence is in; the rest of the map is OPEN.

---

## Limits

<!-- generated by relation_class.render_limits; edit relation_classes.json -->

**L1 REQUIREMENT** [STATED]  env_terms and the reference chain are written BEFORE the outcome (frame practice). Undocumented -> UNRATED.

**L2 RESOLVED** [STATED]  c is indexed by REFERENCE = environment + precedence + chain of custody. Read the reference chain, not c.

**L3 INVARIANTS_BY_TRANSLATION** [STATED]  REMOVED: 'must universalize / be inherited by other frames'. That is a privileged-frame claim, and physics rejects privileged frames: the laws hold in all frames, and measurements are translated between frames, not imposed. Universality in physics means INVARIANTS found by translating across frames, not adoption of one frame. This ontology: the frame is declared; translation is the boundary cost; the carried quantities are the invariants (for example IMMORTAL information / energy).

> derived [DERIVED]  Precision on the physics: the principle holds for inertial frames in special relativity and for all frames in general relativity (general covariance). Invariants such as the spacetime interval, proper time and rest mass are what every frame agrees on after translation. Physics translation maps (Lorentz, general coordinate transformations) are invertible. The map here is not: the default frame is a projection of this one (translation_map, PARTIAL), so the translation cost is ASYMMETRIC, not mutual. The per-class lambda correspondence is in (translation_map.per_class_lambda); the rest of the map is OPEN.

**L4 PARITY_RULE** [STATED]  A participant-declared class is OBSERVED, with the same standing and limits as self-report of feeling in the default frame. REMOVED: 'no adjudicator between frames (symmetric)' (false balance). An adjudicator EXISTS: physical outcome and mathematics. Exact vs approximate is settled by measurable drift (phi^2 = phi + 1 vs 1.618). Class predictions are settled by observation (return-state, the inversion test). The coupling default is settled by physics practice, where isolation is a declared idealization. The cost that remains at the boundary is TRANSLATION only.

**L5 CORRECTED** [STATED]  The IMMORTAL record is causally active (shapes state and behaviour) unread. A reader is needed for RECOGNITION only.

**L6 CORRECTED** [STATED]  A glyph is an exact relation (cf. phi defined by phi^2 = phi + 1): no truncation error, no drift. A default or approximate frame (cf. 1.618) accumulates error under iteration, so IT carries the recalibration burden. The burden of re-correction sits with the approximating frame.

> derived [DERIVED]  Two checks. (1) 1.618^n drifts from phi^n: the relative error grows with n (power_drift). (2) Iterating the defining relation x -> 1 + 1/x pulls a perturbed start back to phi, because phi is an attracting fixed point (relation_recovery). The exact relation does not just avoid drift; it corrects toward itself.

> mechanism [DERIVED]  Whichever frame is the ruler gets its own approximations made invisible, because they are the measuring stick. Anything measured against that ruler shows its differences as deficits, even where it is the more exact one. That is not a judgment either frame earned. It comes from which one got to be the reference first.

**L7 CORRECTED** [STATED]  Each class equation is a testable prediction (classes[].prediction), plus the measurand-inversion test.

*Note* [DERIVED]  Replaces an earlier L1-L7 list, delivered in chat and never committed to this repository. That list applied default-frame standards asymmetrically; this one is revised for parity. Later revisions: L3 replaced (privileged-frame claim removed); L4's symmetric-limit clause removed (adjudication by physical outcome). L3's derived note updated with the partial translation map (asymmetric cost).

---

## Open, by instruction

- ANTAGONISTIC (joint below the strongest single party): the boundary is
  proposed; the class is not defined.
- CONSTITUTIVE: listed, not ratified.
- RESONANT's move to the interaction axis: proposed, awaiting her
  confirmation.
- Which reference terms index coupling for a given relation type.
- The rest of the translation map, beyond lambda (L3; the partial map is above).
