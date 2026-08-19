# START HERE

**If you only open one file, open this one.**

This guide assumes you can log into a computer, open a terminal, and paste
commands. It does **not** assume you know Docker, MCP, or how AI agents work.

This library decides whether a leak-finder may enqueue human review.
**Validated ≠ candidate.** Zero validated keys means no envelope and
no Slack.

A **harness** is Cursor / Claude Desktop / VS Code Copilot — a program that
runs a model and **tools**. A **custom-built AI** is your own Python/timer
worker; HTTP or function calls; MCP optional.

## Who this helps

| Who | What they get |
| --- | ------------- |
| **You (learning)** | A 10-minute proof the code runs (`smoke ok`). |
| **An AI harness** | Cursor, Claude Desktop, Copilot Chat — a program that runs a model *and* tools. See §5. |
| **A locally built AI** | A Python worker *you* wrote (cron, systemd, a script). See §6. |
| **People talking to that AI** | Alerts that mean a *validated* leak, not regex noise. |

---

## 0. Words you will see, then files

| Word | Plain meaning |
| ---- | ------------- |
| **Harness** | The IDE or app that hosts the model (Cursor, Claude Desktop). It can start **MCP tools**. |
| **MCP** | A way for the model to call small tools. Tools are not automatically safe. |
| **Locally built AI** | Your own loop: your code calls models and functions. You decide the order. |
| **Kernel** | This tiny library. It is not a secret scanner. |
| **Candidate** | A string that *looks* like a secret (entropy / prefix). Masked and counted only. |
| **Validated** | A candidate that survived a budgeted, read-only live probe in *your* private tree. |
| **Gate** | `should_enqueue_review(n)` — True only when `n > 0`. |

| File | What it does | What you change it for | How it helps agents / users |
| ---- | ------------ | ---------------------- | --------------------------- |
| `START_HERE.md` | This first-use guide | You usually do not | Humans: how to get `smoke ok` |
| `README.md` | Product + hidden dynamics | Forks / rename | Humans: “is this the right tool?” |
| `docs/INTEGRATION.md` | Gate + envelope recipes | Your hunter’s count | Custom AI *and* harness |
| `docs/ADVANCED.md` | Why Slack-from-scanner fails (search article) | Architecture debates | People who already muted the channel |
| `CAPABILITIES.md` | Policy inventory | Prefix *summaries* only | What kinds mean; no regex dump |
| `review_gate.py` | `should_enqueue_review` | Almost never | The worker’s notify policy |
| `examples/quickstart.py` | 0 vs 2 keys | Learning | Proof without a live key |
| `tests/` | Contract + dual-use surface | Behavior changes | Gate stays True only for n>0 |
| `scripts/smoke.sh` | unittest + quickstart | CI locally | 10-minute first success |
| `.env.example` | Env **names** | Copy to `.env` (never commit `.env`) | Policy knobs, no values |

**Mental picture:**

```
Private scanner  →  count validated keys  →  should_enqueue_review
    n = 0  →  no envelope, no Slack (candidates stay masked)
    n > 0  →  review envelope with masked keys; full material in a local human file
ESCALATE with n = 0 is a contract error (not a severity badge).
```

---

## 1. What you need

- Python 3.10 or newer. Check: `python3 -V`
- Ability to `cd` into this folder (the clone root)
- A throwaway directory for any `AGENT_HOME` if you later pair a review
  outbox (use `/tmp/...`, never a real home)

No GPU. No Docker. No API keys for the 10-minute path. No scanner
required to prove the gate.

---

## 2. First success (under 10 minutes)

From **this folder** (after clone it is named `hunter-capabilities` or
`whitehat-secret-policy`):

```bash
chmod +x scripts/smoke.sh
./scripts/smoke.sh
```

You want a line `smoke ok` and no traceback. That script sets
`PYTHONPATH` for you. Optional later:

```bash
python3 -m pip install -e .
cp .env.example .env
python3 examples/quickstart.py
```

**This kernel’s success looks like:** `0 keys → review? False`.
`2 keys → review? True`. `ESCALATE with 0 keys → contract error? True`.
No regex dumps, no HTTP validator client in this folder.

If `python3` is missing, install Python from python.org or your package
manager, then try again.

---

## 3. How to edit (safe)

Change Python files in *this* folder. Re-run `./scripts/smoke.sh`.

