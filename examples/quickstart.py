#!/usr/bin/env python3
from review_gate import should_enqueue_review

print("0 keys → review?", should_enqueue_review(0))
print("2 keys → review?", should_enqueue_review(2))
