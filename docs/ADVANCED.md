# Advanced: precision so humans keep reading

This guide is for people who already ran [`START_HERE.md`](../START_HERE.md)
and want the design that keeps showing up in production: **why a secret
scanner that auto-discloses or floods Slack trains humans to mute the
channel**, why `validated` must not equal `candidate`, and how this
kernel differs from Gitleaks allowlists and TruffleHog `--results=verified`.

Search terms this document is meant to answer: *secret scanner slack
fatigue*, *validated vs candidate API keys*, *never auto disclose leaked
tokens*, *gitleaks allowlist vs notify policy*, *trufflehog verified
still prints raw result*.

---

## 1. The failure that looks like success

A nightly hunter runs. Entropy and prefix detectors fire. The shortest
path to “security is working” is: **post every hit to Slack**.

That path has three hidden properties:

1. **The channel becomes the leak.** Per the Cynical0n3 NotebookLM
   (`systems`): auto-disclosing unredacted secrets to a shared Slack
   channel turns a restricted-repository vulnerability into a wide,
   visible, indexed plain-text credential leak.
2. **Candidates are not proof.** NotebookLM (`systems`): a candidate is
   a probabilistic guess (“looks reasonable”). Validated requires
   deterministic, out-of-band behavioral proof that the credential is
   live. Treating candidates as authoritative leaks builds
   **verification debt**. Maker-checker: the finder does not get to
   declare the finding real by paging.
3. **Alert storms cause cognitive surrender.** NotebookLM (`systems`):
   un-deduplicated floods make operators stop having an opinion and
   silence the channel. The next real key is unread.

Gitleaks pre-commit “Failed” and TruffleHog `--fail` (exit 183) look
like success because they *did* report something. Reporting candidates
on the human channel is still the mute incident.

---

## 2. Quantified incident (lab shape, no live host)

One worker. Nightly scan. Slack is the “security” channel. Operator
reads it on a phone.

| Step | Without this kernel | With this kernel |
| ---- | ------------------- | ---------------- |
| Night 1 | 40 entropy *candidates*, 0 live probes → 40 Slack messages | `should_enqueue_review(0)` → False; 0 envelopes |
| Night 1 result | Channel muted; “scanner is noisy” | Candidates stay masked on disk |
| Night 2 | 1 validated key is message 41, unread | 1 envelope, masked; full material in a local human file |
| 7 nights, 0 live keys | ~280 messages, 0 rotations | 0 pages; humans still read the channel |
| `ESCALATE` on empty scan | Severity badge on noise | `escalate_is_contract_error` → True (loop-guardrail) |

If your dashboard’s “secrets found” goes up while `valid_keys_found`
stays 0, you inverted the fix: you counted regex as work.

---

## 3. Real-world: Gitleaks allowlists skip detection, not notify

Context7 `libraryId=/gitleaks/gitleaks` and GitHub-MCP
`gitleaks/gitleaks`:

- README.md — product is **detecting** secrets. Policy surfaces:
  `[[allowlists]]` (global and per-rule), `--baseline-path`,
  `--redact`, `--report-path`, `--exit-code`, `gitleaks:allow`,
  `.gitleaksignore`.
- `config/config.go` — `ViperConfig.Allowlists`, `Config.Allowlists`.
- `config/allowlist.go` — `AllowlistMatchCondition` (`OR` / `AND`).
- `config/gitleaks.toml` — default global allowlist (paths such as
  media and `.git`; no notify router).
- `gitleaks/gitleaks-action` `action.yml` — run Gitleaks on push/PR.
  Fail the job. Not a second-process review gate.

`--redact` hides secrets in **logs/stdout**. `--report-path` is still
a finding dump the CI job owns. Allowlists answer “do not *detect*
this fixture.” They do not answer “do not *page* until a live probe
and a different process.”

---

## 4. Real-world: TruffleHog verified still prints the raw key

GitHub-MCP + Context7 `libraryId=/trufflesecurity/trufflehog`, file
`main.go`:

- `--results` kinds: `verified` (confirmed valid by API), `unverified`
  (detected but not verified), `unknown` (verification error).
  Default: `verified,unverified,unknown`.
- `--no-verification` skips API tests.
- `--only-verified` is **hidden**; README teaches `--results=verified`.
- `--fail` exits 183 if results are found.

README “What is credential verification?”: programmatic API tests
eliminate false positives. The same README’s happy path prints
`Found verified result` and **`Raw result:`** plus a JSON blob with
`"Raw": "..."` on the scanner channel. `--json` / `--sarif` /
`--github-actions` are output formats, not a human-file dual-control.

DeepWiki `trufflesecurity/trufflehog` after GitHub confirmed identity:
`engine.Engine` has a `dispatcher` (`ResultsDispatcher`) and
verification cache. Pipeline is source → detector → optional verify →
**output**. There is no required second process before a human (or a
CI log) sees the secret.

TruffleHog **Analysis** sends many follow-up requests to learn
permissions on a live key. That is the opposite of a budgeted
read-only white-hat probe. Do not copy Analysis into a public kernel.

