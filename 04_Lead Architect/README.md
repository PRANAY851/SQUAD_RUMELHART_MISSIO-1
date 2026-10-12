# 04 Systems Architect: AURA Dialogic Engine

**Station role:** Systems Architect

Runs both dialogue modes. Pure standard library, Python 3.9+.

```bash
cd 04_Systems_Architect
python run_tests.py                          # 5 tests (owned by folders 02 and 03)
python 04_dialogic_engine.py --mode both     # offline scripted run
python 04_dialogic_engine.py --mode both --live   # real Gemini / OpenAI / Claude (needs keys)
```

Traces are written into `02_Protocol_Officer/traces/` and `03_Security_Sentinel/traces/`.

## Files in this folder
| File | Purpose |
|---|---|
| `04_dialogic_engine.py` | Entry point: wires the Socratic (02) and Galilean (03) engines to the LLM back-ends |
| `backends.py` | Gemini, Open AI (ChatGPT), Claude adapters and the offline mock backend |
| `dialogue_trace.py` | Records each dialogue step; writes .md and .json traces |
| `run_tests.py` | Runs the tests in folders 02 and 03 |
| `.vscode/launch.json` | VS Code run/debug configurations |
| `.env.example` | Template for API keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) |
| `.gitignore` | Keeps `.env` and caches out of Git |

Keep the four role folders side by side: the engine imports code from folders 02 and 03.

