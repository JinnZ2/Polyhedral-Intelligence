# relation classes

This is a distinct relational ontology. Its classes exist and are relevant
to the degree they are useful. It is declared as a frame, not asserted as
the only frame. Every record declares its frame; class values are
frame-indexed.  [STATED]

CC0 1.0. Co-authored: STATED = the operator's definitions, DERIVED = the
formalization, OPEN = not defined, do not invent.

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
     +-- class absent ............................ UNCLASSED (never defaulted)
     +-- class not in set ........................ UNRATIFIED (never coerced)
     +-- frame absent ............................ INCOMPLETE (field: frame)
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
     +-- pre-filter: drop CYCLICAL off-phase and IMMORTAL form-change readings
     +-- class change, no declared rule ......... UNDECLARED_THRESHOLD
     +-- class change, environment unchanged .... CONTRADICTS_CLASS
     +-- rule declared, readings diverge ........ per reading; relation-level
     |                                             only at >= min_n
     +-- history spans two frames ............... CONFLICT (frame clash only)
```

Every verdict has its own next action. The table is `result_states` in the
JSON; a test fails if two verdicts share an action.

---

## Reading the coupling  [DERIVED]

```
   c = c(E(t))         not c(t)
   dc/dt = (dc/dE) * (dE/dt)

   E unchanged  ->  c unchanged, however much time passes
```

Read the environment terms (constraints, interactions, what is present);
`c` is not read directly. A record's readings carry `env_terms`. Which
terms index `c` for a given relation type is OPEN.

---

## Open, by instruction

- ANTAGONISTIC (joint below the strongest single party): the boundary is
  proposed; the class is not defined.
- CONSTITUTIVE: listed, not ratified.
- Which environment terms index coupling for a given relation type.
