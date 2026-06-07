"""Tests for Applied Intelligence suite question persistence."""

from __future__ import annotations

import json

import applied_intelligence_persistent_state as aips


class _FakeSessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class _FakeSt:
    def __init__(self) -> None:
        self.session_state = _FakeSessionState()


def test_build_state_persists_suite_ai_question_and_view_mode() -> None:
    st = _FakeSt()
    st.session_state["_suite_ai_question"] = "What is the expected HR rate?"
    st.session_state["_suite_ai_context"] = json.dumps({"player": "Aaron Judge"})
    st.session_state["_suite_ai_source_app"] = "baseball"
    st.session_state["_suite_ai_source_page"] = "Trend Value"
    st.session_state["ps_area_id"] = "sports"

    state = aips.build_applied_intelligence_disk_state(st)

    assert state["view_mode"] == "Solve a Problem"
    assert state["_suite_ai_question"] == "What is the expected HR rate?"
    assert state["_suite_ai_source_app"] == "baseball"
    assert state["ps_library_problem"] == "What is the expected HR rate?"


def test_apply_state_restores_suite_ai_question_and_view_mode() -> None:
    st = _FakeSt()
    saved = {
        "view_mode": "Home",
        "_suite_ai_question": "How volatile is this portfolio?",
        "_suite_ai_context": json.dumps({"tickers": ["SPY", "BND"]}),
        "_suite_ai_source_app": "investment",
        "_suite_ai_source_page": "Portfolio Health",
        "ps_area_id": "finance",
        "ps_library_problem": "How volatile is this portfolio?",
    }

    aips.apply_applied_intelligence_disk_state(st, saved)

    assert st.session_state["view_mode"] == "Solve a Problem"
    assert st.session_state["_suite_ai_question"] == "How volatile is this portfolio?"
    assert st.session_state["_suite_ai_context"] == saved["_suite_ai_context"]
    assert st.session_state["ps_library_problem"] == "How volatile is this portfolio?"


def test_autosave_does_not_skip_when_suite_ai_question_loaded() -> None:
    st = _FakeSt()
    st.session_state["_suite_ai_question"] = "Test question"
    st.session_state["view_mode"] = "Solve a Problem"

    saved: list[dict] = []

    def _fake_autosave(_st, app_id, build_state):
        saved.append(build_state(_st))

    orig = aips.autosave_if_changed
    aips.autosave_if_changed = _fake_autosave
    try:
        aips.autosave_applied_intelligence_state(st)
    finally:
        aips.autosave_if_changed = orig

    assert saved
    assert saved[0]["_suite_ai_question"] == "Test question"
    assert saved[0]["view_mode"] == "Solve a Problem"


def test_reset_clears_suite_ai_question_keys() -> None:
    st = _FakeSt()
    st.session_state.update(
        {
            "view_mode": "Solve a Problem",
            "_suite_ai_question": "Test question",
            "_suite_ai_context": "{}",
            "_suite_ai_source_app": "music",
            "ps_library_problem": "Test question",
            "ps_area_id": "music",
        }
    )

    aips.apply_applied_intelligence_session_defaults(st)

    assert st.session_state.get("view_mode") == "Home"
    assert "_suite_ai_question" not in st.session_state
    assert "ps_library_problem" not in st.session_state
