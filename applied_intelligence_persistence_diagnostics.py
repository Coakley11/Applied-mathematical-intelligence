"""Daniel-only AMI persistence diagnostics (Developer Mode + Daniel workspace)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

APP_ID = "applied_intelligence"
_DIAG_LOG_KEY = "_ami_persistence_diag_log"
_DIAG_UI_KEY = "_ami_persistence_diag_ui"
_EXPECTED_FIX_COMMIT = "e49503e+cloud-sync"


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


def _ui_blob_from_state(state: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(state, dict):
        return {}
    ui = state.get("_ami_ui_state")
    if isinstance(ui, dict) and ui:
        return ui
    legacy = state.get("_ami_control_state")
    return legacy if isinstance(legacy, dict) else {}


def _read_disk_file_meta(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {
        "path": str(path),
        "exists": path.is_file(),
        "size_bytes": 0,
        "saved_at": "",
        "state_keys": [],
        "view_mode": "",
        "ps_area_id": "",
        "mie_example": "",
        "mie_custom": "",
        "ami_last_mie_input": "",
        "ui_key_count": 0,
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
        ui = _ui_blob_from_state(state)
        out["ui_key_count"] = len(ui)
        out["ui_keys"] = sorted(str(k) for k in ui.keys())[:32]
        out["mie_example"] = str(state.get("mie_example") or ui.get("mie_example") or ui.get("mie_tab_example") or "")
        out["mie_custom"] = str(state.get("mie_custom") or ui.get("mie_custom") or ui.get("mie_tab_custom") or "")
        out["ami_last_mie_input"] = str(state.get("ami_last_mie_input") or "")
        controls = state.get("_ami_control_state")
        if isinstance(controls, dict):
            out["control_key_count"] = len(controls)
            out["control_keys"] = sorted(str(k) for k in controls.keys())[:32]
        elif ui:
            out["control_key_count"] = len(ui)
            out["control_keys"] = out["ui_keys"]
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

    try:
        from applied_intelligence_persistent_state import (
            build_applied_intelligence_disk_state,
            scan_ami_session_keys_for_diagnostics,
        )

        key_scan = scan_ami_session_keys_for_diagnostics(ss)
        built = build_applied_intelligence_disk_state(st)
        built_ui = _ui_blob_from_state(built if isinstance(built, dict) else None)
    except Exception as exc:
        key_scan = {"scan_error": str(exc)}
        built = {"build_error": str(exc)}
        built_ui = {}

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

    session_ui = _ui_blob_from_state(
        {
            "_ami_ui_state": {
                str(k): ss.get(k)
                for k in ss.keys()
                if str(k).startswith(("mie_", "ami_", "ps_", "idea_", "opt_", "tw_"))
            }
        }
    )

    return {
        "phase": phase,
        "git_head": _git_short_head(),
        "expected_fix": _EXPECTED_FIX_COMMIT,
        "active_workspace_id": meta.get("active_workspace_id", ""),
        "workspace_disk_path": str(disk_path),
        "disk_file_exists": disk_meta.get("exists"),
        "disk_saved_at": disk_meta.get("saved_at"),
        "disk_state_keys": disk_meta.get("state_keys"),
        "disk_view_mode": disk_meta.get("view_mode"),
        "disk_ps_area_id": disk_meta.get("ps_area_id"),
        "disk_mie_example": disk_meta.get("mie_example"),
        "disk_mie_custom": disk_meta.get("mie_custom"),
        "disk_ami_last_mie_input": disk_meta.get("ami_last_mie_input"),
        "disk_ui_key_count": disk_meta.get("ui_key_count"),
        "disk_ui_keys": disk_meta.get("ui_keys", []),
        "disk_control_key_count": disk_meta.get("control_key_count"),
        "session_view_mode": str(ss.get("view_mode") or ""),
        "session_ps_area_id": str(ss.get("ps_area_id") or ""),
        "session_ps_library_problem": str(ss.get("ps_library_problem") or "")[:80],
        "session_mie_example": str(ss.get("mie_example") or ss.get("mie_tab_example") or ""),
        "session_mie_custom": str(ss.get("mie_custom") or ss.get("mie_tab_custom") or "")[:80],
        "session_ami_last_mie_input": str(ss.get("ami_last_mie_input") or ""),
        "session_ui_key_count": len(session_ui),
        "session_key_scan": key_scan,
        "built_state_keys": sorted(str(k) for k in built.keys()) if isinstance(built, dict) else [],
        "built_view_mode": str(built.get("view_mode") or "") if isinstance(built, dict) else "",
        "built_ps_area_id": str(built.get("ps_area_id") or "") if isinstance(built, dict) else "",
        "built_mie_example": str(
            (built.get("mie_example") if isinstance(built, dict) else "")
            or built_ui.get("mie_example", "")
            or built_ui.get("mie_tab_example", "")
        ),
        "built_ami_last_mie_input": str(built.get("ami_last_mie_input") or "") if isinstance(built, dict) else "",
        "built_ui_key_count": len(built_ui),
        "built_ui_keys": sorted(str(k) for k in built_ui.keys())[:32],
        "built_control_key_count": len(built_ui),
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
    """Sidebar panel — Developer Mode (any workspace profile)."""
    try:
        from suite_workspace import is_developer_mode_enabled
    except ImportError:
        return
    if not is_developer_mode_enabled(st=st):
        return

    ss = st.session_state
    record_ami_persistence_phase(st, phase="sidebar_panel")

    with st.sidebar.expander("AMI persistence diagnostics", expanded=False):
        ui = ss.get(_DIAG_UI_KEY)
        if not isinstance(ui, dict):
            st.caption("No diagnostics captured yet.")
            return

        st.markdown(f"**Deploy commit:** `{ui.get('git_head', 'unknown')}`")
        st.markdown(f"**Expected fix:** `{ui.get('expected_fix', _EXPECTED_FIX_COMMIT)}`")
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
                    "mie_example": ui.get("disk_mie_example"),
                    "mie_custom": ui.get("disk_mie_custom"),
                    "ami_last_mie_input": ui.get("disk_ami_last_mie_input"),
                    "ui_keys": ui.get("disk_ui_key_count"),
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
                    "mie_example": ui.get("session_mie_example"),
                    "mie_custom": ui.get("session_mie_custom"),
                    "ami_last_mie_input": ui.get("session_ami_last_mie_input"),
                    "ui_keys": ui.get("session_ui_key_count"),
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
                    "mie_example": ui.get("built_mie_example"),
                    "ami_last_mie_input": ui.get("built_ami_last_mie_input"),
                    "ui_key_count": ui.get("built_ui_key_count"),
                    "ui_keys_sample": ui.get("built_ui_keys"),
                    "keys": ui.get("built_state_keys"),
                },
                indent=2,
            ),
            language="json",
        )

        scan = ui.get("session_key_scan")
        if isinstance(scan, dict):
            st.markdown("**Session key scan** (area / question / problem / slider / control / solver / ps_ / ami_ / _suite_ai)")
            st.code(
                json.dumps(
                    {
                        "matched_keys": scan.get("matched_keys", [])[:48],
                        "matched_values": scan.get("matched_values", {}),
                        "persisted_keys": scan.get("persisted_keys", [])[:48],
                        "persisted_values": scan.get("persisted_values", {}),
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
                    f"mie={row.get('session_mie_example')!r} "
                    f"ui_keys={row.get('session_ui_key_count')} "
                    f"blocked={row.get('autosave_blocked')} "
                    f"disk={row.get('disk_file_exists')}"
                )

        try:
            from applied_intelligence_cloud_sync_diagnostics import build_ami_cloud_sync_snapshot

            cloud = build_ami_cloud_sync_snapshot(st)
        except Exception as exc:
            cloud = {"build_error": str(exc)}

        st.markdown("**Cloud sync / namespace**")
        st.code(
            json.dumps(
                {
                    "workspace_id": cloud.get("workspace_id"),
                    "suite_user_id": cloud.get("suite_user_id"),
                    "account_user_id": cloud.get("account_user_id"),
                    "cloud_read_namespace": cloud.get("cloud_read_namespace"),
                    "cloud_write_namespace": cloud.get("cloud_write_namespace"),
                    "cloud_updated_at": cloud.get("cloud_updated_at"),
                    "disk_saved_at": cloud.get("disk_saved_at"),
                    "cloud_ui_keys": cloud.get("cloud_ui_key_count"),
                    "disk_ui_keys": cloud.get("disk_ui_key_count"),
                    "cloud_has_ami_ui_state": cloud.get("cloud_has_ami_ui_state"),
                    "disk_has_ami_ui_state": cloud.get("disk_has_ami_ui_state"),
                    "startup_overwrite": cloud.get("startup_overwrite"),
                },
                indent=2,
            ),
            language="json",
        )

        st.markdown("**Activity emit (AMI → CC)**")
        st.code(
            json.dumps(cloud.get("activity") or {}, indent=2),
            language="json",
        )
