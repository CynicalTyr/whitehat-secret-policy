# Advanced: precision so humans keep reading

Search terms: *secret scanner slack fatigue*, *validated vs candidate API
keys*, *never auto disclose leaked tokens*, *read-only key validation
budget*.

## Incentive bug

If you measure “findings per night,” generic entropy wins and the channel
dies. Measure **new validated keys after dedup**.

## Dual-use

Token-shape tables help defenders and attackers. This repo ships policy,
not regexes. Community “key hacks” lists already exist; do not paste probe
clients here.

## Related

`agent-review-envelope` (admin-only code fences) · `agent-loop-guardrails`
(remember ESCALATE-on-zero).

## Hidden dynamics (short)

- Pattern: validated ≠ candidate. Review enqueue only if valid_keys_found > 0. Never auto-disclose.
- Loop: Measure findings/night → entropy detector wins → humans mute Slack → real keys ignored.
- Incentive: “Just Slack it” is the shortest path to looking useful. White-hat is the expensive path.
- Leverage: DETECT_ONLY and per-run probe budget. ESCALATE with 0 keys is a contract error (loop-guardrails).
- Harness: Never add MCP validate_leaked_key. The model must not POST found tokens.
- Custom AI: if should_enqueue_review(n): enqueue envelope with masked keys. Full material stays in a local file.

