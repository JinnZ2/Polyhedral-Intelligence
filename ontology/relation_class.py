"""
relation_class.py -- validator for the decay / relation-class enum.

The class set, referent sets and additive-method list are READ from
relation_classes.json beside this file. Nothing here retypes them, so the
JSON stays the single source of truth.

validate(assignment) -> {"verdict": STATE, "findings": [...], "class": id}

    assignment keys (all optional except "class"):
        class          one of the ids in relation_classes.json
        frame          the frame the class is asserted in
        decay          a decay value, if one is claimed
        referent_type  ENERGY | RELATION_AS_ENERGY | MATERIAL | ...
        period, phase, env_index         (CYCLICAL)
        joint, separate (list), tol      (RESONANT: two-reference test)
        interaction_status               (RESONANT: "UNMEASURED")
        method                           (RESONANT: how it was scored)
        last_checked, status_inherited   (REVISABLE)
        readability, reader              (IMMORTAL: local readability is
                                          reader-relative)

        switch         {from, to, condition}; condition =
                       {reads: [...], threshold: {relation_type:
                        {value: "P3M", unit: "iso8601_duration"}}}

read_cyclical_absence(phase_state) -> "EXPECTED" | "SIGNAL" | "INCOMPLETE"
check_switch(history, declared_class=None) -> switch verdict for ONE relation
    in ONE frame; readings carry class, gap (ISO 8601 duration),
    relation_type, and optionally env_terms / phase_state / form_change /
    switch. A class change with env_terms declared and identical on both
    sides is CONTRADICTS_CLASS: coupling is c(E(t)), and time alone does
    not drive decay.
interaction_test(joint, separate, tol) -> two-reference outcome.

Verdict precedence (worst first): see PRECEDENCE. CONFLICT is reserved for
a frame clash (a history spanning two frames). A value that contradicts
its class is CONTRADICTS_CLASS. A rule with from == to is MALFORMED_RULE.

Stdlib only. Python >= 3.8. CC0.
"""

import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "relation_classes.json")

PRECEDENCE = ("UNCLASSED", "UNRATED", "UNRATIFIED", "CATEGORY_ERROR",
              "CONTRADICTS_CLASS", "CONFLICT",
              "MALFORMED_RULE", "UNDECLARED_THRESHOLD",
              "DECLARED_NOT_FOLLOWED", "INSUFFICIENT_READINGS",
              "BOUNDARY_AMBIGUOUS", "OPEN_CLASS",
              "INCOMPLETE", "UNMEASURED", "OK")

# ISO 8601 durations. Years and months have no fixed length; to compare a
# P3M threshold against a PT2000H gap they need one.  [CHOICE] mean
# Gregorian lengths: Y = 365.2425 d, M = Y / 12 = 30.436875 d.  A gap within
# a few days of a month-denominated threshold is therefore decided by this
# convention, not by the rule.
THRESHOLD_UNIT = "iso8601_duration"
_DAY = 86400.0
_ISO = re.compile(
    r"^P(?!$)(?:(\d+(?:\.\d+)?)Y)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)W)?"
    r"(?:(\d+(?:\.\d+)?)D)?(?:T(?=\d)(?:(\d+(?:\.\d+)?)H)?"
    r"(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?)?$")
_SCALE = (365.2425 * _DAY, 30.436875 * _DAY, 7 * _DAY, _DAY,
          3600.0, 60.0, 1.0)


def iso_seconds(text):
    """Seconds in an ISO 8601 duration string; None if not one."""
    if not isinstance(text, str):
        return None
    m = _ISO.match(text)
    if not m:
        return None
    return sum(float(g) * s for g, s in zip(m.groups(), _SCALE) if g)


# Calendar length of each component: a real month is 28..31 days, a real
# year 365..366. W, D, H, M(inute), S are exact. Use P{n}D to avoid a band.
_CAL = ((365 * _DAY, 366 * _DAY), (28 * _DAY, 31 * _DAY), (7 * _DAY,) * 2,
        (_DAY,) * 2, (3600.0,) * 2, (60.0,) * 2, (1.0,) * 2)


