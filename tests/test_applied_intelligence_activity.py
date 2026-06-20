"""AMI → Command Center activity logging."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch


class TestAmiWorkflowActivity(unittest.TestCase):
    @patch("applied_intelligence_activity._record")
    @patch("suite_analytical_question._upsert_applied_intelligence_resume")
    @patch("suite_analytical_question.build_applied_math_resume_url", return_value="https://ami.test/resume")
    def test_log_ami_workflow_writes_analytical_question(
        self,
        _url_mock: MagicMock,
        upsert_mock: MagicMock,
        record_mock: MagicMock,
    ) -> None:
        from applied_intelligence_activity import log_ami_workflow_activity

        with patch("suite_workspace.get_active_workspace_id", return_value="daniel"):
            log_ami_workflow_activity(
                question="What is the expected value of this bet?",
                area_id="sports",
                area_name="Sports betting",
                interactive="ev_bet",
            )

        record_mock.assert_called_once()
        kwargs = record_mock.call_args.kwargs
        self.assertEqual(record_mock.call_args.args[0], "analytical_question")
        self.assertTrue(str(kwargs.get("resume_key") or "").startswith("ai:question:"))
        self.assertEqual(kwargs["metrics"]["workspace_id"], "daniel")
        self.assertEqual(kwargs["metrics"]["source_app"], "applied_intelligence")
        upsert_mock.assert_called_once()

    @patch("applied_intelligence_activity._record")
    @patch("suite_analytical_question._upsert_applied_intelligence_resume")
    @patch("suite_analytical_question.build_applied_math_resume_url", return_value="https://ami.test/resume")
    def test_ariel_workflow_tags_workspace_id(
        self,
        _url_mock: MagicMock,
        upsert_mock: MagicMock,
        record_mock: MagicMock,
    ) -> None:
        from applied_intelligence_activity import log_ami_workflow_activity

        with patch("suite_workspace.get_active_workspace_id", return_value="ariel"):
            log_ami_workflow_activity(
                question="How volatile is this portfolio?",
                area_id="finance",
                area_name="Finance",
            )

        self.assertEqual(record_mock.call_args.kwargs["metrics"]["workspace_id"], "ariel")
        upsert_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
