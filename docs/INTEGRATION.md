# Integration patterns

```python
from review_gate import should_enqueue_review, escalate_is_contract_error

if should_enqueue_review(valid_keys_found):
    enqueue_systems_review(...)  # agent-review-envelope
elif escalate_is_contract_error(valid_keys_found, verdict):
    append_loop_guardrail(...)   # agent-loop-guardrails
```

Implement detectors in a **private** tree. This package is the gate and
the written policy (`CAPABILITIES.md`).
