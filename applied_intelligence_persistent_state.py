"""Disk + cloud persistence for Applied Mathematical Intelligence."""

from __future__ import annotations

import copy
import re
from typing import Any

from suite_user_persistence import autosave_if_changed, finalize_suite_reset, sync_workspace_protocol

APP_ID = "applied_intelligence"
_DISK_SHELL_KEY = "_applied_intelligence_disk_shell_applied"
_WORKSPACE_PREPARED_KEY = "_applied_intelligence_workspace_prepared"

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

_CONTROL_STATE_KEY = "_ami_control_state"
_UI_STATE_KEY = "_ami_ui_state"
_AMI_SOLVER_PREFIX = "ami_solver_"
_PS_CONTROL_RE = re.compile(r"^ps_[a-z]+_[a-f0-9]{10}_")

# Widget keys across AMI views (Solve a Problem, Math Idea Explorer, labs, workshop, …).
_AMI_UI_PREFIXES = (
    "ami_solver_",
    "ami_ref_",
    "ps_",
    "mie_",
    "idea_",
    "opt_",
    "tw_",
    "sb_",
    "sir_",
    "pk_",
    "ev_",
    "po_",
    "fc_",
    "fn_",
    "tail_",
    "ef_",
    "dd_",
    "wc_",
    "cl_",
    "sp_",
    "reg_",
    "proj_",
    "pi_",
    "kf_",
    "gl_",
    "nn_",
    "tr_",
    "orb_",
    "rsa_",
    "mod_",
    "ai_",
    "k_",
)

_DIAG_KEY_SUBSTRINGS = (
    "area",
    "question",
    "problem",
    "slider",
    "control",
    "solver",
    "mie",
    "idea",
    "ps_",
    "ami_",
    "_suite_ai",
)


def _is_persisted_ui_session_key(key: str) -> bool:
    sk = str(key)
    if sk in _PERSIST_KEYS or sk in (_CONTROL_STATE_KEY, _UI_STATE_KEY):
        return False
    if any(sk.startswith(p) for p in _SUITE_PRELOAD_PREFIXES):
        return False
    if sk.startswith("_ami_persisted") or sk.startswith("_ami_persistence"):
        return False
    if any(sk.startswith(p) for p in _AMI_UI_PREFIXES):
        return True
    return bool(_PS_CONTROL_RE.match(sk))


def _is_persisted_control_key(key: str) -> bool:
    return _is_persisted_ui_session_key(key)


def _collect_ami_ui_state(ss: Any) -> dict[str, Any]:
    ui: dict[str, Any] = {}
    for key in list(ss.keys()):
        sk = str(key)
        if _is_persisted_ui_session_key(sk):
            ui[sk] = copy.deepcopy(ss[sk])
    return ui


def _merged_ui_blob(state: dict[str, Any]) -> dict[str, Any]:
    ui = state.get(_UI_STATE_KEY)
    if isinstance(ui, dict) and ui:
        return ui
    legacy = state.get(_CONTROL_STATE_KEY)
    return legacy if isinstance(legacy, dict) else {}


def _apply_ami_ui_state(ss: Any, ui_state: dict[str, Any] | None) -> None:
    if not isinstance(ui_state, dict):
        return
    for key, val in ui_state.items():
        sk = str(key)
        if _is_persisted_ui_session_key(sk):
            ss[sk] = copy.deepcopy(val)


def _short_session_value(val: Any, *, limit: int = 80) -> Any:
    if isinstance(val, (int, float, bool)) or val is None:
        return val
    text = str(val)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def scan_ami_session_keys_for_diagnostics(ss: Any) -> dict[str, Any]:
    """List session keys matching AMI UI / diagnostic patterns."""
    all_keys = sorted(str(k) for k in ss.keys())
    matched = [
        k
        for k in all_keys
        if any(sub in k.lower() for sub in _DIAG_KEY_SUBSTRINGS)
        and not k.startswith("_ami_persistence")
    ]
    persisted = [k for k in all_keys if k in _PERSIST_KEYS or _is_persisted_ui_session_key(k)]
    return {
        "matched_keys": matched,
        "persisted_keys": persisted,
        "matched_values": {k: _short_session_value(ss.get(k)) for k in matched},
        "persisted_values": {k: _short_session_value(ss.get(k)) for k in persisted},
        "ui_prefixes": list(_AMI_UI_PREFIXES),
    }


def _sync_derived_ami_anchors(ss: Any, state: dict[str, Any]) -> None:
    """Human-readable anchors for diagnostics and cloud summaries."""
    mie = str(ss.get("mie_custom") or ss.get("mie_tab_custom") or "").strip()
    if not mie:
        mie = str(ss.get("mie_example") or ss.get("mie_tab_example") or "").strip()
    if mie and mie != "Custom input (type below)":
        state["ami_last_mie_input"] = mie
    idea = str(ss.get("idea_input") or "").strip()
    if idea:
        state["ami_last_idea_input"] = idea
    tw = str(ss.get("tw_problem") or ss.get("tw_custom_problem") or ss.get("tw_problem_input") or "").strip()
    if tw:
        state["ami_last_tw_problem"] = tw


