"""Tests for ontology/relation_class.py. Stdlib unittest; run from repo root:

    python3 -m unittest tests/test_relation_class.py
"""

import json
import math
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ontology"))

import relation_class as rc  # noqa: E402

F = {"frame": "operator",
     "contact_pattern": [{"pattern": "IRREGULAR", "interval_set_by": "mutual"}]}
ANNUAL = {"pattern": "CYCLICAL", "period": "P1Y", "phase": "birthday",
          "env_index": "calendar"}
MUTUAL = {"pattern": "IRREGULAR", "interval_set_by": "mutual"}


def ref(env, written="2026-09-01", precedence="declarer", custody=("kin",)):
    """A reference written before the default outcome date (L1)."""
    return {"env_terms": dict(env), "precedence": precedence,
            "custody": list(custody), "written": written}


OBSERVED = "2026-10-01"


def v(**kw):
    return rc.validate(kw)["verdict"]


class TestSource(unittest.TestCase):
    def test_two_axes_from_json(self):
        with open(rc.SOURCE, encoding="utf-8") as fh:
            data = json.load(fh)
        ids = [c["id"] for c in data["state_classes"]]
        self.assertEqual(ids, ["COUPLED", "CONTINUOUS", "REVISABLE",
                               "CONSTITUTIVE", "RESONANT", "IMMORTAL"])
        self.assertEqual(set(ids), set(rc.CLASSES))
        cps = [c["id"] for c in data["contact_patterns"]]
        self.assertEqual(cps, ["CYCLICAL", "IRREGULAR", "CONSTANT", "NONE"])
        self.assertEqual(set(cps), set(rc.CONTACT_PATTERNS))
        self.assertNotIn("classes", data)            # schema 1 key gone
        self.assertEqual(data["schema"], "relation_class/2")

    def test_resonant_axis_move_flagged_not_finalized(self):
        move = rc.CLASSES["RESONANT"]["axis_move"]
        self.assertEqual(move["status"], "PROPOSED")
        self.assertIn("PENDING", move["confirmation"])
        out = rc.validate(dict(F, **{"state_class": "RESONANT",
                                     "interaction_status": "UNMEASURED"}))
        self.assertIn("RESONANT_AXIS_PROPOSED", out["flags"])
        self.assertEqual(rc.validate(dict(F, **{"state_class": "CONTINUOUS"}))
                         ["flags"], [])

    def test_every_text_field_tagged(self):
        for cid, spec in rc.CLASSES.items():
            self.assertEqual(spec["axis"], "state", cid)
            for key in ("definition", "decay", "valid_referents", "measurand"):
                self.assertIn(spec[key]["tag"], ("STATED", "DERIVED", "OPEN"),
                              "%s.%s" % (cid, key))

    def test_no_class_list_retyped_in_module(self):
        src = open(os.path.join(ROOT, "ontology", "relation_class.py"),
                   encoding="utf-8").read()
        self.assertIn("CLASSES = load()", src)
        self.assertNotIn("sum_of_parts", src)
        self.assertNotIn("RELATION_AS_ENERGY\"]", src)


class TestUnknown(unittest.TestCase):
    def test_old_vocabulary_is_unratified_not_coerced(self):
        for old in ("exponential", "linear", "persistent", "power",
                    "immortal", "Resonant", "CYCLICAL", "IRREGULAR"):
            self.assertEqual(v(**dict(F, **{"state_class": old})), "UNRATIFIED", old)
        why = rc.validate(dict(F, **{"state_class": "CYCLICAL"}))["findings"]
        self.assertIn("contact_pattern in schema 2", why[0][1])

    def test_absent_class_is_unclassed_never_defaulted(self):
        for blank in (None, ""):
            self.assertEqual(v(**dict(F, **{"state_class": blank})), "UNCLASSED")
        self.assertEqual(rc.validate(dict(F))["verdict"], "UNCLASSED")
        self.assertIsNone(rc.validate(dict(F))["state_class"])
        # a schema-1 'class' key is not read as the state: migrate() first
        legacy = rc.validate(dict(F, **{"class": "CONTINUOUS"}))
        self.assertEqual(legacy["verdict"], "UNCLASSED")
        self.assertIn("migrate()", legacy["findings"][0][1])


class TestFrame(unittest.TestCase):
    def test_frame_required_everywhere_but_constitutive(self):
        for cls in ("CONTINUOUS", "COUPLED"):
            out = rc.validate({"state_class": cls})
            self.assertEqual(out["verdict"], "INCOMPLETE")
            self.assertTrue(any("frame" in m for _, m in out["findings"]))
        self.assertEqual(v(**dict(F, **{"state_class": "CONTINUOUS"})), "OK")
        self.assertNotIn("FRAME_UNDECLARED", rc.PRECEDENCE)


