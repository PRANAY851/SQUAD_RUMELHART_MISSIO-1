"""Runs the tests owned by folders 02 and 03."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
suite = unittest.TestSuite()
for d in ("02_Protocol & System", "03_Security & Alignment"):
    suite.addTests(unittest.defaultTestLoader.discover(str(ROOT / d / "tests")))
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
