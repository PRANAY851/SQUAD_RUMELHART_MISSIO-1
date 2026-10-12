import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for d in ("02_Protocol_Officer", "03_Security_Sentinel", "04_Systems_Architect"):
    sys.path.insert(0, str(ROOT / d))

import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import mock_socratic

import mock_socratic
from backends import MockBackend
from socratic import SocraticEngine


def socratic(max_revisions=3, max_probes=3):
    b = mock_socratic.socratic_mock()
    return SocraticEngine(b["questioner"], b["respondent"], b["judge"],
                          max_probes=max_probes, max_revisions=max_revisions).run(mock_socratic.SOCRATIC_TOPIC)


class SocraticTests(unittest.TestCase):
    def test_contradiction_revise_then_refined(self):
        t = socratic()
        states = [e.state for e in t.events]
        self.assertEqual(t.outcome, "REFINED")
        self.assertEqual(states.count("CONTRADICTION"), 1)
        self.assertEqual(states.count("REVISE"), 1)
        self.assertIn("same", t.summary["final_definition"])

    def test_aporia_when_no_revisions_allowed(self):
        self.assertEqual(socratic(max_revisions=0).outcome, "APORIA")

    def test_questioner_only_asks_questions(self):
        for e in socratic().events:
            if e.speaker == "Questioner":
                self.assertTrue(e.text.endswith("?"), e.text)

    def test_guard_rejects_assertion(self):
        b = mock_socratic.socratic_mock()
        bad_q = MockBackend({"questioner": lambda _p: "Therefore you are wrong."})
        t = SocraticEngine(bad_q, b["respondent"], b["judge"], max_probes=1).run("x")
        self.assertTrue(any(e.speaker == "guard" for e in t.events))


if __name__ == "__main__":
    unittest.main()