class TestClasses(unittest.TestCase):
    def test_coupled(self):
        self.assertEqual(v(**dict(F, **{"state_class": "COUPLED", "decay": "none"})), "OK")
        self.assertEqual(v(**dict(F, **{"state_class": "COUPLED", "decay": 0.1})), "CONTRADICTS_CLASS")

    def test_continuous_zero_by_standing(self):
        self.assertEqual(v(**dict(F, **{"state_class": "CONTINUOUS", "decay": 0})), "OK")
        self.assertEqual(v(**dict(F, **{"state_class": "CONTINUOUS", "decay": 0.2})), "CONTRADICTS_CLASS")

    def test_revisable(self):
        base = dict(F, **{"state_class": "REVISABLE", "last_checked": "2026-10-07"})
        self.assertEqual(v(**dict(base, decay=0.3)), "OK")
        self.assertEqual(v(**dict(base, decay=0)), "CONTRADICTS_CLASS")
        self.assertEqual(v(**dict(base, status_inherited=True)),
                         "CONTRADICTS_CLASS")
        self.assertEqual(v(**dict(F, **{"state_class": "REVISABLE"})), "INCOMPLETE")

    def test_constitutive_decay_is_category_error_not_zero(self):
        self.assertEqual(v(**{"state_class": "CONSTITUTIVE", "decay": 0}), "CATEGORY_ERROR")
        self.assertEqual(v(**{"state_class": "CONSTITUTIVE"}), "OPEN_CLASS")

    def test_cyclical_is_a_contact_pattern(self):
        cyc = {"pattern": "CYCLICAL", "period": "1 y", "phase": "spring",
               "env_index": "day length", "cycling_quantity": "observability"}
        full = dict(F, **{"state_class": "CONTINUOUS", "contact_pattern": [cyc]})
        self.assertEqual(v(**full), "OK")
        # held state: a cycling coupling is environment-indexed, not a rhythm
        for cq, want in (("coupling", "CONTRADICTS_CLASS"),
                         ("phase", "UNRATIFIED")):
            bad = dict(full, contact_pattern=[dict(cyc, cycling_quantity=cq)])
            self.assertEqual(v(**bad), want, cq)
        no_cq = {k: x for k, x in cyc.items() if k != "cycling_quantity"}
        self.assertEqual(v(**dict(full, contact_pattern=[no_cq])), "OK")
        self.assertEqual(v(**dict(full, contact_pattern=["CYCLICAL"])),
                         "INCOMPLETE")
        self.assertEqual(rc.read_cyclical_absence("off"), "EXPECTED")
        self.assertEqual(rc.read_cyclical_absence("on"), "SIGNAL")
        self.assertEqual(rc.read_cyclical_absence(None), "INCOMPLETE")

    def test_resonant_needs_interaction_term(self):
        r = dict(F, **{"state_class": "RESONANT", "tol": 0.5})
        self.assertEqual(v(**dict(r, joint=10, separate=[3, 4])), "OK")
        self.assertEqual(v(**dict(F, **{"state_class": "RESONANT", "joint": 10,
                                        "separate": [3, 4]})), "INCOMPLETE")
        self.assertEqual(v(**dict(r, joint=6, separate=[3, 4])),
                         "CONTRADICTS_CLASS")
        self.assertEqual(v(**dict(r, joint=7, separate=[3, 4])),
                         "BOUNDARY_AMBIGUOUS")   # joint == S, inside tol
        self.assertEqual(v(**dict(r, joint=5, separate=[3, 4])),
                         "CONTRADICTS_CLASS")
        self.assertEqual(v(**dict(r, interaction_status="UNMEASURED")), "UNMEASURED")
        self.assertEqual(v(**r), "INCOMPLETE")
        self.assertEqual(v(**dict(r, joint=9, separate=[9])), "INCOMPLETE")

    def test_conflict_never_returned_by_validate(self):
        cases = [
            {"state_class": "COUPLED", "decay": 0.1},
            {"state_class": "CONTINUOUS", "decay": 0.2},
            {"state_class": "REVISABLE", "decay": -1, "status_inherited": True},
            {"state_class": "CONTINUOUS",
             "contact_pattern": [dict(ANNUAL, cycling_quantity="x")]},
            {"state_class": "RESONANT", "joint": 1, "separate": [3, 4], "tol": 0.1},
        ]
        for c in cases:
            states = [s for s, _ in rc.validate(dict(F, **c))["findings"]]
            self.assertNotIn("CONFLICT", states, c)

    def test_resonant_additive_method_flagged(self):
        for m in rc.CLASSES["RESONANT"]["additive_methods"]:
            out = rc.validate(dict(F, **{"state_class": "RESONANT", "method": m,
                                         "interaction_status": "UNMEASURED"}))
            self.assertTrue(any("FALSE_ZERO_RISK" in msg
                                for _, msg in out["findings"]), m)

    def test_immortal_referents(self):
        i = dict(F, **{"state_class": "IMMORTAL"})
        self.assertEqual(v(**dict(i, referent_type="ENERGY")), "OK")
        self.assertEqual(v(**dict(i, referent_type="RELATION_AS_ENERGY")), "OK")
        self.assertEqual(v(**dict(i, referent_type="MATERIAL")), "CATEGORY_ERROR")
        self.assertEqual(v(**i), "INCOMPLETE")
        self.assertEqual(v(**dict(i, referent_type="EMOTION_SENSOR")), "INCOMPLETE")


class TestNulls(unittest.TestCase):
    def test_off_phase_null_licenses_nothing(self):
        f = rc.infer_from_null
        # the phase rule keys on contact CYCLICAL, whatever the state
        for st in ("REVISABLE", "CONTINUOUS"):
            self.assertEqual(f(st, [ANNUAL], "off"), "NOTHING", st)
            self.assertEqual(f(st, [ANNUAL], "on"), "SIGNAL", st)
        self.assertEqual(f("CONTINUOUS", [ANNUAL]), "INCOMPLETE")
        for c in ("IMMORTAL", "COUPLED", "CONTINUOUS"):
            self.assertEqual(f(c, [MUTUAL]), "NOTHING", c)
        self.assertEqual(f("REVISABLE", [MUTUAL]), "EVIDENCE_OF_DECAY")
        self.assertEqual(f("REVISABLE", ["NONE"]), "NOTHING")
        self.assertEqual(f("CONSTITUTIVE", [MUTUAL]), "CATEGORY_ERROR")
        self.assertEqual(f(None, [MUTUAL]), "UNCLASSED")
        self.assertEqual(f("friend", [MUTUAL]), "UNRATIFIED")
        self.assertEqual(f("CYCLICAL", [MUTUAL]), "UNRATIFIED")
        self.assertEqual(f("CONTINUOUS", None), "INCOMPLETE")   # both required


