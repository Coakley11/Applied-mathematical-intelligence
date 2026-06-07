"""Disk + cloud persistence for Applied Mathematical Intelligence."""

from __future__ import annotations

import copy
from typing import Any

from suite_user_persistence import autosave_if_changed, finalize_suite_reset, restore_once

APP_ID = "applied_intelligence"

_PERSIST_KEYS = (
    "view_mode",
    "ps_area_id",
    "ps_library_problem",
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
        if key in ss and not str(key).startswith("_suite_ai_"):
            state[key] = copy.deepcopy(ss[key])
    return state


def apply_applied_intelligence_disk_state(st: Any, state: dict[str, Any]) -> None:
    for key, val in state.items():
        if key.startswith("_suite_ai_"):
            continue
        st.session_state[key] = copy.deepcopy(val)


def apply_applied_intelligence_session_defaults(st: Any) -> None:
    ss = st.session_state
    for key in _PERSIST_KEYS:
        ss.pop(key, None)
    for key in list(ss.keys()):
        sk = str(key)
        if any(sk.startswith(p) for p in _SUITE_PRELOAD_PREFIXES):
            ss.pop(key, None)
    ss["view_mode"] = "Home"
    ss.pop("ps_library_problem", None)
    ss.pop("ps_area_id", None)


def restore_applied_intelligence_disk_state_once(st: Any) -> bool:
    return restore_once(
        st,
        APP_ID,
        apply_state=lambda st_obj, s: apply_applied_intelligence_disk_state(st_obj, s),
    )


def autosave_applied_intelligence_state(st: Any) -> None:
    if st.session_state.get("_suite_ai_question"):
        return
    autosave_if_changed(st, APP_ID, build_state=build_applied_intelligence_disk_state)


def default_reset_applied_intelligence_session(st: Any) -> None:
    apply_applied_intelligence_session_defaults(st)
    fresh = build_applied_intelligence_disk_state(st)
    finalize_suite_reset(st, APP_ID, fresh, summary="Reset to defaults")
