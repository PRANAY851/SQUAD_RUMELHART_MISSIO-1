"""04_dialogic_engine.py - AURA Dialogic Engine entry point.

Sibling role folders (02 Socratic, 03 Galilean, 04 shared) are put on the Python path.
Offline:  python 04_dialogic_engine.py --mode both
Live:     python 04_dialogic_engine.py --mode both --live   (needs API keys)
Traces go to 02_Protocol_Officer/traces and 03_Security_Sentinel/traces unless --out is given.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for _d in ("02_Protocol_Officer", "03_Security_Sentinel", "04_Systems_Architect"):
    sys.path.insert(0, str(ROOT / _d))

from backends import BackendError, make_live_backend

import os
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "03_Security & Alignment"
        )
    )
)

from galilean import (SAGREDO_SYSTEM, SALVIATI_SYSTEM, SIMPLICIO_SYSTEM, GalileanSandbox, Persona)

import os
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "02_Protocol & System"
        )
    )
)
from socratic import SocraticEngine
import mock_galilean
import mock_socratic

# Default model-to-role assignment for --live runs (override with flags).
DEFAULTS = {"questioner": "claude", "respondent": "openai", "judge": "gemini",
            "salviati": "claude", "simplicio": "openai", "sagredo": "gemini"}


def run_socratic(live: bool, assign: dict, max_probes: int):
    if live:
        b = {r: make_live_backend(assign[r]) for r in ("questioner", "respondent", "judge")}
        topic = "What makes an AI system's decision fair?"
    else:
        b = mock_socratic.socratic_mock()
        topic = mock_socratic.SOCRATIC_TOPIC
    return SocraticEngine(b["questioner"], b["respondent"], b["judge"], max_probes=max_probes).run(topic)


def run_galilean(live: bool, assign: dict, rounds: int):
    systems = {"salviati": SALVIATI_SYSTEM, "simplicio": SIMPLICIO_SYSTEM, "sagredo": SAGREDO_SYSTEM}
    names = {"salviati": "Salviati", "simplicio": "Simplicio", "sagredo": "Sagredo"}
    b = ({r: make_live_backend(assign[r]) for r in systems} if live else mock_galilean.galilean_mock())
    cast = {r: Persona(names[r], r, systems[r], b[r]) for r in systems}
    return GalileanSandbox(cast["salviati"], cast["simplicio"], cast["sagredo"], rounds=rounds).run()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="aura_dialogic", description="AURA Dialogic Engine")
    ap.add_argument("--mode", choices=["socratic", "galilean", "both"], default="both")
    ap.add_argument("--live", action="store_true",
                    help="call real LLMs (needs GEMINI_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY)")
    ap.add_argument("--out", default=None, help="override trace directory (default: each role folder's traces/)")
    ap.add_argument("--max-probes", type=int, default=3)
    ap.add_argument("--rounds", type=int, default=3)
    for role, prov in DEFAULTS.items():
        ap.add_argument(f"--{role}", choices=["gemini", "openai", "claude"], default=prov)
    args = ap.parse_args(argv)
    assign = {r: getattr(args, r) for r in DEFAULTS}

    default_dirs = {"socratic": ROOT / "02_Protocol_Officer" / "traces",
                    "galilean": ROOT / "03_Security_Sentinel" / "traces"}
    tag = "live" if args.live else "mock"
    traces = []
    try:
        if args.mode in ("socratic", "both"):
            traces.append(run_socratic(args.live, assign, args.max_probes))
        if args.mode in ("galilean", "both"):
            traces.append(run_galilean(args.live, assign, args.rounds))
    except BackendError as exc:
        print(f"Backend error: {exc}", file=sys.stderr)
        return 2

    for t in traces:
        out = Path(args.out) if args.out else default_dirs[t.mode]
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{t.mode}_{tag}.md").write_text(t.to_markdown(), encoding="utf-8")
        (out / f"{t.mode}_{tag}.json").write_text(t.to_json(), encoding="utf-8")
        print(f"[{t.mode}] outcome: {t.outcome}")
        for e in t.events:
            print(f"  {e.step:>2} {e.state:<13} {e.speaker:<20} {e.text[:110]}")
    print(f"\nTraces written ({tag} run). Default: 02_Protocol_Officer/traces and 03_Security_Sentinel/traces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
