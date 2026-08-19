from __future__ import annotations

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from review_gate import escalate_is_contract_error, should_enqueue_review

_ROOT = Path(__file__).resolve().parents[1]


class HunterGateTests(unittest.TestCase):
    def test_zero_keys_no_review(self) -> None:
        self.assertFalse(should_enqueue_review(0))
        self.assertTrue(should_enqueue_review(1))
        self.assertTrue(should_enqueue_review(2))

    def test_negative_and_unparseable_are_not_review(self) -> None:
        self.assertFalse(should_enqueue_review(-1))
        self.assertFalse(should_enqueue_review("not-a-count"))
        self.assertFalse(should_enqueue_review(None))  # type: ignore[arg-type]
        self.assertTrue(should_enqueue_review("3"))

    def test_escalate_zero_is_error(self) -> None:
        self.assertTrue(escalate_is_contract_error(0, "ESCALATE"))
        self.assertTrue(escalate_is_contract_error(0, "escalate"))
        self.assertFalse(escalate_is_contract_error(2, "ESCALATE"))

    def test_detect_only_zero_is_not_escalate_error(self) -> None:
        self.assertFalse(escalate_is_contract_error(0, "DETECT_ONLY"))
        self.assertFalse(escalate_is_contract_error(0, ""))
        self.assertFalse(escalate_is_contract_error(1, "ESCALATE"))


def _tok(*parts: str) -> str:
    """Join so this file does not contain live-key HTTP or regex-engine literals."""
    return "".join(parts)


class DualUseSurfaceTests(unittest.TestCase):
    """This extract ships policy, not a hunter. tests/ and examples/ stay clean."""

    _HTTP_MARKERS = (
        _tok("url", "lib", ".request"),
        _tok("url", "lib3"),
        _tok("req", "uests", ".get"),
        _tok("req", "uests", ".post"),
        _tok("http", "x."),
        _tok("aio", "http"),
        _tok("http", "lib"),
    )
    _DETECTOR_ENGINE_MARKERS = (
        _tok("re", ".compile("),
        _tok("regex", ".compile("),
        _tok("from", " re", " import"),
        _tok("import", " re", "\n"),
    )

    def test_examples_and_tests_have_no_live_key_http_client(self) -> None:
        hits = self._scan(("examples", "tests"), self._HTTP_MARKERS)
        self.assertEqual(hits, [], msg=f"HTTP live-key client markers: {hits}")

    def test_examples_and_tests_have_no_detector_regex_engine(self) -> None:
        hits = self._scan(("examples", "tests"), self._DETECTOR_ENGINE_MARKERS)
        self.assertEqual(hits, [], msg=f"detector regex engine markers: {hits}")

    def test_review_gate_imports_no_http_or_re(self) -> None:
        src = (_ROOT / "review_gate.py").read_text(encoding="utf-8")
        low = src.lower()
        self.assertNotIn(_tok("import", " ", "re"), low)
        self.assertNotIn(_tok("from", " re", " "), low)
        self.assertNotIn(_tok("url", "lib"), low)
        self.assertNotIn(_tok("http", "x"), low)
        self.assertNotIn(_tok("requ", "ests"), low)

    def _scan(self, rel_dirs: tuple[str, ...], markers: tuple[str, ...]) -> list[str]:
        hits: list[str] = []
        for rel in rel_dirs:
            folder = _ROOT / rel
            if not folder.is_dir():
                continue
            for path in folder.rglob("*"):
                if not path.is_file() or path.suffix not in {".py", ".md", ".sh"}:
                    continue
                text = path.read_text(encoding="utf-8")
                for marker in markers:
                    if marker in text:
                        hits.append(f"{path.relative_to(_ROOT)}:{marker}")
        return hits


if __name__ == "__main__":
    unittest.main()
