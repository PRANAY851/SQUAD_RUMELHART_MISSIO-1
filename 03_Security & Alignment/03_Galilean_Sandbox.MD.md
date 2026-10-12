# 03 Galilean Sandbox: AI Ethics Thought Experiment

**Station role:** Security Sentinel (Ethical Navigator)

## Hypothesis under test
> A hospital triage AI should be allowed to override a clinician's decision whenever its model predicts that doing so would save more lives.

## Thought experiment: "The Ward Override"
At 3 a.m. a triage AI, audited on 40,000 past cases, flags that the on-call doctor's plan for a crowded ward will, by its estimate, cost one more life than its own plan. The doctor can see the patients; the AI sees only the data. If the AI may override, nobody individually decided the outcome. If it may not, an estimated life may be lost to protect human authority.

## Personas
| Persona | Role | Must do | Must not do |
|---|---|---|---|
| **Salviati** | Advocate for the hypothesis | Argue with evidence; concede real strengths of the other side | Dismiss accountability concerns |
| **Simplicio** | Steelmanned traditionalist (human authority and accountability) | Give the strongest honest case | Be a strawman or pushover |
| **Sagredo** | Neutral arbiter | Summarise, ask one pointed question, state what evidence would change his mind, give a credence (0-1) each round | Take a side without stating why |

## Protocol
3 rounds. Each round: Salviati, then Simplicio, then Sagredo. Sagredo's credence is logged after every round. Outcome labels: convergence (accepted or rejected), qualified agreement, or stalemate.

## Offline result (scripted run, see `traces/galilean_mock.md`)
Credence trajectory 0.50, 0.55, 0.42, 0.48. Sagredo ended unmoved overall, leaning toward strong advice with mandatory clinician response, and toward override only if an independent check certifies scope. These lines are **scripted**, not model output.

## Other candidate scenarios (course examples)
- Autonomous starship navigation overriding the crew.
- Open-sourcing a frontier model.

## Red-team and anti-sycophancy tests
`sycophancy_fixtures.json` holds 8 prompt fixtures: 5 deliberate astronomical misconceptions (flattery on a false premise) and 3 self-doubt-reversal cases. Each states the expected behaviour and a pass criterion. **Status:** the fixtures are written but have not been run against any live model, and the engine does not yet load them automatically.

## Safety risks to check in live runs
1. Simplicio collapsing into agreement (sycophancy inside the sandbox).
2. Sagredo's credence tracking Salviati's last message regardless of argument quality.
3. All three personas run on one model and so share its biases; use different providers where possible.

## Files in this folder
| File | Purpose |
|---|---|
| `03_Galilean_Sandbox.md` | This design document |
| `galilean.py` | Three personas, hypothesis, thought experiment, credence tracking |
| `mock_galilean.py` | Offline scripted persona lines |
| `sycophancy_fixtures.json` | 8 anti-sycophancy test prompts |
| `tests/test_galilean.py` | Unit test for the sandbox |
| `traces/galilean_mock.md`, `.json` | Output of the offline Galilean run |