def iso_bounds(text):
    """(mean, lo, hi) seconds for an ISO 8601 duration; None if not one.

    lo == hi exactly when the duration has no Y or M (month) component.
    """
    if iso_seconds(text) is None:
        return None
    groups = _ISO.match(text).groups()
    lo = sum(float(g) * c[0] for g, c in zip(groups, _CAL) if g)
    hi = sum(float(g) * c[1] for g, c in zip(groups, _CAL) if g)
    return (iso_seconds(text), lo, hi)


def load(path=SOURCE):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return {c["id"]: c for c in data["classes"]}


CLASSES = load()
with open(SOURCE, encoding="utf-8") as _fh:
    _RAW = json.load(_fh)

# CYCLICAL must say which quantity cycles: the coupling itself, or only
# whether it can be observed (the moon in Earth's shadow).
CYCLING_QUANTITIES = ("observability", "coupling")


def _absent(a, key):
    v = a.get(key)
    return v is None or v == ""


def _worst(states):
    for s in PRECEDENCE:
        if s in states:
            return s
    return "OK"


def validate(assignment, classes=None):
    classes = CLASSES if classes is None else classes
    a = dict(assignment)
    cid = a.get("class")
    f = []   # (state, message)

    if cid is None or cid == "":
        f.append(("UNCLASSED",
                  "no class declared; the class is the decay spec, and none "
                  "is defaulted (REVISABLE included)"))
        return {"class": cid, "verdict": "UNCLASSED", "findings": f}

    if cid not in classes:
        f.append(("UNRATIFIED",
                  "class %r is not in relation_classes.json; not coerced "
                  "to the nearest member" % (cid,)))
        return {"class": cid, "verdict": "UNRATIFIED", "findings": f}

    spec = classes[cid]

    if "observed" in a:
        why = reference_gate(a)
        if why:
            f.append(("UNRATED", why))
            return {"class": cid, "verdict": "UNRATED", "findings": f}

    evidence = None
    if "class_source" in a:
        evidence = CLASS_SOURCES.get(a["class_source"])
        if evidence is None:
            f.append(("UNRATIFIED", "class_source %r is not one of %s"
                      % (a["class_source"], sorted(CLASS_SOURCES))))

    if cid == "CONSTITUTIVE":
        f.append(("OPEN_CLASS", "CONSTITUTIVE is listed, not ratified"))
        if "decay" in a:
            f.append(("CATEGORY_ERROR",
                      "a decay value on CONSTITUTIVE is malformed (not 0)"))
        return {"class": cid, "verdict": _worst([s for s, _ in f]),
                "findings": f}

    if _absent(a, "frame"):
        f.append(("INCOMPLETE", "frame undeclared; rates are frame-indexed"))

    d = a.get("decay")

    if cid == "COUPLED":
        if "decay" in a and d not in (None, "none"):
            f.append(("CONTRADICTS_CLASS",
                      "COUPLED carries decay 'none', got %r" % (d,)))

    elif cid == "CONTINUOUS":
        if "decay" in a and d not in (0, 0.0):
            f.append(("CONTRADICTS_CLASS",
                      "CONTINUOUS has decay 0 by standing in its frame, "
                      "got %r" % (d,)))

    elif cid == "REVISABLE":
        if isinstance(d, (int, float)) and not isinstance(d, bool) and d <= 0:
            f.append(("CONTRADICTS_CLASS",
                      "REVISABLE carries decay > 0, got %r" % (d,)))
        if a.get("status_inherited") is True:
            f.append(("CONTRADICTS_CLASS", "status re-checked, never inherited"))
        if _absent(a, "last_checked"):
            f.append(("INCOMPLETE", "last_checked absent"))

    elif cid == "CYCLICAL":
        for key in ("period", "phase", "env_index"):
            if _absent(a, key):
                f.append(("INCOMPLETE", "%s required for CYCLICAL" % key))
        cq = a.get("cycling_quantity")
        if cq == "coupling":
            f.append(("CONTRADICTS_CLASS",
                      "CYCLICAL is a held state; a cycling coupling is "
                      "environment-indexed c(E(t)), not CYCLICAL"))
        elif not _absent(a, "cycling_quantity") and cq not in CYCLING_QUANTITIES:
            f.append(("UNRATIFIED", "cycling_quantity %r is not one of %s"
                      % (cq, CYCLING_QUANTITIES)))

    elif cid == "RESONANT":
        method = a.get("method")
        if method in spec.get("additive_methods", []):
            f.append(("UNMEASURED",
                      "FALSE_ZERO_RISK: method %r scores the interaction "
                      "term 0 by construction" % (method,)))
        if "joint" in a and "separate" in a:
            sep = a["separate"]
            if len(sep) < 2:
                f.append(("INCOMPLETE", "RESONANT needs two or more parties"))
            elif a.get("tol") is None:
                f.append(("INCOMPLETE", "tol undeclared; the interaction "
                          "test needs a declared tolerance"))
            else:
                out = interaction_test(a["joint"], sep, a["tol"])
                o = out["outcome"]
                if o == "BOUNDARY_AMBIGUOUS":
                    f.append(("BOUNDARY_AMBIGUOUS", "joint %r is within tol "
                              "of a reference (S=%r, M=%r): %s"
                              % (a["joint"], out["S"], out["M"],
                                 out["between"])))
                elif o == "ANTAGONISTIC":
                    f.append(("CONTRADICTS_CLASS", "measured ANTAGONISTIC "
                              "(joint < M); that class is OPEN, not assigned"))
                elif o != "RESONANT":
                    f.append(("CONTRADICTS_CLASS", "measured %s, not RESONANT "
                              "(joint %r, S=%r, M=%r)"
                              % (o, a["joint"], out["S"], out["M"])))
        elif a.get("interaction_status") == "UNMEASURED":
            f.append(("UNMEASURED", "interaction term not measured"))
        else:
            f.append(("INCOMPLETE",
                      "RESONANT requires joint + separate, or "
                      "interaction_status UNMEASURED; never defaults additive"))

    elif cid == "IMMORTAL":
        rt = a.get("referent_type")
        valid = spec["valid_referents"]["values"]
        if rt == "MATERIAL":
            f.append(("CATEGORY_ERROR",
                      "IMMORTAL does not apply to a material referent "
                      "(not 0, not null)"))
        elif rt is None:
            f.append(("INCOMPLETE", "referent_type undeclared"))
        elif rt not in valid:
            f.append(("INCOMPLETE",
                      "referent_type %r is not one of %s" % (rt, valid)))
        if "readability" in a and _absent(a, "reader"):
            f.append(("INCOMPLETE", "readability is reader-relative; "
                      "declare the reader and key"))

    if "switch" in a:
        f.extend(_check_switch_rule(a["switch"], classes))

    out = {"class": cid, "verdict": _worst([s for s, _ in f]), "findings": f}
    if evidence is not None:
        out["evidence"] = evidence
    return out


