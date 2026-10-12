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
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import mock_galilean

import mock_galilean
from galilean import GalileanSandbox, Persona, SALVIATI_SYSTEM, SIMPLICIO_SYSTEM, SAGREDO_SYSTEM


class GalileanTests(unittest.TestCase):
    def test_three_rounds_and_credence(self):
        b = mock_galilean.galilean_mock()
        cast = [Persona(n, r, s, b[r]) for n, r, s in
                (("Salviati", "salviati", SALVIATI_SYSTEM), ("Simplicio", "simplicio", SIMPLICIO_SYSTEM),
                 ("Sagredo", "sagredo", SAGREDO_SYSTEM))]
        t = GalileanSandbox(*cast).run()
        self.assertEqual(t.summary["credence_trajectory"], [0.5, 0.55, 0.42, 0.48])
        self.assertTrue(t.outcome.startswith("stalemate") or t.outcome.startswith("qualified"))
        self.assertEqual(sum(1 for e in t.events if e.speaker == "Simplicio"), 3)


if __name__ == "__main__":
    unittest.main()