---

## How this stands out

Researched with Context7 (`libraryId=/gitleaks/gitleaks` allowlists /
`--redact` / `--report-path` / `--baseline-path`;
`libraryId=/trufflesecurity/trufflehog` `--results=verified` /
`--no-verification` / verification statuses) and GitHub-MCP
(`gitleaks/gitleaks` files `README.md`, `config/config.go`,
`config/allowlist.go`, `config/gitleaks.toml`;
`gitleaks/gitleaks-action` `action.yml`;
`trufflesecurity/trufflehog` `main.go`, `README.md`). DeepWiki on
`trufflesecurity/trufflehog` after GitHub confirmed identity: engine
dispatches results after optional verify; it does not split finder ≠
notifier. `search_code` for `should_enqueue_review` and
`escalate_is_contract_error` returned **zero hits**. Incident search
*secret scanner slack fatigue auto disclose* returned **zero
repositories**.

| Obvious alternative | What they optimize | What they miss | This kernel |
| ------------------- | ------------------ | -------------- | ----------- |
| Gitleaks `[[allowlists]]` / `.gitleaksignore` | Skip known fixtures so CI is quiet | Skip *detection*, not *notify*; report still dumps findings | `should_enqueue_review` is notify policy; candidates never increment `n` |
| Gitleaks `--redact` / `--report-path` | Hide secrets in logs; write a report file | The scanner process still owns the raw finding | Full material stays in a *human* file; envelope is masked |
| TruffleHog `--results=verified` | Filter output to API-confirmed keys | Prints `Raw result` on the same channel; ships 800+ HTTP detectors | No detector, no HTTP client; gate only |
| TruffleHog `--fail` / Gitleaks exit 1 | Fail the build on findings | Build failure ≠ dual-control; CI logs are a leak channel | Review envelope in a different process |
| leakferret (MCP scanner) | Verify live keys; keep raw secret on disk | Still a detector engine + provider calls | Policy extract only |
| `agent-review-envelope` (sibling) | Finder ≠ messenger for *speech* | Does not know validated vs candidate | This gate decides *whether* to file |

**Non-obvious / high-leverage:** `valid_keys_found` is a *count*, not
a list of tokens, on the tool-result channel the model sees. Tests
assert `should_enqueue_review(0)` is False even if your scanner
“found” forty candidates. `escalate_is_contract_error` catches the
severity-badge cheat.

**Mental model to replace:** adopters think “verified means print it”
and “allowlist means we designed paging.” The governing model is
**detector ≠ policy**, and **validated ≠ candidate**. NotebookLM
(`systems`): keep pattern-matching isolated from rule-bound
gatekeeping.

**Incentive:** the stack will keep Slacking because it is cheaper than
a human file, and will count candidates because findings-per-night
looks better.

**Second-order effect:** once copied, teams add `force_notify` or a
Slack webhook “only for verified.” Count pages from the finder
process (should be **zero**) and envelopes filed with `n = 0`
(should be **zero**). Do **not** add `force_notify`. Do **not** vendor
detector regexes into this tree.

---

## 5. Architecture decisions worth copying

1. **Kinds first.** `validated` vs `candidate` is a registry decision,
   not a Slack decision.
2. **Gate on the validated count.** `should_enqueue_review(n)` — not
   on “we had findings.”
3. **Never auto-disclose.** Shared chat is a leak amplifier
   (NotebookLM `systems`).
4. **Budgeted read-only probes live in a private tree.** This repo
   does not ship them.
5. **ESCALATE-on-zero is a contract error.** Pair loop-guardrails;
   do not treat it as severity.

---

## 6. Measuring whether anyone *uses* this

Stars are vanity. Count:

- Review envelopes filed when `valid_keys_found == 0` (should be
  **zero**).
- Slack / chat messages from the *finder* process (should be
  **zero**).
- Candidate hits that were treated as validated (should be **zero**).
- `escalate_is_contract_error` trips (those are the severity-badge
  bug).

---

## 7. Where this sits in the kernel family

White-hat gate (this repo) + speech queues (`agent-review-envelope`)
+ loop metadata (`agent-loop-guardrails`) are the unusual parts of an
autonomous hunter. The detector engine stays **private**. The model
does not get the raw key.

## Hidden dynamics (short)

- Pattern: validated ≠ candidate. Review enqueue only if
  `valid_keys_found > 0`. Never auto-disclose.
- Loop: Measure findings/night → entropy wins → humans mute Slack →
  real keys ignored.
- Incentive: “Just Slack it” looks useful. White-hat is expensive.
- Leverage: `should_enqueue_review`. `DETECT_ONLY`. Per-run probe
  budget. `escalate_is_contract_error`.
- Harness: Never add MCP `validate_leaked_key`. The model must not
  POST found tokens.
- Custom AI: if `should_enqueue_review(n)`: enqueue envelope with
  masked keys. Full material stays in a local file.
