"""AMI-owned hydration helpers must survive suite sync without changing saved work."""
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
from suite_resume_launch import hydrate_applied_intelligence_from_url


def test_plain_startup_preserves_workspace_and_does_not_hydrate_a_url():
    state = {'saved_projects': {'project': {'question': 'Saved problem'}}, 'view_mode': 'Solve a Problem'}
    before = deepcopy(state)
    st = SimpleNamespace(query_params={}, session_state=state)
    with patch('suite_analytical_question.hydrate_applied_intelligence_session') as hydrate:
        assert not hydrate_applied_intelligence_from_url(st)
        hydrate.assert_not_called()
    assert state == before


def test_practice_analysis_return_reapplies_insight_without_resetting_saved_projects():
    saved = {'saved_projects': {'project': {'question': 'Saved problem'}}}
    state = deepcopy(saved)
    st = SimpleNamespace(query_params={'suite_practice_analysis_run_id': 'disposable-run'}, session_state=state)
    with patch('suite_analytical_question.hydrate_applied_intelligence_session') as hydrate, patch(
        'applied_math_return_insight.apply_ami_insight_from_query'
    ) as insight:
        assert hydrate_applied_intelligence_from_url(st)
        assert hydrate_applied_intelligence_from_url(st)
        assert hydrate.call_count == 2
        assert insight.call_count == 2
    assert state == saved