def parse_threshold(threshold):
    """{relation_type: {value: ISO-8601 duration, unit: iso8601_duration}}
    -> ({relation_type: seconds}, findings). A bare number or bare string
    is MALFORMED_RULE: the unit must be typed, not implied."""
    if not isinstance(threshold, dict) or not threshold:
        return {}, [("UNDECLARED_THRESHOLD",
                     "threshold absent; it must be keyed by relation_type")]
    out, f = {}, []
    for rt, entry in threshold.items():
        if not isinstance(entry, dict):
            f.append(("MALFORMED_RULE", "threshold[%r] = %r is not typed "
                      "{value, unit}" % (rt, entry)))
            continue
        if entry.get("unit") != THRESHOLD_UNIT:
            f.append(("MALFORMED_RULE", "threshold[%r] unit %r is not %r"
                      % (rt, entry.get("unit"), THRESHOLD_UNIT)))
            continue
        bounds = iso_bounds(entry.get("value"))
        if bounds is None:
            f.append(("MALFORMED_RULE", "threshold[%r] value %r is not an "
                      "ISO 8601 duration" % (rt, entry.get("value"))))
            continue
        out[rt] = bounds
    return out, f


def interaction_test(joint, separate, tol):
    """Two-reference interaction test. S = sum(separate), M = max(separate).

    joint > S -> RESONANT; M < joint <= S -> ENHANCED_SUBADDITIVE;
    |joint - M| <= tol -> REDUNDANT; joint < M -> ANTAGONISTIC (OPEN).
    A joint value within tol of S cannot be told RESONANT from
    ENHANCED_SUBADDITIVE, and one within tol of both S and M cannot be
    placed either: BOUNDARY_AMBIGUOUS, with the candidates named.
    tol is declared by the caller; it is never defaulted.
    """
    if isinstance(tol, bool) or not isinstance(tol, (int, float)) or tol < 0:
        raise ValueError("tol must be a non-negative number, got %r" % (tol,))
    S, M = sum(separate), max(separate)
    near_m = abs(joint - M) <= tol
    # At tol 0 the stated ranges decide exactly (joint == S is
    # ENHANCED_SUBADDITIVE); the S band exists only for tol > 0.
    near_s = tol > 0 and abs(joint - S) <= tol
    between = None
    if near_m and near_s:
        outcome, between = "BOUNDARY_AMBIGUOUS", "REDUNDANT or above"
    elif near_m:
        outcome = "REDUNDANT"
    elif near_s:
        outcome, between = "BOUNDARY_AMBIGUOUS", \
            "RESONANT or ENHANCED_SUBADDITIVE"
    elif joint > S:
        outcome = "RESONANT"
    elif joint > M:
        outcome = "ENHANCED_SUBADDITIVE"
    else:
        outcome = "ANTAGONISTIC"
    return {"outcome": outcome, "S": S, "M": M, "interaction": joint - S,
            "between": between}


