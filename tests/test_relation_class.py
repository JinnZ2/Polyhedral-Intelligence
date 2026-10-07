"""Tests for ontology/relation_class.py. Stdlib unittest; run from repo root:

    python3 -m unittest tests/test_relation_class.py
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ontology"))

import relation_class as rc  # noqa: E402

F = {"frame": "operator"}


def ref(env, written="2026-09-01", precedence="declarer", custody=("kin",)):
    """A reference written before the default outcome date (L1)."""
    return {"env_terms": dict(env), "precedence": precedence,
            "custody": list(custody), "written": written}


OBSERVED = "2026-10-01"


def v(**kw):
    return rc.validate(kw)["verdict"]


class TestSource(unittest.TestCase):
    def test_seven_classes_from_json(self):
        with open(rc.SOURCE, encoding="utf-8") as fh:
            ids = [c["id"] for c in json.load(fh)["classes"]]
        self.assertEqual(ids, ["COUPLED", "CONTINUOUS", "REVISABLE",
                               "CONSTITUTIVE", "CYCLICAL", "RESONANT",
                               "IMMORTAL"])
        self.assertEqual(set(ids), set(rc.CLASSES))

    def test_every_text_field_tagged(self):
        for cid, spec in rc.CLASSES.items():
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
                    "immortal", "Resonant"):
            self.assertEqual(v(**dict(F, **{"class": old})), "UNRATIFIED", old)

    def test_absent_class_is_unclassed_never_defaulted(self):
        for blank in (None, ""):
            self.assertEqual(v(**dict(F, **{"class": blank})), "UNCLASSED")
        self.assertEqual(rc.validate(dict(F))["verdict"], "UNCLASSED")
        self.assertIsNone(rc.validate(dict(F))["class"])


class TestFrame(unittest.TestCase):
    def test_frame_required_everywhere_but_constitutive(self):
        for cls in ("CONTINUOUS", "COUPLED"):
            out = rc.validate({"class": cls})
            self.assertEqual(out["verdict"], "INCOMPLETE")
            self.assertTrue(any("frame" in m for _, m in out["findings"]))
        self.assertEqual(v(**dict(F, **{"class": "CONTINUOUS"})), "OK")
        self.assertNotIn("FRAME_UNDECLARED", rc.PRECEDENCE)


class TestClasses(unittest.TestCase):
    def test_coupled(self):
        self.assertEqual(v(**dict(F, **{"class": "COUPLED", "decay": "none"})), "OK")
        self.assertEqual(v(**dict(F, **{"class": "COUPLED", "decay": 0.1})), "CONTRADICTS_CLASS")

    def test_continuous_zero_by_standing(self):
        self.assertEqual(v(**dict(F, **{"class": "CONTINUOUS", "decay": 0})), "OK")
        self.assertEqual(v(**dict(F, **{"class": "CONTINUOUS", "decay": 0.2})), "CONTRADICTS_CLASS")

    def test_revisable(self):
        base = dict(F, **{"class": "REVISABLE", "last_checked": "2026-10-07"})
        self.assertEqual(v(**dict(base, decay=0.3)), "OK")
        self.assertEqual(v(**dict(base, decay=0)), "CONTRADICTS_CLASS")
        self.assertEqual(v(**dict(base, status_inherited=True)),
                         "CONTRADICTS_CLASS")
        self.assertEqual(v(**dict(F, **{"class": "REVISABLE"})), "INCOMPLETE")

    def test_constitutive_decay_is_category_error_not_zero(self):
        self.assertEqual(v(**{"class": "CONSTITUTIVE", "decay": 0}), "CATEGORY_ERROR")
        self.assertEqual(v(**{"class": "CONSTITUTIVE"}), "OPEN_CLASS")

    def test_cyclical(self):
        full = dict(F, **{"class": "CYCLICAL", "period": "1 y",
                          "phase": "spring", "env_index": "day length",
                          "cycling_quantity": "observability"})
        self.assertEqual(v(**full), "OK")
        # held state: a cycling coupling is environment-indexed, not CYCLICAL
        self.assertEqual(v(**dict(full, cycling_quantity="coupling")),
                         "CONTRADICTS_CLASS")
        self.assertEqual(v(**dict(full, cycling_quantity="phase")), "UNRATIFIED")
        no_cq = dict(full)
        del no_cq["cycling_quantity"]
        self.assertEqual(v(**no_cq), "OK")   # optional now
        self.assertEqual(v(**dict(F, **{"class": "CYCLICAL"})), "INCOMPLETE")
        self.assertEqual(rc.read_cyclical_absence("off"), "EXPECTED")
        self.assertEqual(rc.read_cyclical_absence("on"), "SIGNAL")
        self.assertEqual(rc.read_cyclical_absence(None), "INCOMPLETE")

    def test_resonant_needs_interaction_term(self):
        r = dict(F, **{"class": "RESONANT", "tol": 0.5})
        self.assertEqual(v(**dict(r, joint=10, separate=[3, 4])), "OK")
        self.assertEqual(v(**dict(F, **{"class": "RESONANT", "joint": 10,
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
            {"class": "COUPLED", "decay": 0.1},
            {"class": "CONTINUOUS", "decay": 0.2},
            {"class": "REVISABLE", "decay": -1, "status_inherited": True},
            {"class": "CYCLICAL", "cycling_quantity": "x"},
            {"class": "RESONANT", "joint": 1, "separate": [3, 4], "tol": 0.1},
        ]
        for c in cases:
            states = [s for s, _ in rc.validate(dict(F, **c))["findings"]]
            self.assertNotIn("CONFLICT", states, c)

    def test_resonant_additive_method_flagged(self):
        for m in rc.CLASSES["RESONANT"]["additive_methods"]:
            out = rc.validate(dict(F, **{"class": "RESONANT", "method": m,
                                         "interaction_status": "UNMEASURED"}))
            self.assertTrue(any("FALSE_ZERO_RISK" in msg
                                for _, msg in out["findings"]), m)

    def test_immortal_referents(self):
        i = dict(F, **{"class": "IMMORTAL"})
        self.assertEqual(v(**dict(i, referent_type="ENERGY")), "OK")
        self.assertEqual(v(**dict(i, referent_type="RELATION_AS_ENERGY")), "OK")
        self.assertEqual(v(**dict(i, referent_type="MATERIAL")), "CATEGORY_ERROR")
        self.assertEqual(v(**i), "INCOMPLETE")
        self.assertEqual(v(**dict(i, referent_type="EMOTION_SENSOR")), "INCOMPLETE")


class TestNulls(unittest.TestCase):
    def test_off_phase_null_licenses_nothing(self):
        self.assertEqual(rc.infer_from_null("CYCLICAL", "off"), "NOTHING")
        self.assertEqual(rc.infer_from_null("CYCLICAL", "on"), "SIGNAL")
        self.assertEqual(rc.infer_from_null("CYCLICAL"), "INCOMPLETE")
        for c in ("IMMORTAL", "COUPLED", "CONTINUOUS"):
            self.assertEqual(rc.infer_from_null(c), "NOTHING", c)
        self.assertEqual(rc.infer_from_null("REVISABLE"), "EVIDENCE_OF_DECAY")
        self.assertEqual(rc.infer_from_null("CONSTITUTIVE"), "CATEGORY_ERROR")
        self.assertEqual(rc.infer_from_null(None), "UNCLASSED")
        self.assertEqual(rc.infer_from_null("friend"), "UNRATIFIED")


class TestInversion(unittest.TestCase):
    def test_spearman_known_answers(self):
        self.assertAlmostEqual(rc.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(rc.spearman([1, 2, 3, 4], [40, 30, 20, 10]), -1.0)
        self.assertIsNone(rc.spearman([1, 2], [1, 2]))
        self.assertIsNone(rc.spearman([1, 1, 1], [1, 2, 3]))

    def test_per_class_never_pooled(self):
        rows = (
            [{"class": "REVISABLE", "declared_strength": s, "contact_proxy": s}
             for s in (1, 2, 3, 4)] +
            [{"class": "CYCLICAL", "declared_strength": s, "contact_proxy": -s}
             for s in (1, 2, 3, 4)] +
            [{"class": "IMMORTAL", "declared_strength": 5, "contact_proxy": 1}] +
            [{"class": None, "declared_strength": 3, "contact_proxy": 3}]
        )
        out = rc.inversion_test(rows)
        self.assertIsNone(out["pooled"])
        self.assertAlmostEqual(out["per_class"]["REVISABLE"]["rho"], 1.0)
        self.assertAlmostEqual(out["per_class"]["CYCLICAL"]["rho"], -1.0)
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
    RULE = {"from": "CYCLICAL", "to": "REVISABLE",
            "condition": {"reads": ["gap_length", "relation_type"],
                          "threshold": _thr(kin="P3M", colleague="PT8H")}}

    def _held(self, **kw):
        base = dict(F, **{"class": "CYCLICAL", "period": "1 d",
                          "phase": "workday", "env_index": "work schedule",
                          "cycling_quantity": "observability"})
        base.update(kw)
        return base

    def test_declared_switch_passes(self):
        self.assertEqual(v(**self._held(switch=self.RULE)), "OK")

    def test_switch_without_condition_flagged(self):
        sw = {"from": "CYCLICAL", "to": "REVISABLE"}
        self.assertEqual(v(**self._held(switch=sw)), "UNDECLARED_THRESHOLD")
        self.assertEqual(v(**self._held(switch=True)), "UNDECLARED_THRESHOLD")
        vague = dict(self.RULE, condition={"reads": ["gap_length"]})
        self.assertEqual(v(**self._held(switch=vague)), "UNDECLARED_THRESHOLD")

    def test_switch_bad_classes(self):
        self.assertEqual(v(**self._held(switch=dict(self.RULE, to="decay"))),
                         "UNRATIFIED")

    def test_same_class_rule_is_malformed_not_conflict(self):
        same = dict(self.RULE, to="CYCLICAL")
        self.assertEqual(v(**self._held(switch=same)), "MALFORMED_RULE")
        out = rc.check_switch([{"frame": "F1", "class": "CYCLICAL",
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
        return dict({"frame": "F1", "class": cls, "gap": gap,
                     "relation_type": rt, "observed": OBSERVED,
                     "reference": ref({"t": gap})}, **kw)

    def test_undeclared_switch_detected(self):
        out = rc.check_switch([self._r("REVISABLE", "P4M"),
                               self._r("CYCLICAL", "PT8H")])
        self.assertEqual(out["verdict"], "UNDECLARED_THRESHOLD")
        same = rc.check_switch([self._r("CYCLICAL", "PT8H"),
                                self._r("CYCLICAL", "PT9H")])
        self.assertEqual(same["verdict"], "OK")

    def test_declared_and_followed(self):
        out = rc.check_switch([self._r("CYCLICAL", "PT8H", switch=self.RULE),
                               self._r("REVISABLE", "P4M")])
        self.assertEqual(out["verdict"], "OK")

    def test_declared_not_followed(self):
        # kin threshold P3M: still CYCLICAL at P4M -> rule says REVISABLE
        late = rc.check_switch([self._r("CYCLICAL", "PT8H", switch=self.RULE),
                                self._r("CYCLICAL", "P4M")], min_n=1)
        self.assertEqual(late["verdict"], "DECLARED_NOT_FOLLOWED")
        # switched early: REVISABLE at P1M, below the P3M threshold
        early = rc.check_switch([self._r("CYCLICAL", "PT8H", switch=self.RULE),
                                 self._r("REVISABLE", "P1M")], min_n=1)
        self.assertEqual(early["verdict"], "DECLARED_NOT_FOLLOWED")
        self.assertEqual([p["status"] for p in early["per_reading"]],
                         ["MATCH", "MISMATCH"])

    def test_min_n_gates_relation_verdict(self):
        hist = [self._r("CYCLICAL", "PT8H", switch=self.RULE),
                self._r("CYCLICAL", "P4M"), self._r("CYCLICAL", "P5M"),
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
        out = rc.check_switch([self._r("CYCLICAL", "PT8H", switch=self.RULE),
                               self._r("REVISABLE", "P4M")], min_n=1)
        self.assertEqual(out["mismatch"]["mismatches"], 0)
        self.assertEqual(out["mismatch"]["rate"], 0.0)
        empty = rc.check_switch([self._r("CYCLICAL", "PT8H")], min_n=1)
        self.assertIsNone(empty["mismatch"]["rate"])   # nothing tested

    def test_calendar_band_gives_no_verdict(self):
        # P3M band is 84..93 d; P88D sits inside it
        inside = rc.check_switch([self._r("CYCLICAL", "PT8H", switch=self.RULE),
                                  self._r("REVISABLE", "P88D")], min_n=1)
        self.assertEqual(inside["verdict"], "BOUNDARY_AMBIGUOUS")
        self.assertEqual(inside["per_reading"][1]["status"],
                         "BOUNDARY_AMBIGUOUS")
        self.assertIsNone(inside["per_reading"][1]["expected"])
        self.assertEqual(inside["mismatch"]["tested"], 1)
        # same reading against a day-denominated rule: decided
        day_rule = dict(self.RULE, condition={
            "reads": ["gap_length"], "threshold": _thr(kin="P90D")})
        decided = rc.check_switch([self._r("CYCLICAL", "PT8H", switch=day_rule),
                                   self._r("REVISABLE", "P88D")], min_n=1)
        self.assertEqual(decided["verdict"], "DECLARED_NOT_FOLLOWED")
        # just outside the band on either side is decided
        below = rc.check_switch([self._r("CYCLICAL", "PT8H", switch=self.RULE),
                                 self._r("CYCLICAL", "P83D")], min_n=1)
        self.assertEqual(below["verdict"], "OK")
        above = rc.check_switch([self._r("CYCLICAL", "PT8H", switch=self.RULE),
                                 self._r("REVISABLE", "P93D")], min_n=1)
        self.assertEqual(above["verdict"], "OK")

    def test_threshold_is_keyed_by_relation_type(self):
        # colleague threshold PT8H: REVISABLE at P1D is what the rule says
        ok = rc.check_switch([self._r("CYCLICAL", "PT1H", "colleague",
                                      switch=self.RULE),
                              self._r("REVISABLE", "P1D", "colleague")])
        self.assertEqual(ok["verdict"], "OK")
        uncovered = rc.check_switch([self._r("CYCLICAL", "PT1H", "neighbour",
                                             switch=self.RULE),
                                     self._r("REVISABLE", "P1D", "neighbour")])
        self.assertEqual(uncovered["verdict"], "UNDECLARED_THRESHOLD")

    def test_disagreeing_rules_malformed(self):
        other = dict(self.RULE, condition={"reads": ["gap_length"],
                                           "threshold": _thr(kin="P6M")})
        out = rc.check_switch([self._r("CYCLICAL", "PT8H", switch=self.RULE),
                               self._r("CYCLICAL", "PT9H", switch=other)])
        self.assertEqual(out["verdict"], "MALFORMED_RULE")

    def test_non_iso_gap_excluded(self):
        out = rc.check_switch([self._r("CYCLICAL", 8)])
        self.assertEqual(out["verdict"], "INCOMPLETE")

    # --- pre-filter -------------------------------------------------------

    def test_seasonal_gap_is_not_a_switch(self):
        history = [self._r("CYCLICAL", "PT8H", phase_state="on"),
                   self._r("REVISABLE", "P5M", phase_state="off")]
        out = rc.check_switch(history, declared_class="CYCLICAL")
        self.assertEqual(out["verdict"], "OK")
        self.assertEqual(out["dropped"], [("P5M", "CYCLICAL off-phase")])
        # control: same readings, no declared class -> the false switch fires
        self.assertEqual(rc.check_switch(history)["verdict"],
                         "UNDECLARED_THRESHOLD")

    def test_immortal_form_change_dropped(self):
        history = [self._r("IMMORTAL", "P1Y"),
                   self._r("REVISABLE", "P2Y", form_change=True)]
        out = rc.check_switch(history, declared_class="IMMORTAL")
        self.assertEqual(out["verdict"], "OK")
        self.assertEqual(len(out["dropped"]), 1)
        # off-phase flag means nothing for an IMMORTAL relation
        kept = rc.check_switch([self._r("IMMORTAL", "P1Y"),
                                self._r("REVISABLE", "P2Y", phase_state="off")],
                               declared_class="IMMORTAL")
        self.assertEqual(kept["verdict"], "UNDECLARED_THRESHOLD")

    def test_history_across_frames_is_conflict(self):
        out = rc.check_switch([self._r("CYCLICAL", "PT1H"),
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
        r = dict(F, **{"class": "RESONANT", "tol": self.T, "separate": [3, 4]})
        self.assertEqual(v(**dict(r, joint=10)), "OK")
        for joint in (6, 4.2, 2):
            out = rc.validate(dict(r, joint=joint))
            self.assertEqual(out["verdict"], "CONTRADICTS_CLASS", joint)
        self.assertEqual(v(**dict(r, joint=7.3)), "BOUNDARY_AMBIGUOUS")
        anta = rc.validate(dict(r, joint=2))["findings"]
        self.assertTrue(any("OPEN" in m for _, m in anta))


class TestImmortalInformation(unittest.TestCase):
    def test_information_referent_valid(self):
        i = dict(F, **{"class": "IMMORTAL"})
        self.assertEqual(v(**dict(i, referent_type="RELATION_AS_INFORMATION")),
                         "OK")
        self.assertEqual(v(**dict(i, referent_type="MATERIAL")),
                         "CATEGORY_ERROR")

    def test_readability_needs_reader(self):
        i = dict(F, **{"class": "IMMORTAL",
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
        d = {"frame": "F1", "class": cls, "gap": gap, "relation_type": "kin",
             "observed": OBSERVED}
        if env is not None:
            d["reference"] = ref(env, **refkw)
        return d

    def test_time_only_class_change_contradicts(self):
        env = {"shared_work": True, "household": "same"}
        out = rc.check_switch([self._r("CYCLICAL", "PT8H", env),
                               self._r("REVISABLE", "P200D", dict(env))])
        self.assertEqual(out["verdict"], "CONTRADICTS_CLASS")
        self.assertEqual(out["transitions"][0]["reference_changed"], [])

    def test_env_driven_change_not_contradiction(self):
        out = rc.check_switch([self._r("CYCLICAL", "PT8H", {"household": "same"}),
                               self._r("REVISABLE", "P200D", {"household": "moved"})])
        self.assertEqual(out["verdict"], "UNDECLARED_THRESHOLD")  # rule still owed
        self.assertEqual(out["transitions"][0]["reference_changed"],
                         ["env_terms.household"])

    def test_precedence_or_custody_change_counts(self):
        env = {"household": "same"}
        out = rc.check_switch([self._r("CYCLICAL", "PT8H", env),
                               self._r("REVISABLE", "P200D", env,
                                       custody=("kin", "court"))])
        self.assertEqual(out["transitions"][0]["reference_changed"], ["custody"])
        self.assertNotIn("CONTRADICTS_CLASS", [s for s, _ in out["findings"]])

    def test_no_reference_is_unrated_not_judged(self):
        out = rc.check_switch([self._r("CYCLICAL", "PT8H"),
                               self._r("REVISABLE", "P200D")])
        self.assertEqual(out["verdict"], "UNRATED")
        self.assertEqual(len(out["unrated"]), 2)
        self.assertNotIn("CONTRADICTS_CLASS", [s for s, _ in out["findings"]])

    def test_time_only_rule_annotated(self):
        rule = {"from": "CYCLICAL", "to": "REVISABLE",
                "condition": {"reads": ["gap_length", "relation_type"],
                              "threshold": {"kin": {"value": "P90D",
                                                    "unit": "iso8601_duration"}}}}
        out = rc.check_switch([dict(self._r("CYCLICAL", "PT8H", {}), switch=rule)])
        self.assertTrue(out["rules"]["CYCLICAL->REVISABLE"]["time_only"])
        env_rule = dict(rule, condition=dict(rule["condition"],
                                             reads=["gap_length", "household"]))
        out = rc.check_switch([dict(self._r("CYCLICAL", "PT8H", {}),
                                    switch=env_rule)])
        self.assertFalse(out["rules"]["CYCLICAL->REVISABLE"]["time_only"])


class TestReferenceGate(unittest.TestCase):
    """L1: reference written BEFORE the outcome, or UNRATED."""
    def rec(self, **kw):
        base = dict(F, **{"class": "CONTINUOUS", "observed": OBSERVED,
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
        good = {"frame": "F1", "class": "CYCLICAL", "gap": "PT8H",
                "relation_type": "kin", "observed": OBSERVED,
                "reference": ref({"t": 1})}
        bad = dict(good, gap="P5D", reference=None)
        out = rc.check_switch([good, bad])
        self.assertEqual(out["verdict"], "OK")
        self.assertEqual(out["unrated"][0][0], "P5D")


class TestParity(unittest.TestCase):
    """L4: participant-declared class is OBSERVED; disagreement is symmetric."""
    def test_participant_is_observed(self):
        out = rc.validate(dict(F, **{"class": "CONTINUOUS",
                                     "class_source": "participant"}))
        self.assertEqual(out["evidence"]["tag"], "OBSERVED")
        self.assertIn("self-report of feeling", out["evidence"]["limits"])
        obs = rc.validate(dict(F, **{"class": "CONTINUOUS",
                                     "class_source": "observer"}))
        self.assertEqual(obs["evidence"]["tag"], out["evidence"]["tag"])

    def test_unknown_source_unratified(self):
        self.assertEqual(v(**dict(F, **{"class": "CONTINUOUS",
                                        "class_source": "hearsay"})),
                         "UNRATIFIED")

    def test_disagreement_limits_both_frames(self):
        out = rc.compare_frames({"relational": "CYCLICAL",
                                 "default": "REVISABLE"})
        self.assertFalse(out["agree"])
        self.assertEqual(out["limit_on"], ["default", "relational"])
        same = rc.compare_frames({"a": "IMMORTAL", "b": "IMMORTAL"})
        self.assertEqual(same["limit_on"], [])
        swapped = rc.compare_frames({"default": "REVISABLE",
                                     "relational": "CYCLICAL"})
        self.assertEqual(swapped["limit_on"], out["limit_on"])


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


class TestCLI(unittest.TestCase):
    def test_selftest_refused(self):
        self.assertEqual(rc.main(["--selftest"]), 2)


if __name__ == "__main__":
    unittest.main()
