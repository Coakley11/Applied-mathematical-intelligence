"""Store trace must not raise UnboundLocalError on duplicate_handled."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from applied_math_return_insight import store_applied_math_insight


class TestAppliedMathStoreTrace(unittest.TestCase):
    def test_store_write_trace_sets_duplicate_handled_without_unbound_error(self) -> None:
        class _FakeSessionState(dict):
            def __getattr__(self, name):
                return self[name]

            def __setattr__(self, name, value):
                self[name] = value

        class _FakeSt:
            def __init__(self) -> None:
                self.session_state = _FakeSessionState()

        st = _FakeSt()
        insight = {
            "insight_id": "dup-test",
            "question_id": "q-dup",
            "source_app": "investment",
            "source_page": "Portfolio Health",
            "conclusion": "Test",
        }
        call_n = {"n": 0}

        def _remember_saved_item(_app, _item_type, _item_key, *, title="", payload=None, **_kwargs):
            call_n["n"] += 1
            if call_n["n"] <= 3:
                return {"write_mode": "upsert", "duplicate_handled": False}
            return {"write_mode": "update", "duplicate_handled": True}

        with patch("suite_account.remember_saved_item", side_effect=_remember_saved_item), patch(
            "suite_activity_client.record_activity",
            return_value=None,
        ):
            store_applied_math_insight(insight, st=st)

        trace = st.session_state.get("_ami_insight_store_trace") or {}
        self.assertTrue(trace.get("store_blob_written_success"))
        self.assertEqual(trace.get("store_write_mode"), "update")
        self.assertTrue(trace.get("store_duplicate_handled"))
        self.assertIsNone(trace.get("store_exception"))


if __name__ == "__main__":
    unittest.main()
