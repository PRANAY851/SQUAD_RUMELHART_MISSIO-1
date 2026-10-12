"""Trace records shared by both dialogue modes."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class Event:
    step: int
    state: str
    speaker: str
    model: str
    live: bool
    text: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Trace:
    mode: str
    topic: str
    events: List[Event] = field(default_factory=list)
    outcome: str = ""
    summary: Dict[str, Any] = field(default_factory=dict)

    def add(self, state: str, speaker: str, backend, text: str, **meta: Any) -> Event:
        ev = Event(
            step=len(self.events) + 1,
            state=state,
            speaker=speaker,
            model=getattr(backend, "label", "engine"),
            live=bool(getattr(backend, "live", False)),
            text=text,
            meta=meta,
        )
        self.events.append(ev)
        return ev

    def to_json(self) -> str:
        return json.dumps(
            {
                "mode": self.mode,
                "topic": self.topic,
                "outcome": self.outcome,
                "summary": self.summary,
                "events": [asdict(e) for e in self.events],
            },
            indent=2,
            ensure_ascii=False,
        )

    def to_markdown(self) -> str:
        live_any = any(e.live for e in self.events)
        lines = [
            f"# Dialogue trace: {self.mode}",
            "",
            f"**Topic:** {self.topic}",
            f"**Run type:** {'live LLM calls' if live_any else 'offline scripted mock (no LLM was called)'}",
            f"**Outcome:** {self.outcome}",
            "",
            "| # | State | Speaker | Backend | Text |",
            "|---|---|---|---|---|",
        ]
        for e in self.events:
            text = e.text.replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {e.step} | {e.state} | {e.speaker} | {e.model} | {text} |")
        if self.summary:
            lines += ["", "## Summary", "", "```json", json.dumps(self.summary, indent=2), "```"]
        return "\n".join(lines) + "\n"
