"""Offline tests of the checks (no model needed): python -m unittest test_checks"""
import unittest
from pathlib import Path

import postmortem as pm

HERE = Path(__file__).parent


def narrative(**kw):
    base = dict(summary="", impact="", root_cause="", contributing_factors=[],
                action_items=[pm.ActionItem(action="Add a pool size check", owner_role="backend lead",
                                            priority="P1")])
    base.update(kw)
    return pm.Narrative(**base)


class ChecksTest(unittest.TestCase):
    def setUp(self):
        self.events, self.facts, self.names, self.masked = pm.prepare(HERE / "incidents" / "checkout-outage")

    def test_timeline_and_masking(self):
        self.assertEqual((len(self.events), self.masked), (24, 5))
        self.assertEqual(self.facts["impact_minutes"], 40)
        self.assertIn("db_password=<SECRET>", self.events[15].text)
        self.assertEqual(self.events[13].text, "the backend engineer forgot to check the prod value, classic")

    def test_duration_reads_hours_and_minutes(self):
        self.assertIn(("duration", 75), pm.values_in("lasted 1 hour and 15 minutes"))
        self.assertIn(("duration", 40), pm.values_in("a 40-minute outage"))

    def test_wrong_duration_and_impact(self):
        n = narrative(impact="Checkout failed from 14:06 to 14:46 UTC, for 45 minutes.")
        r = pm.check_numbers(n, self.events, self.facts)
        self.assertEqual(r["wrong_durations"], ["impact: 45 minutes"])
        self.assertFalse(r["impact_ok"])

    def test_real_time_in_wrong_place_passes(self):
        n = narrative(summary="The incident began at 13:48 UTC.")  # a real time, wrong meaning
        r = pm.check_numbers(n, self.events, self.facts)
        self.assertEqual(r["unsupported"], [])

    def test_blame_flags(self):
        n = narrative(contributing_factors=[
            "The backend engineer did not verify the production configuration before deploying the change (E14). (E2, E13)"])
        flags = pm.flag_wording(n, self.names)
        self.assertEqual(flags, ["factor 1: a person as the subject of a failure 'engineer did not'"])

    def test_one_owner_rule_flags_and_in_a_role_name(self):
        n = narrative(action_items=[pm.ActionItem(action="Add an alert", priority="P2",
                                                  owner_role="Monitoring and Alerting Team Lead")])
        self.assertEqual(len(pm.flag_wording(n, self.names)), 1)


if __name__ == "__main__":
    unittest.main()
