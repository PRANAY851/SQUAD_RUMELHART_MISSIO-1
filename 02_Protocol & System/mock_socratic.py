"""Offline scripted backends for the Socratic engine (the judge applies a real keyword rule)."""
from __future__ import annotations

import json
from typing import Dict, List


import os
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "04_Lead Architect"
        )
    )
)

from backends import MockBackend, queue_handler as _queue


from backends import MockBackend, queue_handler as _queue


SAMENESS = ("identical", "same")
DIFFERENCE = ("different", "exception", "unequal", "need")


def _judge(payload: str) -> str:
    data = json.loads(payload)
    items: List[str] = data["commitments"]
    for i, a in enumerate(items):
        if not any(w in a.lower() for w in SAMENESS):
            continue
        for b in items[i + 1:]:
            if any(w in b.lower() for w in DIFFERENCE):
                return json.dumps({"contradiction": True, "a": a, "b": b})
    return json.dumps({"contradiction": False, "a": "", "b": ""})


SOCRATIC_TOPIC = "What makes an AI system's decision fair?"


def socratic_mock() -> Dict[str, MockBackend]:
    questioner = MockBackend({"questioner": _queue([
        "When you say an AI decision is fair, what exactly do you mean by fair?",
        "If two applicants have the same record, should the system always give them the same result?",
        "What if one applicant uses a wheelchair and the entrance has stairs; is identical treatment then fair?",
        "Which distinctions between people count as relevant, and who gets to decide?",
        "Would a person's nationality be a relevant distinction for a loan decision?",
        "And what must an affected person be able to do when a distinction is applied to them?",
    ])})
    respondent = MockBackend({"respondent": _queue([
        "A decision is fair when it treats everyone in exactly the same way, with identical rules for all.",
        "Yes. If two applicants have the same record, they must get the same result.",
        "Well, in that case the person has a different need, so an exception seems right.",
        "Then fairness is treating people the same unless there is a relevant distinction I can justify to the person affected.",
        "A relevant distinction is one connected to the purpose of the decision, like a medical condition for a ramp.",
        "Nationality would not be relevant for a loan decision, because it is unrelated to repayment.",
        "The affected person must be able to ask for the reason and challenge it.",
    ])})
    judge = MockBackend({"judge": _judge})
    return {"questioner": questioner, "respondent": respondent, "judge": judge}
