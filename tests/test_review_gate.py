from __future__ import annotations

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from review_gate import escalate_is_contract_error, should_enqueue_review


class HunterGateTests(unittest.TestCase):
    def test_zero_keys_no_review(self) -> None:
        self.assertFalse(should_enqueue_review(0))
        self.assertTrue(should_enqueue_review(1))

    def test_escalate_zero_is_error(self) -> None:
        self.assertTrue(escalate_is_contract_error(0, "ESCALATE"))
        self.assertFalse(escalate_is_contract_error(2, "ESCALATE"))


if __name__ == "__main__":
    unittest.main()
