"""Disk + cloud persistence for Applied Mathematical Intelligence."""

from __future__ import annotations

import copy
from typing import Any

from suite_user_persistence import autosave_if_changed, finalize_suite_reset, restore_once

APP_ID = "applied_intelligence"

VIEW_MODE_KEY = "view_mode"
SOLVE_A_PROBLEM_VIEW = "Solve a Problem"

_PERSIST_KEYS = (
    VIEW_MODE_KEY,
    "ps_area_id",
    "ps_library_problem",
    "_suite_ai_question",
    "_suite_ai_context",
    "_suite_ai_source_app",
    "_suite_ai_source_page",
    "_suite_ai_area",
    "_suite_ai_lesson",
)

_SUITE_PRELOAD_PREFIXES = (
    "_suite_ai_",
    "_suite_resume_",
    "_ami_",
    "_cc_ai_",
)


def build_applied_intelligence_disk_state(st: Any) -> dict[str, Any]:
    ss = st.session_state
    state: dict[str, Any] = {}
    for key in _PERSIST_KEYS:
        if key in ss:
            state[key] = copy.deepcopy(ss[key])
    if ss.get("_suite_ai_question"):
        state[VIEW_MODE_KEY] = SOLVE_A_PROBLEM_VIEW
        state["ps_library_problem"] = ss.get("ps_library_problem") or ss.get("_suite_ai_question")
    return state


def apply_applied_intelligence_disk_state(st: Any, state: dict[str, Any]) -> None:
    url_authoritative = bool(st.session_state.get("_suite_ai_url_authoritative"))
    url_qid = str(st.session_state.get("_suite_ai_url_question_id") or "").strip()
    skip_when_url = {
        "_suite_ai_question",
        "ps_library_problem",
        "_suite_ai_context",
        "_suite_ai_source_app",
        "_suite_ai_source_page",
        "_suite_ai_area",
    }
    for key, val in state.items():
        if url_authoritative and key in skip_when_url:
            continue
        st.session_state[key] = copy.deepcopy(val)
    if url_authoritative and url_qid:
        st.session_state["_suite_ai_question_id"] = url_qid
    ensure_applied_intelligence_view_from_restore(st)


def ensure_applied_intelligence_view_from_restore(st: Any) -> None:
    """Keep Solve a Problem active when a suite question was restored from disk/cloud."""
    ss = st.session_state
    question = str(ss.get("_suite_ai_question") or "").strip()
    if question:
        ss[VIEW_MODE_KEY] = SOLVE_A_PROBLEM_VIEW
        if not str(ss.get("ps_library_problem") or "").strip():
            ss["ps_library_problem"] = question
        return
    if ss.get(VIEW_MODE_KEY) not in _valid_view_modes():
        ss[VIEW_MODE_KEY] = "Home"


def ensure_applied_intelligence_view_mode(st: Any) -> None:
    """Seed sidebar nav from restored state before the view_mode radio renders."""
    ss = st.session_state
    if ss.get(VIEW_MODE_KEY) not in _valid_view_modes():
        ss[VIEW_MODE_KEY] = "Home"
    ensure_applied_intelligence_view_from_restore(st)


def _valid_view_modes() -> tuple[str, ...]:
    try:
        from content.practical_labs import PRIMARY_ACTIONS

        return ("Home", *PRIMARY_ACTIONS, "Advanced reference")
    except Exception:
        return ("Home", SOLVE_A_PROBLEM_VIEW, "Advanced reference")


def apply_applied_intelligence_session_defaults(st: Any) -> None:
    ss = st.session_state
    for key in _PERSIST_KEYS:
        ss.pop(key, None)
    for key in list(ss.keys()):
        sk = str(key)
        if any(sk.startswith(p) for p in _SUITE_PRELOAD_PREFIXES):
            ss.pop(key, None)
    ss[VIEW_MODE_KEY] = "Home"
    ss.pop("ps_library_problem", None)
    ss.pop("ps_area_id", None)
    ss.pop("_suite_ami_persistence_bootstrapped", None)


def restore_applied_intelligence_disk_state_once(st: Any) -> bool:
    return restore_once(
        st,
        APP_ID,
        apply_state=lambda st_obj, s: apply_applied_intelligence_disk_state(st_obj, s),
    )


def autosave_applied_intelligence_state(st: Any) -> None:
    autosave_if_changed(st, APP_ID, build_state=build_applied_intelligence_disk_state)


def default_reset_applied_intelligence_session(st: Any) -> None:
    apply_applied_intelligence_session_defaults(st)
    fresh = build_applied_intelligence_disk_state(st)
    finalize_suite_reset(st, APP_ID, fresh, page="Home", summary="Reset to defaults")
