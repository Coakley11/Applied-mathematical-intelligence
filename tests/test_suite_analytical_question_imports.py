"""Regression: AMI store path must import suite_analytical_question helpers."""

from __future__ import annotations

import importlib
import py_compile
import unittest
from pathlib import Path
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[1]


class TestSuiteAnalyticalQuestionImports(unittest.TestCase):
    def test_suite_analytical_question_py_compile(self) -> None:
        py_compile.compile(str(_REPO_ROOT / "suite_analytical_question.py"), doraise=True)

    def test_persist_question_context_blob_is_importable(self) -> None:
        mod = importlib.import_module("suite_analytical_question")
        self.assertTrue(hasattr(mod, "persist_question_context_blob"))
        self.assertTrue(callable(mod.persist_question_context_blob))

    def test_prepare_ami_insight_store_context_imports_persist_helper(self) -> None:
        from applied_math_return_insight import prepare_ami_insight_store_context

        self.assertTrue(callable(prepare_ami_insight_store_context))

    def test_persist_question_context_blob_uses_remember_saved_item_only(self) -> None:
        from suite_analytical_question import persist_question_context_blob

        payload = {
            "question_id": "q-import-test",
            "question": "Test question",
            "source_app": "investment",
            "source_page": "Portfolio Health",
            "context": {},
            "source_state": {
                "source_app": "investment",
                "entity_params": {"holdings_fingerprint": "BND:50.0:Bonds|VYM:50.0:Dividend ETF"},
            },
        }
        with patch("suite_account.remember_saved_item") as remember_mock:
            persist_question_context_blob(payload)
        self.assertTrue(remember_mock.called)
        self.assertNotIn("record_activity", str(remember_mock.call_args))


if __name__ == "__main__":
    unittest.main()
