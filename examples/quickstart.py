#!/usr/bin/env python3
"""First success: review fires only when validated keys exist."""

from review_gate import escalate_is_contract_error, should_enqueue_review

print("0 keys → review?", should_enqueue_review(0))
print("2 keys → review?", should_enqueue_review(2))
print(
    "ESCALATE with 0 keys → contract error?",
    escalate_is_contract_error(0, "ESCALATE"),
)
