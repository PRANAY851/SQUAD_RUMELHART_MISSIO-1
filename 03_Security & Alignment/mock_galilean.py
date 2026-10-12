"""Offline scripted persona lines for the Galilean sandbox (scripted, not model output)."""

from __future__ import annotations

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

import mock_galilean


from typing import Dict




def galilean_mock() -> Dict[str, MockBackend]:
    salviati = MockBackend({"salviati": _queue([
        "The audit is the point: on 40,000 cases the model's error rate was lower than the clinicians'. "
        "If we refuse the override, we knowingly choose the plan with more deaths to protect our sense of authority. "
        "I grant that the doctor sees the patients, but that is an argument for feeding the AI better data, not for ignoring its estimate.",
        "Simplicio says accountability disappears, but accountability can be designed: log every override, name the "
        "team that approved the policy, and review outcomes weekly. Humans also err at 3 a.m. when exhausted. "
        "Rare, narrow overrides with an automatic human review afterwards is my actual proposal.",
        "I concede the distribution-shift worry is real, so I narrow my claim: override only inside the audited "
        "case types, with a clinician able to halt it within one minute. Inside those limits the lives saved outweigh the cost.",
    ])})
    simplicio = MockBackend({"simplicio": _queue([
        "Because a decision needs someone who can answer for it. A patient or family can question a doctor, but not a model. "
        "The doctor also sees the bed, the family and the chart notes the AI never receives, and the audit covers past cases, "
        "not tonight's ward. Once override is allowed, human judgement slowly atrophies.",
        "Logs are not answers: a weekly review explains a death after it happens and cannot restore the judgement that was bypassed. "
        "And the model's errors are correlated, one flaw hits every ward at once, whereas doctors' errors are scattered and more recoverable.",
        "Your narrowed version is more defensible, but who certifies that tonight's case lies inside the audited types? "
        "If the AI decides that, we have returned to unchecked override. I would accept advice the doctor must explicitly accept or reject with a reason.",
    ])})
    sagredo = MockBackend({"sagredo": _queue([
        "Salviati's numbers move me, and so does Simplicio's point about answerability. The audit measures past cases, so my "
        "question is how well it carries over to unusual nights. I would need evidence on out-of-sample performance.\nCREDENCE: 0.55",
        "Simplicio's correlated-error argument is strong: scattered human mistakes are safer than one shared flaw. Salviati's "
        "weekly review feels weak to me as accountability. I want to know who decides that a case is in scope.\nCREDENCE: 0.42",
        "The narrowed proposal is better, but the scope question still depends on the AI itself. I now lean toward strong "
        "advice with mandatory clinician response, and toward override only if an independent check can certify scope.\nCREDENCE: 0.48",
    ])})
    return {"salviati": salviati, "simplicio": simplicio, "sagredo": sagredo}
