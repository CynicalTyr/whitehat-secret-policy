# Integration patterns

Call **`should_enqueue_review` with the validated count**, not the
candidate count. If it is False, do not file a review envelope and do
not send Slack. Candidates stay masked on disk.

This kernel has **no** MCP server. A harness (Cursor, Claude Desktop)
must not gain `validate_leaked_key` or `send_slack`. Live probes, if
you implement them, stay in *your* private scanner: read-only, single
request, budgeted.

```
Your private hunter
    │
    ▼
detect (private; not this repo)
    │
    ├── candidate → mask + count; never probe as live
    └── validated kind → optional read-only probe (budgeted)
            │
            ▼
    valid_keys_found = N
            │
            ▼
    should_enqueue_review(N)   ← this library
            │
            ├── False → no envelope, no Slack
            └── True  → enqueue review envelope (sibling; masked)
```

## Dispatcher (local agent)

```python
from review_gate import escalate_is_contract_error, should_enqueue_review

n = valid_keys_found  # int from *your* scanner
verdict = hunter_verdict  # e.g. "DETECT_ONLY" | "ESCALATE"

if should_enqueue_review(n):
    enqueue_systems_review(...)  # sibling on PYTHONPATH; masked keys
elif escalate_is_contract_error(n, verdict):
    append_loop_guardrail(...)   # sibling: ESCALATE-on-zero is illegal
# else: write counts to disk; humans are not paged
```

Do not copy sibling schema strings into this repo.

## Env names (no values in git)

| Name | Policy meaning |
| ---- | -------------- |
| `AGENT_HUNTER_DETECT_ONLY` | Detect+mask only; skip live probes |
| `AGENT_HUNTER_ENTROPY_MIN` | Shannon floor for generic *candidates* |
| `AGENT_HUNTER_CONTEXT_WINDOW` | Nearby-keyword window for context-gated kinds |
| `AGENT_HUNTER_MAX_VALIDATIONS_PER_RUN` | Live probe budget |
| `AGENT_HUNTER_VALIDATION_SLEEP_SEC` | Inter-probe sleep |
| `AGENT_HOME` | Optional throwaway outbox root for the sibling envelope kernel |

This library does not read the environment. Copy `.env.example`; never
commit `.env`. Do not store a Slack webhook there.

## Gitleaks vs this kernel

Context7 `libraryId=/gitleaks/gitleaks` (README.md, `config/config.go`,
`config/allowlist.go`):

| Gitleaks surface | What it does | What to do instead here |
| ---------------- | ------------ | ----------------------- |
| `[[allowlists]]` | Skip commits/paths/stopwords so the *detector* stays quiet | Keep fixtures out of `valid_keys_found`; do not page on them |
| `--baseline-path` | Ignore old findings on the next detect | Dedup in your private `seen_findings` — still do not Slack |
| `--redact` | Hide secrets in logs/stdout | Mask on the envelope; full material in a human file |
| `--report-path` / SARIF | Finding dump owned by CI | CI logs are a leak channel; do not dump raw keys |
| `--exit-code` | Fail the job on any leak | Build failure ≠ dual-control |
| `gitleaks:allow` / `.gitleaksignore` | Line/fingerprint ignore | Fine in *your* scanner; this gate still wants `n > 0` |

Use Gitleaks (or any detector) in a **private** tree. Pipe only the
validated *count* into `should_enqueue_review`.

## TruffleHog vs this kernel

Context7 `libraryId=/trufflesecurity/trufflehog` and GitHub-MCP
`main.go`:

| TruffleHog surface | What it does | What to do instead here |
| ------------------ | ------------ | ----------------------- |
| `--results=verified` | Print only API-confirmed findings | Still a print; this gate files an envelope or nothing |
| `--no-verification` | Skip API tests (everything stays unverified) | Unverified ≡ candidate; `n` stays 0 |
| `--fail` (exit 183) | Fail CI if results exist | Pair CI fail *and* this gate; do not Slack from CI logs |
| Analysis | Many follow-up API calls on a live key | Out of scope; white-hat probes are single read-only + budget |
| `--json` `"Raw"` field | Machine-readable secret | Do not put `Raw` on a channel the model or Slack can see |

DeepWiki: the engine `dispatcher` emits results after optional verify.
Replace “emit to stdout/Slack” with “increment `valid_keys_found` /
mask.”

## Harness

Paste-ready policy: see [`START_HERE.md`](../START_HERE.md) §5. Hide any
validate-or-notify tool. Keep a cheap “show last gate decision” inspect
path if you want the model to *see* `n` and the boolean — never the
token.

## Review enqueue (optional sibling)

When the gate is True, call the sibling review kernel on `PYTHONPATH` —
not Slack from this process. Without that sibling, write a masked
record to a local file a human already opens. Do not invent a webhook
because the import failed.

## Pair kernels

| Kernel | Pair when |
| ------ | --------- |
| `agent-review-envelope` | `should_enqueue_review` is True |
| `agent-loop-guardrails` | `escalate_is_contract_error` is True |
| `casualty-aware-watchdog` | Unrelated (dead chat API, not secrets) |
| `epistemic-deny` | Tool denies; unrelated to hunters |