def build_applied_intelligence_disk_state(st: Any) -> dict[str, Any]:
    ss = st.session_state
    state: dict[str, Any] = {}
    for key in _PERSIST_KEYS:
        if key in ss:
            state[key] = copy.deepcopy(ss[key])
    ui_state = _collect_ami_ui_state(ss)
    if ui_state:
        state[_UI_STATE_KEY] = ui_state
        state[_CONTROL_STATE_KEY] = ui_state
    _sync_derived_ami_anchors(ss, state)
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
        if key in (_CONTROL_STATE_KEY, _UI_STATE_KEY):
            continue
        if url_authoritative and key in skip_when_url:
            continue
        st.session_state[key] = copy.deepcopy(val)
    _apply_ami_ui_state(st.session_state, _merged_ui_blob(state))
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
        elif _is_persisted_ui_session_key(sk):
            ss.pop(key, None)
    ss[VIEW_MODE_KEY] = "Home"
    ss.pop("ps_library_problem", None)
    ss.pop("ps_area_id", None)
    ss.pop("_suite_ami_persistence_bootstrapped", None)
    ss.pop(_WORKSPACE_PREPARED_KEY, None)


def clear_applied_intelligence_startup_restore_flags(st: Any) -> None:
    """Reset restore flags when workspace profile changes."""
    for key in (_DISK_SHELL_KEY, "_applied_intelligence_disk_shell_had_state", _WORKSPACE_PREPARED_KEY):
        st.session_state.pop(key, None)


def restore_applied_intelligence_disk_shell(st: Any) -> bool:
    """Fast disk-only restore — once per session before widgets."""
    if st.session_state.get(_DISK_SHELL_KEY):
        return bool(st.session_state.get("_applied_intelligence_disk_shell_had_state"))
    cloud_newer = False
    try:
        from suite_cloud_state import load_cloud_full_session, parse_persist_timestamp
        from suite_user_persistence import _load_raw

        cloud_state, cloud_ts = load_cloud_full_session(APP_ID)
        _, _, disk_ts = _load_raw(APP_ID)
        cloud_epoch = parse_persist_timestamp(cloud_ts)
        disk_epoch = parse_persist_timestamp(disk_ts)
        cloud_newer = bool(cloud_state and cloud_ts and cloud_epoch > disk_epoch)
        st.session_state["_ami_disk_shell_cloud_newer"] = cloud_newer
    except Exception:
        pass
    try:
        from suite_user_persistence import _load_raw

        disk_state, _, _ = _load_raw(APP_ID)
    except Exception:
        st.session_state[_DISK_SHELL_KEY] = True
        st.session_state["_applied_intelligence_disk_shell_had_state"] = False
        return False
    if disk_state and not cloud_newer:
        apply_applied_intelligence_disk_state(st, disk_state)
        _finalize_disk_shell_restore(st, disk_state)
    elif cloud_newer:
        st.session_state["_ami_disk_shell_skipped_for_cloud"] = True
    st.session_state[_DISK_SHELL_KEY] = True
    st.session_state["_applied_intelligence_disk_shell_had_state"] = bool(disk_state) and not cloud_newer
    return bool(disk_state) and not cloud_newer


def _finalize_disk_shell_restore(st: Any, disk_state: dict[str, Any]) -> None:
    """Lock restore fingerprint and block autosave until end-of-run clear."""
    if not disk_state:
        return
    try:
        from suite_user_persistence import _autosave_block_key, _lock_fingerprint_after_restore

        _lock_fingerprint_after_restore(st, APP_ID, disk_state)
        st.session_state[_autosave_block_key(APP_ID)] = True
        st.session_state["_suite_autosave_block_reason"] = "post-disk-shell restore cooldown"
    except ImportError:
        pass


def prepare_applied_intelligence_workspace(st: Any, *, cloud_first: bool = True) -> bool:
    """Authoritative workspace-scoped disk + cloud sync before sidebar widgets."""
    # Cross-device AMI state must prefer cloud over per-container ephemeral disk.
    cloud_first = True
    return sync_workspace_protocol(
        st,
        APP_ID,
        apply_state=lambda st_obj, s: apply_applied_intelligence_disk_state(st_obj, s),
        cloud_first=cloud_first,
    )


def restore_applied_intelligence_disk_state_once(st: Any) -> bool:
    """Backward-compatible alias — prefer ``prepare_applied_intelligence_workspace()``."""
    return prepare_applied_intelligence_workspace(st)


def autosave_applied_intelligence_state(st: Any) -> None:
    autosave_if_changed(st, APP_ID, build_state=build_applied_intelligence_disk_state)


def persist_applied_intelligence_ui_state(
    st: Any,
    *,
    view_mode: str | None = None,
    ps_area_id: str | None = None,
    ps_library_problem: str | None = None,
    suite_ai_question: str | None = None,
    reason: str = "ui_change",
) -> bool:
    """Immediately persist AMI page/area/question state for the active workspace."""
    ss = st.session_state
    if view_mode is not None:
        ss[VIEW_MODE_KEY] = view_mode
    if ps_area_id is not None:
        ss["ps_area_id"] = ps_area_id
    if ps_library_problem is not None:
        ss["ps_library_problem"] = ps_library_problem
    if suite_ai_question is not None:
        ss["_suite_ai_question"] = suite_ai_question
        if not str(ss.get("ps_library_problem") or "").strip():
            ss["ps_library_problem"] = suite_ai_question
        ss[VIEW_MODE_KEY] = SOLVE_A_PROBLEM_VIEW
    from suite_user_persistence import _local_dirty_key, force_autosave

    ss[_local_dirty_key(APP_ID)] = True
    return force_autosave(
        st,
        APP_ID,
        build_state=build_applied_intelligence_disk_state,
        reason=reason,
    )


def default_reset_applied_intelligence_session(st: Any) -> None:
    apply_applied_intelligence_session_defaults(st)
    fresh = build_applied_intelligence_disk_state(st)
    finalize_suite_reset(st, APP_ID, fresh, page="Home", summary="Reset to defaults")
