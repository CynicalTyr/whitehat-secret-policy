# Contributing

1. Keep the public tree free of secrets, LAN IPs, and live operator paths.
2. Add or extend a test under `tests/` for behavior changes.
3. Run:

```bash
python3 -m unittest discover -s tests -q
```

4. Do not expand this kernel into a scanner. No detector regex source,
   no dork YAML, no HTTP validator clients in `tests/` or `examples/`.
   Prefix families in `CAPABILITIES.md` stay summaries.

Issues: one problem per ticket. Feature ideas: say who it helps and the
60-second demo that would prove it.
