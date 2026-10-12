"""Socratic elenchus as an explicit state machine.

States: INPUT -> ELICIT -> PROBE -> CHECK -> (PROBE | CONTRADICTION | REFINED)
        CONTRADICTION -> REVISE -> (PROBE | APORIA)
"""
from __future__ import annotations

import json
import re
from enum import Enum
from typing import Dict, List, Optional, Tuple



import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "04_Systems_Architect")
    )
)

from dialogue_trace import Trace


from dialogue_trace import Trace


class State(str, Enum):
    INPUT = "INPUT"
    ELICIT = "ELICIT"
    PROBE = "PROBE"
    CHECK = "CHECK"
    CONTRADICTION = "CONTRADICTION"
    REVISE = "REVISE"
    REFINED = "REFINED"
    APORIA = "APORIA"


QUESTIONER_SYSTEM = (
    "You are a Socratic questioner. You profess ignorance and ONLY ask questions. "
    "Never assert a conclusion, never say the respondent is wrong. Reply with exactly one "
    "short question that ends with a question mark."
)
RESPONDENT_SYSTEM = (
    "You are a thoughtful respondent in a Socratic dialogue. Answer honestly and briefly "
    "(1-3 sentences). If you realise you do not know, say so."
)
JUDGE_SYSTEM = (
    "You check a respondent's commitments for logical inconsistency. Reply with ONLY JSON: "
    '{"contradiction": true|false, "a": "<verbatim commitment>", "b": "<verbatim commitment>"}. '
    "Quote commitments verbatim from the list. Set a and b to empty strings if consistent."
)

ASSERTION_MARKERS = ("therefore", "the answer is", "you are wrong", "this proves", "clearly,")
FALLBACK_QUESTIONS = {
    "elicit": "What exactly do you mean by that?",
    "probe": "Can you give a case where that would not hold?",
}


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"contradiction": False, "a": "", "b": ""}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"contradiction": False, "a": "", "b": ""}


class SocraticEngine:
    def __init__(self, questioner, respondent, judge, max_probes: int = 3, max_revisions: int = 3):
        self.questioner = questioner
        self.respondent = respondent
        self.judge = judge
        self.max_probes = max_probes
        self.max_revisions = max_revisions

    # -- guards ---------------------------------------------------------
    def _question(self, kind: str, prompt: str, trace: Trace, state: str) -> str:
        raw = self.questioner.complete("questioner", QUESTIONER_SYSTEM, prompt).strip()
        low = raw.lower()
        violation = None
        if not raw.endswith("?"):
            violation = "not a question"
        elif any(m in low for m in ASSERTION_MARKERS):
            violation = "contains assertion"
        if violation:
            trace.add(state, "guard", None, f"Questioner output rejected ({violation}); fallback used.", rejected=raw)
            raw = FALLBACK_QUESTIONS[kind]
        trace.add(state, "Questioner", self.questioner, raw)
        return raw

    def _answer(self, role: str, prompt: str, trace: Trace, state: str) -> str:
        ans = self.respondent.complete(role, RESPONDENT_SYSTEM, prompt).strip()
        trace.add(state, "Respondent", self.respondent, ans)
        return ans

    def _check(self, definition: str, commitments: List[str]) -> Tuple[bool, str, str]:
        payload = json.dumps({"definition": definition, "commitments": commitments})
        verdict = _extract_json(self.judge.complete("judge", JUDGE_SYSTEM, payload))
        a, b = verdict.get("a", ""), verdict.get("b", "")
        found = bool(verdict.get("contradiction")) and bool(a) and bool(b)
        return found, a, b

    # -- main loop ------------------------------------------------------
    def run(self, topic: str) -> Trace:
        trace = Trace(mode="socratic", topic=topic)
        state = State.INPUT
        definition = ""
        commitments: List[str] = []
        probes = 0
        revisions = 0
        pair: Tuple[str, str] = ("", "")
        transcript: List[str] = []

        while state not in (State.REFINED, State.APORIA):
            if state is State.INPUT:
                trace.add("INPUT", "system", None, f"Topic received: {topic}")
                state = State.ELICIT

            elif state is State.ELICIT:
                q = self._question("elicit", f"Topic: {topic}\nAsk what the respondent means by the key term.", trace, "ELICIT")
                transcript.append(f"Q: {q}")
                definition = self._answer("respondent", "\n".join(transcript), trace, "ELICIT")
                transcript.append(f"A: {definition}")
                commitments = [definition]
                state = State.PROBE

            elif state is State.PROBE:
                q = self._question(
                    "probe",
                    f"Topic: {topic}\nCurrent definition: {definition}\nAsk ONE probing question using a concrete case.\n"
                    + "\n".join(transcript[-6:]),
                    trace,
                    "PROBE",
                )
                transcript.append(f"Q: {q}")
                ans = self._answer("respondent", "\n".join(transcript[-8:]), trace, "PROBE")
                transcript.append(f"A: {ans}")
                commitments.append(ans)
                probes += 1
                state = State.CHECK

            elif state is State.CHECK:
                found, a, b = self._check(definition, commitments)
                trace.add("CHECK", "Judge", self.judge, "inconsistent" if found else "consistent",
                          probes=probes, revisions=revisions)
                if found:
                    pair = (a, b)
                    state = State.CONTRADICTION
                elif probes >= self.max_probes:
                    state = State.REFINED
                else:
                    state = State.PROBE

            elif state is State.CONTRADICTION:
                q = (f'You said: "{pair[0]}" and also: "{pair[1]}". '
                     "Can both of these hold together, or would you like to revise your view?")
                trace.add("CONTRADICTION", "Questioner (template)", None, q)
                transcript.append(f"Q: {q}")
                state = State.REVISE

            elif state is State.REVISE:
                if revisions >= self.max_revisions:
                    state = State.APORIA
                    continue
                new_def = self._answer(
                    "respondent",
                    "\n".join(transcript[-6:]) + "\nGive a revised definition, or say 'I do not know' if you cannot.",
                    trace,
                    "REVISE",
                )
                transcript.append(f"A: {new_def}")
                revisions += 1
                if re.search(r"\bi (do not|don't) know\b", new_def.lower()):
                    state = State.APORIA
                    continue
                definition = new_def
                commitments = [definition]
                probes = 0
                state = State.PROBE

        final = State(state)
        trace.add(final.value, "system", None,
                  "Definition survived the tests (not proven true)." if final is State.REFINED
                  else "Productive impasse: the respondent cannot yet define the term.")
        trace.outcome = final.value
        trace.summary = {"final_definition": definition if final is State.REFINED else None,
                         "revisions": revisions, "probes_in_last_round": probes}
        return trace