class TestInversion(unittest.TestCase):
    def test_spearman_known_answers(self):
        self.assertAlmostEqual(rc.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(rc.spearman([1, 2, 3, 4], [40, 30, 20, 10]), -1.0)
        self.assertIsNone(rc.spearman([1, 2], [1, 2]))
        self.assertIsNone(rc.spearman([1, 1, 1], [1, 2, 3]))

    def test_per_class_never_pooled(self):
        rows = (
            [{"state_class": "REVISABLE", "declared_strength": s, "contact_proxy": s}
             for s in (1, 2, 3, 4)] +
            [{"state_class": "CONTINUOUS", "contact_pattern": [ANNUAL, MUTUAL],
              "declared_strength": s, "contact_proxy": -s}
             for s in (1, 2, 3, 4)] +
            [{"state_class": "IMMORTAL", "declared_strength": 5, "contact_proxy": 1}] +
            [{"state_class": None, "declared_strength": 3, "contact_proxy": 3}]
        )
        out = rc.inversion_test(rows)
        self.assertIsNone(out["pooled"])
        self.assertAlmostEqual(out["per_class"]["REVISABLE"]["rho"], 1.0)
        self.assertAlmostEqual(out["per_class"]["CONTINUOUS"]["rho"], -1.0)
        by_contact = rc.inversion_test(rows, by_axis="contact_pattern")
        self.assertAlmostEqual(
            by_contact["per_class"]["CYCLICAL+IRREGULAR"]["rho"], -1.0)
        self.assertEqual(by_contact["unclassed_excluded"], 6)   # no contact
        self.assertIsNone(out["per_class"]["IMMORTAL"]["rho"])
        self.assertEqual(out["per_class"]["IMMORTAL"]["n"], 1)
        self.assertEqual(out["unclassed_excluded"], 1)


def _thr(**by_type):
    return {rt: {"value": val, "unit": "iso8601_duration"}
            for rt, val in by_type.items()}


class TestIsoDuration(unittest.TestCase):
    def test_known_answers(self):
        self.assertEqual(rc.iso_seconds("PT8H"), 8 * 3600)
        self.assertEqual(rc.iso_seconds("P1D"), 86400)
        self.assertEqual(rc.iso_seconds("PT90M"), 5400)
        self.assertEqual(rc.iso_seconds("P1W"), 7 * 86400)
        self.assertAlmostEqual(rc.iso_seconds("P3M"), 3 * 30.436875 * 86400)
        self.assertAlmostEqual(rc.iso_seconds("P1Y"), 365.2425 * 86400)
        # M before T is months, after T is minutes
        self.assertNotEqual(rc.iso_seconds("P1M"), rc.iso_seconds("PT1M"))

    def test_rejects(self):
        for bad in ("P", "PT", "8H", "P8H", "PT8D", "", None, 8, "P3M ", "p3m"):
            self.assertIsNone(rc.iso_seconds(bad), repr(bad))
            self.assertIsNone(rc.iso_bounds(bad), repr(bad))

    def test_calendar_bands(self):
        d = 86400
        mean, lo, hi = rc.iso_bounds("P3M")
        self.assertEqual((lo, hi), (84 * d, 93 * d))
        self.assertTrue(lo < mean < hi)
        _, lo, hi = rc.iso_bounds("P1Y")
        self.assertEqual((lo, hi), (365 * d, 366 * d))
        for exact in ("P90D", "PT8H", "P2W", "PT30M"):
            mean, lo, hi = rc.iso_bounds(exact)
            self.assertEqual((mean, lo), (hi, hi), exact)


class TestSwitch(unittest.TestCase):
    RULE = {"from": "CONTINUOUS", "to": "REVISABLE",
            "condition": {"reads": ["gap_length", "relation_type"],
                          "threshold": _thr(kin="P3M", colleague="PT8H")}}

    def _held(self, **kw):
        base = dict(F, **{"state_class": "CONTINUOUS", "contact_pattern": [
            {"pattern": "CYCLICAL", "period": "P1D", "phase": "workday",
             "env_index": "work schedule", "cycling_quantity": "observability"}]})
        base.update(kw)
        return base

    def test_declared_switch_passes(self):
        self.assertEqual(v(**self._held(switch=self.RULE)), "OK")

    def test_switch_without_condition_flagged(self):
        sw = {"from": "CONTINUOUS", "to": "REVISABLE"}
        self.assertEqual(v(**self._held(switch=sw)), "UNDECLARED_THRESHOLD")
        self.assertEqual(v(**self._held(switch=True)), "UNDECLARED_THRESHOLD")
        vague = dict(self.RULE, condition={"reads": ["gap_length"]})
        self.assertEqual(v(**self._held(switch=vague)), "UNDECLARED_THRESHOLD")

    def test_switch_bad_classes(self):
        self.assertEqual(v(**self._held(switch=dict(self.RULE, to="decay"))),
                         "UNRATIFIED")
        # a contact pattern is not a state; a switch is between states
        out = rc.validate(self._held(switch=dict(self.RULE, **{"from": "CYCLICAL"})))
        self.assertEqual(out["verdict"], "UNRATIFIED")
        self.assertTrue(any("contact pattern" in m for _, m in out["findings"]))

    def test_same_class_rule_is_malformed_not_conflict(self):
        same = dict(self.RULE, to="CONTINUOUS")
        self.assertEqual(v(**self._held(switch=same)), "MALFORMED_RULE")
        out = rc.check_switch([{"frame": "F1", "state_class": "CONTINUOUS",
                                "gap": "PT1H", "relation_type": "kin",
                                "observed": OBSERVED,
                                "reference": ref({"t": "PT1H"}),
                                "switch": same}])
        self.assertEqual(out["verdict"], "MALFORMED_RULE")

    def test_threshold_must_be_typed_iso(self):
        for bad in ({"kin": "P3M"}, {"kin": 90},
                    {"kin": {"value": "P3M", "unit": "days"}},
                    {"kin": {"value": "3 months", "unit": "iso8601_duration"}}):
            rule = dict(self.RULE, condition={"reads": ["gap_length"],
                                              "threshold": bad})
            self.assertEqual(v(**self._held(switch=rule)), "MALFORMED_RULE",
                             repr(bad))
        empty = dict(self.RULE, condition={"reads": ["gap_length"],
                                           "threshold": {}})
        self.assertEqual(v(**self._held(switch=empty)), "UNDECLARED_THRESHOLD")

    # --- history ----------------------------------------------------------

    def _r(self, cls, gap, rt="kin", **kw):
        # The environment differs at every reading ({"t": gap}), so these
        # tests exercise switch logic; reference-unchanged has its own tests.
        return dict({"frame": "F1", "state_class": cls, "gap": gap,
                     "relation_type": rt, "observed": OBSERVED,
                     "reference": ref({"t": gap})}, **kw)

    def test_undeclared_switch_detected(self):
        out = rc.check_switch([self._r("REVISABLE", "P4M"),
                               self._r("CONTINUOUS", "PT8H")])
        self.assertEqual(out["verdict"], "UNDECLARED_THRESHOLD")
        same = rc.check_switch([self._r("CONTINUOUS", "PT8H"),
                                self._r("CONTINUOUS", "PT9H")])
        self.assertEqual(same["verdict"], "OK")

    def test_declared_and_followed(self):
        out = rc.check_switch([self._r("CONTINUOUS", "PT8H", switch=self.RULE),
                               self._r("REVISABLE", "P4M")])
        self.assertEqual(out["verdict"], "OK")

    def test_declared_not_followed(self):
        # kin threshold P3M: still CYCLICAL at P4M -> rule says REVISABLE
        late = rc.check_switch([self._r("CONTINUOUS", "PT8H", switch=self.RULE),
                                self._r("CONTINUOUS", "P4M")], min_n=1)
        self.assertEqual(late["verdict"], "DECLARED_NOT_FOLLOWED")
        # switched early: REVISABLE at P1M, below the P3M threshold
        early = rc.check_switch([self._r("CONTINUOUS", "PT8H", switch=self.RULE),
                                 self._r("REVISABLE", "P1M")], min_n=1)
        self.assertEqual(early["verdict"], "DECLARED_NOT_FOLLOWED")
        self.assertEqual([p["status"] for p in early["per_reading"]],
                         ["MATCH", "MISMATCH"])

    def test_min_n_gates_relation_verdict(self):
        hist = [self._r("CONTINUOUS", "PT8H", switch=self.RULE),
                self._r("CONTINUOUS", "P4M"), self._r("CONTINUOUS", "P5M"),
                self._r("REVISABLE", "P6M")]
        three = rc.check_switch(hist, min_n=3)
        self.assertEqual(three["verdict"], "INSUFFICIENT_READINGS")
        self.assertEqual(three["mismatch"]["mismatches"], 2)
        self.assertEqual(three["mismatch"]["tested"], 4)
        self.assertAlmostEqual(three["mismatch"]["rate"], 0.5)
        self.assertEqual(three["mismatch"]["min_n"], 3)
        self.assertEqual(rc.check_switch(hist, min_n=2)["verdict"],
                         "DECLARED_NOT_FOLLOWED")
        # min_n undeclared: flags kept, no relation-level call
        none = rc.check_switch(hist)
        self.assertEqual(none["verdict"], "INCOMPLETE")
        self.assertEqual(sum(p["status"] == "MISMATCH"
                             for p in none["per_reading"]), 2)

    def test_min_n_must_be_positive_int(self):
        for bad in (0, -1, 1.5, True, "3"):
            with self.assertRaises(ValueError, msg=repr(bad)):
                rc.check_switch([], min_n=bad)

    def test_no_mismatch_reports_zero_rate(self):
        out = rc.check_switch([self._r("CONTINUOUS", "PT8H", switch=self.RULE),
                               self._r("REVISABLE", "P4M")], min_n=1)
        self.assertEqual(out["mismatch"]["mismatches"], 0)
        self.assertEqual(out["mismatch"]["rate"], 0.0)
        empty = rc.check_switch([self._r("CONTINUOUS", "PT8H")], min_n=1)
        self.assertIsNone(empty["mismatch"]["rate"])   # nothing tested

    def test_calendar_band_gives_no_verdict(self):
        # P3M band is 84..93 d; P88D sits inside it
        inside = rc.check_switch([self._r("CONTINUOUS", "PT8H", switch=self.RULE),
                                  self._r("REVISABLE", "P88D")], min_n=1)
        self.assertEqual(inside["verdict"], "BOUNDARY_AMBIGUOUS")
        self.assertEqual(inside["per_reading"][1]["status"],
                         "BOUNDARY_AMBIGUOUS")
        self.assertIsNone(inside["per_reading"][1]["expected"])
        self.assertEqual(inside["mismatch"]["tested"], 1)
        # same reading against a day-denominated rule: decided
        day_rule = dict(self.RULE, condition={
            "reads": ["gap_length"], "threshold": _thr(kin="P90D")})
        decided = rc.check_switch([self._r("CONTINUOUS", "PT8H", switch=day_rule),
                                   self._r("REVISABLE", "P88D")], min_n=1)
        self.assertEqual(decided["verdict"], "DECLARED_NOT_FOLLOWED")
        # just outside the band on either side is decided
        below = rc.check_switch([self._r("CONTINUOUS", "PT8H", switch=self.RULE),
                                 self._r("CONTINUOUS", "P83D")], min_n=1)
        self.assertEqual(below["verdict"], "OK")
        above = rc.check_switch([self._r("CONTINUOUS", "PT8H", switch=self.RULE),
                                 self._r("REVISABLE", "P93D")], min_n=1)
        self.assertEqual(above["verdict"], "OK")

    def test_threshold_is_keyed_by_relation_type(self):
        # colleague threshold PT8H: REVISABLE at P1D is what the rule says
        ok = rc.check_switch([self._r("CONTINUOUS", "PT1H", "colleague",
                                      switch=self.RULE),
                              self._r("REVISABLE", "P1D", "colleague")])
        self.assertEqual(ok["verdict"], "OK")
        uncovered = rc.check_switch([self._r("CONTINUOUS", "PT1H", "neighbour",
                                             switch=self.RULE),
                                     self._r("REVISABLE", "P1D", "neighbour")])
        self.assertEqual(uncovered["verdict"], "UNDECLARED_THRESHOLD")

    def test_disagreeing_rules_malformed(self):
        other = dict(self.RULE, condition={"reads": ["gap_length"],
                                           "threshold": _thr(kin="P6M")})
        out = rc.check_switch([self._r("CONTINUOUS", "PT8H", switch=self.RULE),
                               self._r("CONTINUOUS", "PT9H", switch=other)])
        self.assertEqual(out["verdict"], "MALFORMED_RULE")

    def test_non_iso_gap_excluded(self):
        out = rc.check_switch([self._r("CONTINUOUS", 8)])
        self.assertEqual(out["verdict"], "INCOMPLETE")

    # --- pre-filter -------------------------------------------------------

    def test_seasonal_gap_is_not_a_switch(self):
        history = [self._r("CONTINUOUS", "PT8H", phase_state="on"),
                   self._r("REVISABLE", "P5M", phase_state="off")]
        out = rc.check_switch(history, declared_state="CONTINUOUS",
                              contact_patterns=[ANNUAL])
        self.assertEqual(out["verdict"], "OK")
        self.assertEqual(out["dropped"], [("P5M", "CYCLICAL off-phase")])
        # control: same readings, no declared contact -> the false switch fires
        self.assertEqual(rc.check_switch(history)["verdict"],
                         "UNDECLARED_THRESHOLD")
        # the off-phase drop keys on contact, not on the state
        no_cyc = rc.check_switch(history, declared_state="CONTINUOUS",
                                 contact_patterns=[MUTUAL])
        self.assertEqual(no_cyc["verdict"], "UNDECLARED_THRESHOLD")

    def test_immortal_form_change_dropped(self):
        history = [self._r("IMMORTAL", "P1Y"),
                   self._r("REVISABLE", "P2Y", form_change=True)]
        out = rc.check_switch(history, declared_state="IMMORTAL")
        self.assertEqual(out["verdict"], "OK")
        self.assertEqual(len(out["dropped"]), 1)
        # off-phase flag means nothing for an IMMORTAL relation
        kept = rc.check_switch([self._r("IMMORTAL", "P1Y"),
                                self._r("REVISABLE", "P2Y", phase_state="off")],
                               declared_state="IMMORTAL",
                               contact_patterns=["NONE"])
        self.assertEqual(kept["verdict"], "UNDECLARED_THRESHOLD")

    def test_history_across_frames_is_conflict(self):
        out = rc.check_switch([self._r("CONTINUOUS", "PT1H"),
                               dict(self._r("REVISABLE", "PT2H"), frame="F2")])
        self.assertEqual(out["verdict"], "CONFLICT")


class TestFrameStatement(unittest.TestCase):
    def test_doc_opens_with_the_stated_frame(self):
        with open(rc.SOURCE, encoding="utf-8") as fh:
            data = json.load(fh)
        fs = data["frame_statement"]
        self.assertEqual(fs["tag"], "STATED")
        self.assertEqual(list(data)[3], "frame_statement")
        doc = open(os.path.join(ROOT, "ontology", "relation_classes.md"),
                   encoding="utf-8").read()
        body = doc.split("\n## ")[0]       # text before the first section
        self.assertIn(fs["text"], " ".join(body.split()))


class TestVerdictAudit(unittest.TestCase):
    def test_every_verdict_has_a_distinct_next_action(self):
        with open(rc.SOURCE, encoding="utf-8") as fh:
            states = json.load(fh)["result_states"]
        self.assertEqual(set(states), set(rc.PRECEDENCE))
        actions = [s["next_action"] for s in states.values()]
        self.assertEqual(len(actions), len(set(actions)))


class TestInteraction(unittest.TestCase):
    T = 0.5

    def o(self, joint, sep=(3, 4)):
        return rc.interaction_test(joint, list(sep), self.T)["outcome"]

    def test_four_outcomes(self):
        self.assertEqual(self.o(10), "RESONANT")              # > S = 7
        self.assertEqual(self.o(6), "ENHANCED_SUBADDITIVE")   # M=4 < 6 <= 7
        self.assertEqual(self.o(4.2), "REDUNDANT")            # |4.2-4| <= .5
        self.assertEqual(self.o(2), "ANTAGONISTIC")           # < M

    def test_bands_are_ambiguous(self):
        out = rc.interaction_test(7.3, [3, 4], self.T)       # near S
        self.assertEqual(out["outcome"], "BOUNDARY_AMBIGUOUS")
        self.assertIn("RESONANT", out["between"])
        # one party ~0: S ~ M, so near both references
        self.assertEqual(self.o(4.1, (4, 0.2)), "BOUNDARY_AMBIGUOUS")

    def test_exact_additive_is_subadditive_side_without_band(self):
        self.assertEqual(rc.interaction_test(7, [3, 4], 0)["outcome"],
                         "ENHANCED_SUBADDITIVE")
        self.assertEqual(rc.interaction_test(4, [3, 4], 0)["outcome"],
                         "REDUNDANT")

    def test_tol_never_defaulted(self):
        for bad in (None, -1, "0.5", True):
            with self.assertRaises(ValueError, msg=repr(bad)):
                rc.interaction_test(7, [3, 4], bad)

    def test_validate_maps_outcomes(self):
        r = dict(F, **{"state_class": "RESONANT", "tol": self.T, "separate": [3, 4]})
        self.assertEqual(v(**dict(r, joint=10)), "OK")
        for joint in (6, 4.2, 2):
            out = rc.validate(dict(r, joint=joint))
            self.assertEqual(out["verdict"], "CONTRADICTS_CLASS", joint)
        self.assertEqual(v(**dict(r, joint=7.3)), "BOUNDARY_AMBIGUOUS")
        anta = rc.validate(dict(r, joint=2))["findings"]
        self.assertTrue(any("OPEN" in m for _, m in anta))


class TestImmortalInformation(unittest.TestCase):
    def test_information_referent_valid(self):
        i = dict(F, **{"state_class": "IMMORTAL"})
        self.assertEqual(v(**dict(i, referent_type="RELATION_AS_INFORMATION")),
                         "OK")
        self.assertEqual(v(**dict(i, referent_type="MATERIAL")),
                         "CATEGORY_ERROR")

    def test_readability_needs_reader(self):
        i = dict(F, **{"state_class": "IMMORTAL",
                       "referent_type": "RELATION_AS_INFORMATION",
                       "readability": 0.4})
        self.assertEqual(v(**i), "INCOMPLETE")
        self.assertEqual(v(**dict(i, reader="kin, keyed by shared practice")),
                         "OK")

    def test_invariant_recorded_with_correction(self):
        inv = rc.CLASSES["IMMORTAL"]["invariant"]
        self.assertEqual(inv["conserved"], "INFORMATION (global total)")
        self.assertIn("Noether", inv["correction"]["text"])
        self.assertEqual(inv["measurand_candidate"]["status"], "PROPOSED")


class TestEnvironmentIndexed(unittest.TestCase):
    def test_env_change(self):
        self.assertEqual(rc.env_change({"a": 1}, {"a": 1}), [])
        self.assertEqual(rc.env_change({"a": 1}, {"a": 2, "b": 0}), ["a", "b"])
        self.assertEqual(rc.env_change({"a": None}, {}), ["a"])
        self.assertIsNone(rc.env_change(None, {"a": 1}))

    def _r(self, cls, gap, env=None, **refkw):
        d = {"frame": "F1", "state_class": cls, "gap": gap, "relation_type": "kin",
             "observed": OBSERVED}
        if env is not None:
            d["reference"] = ref(env, **refkw)
        return d

    def test_time_only_class_change_contradicts(self):
        env = {"shared_work": True, "household": "same"}
        out = rc.check_switch([self._r("CONTINUOUS", "PT8H", env),
                               self._r("REVISABLE", "P200D", dict(env))])
        self.assertEqual(out["verdict"], "CONTRADICTS_CLASS")
        self.assertEqual(out["transitions"][0]["reference_changed"], [])

    def test_env_driven_change_not_contradiction(self):
        out = rc.check_switch([self._r("CONTINUOUS", "PT8H", {"household": "same"}),
                               self._r("REVISABLE", "P200D", {"household": "moved"})])
        self.assertEqual(out["verdict"], "UNDECLARED_THRESHOLD")  # rule still owed
        self.assertEqual(out["transitions"][0]["reference_changed"],
                         ["env_terms.household"])

    def test_precedence_or_custody_change_counts(self):
        env = {"household": "same"}
        out = rc.check_switch([self._r("CONTINUOUS", "PT8H", env),
                               self._r("REVISABLE", "P200D", env,
                                       custody=("kin", "court"))])
        self.assertEqual(out["transitions"][0]["reference_changed"], ["custody"])
        self.assertNotIn("CONTRADICTS_CLASS", [s for s, _ in out["findings"]])

    def test_no_reference_is_unrated_not_judged(self):
        out = rc.check_switch([self._r("CONTINUOUS", "PT8H"),
                               self._r("REVISABLE", "P200D")])
        self.assertEqual(out["verdict"], "UNRATED")
        self.assertEqual(len(out["unrated"]), 2)
        self.assertNotIn("CONTRADICTS_CLASS", [s for s, _ in out["findings"]])

    def test_time_only_rule_annotated(self):
        rule = {"from": "CONTINUOUS", "to": "REVISABLE",
                "condition": {"reads": ["gap_length", "relation_type"],
                              "threshold": {"kin": {"value": "P90D",
                                                    "unit": "iso8601_duration"}}}}
        out = rc.check_switch([dict(self._r("CONTINUOUS", "PT8H", {}), switch=rule)])
        self.assertTrue(out["rules"]["CONTINUOUS->REVISABLE"]["time_only"])
        env_rule = dict(rule, condition=dict(rule["condition"],
                                             reads=["gap_length", "household"]))
        out = rc.check_switch([dict(self._r("CONTINUOUS", "PT8H", {}),
                                    switch=env_rule)])
        self.assertFalse(out["rules"]["CONTINUOUS->REVISABLE"]["time_only"])


class TestReferenceGate(unittest.TestCase):
    """L1: reference written BEFORE the outcome, or UNRATED."""
    def rec(self, **kw):
        base = dict(F, **{"state_class": "CONTINUOUS", "observed": OBSERVED,
                          "reference": ref({"household": "same"})})
        base.update(kw)
        return base

    def test_written_before_is_ratable(self):
        self.assertEqual(v(**self.rec()), "OK")
        self.assertIsNone(rc.reference_gate(self.rec()))

    def test_unrated_cases(self):
        late = ref({"household": "same"}, written="2026-10-02")
        same = ref({"household": "same"}, written=OBSERVED)
        part = {"env_terms": {}, "precedence": "x", "written": "2026-09-01"}
        undated = dict(ref({}), written=None)
        for bad in (None, late, same, part, undated):
            r = self.rec(reference=bad)
            self.assertEqual(v(**r), "UNRATED", repr(bad))
        self.assertEqual(v(**self.rec(observed="last spring")), "UNRATED")

    def test_datetimes_and_offsets(self):
        r = self.rec(observed="2026-10-01T09:00:00+02:00",
                     reference=ref({}, written="2026-10-01T06:59:00Z"))
        self.assertEqual(v(**r), "OK")          # 06:59Z < 07:00Z
        r = self.rec(observed="2026-10-01T09:00:00+02:00",
                     reference=ref({}, written="2026-10-01T07:00:00Z"))
        self.assertEqual(v(**r), "UNRATED")     # equal, not before

    def test_mixed_history_reports_unrated_readings(self):
        good = {"frame": "F1", "state_class": "CONTINUOUS", "gap": "PT8H",
                "relation_type": "kin", "observed": OBSERVED,
                "reference": ref({"t": 1})}
        bad = dict(good, gap="P5D", reference=None)
        out = rc.check_switch([good, bad])
        self.assertEqual(out["verdict"], "OK")
        self.assertEqual(out["unrated"][0][0], "P5D")


class TestParity(unittest.TestCase):
    """L4: participant-declared class is OBSERVED; disagreement is symmetric."""
    def test_participant_is_observed(self):
        out = rc.validate(dict(F, **{"state_class": "CONTINUOUS",
                                     "class_source": "participant"}))
        self.assertEqual(out["evidence"]["tag"], "OBSERVED")
        self.assertIn("self-report of feeling", out["evidence"]["limits"])
        obs = rc.validate(dict(F, **{"state_class": "CONTINUOUS",
                                     "class_source": "observer"}))
        self.assertEqual(obs["evidence"]["tag"], out["evidence"]["tag"])

    def test_unknown_source_unratified(self):
        self.assertEqual(v(**dict(F, **{"state_class": "CONTINUOUS",
                                        "class_source": "hearsay"})),
                         "UNRATIFIED")

    def test_disagreement_is_adjudicated_by_outcome(self):
        frames = {"relational": "CONTINUOUS", "default": "REVISABLE"}
        pending = rc.compare_frames(frames)
        self.assertEqual(pending["status"], "UNADJUDICATED")
        self.assertIn("prediction test", pending["next_step"])
        # return at the same state after the gap: CONTINUOUS's prediction held
        held = {"consistent_with": ["CONTINUOUS"],
                "basis": "state at return equal to state at leave"}
        out = rc.compare_frames(frames, held)
        self.assertEqual(out["status"], "ADJUDICATED")
        self.assertEqual(out["supported"], ["relational"])
        self.assertEqual(out["not_supported"], ["default"])
        self.assertEqual(out["remaining_cost"], "translation")
        # the adjudicator is the outcome, not the frame: flip the outcome
        decayed = {"consistent_with": ["REVISABLE"],
                   "basis": "lower state at return, reference changed"}
        self.assertEqual(rc.compare_frames(frames, decayed)["supported"],
                         ["default"])

    def test_outcome_edge_cases(self):
        frames = {"a": "CONTINUOUS", "b": "REVISABLE"}
        both = {"consistent_with": ["CONTINUOUS", "REVISABLE"], "basis": "x"}
        self.assertEqual(rc.compare_frames(frames, both)["status"],
                         "OUTCOME_DOES_NOT_SEPARATE")
        none = {"consistent_with": ["IMMORTAL"], "basis": "x"}
        self.assertEqual(rc.compare_frames(frames, none)["status"],
                         "NEITHER_SUPPORTED")
        nobasis = {"consistent_with": ["CONTINUOUS"]}
        self.assertEqual(rc.compare_frames(frames, nobasis)["status"],
                         "UNADJUDICATED")
        self.assertEqual(rc.compare_frames({"a": "IMMORTAL",
                                            "b": "IMMORTAL"})["status"],
                         "AGREE")

    def test_no_symmetric_limit_field(self):
        out = rc.compare_frames({"a": "CONTINUOUS", "b": "REVISABLE"})
        self.assertNotIn("limit_on", out)


class TestDrift(unittest.TestCase):
    """L6: the approximation drifts; the defining relation recovers."""
    def test_exact_value_has_no_drift(self):
        for n in (1, 10, 100):
            self.assertLess(rc.power_drift(rc.PHI, n), 1e-12)

    def test_truncation_compounds(self):
        d = [rc.power_drift(1.618, n) for n in (1, 10, 100, 1000)]
        self.assertTrue(all(a < b for a, b in zip(d, d[1:])))
        self.assertGreater(d[-1], 0.01)       # ~2% off after 1000 steps

    def test_relation_corrects_toward_itself(self):
        e = [rc.relation_recovery(1.618, n) for n in (0, 5, 20)]
        self.assertTrue(e[0] > e[1] > e[2])
        self.assertLess(rc.relation_recovery(1.0, 60), 1e-12)


class TestLimitsAndPredictions(unittest.TestCase):
    def test_every_class_has_a_prediction(self):
        for cid, spec in rc.CLASSES.items():
            self.assertIn(spec["prediction"]["tag"],
                          ("STATED", "DERIVED", "OPEN"), cid)
        self.assertEqual(rc.CLASSES["CONSTITUTIVE"]["prediction"]["tag"], "OPEN")

    def test_doc_limits_section_is_generated(self):
        doc = open(os.path.join(ROOT, "ontology", "relation_classes.md"),
                   encoding="utf-8").read()
        self.assertIn(rc.render_limits(), doc)

    def test_limits_l1_to_l7(self):
        with open(rc.SOURCE, encoding="utf-8") as fh:
            lim = json.load(fh)["limits"]
        self.assertEqual(sorted(k for k in lim if k.startswith("L")),
                         ["L%d" % i for i in range(1, 8)])


class TestTranslation(unittest.TestCase):
    def rec(self, cls, env, contact=(MUTUAL,)):
        return dict(F, **{"state_class": cls, "contact_pattern": list(contact),
                          "observed": OBSERVED, "gap": "P30D",
                          "relation_type": "kin", "reference": ref(env)})

    def test_projection_is_lossy_many_to_one(self):
        a = rc.project_to_default(self.rec("CONTINUOUS", {"season": "on"},
                                           (ANNUAL, MUTUAL)), 0.1)
        b = rc.project_to_default(self.rec("IMMORTAL", {"household": "x"}), 0.1)
        self.assertEqual(a["record"], b["record"])          # not injective
        self.assertEqual(a["record"]["class"], "REVISABLE")
        self.assertEqual(a["record"]["driver"], "t")
        self.assertIn("reference", a["lost"])
        self.assertIn("state_class", a["lost"])
        self.assertIn("contact_pattern", a["lost"])
        # the default frame merges the axes: contact frequency is the state
        self.assertEqual(a["record"]["state_proxy"], "contact_frequency")

    def test_not_recoverable_from_default_data(self):
        d = rc.project_to_default(self.rec("CONTINUOUS", {}, (ANNUAL,)),
                                  0.1)["record"]
        out = rc.lift_to_frame(d)
        self.assertEqual(out["status"], "NOT_RECOVERABLE")
        self.assertEqual(out["missing"], ["state_class", "contact_pattern",
                                          "reference", "frame"])
        partial = rc.lift_to_frame(d, state_class="CONTINUOUS")
        self.assertEqual(partial["missing"], ["contact_pattern", "reference",
                                              "frame"])

    def test_lift_with_supplied_information_validates(self):
        d = rc.project_to_default(self.rec("CONTINUOUS", {}), 0.1)["record"]
        out = rc.lift_to_frame(d, state_class="CONTINUOUS",
                               contact_pattern=[MUTUAL],
                               reference=ref({"household": "same"}),
                               frame="relational")
        self.assertEqual(out["status"], "LIFTED")
        self.assertEqual(out["validation"]["verdict"], "OK")
        # a reference written after the outcome is still refused (L1)
        late = rc.lift_to_frame(d, state_class="CONTINUOUS",
                                contact_pattern=[MUTUAL],
                                reference=ref({}, written="2026-11-01"),
                                frame="relational")
        self.assertEqual(late["validation"]["verdict"], "UNRATED")

    def test_map_recorded_as_partial_and_asymmetric(self):
        with open(rc.SOURCE, encoding="utf-8") as fh:
            tm = json.load(fh)["translation_map"]
        self.assertEqual(tm["status"], "PARTIAL")
        self.assertIn("ASYMMETRIC", tm["cost"])
        merge = tm["default_merges_axes"]
        self.assertIn("contact frequency is used as the state proxy",
                      merge["text"])
        self.assertIn("moon", merge["text"])
        self.assertEqual(merge["dropped"], ["state_class", "contact_pattern"])


class TestFittedLambda(unittest.TestCase):
    """Translation map: a fitted default-frame lambda tracks E, not time."""
    @staticmethod
    def continuous_rows(e_of_t, n=100):
        # CONTINUOUS: c depends on the environment only, c = c(E) = E
        return [(t, e_of_t(t)) for t in range(n)]

    def test_known_answer(self):
        rows = [(t, 2.0 * math.exp(-0.3 * t)) for t in range(10)]
        self.assertAlmostEqual(rc.fit_lambda(rows), 0.3)

    def test_env_step_reproduces_decay_constant_env_does_not(self):
        stepped = self.continuous_rows(lambda t: 1.0 if t < 50 else 0.5)
        held = self.continuous_rows(lambda t: 1.0)
        lam_step = rc.fit_lambda(stepped)
        lam_held = rc.fit_lambda(held)
        self.assertGreater(lam_step, 1e-3)          # looks like decay
        self.assertLess(abs(lam_held), 1e-12)       # no decay, same time span
        self.assertEqual(rc.interpret_fitted_lambda("CONTINUOUS", lam_step,
                                                    1e-4, "state")["flag"],
                         "ENV_DRIFT_IN_SAMPLE")
        self.assertEqual(rc.interpret_fitted_lambda("CONTINUOUS", lam_held,
                                                    1e-4, "state")["flag"],
                         "CONSISTENT")

    def test_same_time_span_different_lambda(self):
        # time is identical in both series; only E differs
        a = rc.fit_lambda(self.continuous_rows(lambda t: 1.0 if t < 50 else 0.5))
        b = rc.fit_lambda(self.continuous_rows(lambda t: 1.0 if t < 50 else 0.25))
        self.assertGreater(b, a)

    def test_per_class_flags(self):
        f = rc.interpret_fitted_lambda
        for cls in ("COUPLED", "IMMORTAL", "CONTINUOUS"):
            self.assertEqual(f(cls, 0.2, 0.01, "state")["flag"],
                             "ENV_DRIFT_IN_SAMPLE")
        # the contact-channel rule keys on contact_pattern, whatever the state
        for cp in ([ANNUAL], [MUTUAL], [ANNUAL, MUTUAL]):
            for cls in ("CONTINUOUS", "REVISABLE"):
                self.assertEqual(f(cls, 0.2, 0.01, "contact", cp)["flag"],
                                 "CONTACT_CHANNEL_ARTIFACT", (cls, cp))
        self.assertEqual(f("CONTINUOUS", 0.2, 0.01, "contact", ["CONSTANT"])
                         ["flag"], "ENV_DRIFT_IN_SAMPLE")
        self.assertEqual(f("IMMORTAL", 0.2, 0.01, "contact", ["NONE"])["flag"],
                         "CATEGORY_ERROR")
        self.assertEqual(f("CONTINUOUS", 0.2, 0.01, "contact")["flag"],
                         "INCOMPLETE")          # contact data, no pattern
        self.assertEqual(f("CONTINUOUS", 0.2, 0.01)["flag"], "INCOMPLETE")
        self.assertEqual(f("CONSTITUTIVE", 0.2, 0.01, "state")["flag"],
                         "CATEGORY_ERROR")
        self.assertEqual(f("REVISABLE", 0.2, 0.01, "state")["flag"],
                         "INCOMPLETE")
        self.assertEqual(f("REVISABLE", 0.2, 0.01, "state",
                           e_range=(0, 1))["flag"], "VALID_IN_RANGE")
        self.assertEqual(f("REVISABLE", 0.2, 0.01, "state", e_range=(0, 1),
                           query_e=3)["flag"], "UNRATED")
        self.assertEqual(f("friend", 0.2, 0.01, "state")["flag"], "UNRATIFIED")
        self.assertEqual(f("CYCLICAL", 0.2, 0.01, "state")["flag"],
                         "UNRATIFIED")
        self.assertEqual(f(None, 0.2, 0.01, "state")["flag"], "UNCLASSED")
        with self.assertRaises(ValueError):
            f("CONTINUOUS", 0.2, None)


class TestTwoAxes(unittest.TestCase):
    """Schema 2 (operator, 2026-10-07): state_class and contact_pattern."""

    GROWN_CHILD = [ANNUAL, MUTUAL]       # CYCLICAL ritual on top of IRREGULAR

    def _r(self, state, gap, **kw):
        return dict({"frame": "F1", "state_class": state, "gap": gap,
                     "relation_type": "kin", "observed": OBSERVED,
                     "reference": ref({"t": gap})}, **kw)

    # dispatch 7a
    def test_continuous_with_cyclical_and_irregular_off_phase_gap(self):
        rec = dict(F, **{"state_class": "CONTINUOUS",
                         "contact_pattern": self.GROWN_CHILD})
        self.assertEqual(v(**rec), "OK")
        # off-phase gap: no decay ...
        self.assertEqual(rc.infer_from_null("CONTINUOUS", self.GROWN_CHILD,
                                            "off"), "NOTHING")
        # ... and an irregular gap outside the ritual phase: no decay either
        self.assertEqual(rc.infer_from_null("CONTINUOUS", self.GROWN_CHILD),
                         "NOTHING")
        # ... and no switch: the off-phase reading is dropped, not judged
        history = [self._r("CONTINUOUS", "PT8H", phase_state="on"),
                   self._r("REVISABLE", "P9M", phase_state="off")]
        out = rc.check_switch(history, declared_state="CONTINUOUS",
                              contact_patterns=self.GROWN_CHILD)
        self.assertEqual(out["verdict"], "OK")
        self.assertEqual(out["transitions"], [])
        self.assertEqual(out["dropped"], [("P9M", "CYCLICAL off-phase")])

    # dispatch 7b
    def test_lambda_fitted_to_contact_counts_is_artifact(self):
        # monthly contact counts: a ritual spike each 12 months, irregular
        # contact thinning out; nothing about the state is in these numbers
        counts = []
        for m in range(36):
            irregular = 3 if m < 12 else (2 if m < 24 else 1)
            ritual = 4 if m % 12 == 0 else 0
            counts.append((m, irregular + ritual))
        lam = rc.fit_lambda(counts)
        self.assertGreater(lam, 0.01)               # reads as "decay"
        out = rc.interpret_fitted_lambda("CONTINUOUS", lam, 1e-3, "contact",
                                         self.GROWN_CHILD)
        self.assertEqual(out["flag"], "CONTACT_CHANNEL_ARTIFACT")
        # the same number declared as a fit on state readings is env drift
        self.assertEqual(rc.interpret_fitted_lambda(
            "CONTINUOUS", lam, 1e-3, "state")["flag"], "ENV_DRIFT_IN_SAMPLE")

    # dispatch 7c
    def test_migrated_cyclical_record_is_unclassed_and_refused(self):
        old = {"frame": "operator", "class": "CYCLICAL", "period": "P1Y",
               "phase": "birthday", "env_index": "calendar"}
        m = rc.migrate(old)
        rec = m["record"]
        self.assertNotIn("class", rec)
        self.assertNotIn("state_class", rec)              # never inferred
        self.assertEqual(rec["contact_pattern"],
                         [{"pattern": "CYCLICAL", "period": "P1Y",
                           "phase": "birthday", "env_index": "calendar"}])
        self.assertEqual(sorted(m["moved"]), ["env_index", "period", "phase"])
        self.assertEqual(rc.validate(rec)["verdict"], "UNCLASSED")
        # refused for decay checks
        self.assertEqual(rc.infer_from_null(rec.get("state_class"),
                                            rec["contact_pattern"], "on"),
                         "UNCLASSED")
        self.assertEqual(rc.interpret_fitted_lambda(
            rec.get("state_class"), 0.2, 0.01, "contact",
            rec["contact_pattern"])["flag"], "UNCLASSED")
        # other schema-1 classes rename; contact is left to declare
        cont = rc.migrate({"frame": "operator", "class": "CONTINUOUS"})["record"]
        self.assertEqual(cont["state_class"], "CONTINUOUS")
        self.assertEqual(rc.validate(cont)["verdict"], "INCOMPLETE")
        self.assertEqual(rc.migrate(cont)["note"], "already schema 2")

    # dispatch 7d
    def test_two_contact_patterns_on_one_relation_valid(self):
        out = rc.validate(dict(F, **{"state_class": "CONTINUOUS",
                                     "contact_pattern": self.GROWN_CHILD}))
        self.assertEqual(out["verdict"], "OK")
        self.assertEqual(out["contact_pattern"], ["CYCLICAL", "IRREGULAR"])
        two_rituals = [ANNUAL, dict(ANNUAL, phase="winter holiday")]
        self.assertEqual(v(**dict(F, **{"state_class": "CONTINUOUS",
                                        "contact_pattern": two_rituals})), "OK")

    def test_contact_pattern_required_no_default(self):
        for blank in (None, "", []):
            out = rc.validate({"frame": "operator", "state_class": "CONTINUOUS",
                               "contact_pattern": blank})
            self.assertEqual(out["verdict"], "INCOMPLETE", repr(blank))
            self.assertTrue(any("contact_pattern" in m
                                for _, m in out["findings"]))

    def test_contact_values_checked(self):
        base = dict(F, **{"state_class": "CONTINUOUS"})
        cases = [
            ([{"pattern": "WEEKLY"}], "UNRATIFIED"),
            (["IRREGULAR"], "INCOMPLETE"),          # interval_set_by owed
            ([{"pattern": "IRREGULAR", "interval_set_by": "fate"}], "UNRATIFIED"),
            (["CONSTANT"], "OK"),
            (["NONE"], "OK"),
            (["NONE", MUTUAL], "CONTRADICTS_CLASS"),
            (MUTUAL, "OK"),                          # one pattern, not a list
        ]
        for cp, want in cases:
            self.assertEqual(v(**dict(base, contact_pattern=cp)), want, cp)
        for who in rc.INTERVAL_SET_BY:
            self.assertEqual(v(**dict(base, contact_pattern=[
                {"pattern": "IRREGULAR", "interval_set_by": who}])), "OK", who)

    def test_immortal_across_death_contact_none(self):
        rec = dict(F, **{"state_class": "IMMORTAL",
                         "referent_type": "RELATION_AS_INFORMATION",
                         "contact_pattern": ["NONE"]})
        self.assertEqual(v(**rec), "OK")
        self.assertEqual(rc.infer_from_null("IMMORTAL", ["NONE"]), "NOTHING")

    def test_e1_contact_type_note_recorded(self):
        with open(rc.SOURCE, encoding="utf-8") as fh:
            tests = {t["id"]: t for t in json.load(fh)["proposed_tests"]}
        e1 = tests["E1_CONTACT_TYPE"]
        self.assertIn("ritual", e1["field"]["text"])
        self.assertIn("irregular", e1["field"]["text"])
        self.assertIn("flat", e1["prediction"]["text"])
        self.assertEqual(e1["gap"]["tag"], "OPEN")


class TestCLI(unittest.TestCase):
    def test_selftest_refused(self):
        self.assertEqual(rc.main(["--selftest"]), 2)


if __name__ == "__main__":
    unittest.main()
