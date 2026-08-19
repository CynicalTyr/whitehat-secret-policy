"""Reject hunter review enqueue unless at least one key was validated.

This module is *policy*, not a detector. It does not compile secret regexes
and it does not call provider APIs. Your private scanner counts
``valid_keys_found``; this gate decides whether a *different* process may
see a review envelope.
"""

from __future__ import annotations


def should_enqueue_review(valid_keys_found: int) -> bool:
    """True only when a human should see a systems-review envelope.

    Candidates (entropy / prefix matches that were never live-probed) do
    not increment ``valid_keys_found``. Zero or unparseable counts stay
    on disk: no Slack, no envelope.
    """
    try:
        n = int(valid_keys_found)
    except (TypeError, ValueError):
        return False
    return n > 0


def escalate_is_contract_error(valid_keys_found: int, verdict: str) -> bool:
    """True when a hunter envelope escalates with zero validated keys.

    Pair with a loop-guardrail: ``ESCALATE`` plus an empty validated set
    is alarm fatigue wearing a severity badge.
    """
    v = (verdict or "").strip().upper()
    return v == "ESCALATE" and not should_enqueue_review(valid_keys_found)