def env_change(before, after):
    """Changed environment terms between two readings.

    Returns a sorted list of term names that differ (added, removed or
    changed); [] if both are declared and identical; None if either side
    does not declare env_terms (the change cannot be read).
    """
    if not isinstance(before, dict) or not isinstance(after, dict):
        return None
    keys = set(before) | set(after)
    return sorted(k for k in keys if before.get(k, _MISSING) !=
                  after.get(k, _MISSING))


_MISSING = object()

# L2: coupling is indexed by REFERENCE = environment + precedence + chain of
# custody. The reference is read; c is not.
REFERENCE_PARTS = tuple(_RAW["reference_parts"])

# L4 parity: a participant's declared class is an observation, with the same
# standing and the same limits as self-report of feeling in the default frame.
CLASS_SOURCES = _RAW["class_sources"]


def _when(text):
    """ISO 8601 date or date-time -> aware datetime (UTC if no offset)."""
    if not isinstance(text, str) or not text:
        return None
    try:
        if "T" not in text:
            d = datetime.date.fromisoformat(text)
            t = datetime.datetime(d.year, d.month, d.day)
        else:
            t = datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=datetime.timezone.utc)
    return t


def reference_gate(record):
    """L1: the reference (env_terms, precedence, custody) must be written
    BEFORE the outcome. Returns None when the record is ratable, else the
    reason it is UNRATED. Undocumented order is UNRATED, not assumed fine."""
    ref = record.get("reference")
    if not isinstance(ref, dict):
        return "no reference recorded before the outcome"
    missing = [p for p in REFERENCE_PARTS if p not in ref]
    if missing:
        return "reference lacks %s" % ", ".join(missing)
    written, observed = _when(ref.get("written")), _when(record.get("observed"))
    if written is None or observed is None:
        return ("order not documented: reference.written and observed must "
                "both be ISO 8601 dates")
    if written >= observed:
        return "reference written %s, not before the outcome %s" % (
            ref.get("written"), record.get("observed"))
    return None


def reference_change(before, after):
    """Changed reference parts between two readings ([] if identical, None
    if either side has no reference). env_terms is compared term by term."""
    if not isinstance(before, dict) or not isinstance(after, dict):
        return None
    out = []
    for part in REFERENCE_PARTS:
        if part == "env_terms":
            sub = env_change(before.get(part, {}), after.get(part, {}))
            out.extend("env_terms.%s" % k for k in (sub or []))
        elif before.get(part, _MISSING) != after.get(part, _MISSING):
            out.append(part)
    return out


def compare_frames(class_by_frame):
    """L4: cross-frame disagreement is a limit on BOTH frames. Symmetric:
    nothing here names a frame as the correct one."""
    classes = {f: c for f, c in class_by_frame.items()}
    agree = len(set(classes.values())) <= 1
    return {"agree": agree, "classes": classes,
            "limit_on": [] if agree else sorted(classes)}


PHI = (1 + 5 ** 0.5) / 2


def power_drift(approx, n):
    """L6: relative error of approx**n against PHI**n. A stored truncation
    compounds under iteration."""
    return abs(approx ** n / PHI ** n - 1)


