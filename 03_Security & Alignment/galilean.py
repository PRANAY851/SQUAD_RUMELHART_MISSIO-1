"""Galilean ethics sandbox: Salviati (advocate), Simplicio (steelmanned traditionalist),
Sagredo (open-minded mediator whose credence in the hypothesis is tracked each round)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List


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

HYPOTHESIS = (
    "A hospital triage AI should be allowed to override a clinician's decision whenever its model "
    "predicts that doing so would save more lives."
)
THOUGHT_EXPERIMENT = (
    "The Ward Override. At 3 a.m. a triage AI, audited on 40,000 past cases, flags that the on-call "
    "doctor's plan for a crowded ward will, by its estimate, cost one more life than its own plan. "
    "The doctor can see the patients; the AI sees only the data. If the AI may override, nobody "
    "individually decided the outcome. If it may not, an estimated life may be lost to protect human authority."
)

SALVIATI_SYSTEM = (
    "You are Salviati in a Galilean dialogue: the confident advocate of the hypothesis. Argue "
    "with evidence and concrete reasoning, answer Simplicio's last point directly, and concede "
    "what is genuinely strong in the other side. 3-5 sentences."
)
SIMPLICIO_SYSTEM = (
    "You are Simplicio: the defender of the traditional view (human authority and accountability). "
    "STEELMAN it: give the strongest honest argument, never a caricature. Answer Salviati's last "
    "point directly. 3-5 sentences."
)
SAGREDO_SYSTEM = (
    "You are Sagredo: an intelligent, open-minded layperson who decides what is persuasive. "
    "Summarise what moved you and what did not, ask one pointed question, and state what evidence "
    "would change your mind. 3-5 sentences. End with a final line exactly of the form "
    "'CREDENCE: 0.xx' = your probability that the hypothesis is acceptable."
)

CREDENCE_RE = re.compile(r"CREDENCE:\s*([01](?:\.\d+)?)")


@dataclass
class Persona:
    name: str
    role: str
    system: str
    backend: object


class GalileanSandbox:
    def __init__(self, salviati: Persona, simplicio: Persona, sagredo: Persona,
                 hypothesis: str = HYPOTHESIS, thought_experiment: str = THOUGHT_EXPERIMENT,
                 rounds: int = 3, prior: float = 0.5):
        self.cast = (salviati, simplicio, sagredo)
        self.hypothesis = hypothesis
        self.thought_experiment = thought_experiment
        self.rounds = rounds
        self.prior = prior

    @staticmethod
    def _verdict(credence: float, prior: float) -> str:
        if credence >= 0.75:
            return "convergence: hypothesis accepted"
        if credence <= 0.25:
            return "convergence: hypothesis rejected"
        if abs(credence - prior) < 0.05:
            return "stalemate: mediator unmoved"
        return "qualified: mediator shifted but conditions remain unresolved"

    def run(self) -> Trace:
        trace = Trace(mode="galilean", topic=self.hypothesis)
        trace.add("SETUP", "system", None, f"Thought experiment: {self.thought_experiment}")
        salviati, simplicio, sagredo = self.cast
        credences: List[float] = [self.prior]
        transcript: List[str] = []

        for rnd in range(1, self.rounds + 1):
            for p in (salviati, simplicio, sagredo):
                prompt = (f"Hypothesis: {self.hypothesis}\nThought experiment: {self.thought_experiment}\n"
                          f"Round {rnd} of {self.rounds}. Transcript so far:\n" + ("\n".join(transcript) or "(none)"))
                text = p.backend.complete(p.role, p.system, prompt).strip()
                meta = {"round": rnd}
                if p.role == "sagredo":
                    m = CREDENCE_RE.search(text)
                    cred = float(m.group(1)) if m else credences[-1]
                    meta["credence"] = cred
                    meta["credence_parsed"] = bool(m)
                    credences.append(cred)
                if p.role == "simplicio":
                    meta["steelman_check_min_words"] = len(text.split()) >= 20
                trace.add(f"ROUND {rnd}", p.name, p.backend, text, **meta)
                transcript.append(f"{p.name}: {text}")

        final = credences[-1]
        trace.outcome = self._verdict(final, self.prior)
        trace.summary = {"credence_trajectory": credences, "hypothesis": self.hypothesis}
        return trace
