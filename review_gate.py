"""Reject hunter review enqueue unless at least one key was validated."""

from __future__ import annotations


def should_enqueue_review(valid_keys_found: int) -> bool:
    """True only when a human should see a systems-review envelope."""
    try:
        n = int(valid_keys_found)
    except (TypeError, ValueError):
        return False
    return n > 0


def escalate_is_contract_error(valid_keys_found: int, verdict: str) -> bool:
    """True when a hunter envelope escalates with zero validated keys."""
    v = (verdict or "").strip().upper()
    return v == "ESCALATE" and not should_enqueue_review(valid_keys_found)