def relation_recovery(x0, n):
    """L6: iterate the defining relation x -> 1 + 1/x (phi^2 = phi + 1).
    PHI is an attracting fixed point, so the relation pulls a perturbed
    start back; returns |x_n - PHI|."""
    x = x0
    for _ in range(n):
        x = 1 + 1 / x
    return abs(x - PHI)

# A switch rule that reads only these is driven by elapsed time alone. It is
# annotated, not judged: the rule may belong to a frame other than this one.
TIME_ONLY_READS = {"gap_length", "relation_type"}


def _check_switch_rule(sw, classes):
    """A frame that switches class must declare {from, to, condition}."""
    out = []
    if not isinstance(sw, dict):
        return [("UNDECLARED_THRESHOLD", "switch present with no rule")]
    src, dst, cond = sw.get("from"), sw.get("to"), sw.get("condition")
    for name, val in (("from", src), ("to", dst)):
        if val not in classes:
            out.append(("UNRATIFIED", "switch %s %r is not a ratified class"
                        % (name, val)))
    if src is not None and src == dst:
        out.append(("MALFORMED_RULE",
                    "switch from and to are the same class (%r)" % (src,)))
    if not isinstance(cond, dict) or not cond:
        out.append(("UNDECLARED_THRESHOLD",
                    "switch %r -> %r has no declared condition" % (src, dst)))
        return out
    if not cond.get("reads"):
        out.append(("UNDECLARED_THRESHOLD",
                    "switch condition must name what it reads"))
    out.extend(parse_threshold(cond.get("threshold"))[1])
    return out


# Readings that carry no information about a switch, by declared class.
# A CYCLICAL relation observed off-phase, or an IMMORTAL relation observed
# through a change of form, would otherwise read as a decayed tie and
# produce a false switch.
def _drop_reason(reading, declared_class):
    if declared_class == "CYCLICAL" and reading.get("phase_state") == "off":
        return "CYCLICAL off-phase"
    if declared_class == "IMMORTAL" and reading.get("form_change") is True:
        return "IMMORTAL form change"
    return None


