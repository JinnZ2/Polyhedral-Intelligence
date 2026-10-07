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
        joint, separate (list)           (RESONANT measurement)
        interaction_status               (RESONANT: "UNMEASURED")
        method                           (RESONANT: how it was scored)
        last_checked, status_inherited   (REVISABLE)

        switch         {from, to, condition}; condition =
                       {reads: [...], threshold: {relation_type:
                        {value: "P3M", unit: "iso8601_duration"}}}

read_cyclical_absence(phase_state) -> "EXPECTED" | "SIGNAL" | "INCOMPLETE"
check_switch(history, declared_class=None) -> switch verdict for ONE relation
    in ONE frame; readings carry class, gap (ISO 8601 duration),
    relation_type, and optionally phase_state / form_change / switch.

Verdict precedence (worst first): see PRECEDENCE. CONFLICT is reserved for
a frame clash (a history spanning two frames). A value that contradicts
its class is CONTRADICTS_CLASS. A rule with from == to is MALFORMED_RULE.

Stdlib only. Python >= 3.8. CC0.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "relation_classes.json")

PRECEDENCE = ("UNCLASSED", "UNRATIFIED", "CATEGORY_ERROR",
              "CONTRADICTS_CLASS", "CONFLICT",
              "MALFORMED_RULE", "UNDECLARED_THRESHOLD",
              "DECLARED_NOT_FOLLOWED", "INSUFFICIENT_READINGS",
              "BOUNDARY_AMBIGUOUS", "OPEN_CLASS",
              "FRAME_UNDECLARED", "INCOMPLETE", "UNMEASURED", "OK")

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

    if cid == "CONSTITUTIVE":
        f.append(("OPEN_CLASS", "CONSTITUTIVE is listed, not ratified"))
        if "decay" in a:
            f.append(("CATEGORY_ERROR",
                      "a decay value on CONSTITUTIVE is malformed (not 0)"))
        return {"class": cid, "verdict": _worst([s for s, _ in f]),
                "findings": f}

    if _absent(a, "frame"):
        f.append(("FRAME_UNDECLARED", "rates are frame-indexed; declare frame"))

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
        for key in ("period", "phase", "env_index", "cycling_quantity"):
            if _absent(a, key):
                f.append(("INCOMPLETE", "%s required for CYCLICAL" % key))
        cq = a.get("cycling_quantity")
        if not _absent(a, "cycling_quantity") and cq not in CYCLING_QUANTITIES:
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
            interaction = a["joint"] - sum(sep)
            if len(sep) < 2:
                f.append(("INCOMPLETE", "RESONANT needs two or more parties"))
            elif interaction <= 0:
                f.append(("CONTRADICTS_CLASS",
                          "interaction = %r <= 0; not RESONANT (the "
                          "antagonistic case is OPEN, not assigned)"
                          % (interaction,)))
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

    if "switch" in a:
        f.extend(_check_switch_rule(a["switch"], classes))

    return {"class": cid, "verdict": _worst([s for s, _ in f]),
            "findings": f}


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
                "mismatch": None,
                "findings": [("CONFLICT", "history spans frames %s; compare "
                              "within one frame" % sorted(map(str, frames)))]}
    findings, dropped, kept = [], [], []
    for h in history:
        why = _drop_reason(h, declared_class)
        if why:
            dropped.append((h.get("gap"), why))
            continue
        sec = iso_seconds(h.get("gap"))
        if sec is None:
            findings.append(("INCOMPLETE", "gap %r is not an ISO 8601 "
                             "duration; reading excluded" % (h.get("gap"),)))
            continue
        kept.append((sec, h))

    rules = {}   # (from, to) -> {relation_type: seconds}
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

    kept.sort(key=lambda p: p[0])
    for (_, prev), (_, cur) in zip(kept, kept[1:]):
        a, b = prev.get("class"), cur.get("class")
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

    return {"verdict": _worst([s for s, _ in findings]),
            "findings": findings, "dropped": dropped,
            "per_reading": per_reading, "mismatch": summary}


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


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
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
