# Security

- Never open issues that paste live API keys, cookies, or `.env` values.
- This project is a **policy kernel**, not a hosted secret scanner.
- If you find a way `should_enqueue_review(0)` becomes True, or a path
  that auto-posts a raw key to Slack / chat from this library, file a
  private advisory if the GitHub repo has them enabled; otherwise an
  issue with a **redacted** repro.

Do not ask maintainers to add detector regexes, dork YAML, or an HTTP
validator client “just for the demo.” Shipping a turnkey hunter is out
of scope. Prefix families in `CAPABILITIES.md` stay summaries.