def check_switch(history, declared_class=None, min_n=None):
    """Switch verdict for ONE relation in ONE frame.

    history: readings, each {class, gap (ISO 8601 duration), relation_type,
    frame, optional switch, phase_state, form_change}.
    declared_class: the class the relation's declarer gives it; drives the
    pre-filter (CYCLICAL off-phase and IMMORTAL form-change readings are
    dropped before detection, and reported).
    min_n: DECLARED by the caller, never defaulted. The number of
    mismatching readings needed before the relation as a whole is called
    DECLARED_NOT_FOLLOWED. Undeclared with mismatches present ->
    INCOMPLETE, per-reading flags only.

    Every rule-tested reading gets a per_reading entry: MATCH, MISMATCH, or
    BOUNDARY_AMBIGUOUS (inside the 28-31 d / 365-366 d calendar band of a
    Y/M threshold; no verdict). The mismatch summary reports count, the
    tested denominator and the rate.

    UNDECLARED_THRESHOLD   the class changes and no declared rule covers
                           the change, or the rule has no threshold for
                           this relation_type
    DECLARED_NOT_FOLLOWED  mismatches >= min_n
    INSUFFICIENT_READINGS  0 < mismatches < min_n
    BOUNDARY_AMBIGUOUS     at least one reading fell in a calendar band
    MALFORMED_RULE         a rule is badly formed, or two rules for one
                           switch disagree
    CONFLICT               the history spans more than one frame (a frame
                           clash, not a switch). Reserved for that.
    """
    if min_n is not None and (isinstance(min_n, bool) or
                              not isinstance(min_n, int) or min_n < 1):
        raise ValueError("min_n must be a positive integer, got %r" % (min_n,))
    frames = {h.get("frame") for h in history}
    if len(frames) > 1:
        return {"verdict": "CONFLICT", "dropped": [], "per_reading": [],
                "mismatch": None, "transitions": [], "unrated": [],
                "rules": {},
                "findings": [("CONFLICT", "history spans frames %s; compare "
                              "within one frame" % sorted(map(str, frames)))]}
    findings, dropped, kept, unrated = [], [], [], []
    for h in history:
        why = _drop_reason(h, declared_class)
        if why:
            dropped.append((h.get("gap"), why))
            continue
        not_ratable = reference_gate(h)
        if not_ratable:
            unrated.append((h.get("gap"), not_ratable))
            continue
        sec = iso_seconds(h.get("gap"))
        if sec is None:
            findings.append(("INCOMPLETE", "gap %r is not an ISO 8601 "
                             "duration; reading excluded" % (h.get("gap"),)))
            continue
        kept.append((sec, h))

    rules = {}   # (from, to) -> {relation_type: (mean, lo, hi) seconds}
    rule_meta = {}
    for _, h in kept:
        sw = h.get("switch")
        if sw is None:
            continue
        problems = _check_switch_rule(sw, CLASSES)
        findings.extend(problems)
        if problems:
            continue
        key = (sw["from"], sw["to"])
        thr = parse_threshold(sw["condition"]["threshold"])[0]
        if key in rules and rules[key] != thr:
            findings.append(("MALFORMED_RULE", "two rules for %r -> %r "
                             "disagree" % key))
            continue
        rules[key] = thr
        reads = set(sw["condition"].get("reads") or [])
        rule_meta[key] = {"time_only": not (reads - TIME_ONLY_READS)}

    kept.sort(key=lambda p: p[0])
    transitions = []
    for (_, prev), (_, cur) in zip(kept, kept[1:]):
        a, b = prev.get("class"), cur.get("class")
        changed = reference_change(prev.get("reference"),
                                   cur.get("reference"))
        if a != b:
            transitions.append({"from": a, "to": b, "gap_from": prev.get("gap"),
                                "gap_to": cur.get("gap"),
                                "reference_changed": changed})
            if changed == []:
                findings.append(("CONTRADICTS_CLASS",
                                 "class %r -> %r between gap %s and %s with "
                                 "the reference (environment, precedence, "
                                 "custody) unchanged; time alone is not a "
                                 "decay driver"
                                 % (a, b, prev.get("gap"), cur.get("gap"))))
        if a != b and (a, b) not in rules:
            findings.append(("UNDECLARED_THRESHOLD",
                             "class %r at gap %s -> %r at gap %s with no "
                             "declared switch rule"
                             % (a, prev.get("gap"), b, cur.get("gap"))))

    per_reading = []
    for (src, dst), thr in rules.items():
        for sec, h in kept:
            if h.get("class") not in (src, dst):
                continue
            rt = h.get("relation_type")
            if rt is None:
                findings.append(("INCOMPLETE", "reading at gap %s has no "
                                 "relation_type" % (h.get("gap"),)))
                continue
            if rt not in thr:
                findings.append(("UNDECLARED_THRESHOLD", "rule %r -> %r "
                                 "has no threshold for relation_type %r"
                                 % (src, dst, rt)))
                continue
            _, lo, hi = thr[rt]
            if lo < hi and lo <= sec < hi:
                status, expected = "BOUNDARY_AMBIGUOUS", None
            else:
                expected = src if sec < lo else dst
                status = "MATCH" if h.get("class") == expected else "MISMATCH"
            per_reading.append({"gap": h.get("gap"), "relation_type": rt,
                                "class": h.get("class"), "rule": (src, dst),
                                "expected": expected, "status": status})

    ambiguous = sum(1 for p in per_reading if p["status"] == "BOUNDARY_AMBIGUOUS")
    tested = sum(1 for p in per_reading if p["status"] != "BOUNDARY_AMBIGUOUS")
    mism = sum(1 for p in per_reading if p["status"] == "MISMATCH")
    summary = {"mismatches": mism, "tested": tested,
               "rate": (mism / tested) if tested else None,
               "boundary_ambiguous": ambiguous, "min_n": min_n}
    if ambiguous:
        findings.append(("BOUNDARY_AMBIGUOUS", "%d reading(s) fall inside "
                         "the calendar band of a Y/M threshold; no verdict "
                         "for them (declare the threshold as P{n}D)"
                         % ambiguous))
    if mism:
        if min_n is None:
            findings.append(("INCOMPLETE", "%d mismatch(es) found and min_n "
                             "undeclared; per-reading flags only" % mism))
        elif mism >= min_n:
            findings.append(("DECLARED_NOT_FOLLOWED", "%d of %d tested "
                             "readings diverge from the declared rule "
                             "(min_n %d)" % (mism, tested, min_n)))
        else:
            findings.append(("INSUFFICIENT_READINGS", "%d of %d tested "
                             "readings diverge, below min_n %d"
                             % (mism, tested, min_n)))

    if unrated and not kept:
        findings.append(("UNRATED", "no reading is ratable: %d lack a "
                         "reference written before the outcome" % len(unrated)))
    return {"verdict": _worst([s for s, _ in findings]),
            "findings": findings, "dropped": dropped,
            "per_reading": per_reading, "mismatch": summary,
            "transitions": transitions,
            "unrated": unrated,
            "rules": {"%s->%s" % k: v for k, v in rule_meta.items()}}