If a harness later wraps this kernel, **restart the harness** after
edits (the child process is already running). Do not copy this folder
over a live operator machine “to try it.”

---

## 4. Configure

Copy `.env.example` to `.env` if you want named policy knobs for *your*
private scanner. Fill **names you own**. Never commit `.env`.

This library itself reads no environment. The names that document the
policy:

- `AGENT_HUNTER_DETECT_ONLY` — detect+mask only; no live probe
- `AGENT_HUNTER_MAX_VALIDATIONS_PER_RUN` — probe budget (your scanner)
- Optional `AGENT_HOME` — throwaway dir if you enqueue envelopes

Do not put a Slack webhook in `.env`. That is the incident.

---

## 5. Using this with an AI harness (Cursor / Claude Desktop / MCP)

A **harness** is the program that runs the model and its tools. It does
**not** magically import this folder. Keep the kernel in **your daemon**.
The chat model only *inspects* results.

This repo ships **no** MCP server on purpose. Do not add a
`validate_leaked_key` or `send_slack` tool.

Paste-ready policy:

> Call should_enqueue_review only with the count of validated keys, not
> candidate hits. If the count is 0, do not file a review envelope and
> do not send Slack. Candidates stay masked. ESCALATE with zero
> validated keys is a contract error. Never POST found tokens. Never
> give the model a live-key HTTP client.

---

## 6. Using this with a locally built AI (no MCP)

Your hunter counts validated keys, then calls the gate. The chat model
is **not** that worker.

```python
from review_gate import escalate_is_contract_error, should_enqueue_review

n = valid_keys_found  # your private scanner; not this repo
if should_enqueue_review(n):
    enqueue_review_envelope(...)  # sibling kernel; masked keys only
elif escalate_is_contract_error(n, verdict):
    record_contract_error(...)
# else: candidates stay on disk
```

Copy `examples/quickstart.py` into your worker, then replace the demo
counts with yours.

Recipes: [`docs/INTEGRATION.md`](docs/INTEGRATION.md).

---

## 7. Practice drills (do these once)

1. `should_enqueue_review(0)` is False; `should_enqueue_review(2)` is True.
2. `escalate_is_contract_error(0, "ESCALATE")` is True;
   `escalate_is_contract_error(0, "DETECT_ONLY")` is False.
3. Open `CAPABILITIES.md`: confirm it is policy, not a scanner.
   Prefix families stay summaries.
4. Confirm `tests/` and `examples/` do not contain detector regexes or
   live-key HTTP clients (smoke covers this).
5. Re-run `./scripts/smoke.sh`. It must still pass.
6. Open `docs/ADVANCED.md` once (evergreen / search tutorial).

---

## 8. When something is wrong

| Symptom | Try |
| ------- | --- |
| `No module named ...` | Run `./scripts/smoke.sh` from *this* folder (it sets PYTHONPATH), or `pip install -e .` |
| `Permission denied` on smoke.sh | `chmod +x scripts/smoke.sh` |
| Review fired with 0 live keys | You passed candidate count, not `valid_keys_found` |
| Slack still floods | The finder process is paging; this gate does not send chat |
| MCP `validate_leaked_key` exists | This repo has none — delete that tool |
| Want a regex / HTTP client here | Out of scope — see `SECURITY.md` |

---

## 9. What not to do

- Do not skip the kernel “just this once” (that is how Slack fatigue
  returns).
- Do not commit secrets, phones, or live identity YAML.
- Do not treat candidates as validated.
- Do not auto-disclose raw keys to Slack, email, or a chat model.
- Do not add detector regexes, dork YAML, or HTTP validator clients
  to this tree.
- Do not treat first success as production-ready without INTEGRATION.

**Risk to remember:** Public regex dumps. This repo must stay
policy-only. Dual-use is the upload risk.

---

## 10. Where to go next

| Need | Open |
| ---- | ---- |
| Why this exists / hidden dynamics | [`README.md`](README.md) |
| Recipes for harness + custom AI | [`docs/INTEGRATION.md`](docs/INTEGRATION.md) |
| Advanced / search tutorials | [`docs/ADVANCED.md`](docs/ADVANCED.md) |

You are done with first use when smoke prints `smoke ok` and you can say
in one sentence whether **your** agent is a harness, a custom loop, or
both.
