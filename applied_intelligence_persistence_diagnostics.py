"""Daniel-only AMI persistence diagnostics (Developer Mode + Daniel workspace)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

APP_ID = "applied_intelligence"
_DIAG_LOG_KEY = "_ami_persistence_diag_log"
_DIAG_UI_KEY = "_ami_persistence_diag_ui"


def _git_short_head() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            .strip()
        )
    except Exception:
        return "unknown"


def _read_disk_file_meta(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {
        "path": str(path),
        "exists": path.is_file(),
        "size_bytes": 0,
        "saved_at": "",
        "state_keys": [],
        "view_mode": "",
        "ps_area_id": "",
        "control_key_count": 0,
    }
    if not path.is_file():
        return out
    try:
        out["size_bytes"] = path.stat().st_size
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        out["read_error"] = True
        return out
    if not isinstance(raw, dict):
        return out
    out["saved_at"] = str(raw.get("saved_at") or "")
    state = raw.get("state")
    if isinstance(state, dict):
        out["state_keys"] = sorted(str(k) for k in state.keys())
        out["view_mode"] = str(state.get("view_mode") or "")
        out["ps_area_id"] = str(state.get("ps_area_id") or "")
        controls = state.get("_ami_control_state")
        if isinstance(controls, dict):
            out["control_key_count"] = len(controls)
            out["control_keys"] = sorted(str(k) for k in controls.keys())[:24]
    return out


def build_ami_persistence_snapshot(st: Any, *, phase: str) -> dict[str, Any]:
    """Capture AMI persistence + UI state at a pipeline phase."""
    ss = st.session_state
    try:
        from suite_workspace import workspace_persistence_meta

        meta = workspace_persistence_meta(APP_ID, st=st)
    except Exception:
        meta = {"active_workspace_id": "?", "local_state_path": "?", "cloud_app_key": "?"}

    disk_path = Path(str(meta.get("local_state_path") or ""))
    disk_meta = _read_disk_file_meta(disk_path)

    controls = ss.get("_ami_control_state")
    if not isinstance(controls, dict):
        controls = {
            str(k): ss.get(k)
            for k in ss.keys()
            if str(k).startswith("ami_solver_") or str(k).startswith("ps_")
        }

    try:
        from applied_intelligence_persistent_state import build_applied_intelligence_disk_state

        built = build_applied_intelligence_disk_state(st)
        built_controls = built.get("_ami_control_state")
        if not isinstance(built_controls, dict):
            built_controls = {}
    except Exception as exc:
        built = {"build_error": str(exc)}
        built_controls = {}

    block_key = f"_suite_autosave_blocked::{APP_ID}"
    try:
        from suite_user_persistence import _autosave_block_key

        block_key = _autosave_block_key(APP_ID)
    except ImportError:
        pass

    cloud_overwrote = bool(
        ss.get("_cloud_workspace_restored_this_run")
        or (
            ss.get("_suite_persist_last_restore_source") == "cloud"
            and ss.get("_suite_workspace_winner") == "cloud"
        )
    )

    return {
        "phase": phase,
        "git_head": _git_short_head(),
        "active_workspace_id": meta.get("active_workspace_id", ""),
        "workspace_disk_path": str(disk_path),
        "disk_file_exists": disk_meta.get("exists"),
        "disk_saved_at": disk_meta.get("saved_at"),
        "disk_state_keys": disk_meta.get("state_keys"),
        "disk_view_mode": disk_meta.get("view_mode"),
        "disk_ps_area_id": disk_meta.get("ps_area_id"),
        "disk_control_key_count": disk_meta.get("control_key_count"),
        "session_view_mode": str(ss.get("view_mode") or ""),
        "session_ps_area_id": str(ss.get("ps_area_id") or ""),
        "session_ps_library_problem": str(ss.get("ps_library_problem") or "")[:80],
        "session_control_keys": sorted(
            str(k)
            for k in ss.keys()
            if str(k).startswith("ami_solver_") or str(k).startswith("ps_")
        )[:24],
        "built_state_keys": sorted(str(k) for k in built.keys()) if isinstance(built, dict) else [],
        "built_view_mode": str(built.get("view_mode") or "") if isinstance(built, dict) else "",
        "built_ps_area_id": str(built.get("ps_area_id") or "") if isinstance(built, dict) else "",
        "built_control_key_count": len(built_controls),
        "autosave_blocked": bool(ss.get(block_key)),
        "autosave_block_reason": str(ss.get("_suite_autosave_block_reason") or ""),
        "last_autosave_reason": str(ss.get("_suite_persist_last_save_reason") or ss.get("_suite_autosave_reason") or ""),
        "last_save_disk": ss.get("_suite_persist_last_save_disk"),
        "last_save_cloud": ss.get("_suite_persist_last_save_cloud"),
        "restore_source": str(ss.get("_suite_persist_last_restore_source") or ss.get("_suite_restore_pick_source") or ""),
        "restore_skip_reason": str(ss.get("_suite_persist_restore_skip_reason") or ""),
        "workspace_winner": str(ss.get("_suite_workspace_winner") or ""),
        "workspace_winner_reason": str(ss.get("_suite_workspace_winner_reason") or ""),
        "cloud_sync_overwrote_disk": cloud_overwrote,
        "disk_shell_had_state": bool(ss.get("_applied_intelligence_disk_shell_had_state")),
        "workspace_prepared": bool(ss.get("_applied_intelligence_workspace_prepared")),
        "cloud_app_key": meta.get("cloud_app_key", ""),
    }


def record_ami_persistence_phase(st: Any, phase: str) -> None:
    ss = st.session_state
    log = ss.get(_DIAG_LOG_KEY)
    if not isinstance(log, list):
        log = []
    snap = build_ami_persistence_snapshot(st, phase=phase)
    log.append(snap)
    ss[_DIAG_LOG_KEY] = log[-12:]
    ss[_DIAG_UI_KEY] = snap


def render_ami_persistence_diagnostics(st: Any) -> None:
    """Sidebar panel — Daniel workspace + Developer Mode only."""
    try:
        from suite_workspace import can_show_developer_tools
    except ImportError:
        return
    if not can_show_developer_tools(st=st):
        return

    ss = st.session_state
    record_ami_persistence_phase(st, phase="sidebar_panel")

    with st.sidebar.expander("AMI persistence diagnostics (Daniel)", expanded=False):
        ui = ss.get(_DIAG_UI_KEY)
        if not isinstance(ui, dict):
            st.caption("No diagnostics captured yet.")
            return

        st.markdown(f"**Deploy commit:** `{ui.get('git_head', 'unknown')}`")
        st.markdown(f"**Expected fix:** `0b9c5b1` (slider + CC activity)")
        st.markdown(f"**Workspace:** `{ui.get('active_workspace_id')}`")
        st.markdown(f"**Disk path:** `{ui.get('workspace_disk_path')}`")
        st.markdown(
            f"**Disk file:** {'yes' if ui.get('disk_file_exists') else 'no'}"
            f" · saved `{ui.get('disk_saved_at') or '—'}`"
        )
        st.markdown(f"**Cloud app key:** `{ui.get('cloud_app_key')}`")

        c1, c2 = st.columns(2)
        c1.markdown("**On disk**")
        c1.code(
            json.dumps(
                {
                    "view_mode": ui.get("disk_view_mode"),
                    "ps_area_id": ui.get("disk_ps_area_id"),
                    "control_keys": ui.get("disk_control_key_count"),
                    "state_keys": ui.get("disk_state_keys"),
                },
                indent=2,
            ),
            language="json",
        )
        c2.markdown("**Session / UI now**")
        c2.code(
            json.dumps(
                {
                    "view_mode": ui.get("session_view_mode"),
                    "ps_area_id": ui.get("session_ps_area_id"),
                    "problem": ui.get("session_ps_library_problem"),
                    "control_keys": ui.get("session_control_keys"),
                },
                indent=2,
            ),
            language="json",
        )

        st.markdown("**Built autosave payload**")
        st.code(
            json.dumps(
                {
                    "view_mode": ui.get("built_view_mode"),
                    "ps_area_id": ui.get("built_ps_area_id"),
                    "control_key_count": ui.get("built_control_key_count"),
                    "keys": ui.get("built_state_keys"),
                },
                indent=2,
            ),
            language="json",
        )

        st.markdown("**Restore / autosave**")
        st.code(
            json.dumps(
                {
                    "disk_shell_had_state": ui.get("disk_shell_had_state"),
                    "workspace_prepared": ui.get("workspace_prepared"),
                    "restore_source": ui.get("restore_source"),
                    "restore_skip_reason": ui.get("restore_skip_reason"),
                    "workspace_winner": ui.get("workspace_winner"),
                    "workspace_winner_reason": ui.get("workspace_winner_reason"),
                    "cloud_sync_overwrote_disk": ui.get("cloud_sync_overwrote_disk"),
                    "autosave_blocked": ui.get("autosave_blocked"),
                    "autosave_block_reason": ui.get("autosave_block_reason"),
                    "last_autosave_reason": ui.get("last_autosave_reason"),
                    "last_save_disk": ui.get("last_save_disk"),
                    "last_save_cloud": ui.get("last_save_cloud"),
                },
                indent=2,
            ),
            language="json",
        )

        log = ss.get(_DIAG_LOG_KEY)
        if isinstance(log, list) and len(log) > 1:
            st.markdown("**Phase timeline**")
            for row in log:
                if not isinstance(row, dict):
                    continue
                st.caption(
                    f"{row.get('phase')}: view={row.get('session_view_mode')!r} "
                    f"area={row.get('session_ps_area_id')!r} "
                    f"blocked={row.get('autosave_blocked')} "
                    f"disk={row.get('disk_file_exists')}"
                )