def read_cyclical_absence(phase_state):
    """Absence read against phase. phase_state: 'on' | 'off'."""
    if phase_state == "off":
        return "EXPECTED"
    if phase_state == "on":
        return "SIGNAL"
    return "INCOMPLETE"


def infer_from_null(cls, phase_state=None):
    """What an observed null licenses.

    CYCLICAL off-phase: nothing (scheduled loss of observation).
    CYCLICAL on-phase: a SIGNAL to investigate, not a verdict.
    IMMORTAL: nothing about the quantity; form may have changed.
    COUPLED / CONTINUOUS: nothing from elapsed time or missing contact.
    REVISABLE: a null is admissible evidence of decay.
    """
    if cls == "CYCLICAL":
        r = read_cyclical_absence(phase_state)
        return {"EXPECTED": "NOTHING", "SIGNAL": "SIGNAL"}.get(r, "INCOMPLETE")
    if cls in ("IMMORTAL", "COUPLED", "CONTINUOUS"):
        return "NOTHING"
    if cls == "REVISABLE":
        return "EVIDENCE_OF_DECAY"
    if cls == "CONSTITUTIVE":
        return "CATEGORY_ERROR"
    return "UNCLASSED" if not cls else "UNRATIFIED"


def _ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(xs, ys):
    """Rank correlation with average ranks for ties. None when undefined."""
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    rx, ry = _ranks(xs), _ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    if sxx == 0 or syy == 0:
        return None
    return sxy / (sxx * syy) ** 0.5


def inversion_test(rows, min_n=3):
    """MEASURAND_INVERSION (PROPOSED).

    rows: dicts with class, declared_strength, contact_proxy.
    Returns rank correlation PER CLASS, never pooled. None where a class has
    fewer than min_n rows or a constant column. Unclassed rows are counted
    and excluded, never assigned.
    """
    by, unclassed = {}, 0
    for row in rows:
        c = row.get("class")
        if not c:
            unclassed += 1
            continue
        by.setdefault(c, []).append(row)
    out = {}
    for c, rs in sorted(by.items()):
        rho = None
        if len(rs) >= min_n:
            rho = spearman([r["declared_strength"] for r in rs],
                           [r["contact_proxy"] for r in rs])
        out[c] = {"n": len(rs), "rho": rho}
    return {"per_class": out, "unclassed_excluded": unclassed, "pooled": None}


def render_limits(data=None):
    """The doc's Limits section, rendered from the JSON (single source)."""
    if data is None:
        data = _RAW
    lim = data["limits"]
    lines = ["## Limits", "", "<!-- generated by relation_class.render_limits;"
             " edit relation_classes.json -->", ""]
    for key in sorted(k for k in lim if k.startswith("L")):
        e = lim[key]
        lines.append("**%s %s** [%s]  %s" % (key, e["kind"], e["tag"], e["text"]))
        for sub in ("derived", "mechanism"):
            if sub in e:
                lines.append("")
                lines.append("> %s [%s]  %s" % (sub, e[sub]["tag"], e[sub]["text"]))
        lines.append("")
    lines.append("*Note* [%s]  %s" % (lim["note"]["tag"], lim["note"]["text"]))
    return "\n".join(lines) + "\n"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--limits" in argv:
        sys.stdout.write(render_limits())
        return 0
    if "--selftest" in argv:
        print("library module; run tests/test_relation_class.py",
              file=sys.stderr)
        return 2
    for cid, spec in CLASSES.items():
        print("%-13s %-7s %s" % (cid, spec["status"],
                                 spec["definition"]["text"][:60]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
