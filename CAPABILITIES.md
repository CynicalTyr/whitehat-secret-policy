# Agent Hunter — Capabilities Registry (public-shaped)

Auditable inventory of a **white-hat leak finder**: detect, optionally
validate read-only, never auto-disclose. This file is documentation of
policy and detector *kinds*. It is **not** a scanner, not a dork engine,
and not a copy of production validators.

> **Posture:** read-only, facts-only, never auto-discloses. Validated keys
> go to a local `found_keys.txt` for **manual human review**; everything
> else is masked/counted only.

---

## 1. Detector kinds (`CATALOG` concept)

A finding's **kind** decides downstream behavior:

- `validated` — eligible for a live **read-only** probe + `found_keys.txt`.
- `candidate` — masked/counted/reported only; **never** validated or persisted
  as a live key.

Provider families (shapes are public knowledge; treat as fingerprint
summaries, not a copy-paste exploit kit):

| Provider family | Kind | Context-gated | Shape (summary) |
| --------------- | ---- | ------------- | --------------- |
| OpenAI / project | validated | no | `sk-` / `sk-proj-` prefixes |
| Anthropic | validated | no | `sk-ant-` prefix |
| Google API | validated | no | `AIza` prefix |
| Other LLM gateways | validated | mixed | vendor prefixes (`xai-`, `gsk_`, `pplx-`, `sk-or-v1-`, …) |
| Cloud IAM / payments | validated or candidate | mixed | AWS `AKIA`, Stripe `sk_live_`, … |
| Git forges | validated | no | `ghp_` / `glpat-` families |
| Chat webhooks | candidate | no | Slack webhook URLs (never live-probe as “validated”) |
| Private_Key PEM | candidate | no | `BEGIN … PRIVATE KEY` |
| Generic entropy | candidate | **yes** | 20–64 token near a secret keyword |

**Precision guards (the unique part):**

- Drop pure-hex strings of git/MD5/SHA lengths (32/40/64/128) — otherwise
  every repo is a “finding.”
- Context-gated detectors require a secret keyword (`api_key`, `token`,
  `password`, …) within a small window.
- Per-detector blacklists (e.g. AWS `EXAMPLE`).
- Generic entropy **never** becomes `validated`.

---

## 2. Validators (policy, not a probe list you should copy blindly)

All probes, if you implement them, must be **single-request, read-only**
(typically `GET …/models` or `GET …/user`). A provider is eligible for
`found_keys.txt` only if:

1. it is registered as `validated`, **and**
2. the probe returns success, **and**
3. a **per-run budget** still has slots.

Sleep between probes. Time out fast. Do not POST to payment or send
email. Do not implement “use the key to do something useful.”

Community catalogues of *defensive* read-only checks exist; adding a
provider = one detector + one registry entry. This extract **does not**
ship those HTTP clients.

---

## 3. Discovery (what not to put in a public tree)

Production uses repo/code search and public-gist harvest with YAML query
caps and sleeps. **Do not publish your dork YAML** (it is an attack
surface and often contains org-specific strings). Keep queries private.

Source denylist idea: skip lockfiles / `Info.plist`; skip candidate-only
matches in `*.min.js` / `*.map`.

---

## 4. Review enqueue (the unique product)

Stage a systems-review envelope **only when `valid_keys_found > 0`**.
Candidate-only and empty scans stay on disk. A review gate should
**REJECT** hunter envelopes that escalate with zero validated keys
(alarm fatigue otherwise trains humans to ignore real keys).

Dedup memory (`seen_findings.json`) marks repeats so the same leaked
token does not page every night.

---

## 5. Environment knobs (rename to yours)

| Env var (example) | Default | Effect |
| ----------------- | ------- | ------ |
| `AGENT_HUNTER_DETECT_ONLY` | false | Detect+mask only; no validation |
| `AGENT_HUNTER_ENTROPY_MIN` | 4.0 | Shannon floor for generic candidates |
| `AGENT_HUNTER_CONTEXT_WINDOW` | 40 | Chars for nearby secret keyword |
| `AGENT_HUNTER_MAX_VALIDATIONS_PER_RUN` | 10 | Live probe budget |
| `AGENT_HUNTER_VALIDATION_SLEEP_SEC` | 2.0 | Inter-probe sleep |

---

## Dual-use notice

Token-shape tables help **defenders** tune precision. They also help
attackers. This folder ships **policy**, not a turnkey hunter. If you
fork a scanner, keep human-gated disclosure and never auto-DM vendors
or paste keys into chat models.
