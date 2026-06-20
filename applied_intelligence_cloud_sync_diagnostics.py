"""Cross-device cloud sync + activity namespace diagnostics for AMI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

APP_ID = "applied_intelligence"
_UI_STATE_KEY = "_ami_ui_state"
_CONTROL_STATE_KEY = "_ami_control_state"


def _ui_blob(state: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(state, dict):
        return {}
    ui = state.get(_UI_STATE_KEY)
    if isinstance(ui, dict) and ui:
        return ui
    legacy = state.get(_CONTROL_STATE_KEY)
    return legacy if isinstance(legacy, dict) else {}


def _read_disk_meta(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {
        "path": str(path),
        "exists": path.is_file(),
        "saved_at": "",
        "state_keys": [],
        "ui_key_count": 0,
    }
    if not path.is_file():
        return out
    try:
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
        out["ui_key_count"] = len(_ui_blob(state))
        out["view_mode"] = str(state.get("view_mode") or "")
    return out


def _cloud_row_meta(app_id: str) -> dict[str, Any]:
    out: dict[str, Any] = {
        "cloud_enabled": False,
        "read_namespace": "",
        "write_namespace": "",
        "row_found": False,
        "updated_at": "",
        "page": "",
        "summary": "",
        "ui_key_count": 0,
        "view_mode": "",
        "load_error": "",
    }
    try:
        from suite_cloud_state import _cloud_storage_app_id, load_cloud_full_session
        from suite_storage_config import cloud_storage_enabled
        from suite_workspace import scoped_cloud_app_id

        out["cloud_enabled"] = cloud_storage_enabled()
        ws_key = scoped_cloud_app_id(app_id)
        out["read_namespace"] = _cloud_storage_app_id(app_id)
        out["write_namespace"] = ws_key
        if not out["cloud_enabled"]:
            return out
        cloud_state, cloud_ts = load_cloud_full_session(app_id)
        out["updated_at"] = str(cloud_ts or "")
        out["ui_key_count"] = len(_ui_blob(cloud_state if isinstance(cloud_state, dict) else None))
        if isinstance(cloud_state, dict) and cloud_state:
            out["row_found"] = True
            out["view_mode"] = str(cloud_state.get("view_mode") or "")
        try:
            from suite_cloud_state import _import_storage

            storage, _ = _import_storage()
            row = storage.load_current_states().get(storage.normalize_app_key(_cloud_storage_app_id(app_id))) or {}
            if isinstance(row, dict) and row:
                out["row_found"] = True
                out["page"] = str(row.get("page") or "")
                out["summary"] = str(row.get("summary") or "")[:120]
                if not out["updated_at"]:
                    out["updated_at"] = str(row.get("updated_at") or "")
        except Exception as exc:
            out["load_error"] = str(exc)
    except Exception as exc:
        out["load_error"] = str(exc)
    return out


def _account_identity() -> dict[str, Any]:
    out: dict[str, Any] = {
        "suite_user_id": "",
        "account_user_id": "",
        "account_mode": "",
    }
    try:
        from suite_user import account_mode, get_account_user_id, get_external_user_id

        out["suite_user_id"] = get_external_user_id()
        out["account_user_id"] = get_account_user_id()
        out["account_mode"] = account_mode()
    except Exception as exc:
        out["error"] = str(exc)
    return out


def _startup_overwrite_analysis(st: Any, *, cloud_ts: str, disk_ts: str, cloud_epoch: float, disk_epoch: float) -> dict[str, Any]:
    ss = st.session_state
    blocked = bool(ss.get(f"_suite_autosave_blocked::{APP_ID}"))
    last_save_cloud = ss.get("_suite_persist_last_save_cloud")
    last_save_disk = ss.get("_suite_persist_last_save_disk")
    restore_source = str(
        ss.get("_suite_persist_last_restore_source") or ss.get("_suite_restore_pick_source") or ""
    )
    skip_reason = str(ss.get("_suite_persist_restore_skip_reason") or "")
    cloud_newer = bool(cloud_ts and cloud_epoch > disk_epoch)
    disk_newer = bool(disk_ts and disk_epoch > cloud_epoch)
    risk = "low"
    risk_reason = ""
    if cloud_newer and restore_source == "disk":
        risk = "high"
        risk_reason = "cloud newer but disk restored"
    elif disk_newer and last_save_cloud and not last_save_disk:
        risk = "medium"
        risk_reason = "disk timestamp newer; local disk may block cloud on next open"
    elif skip_reason and "already synced" in skip_reason and cloud_newer:
        risk = "high"
        risk_reason = "sync skipped while cloud newer than disk"
    elif blocked and cloud_newer:
        risk = "medium"
        risk_reason = "post-restore autosave blocked; cloud may not receive edits this rerun"
    return {
        "cloud_newer_than_disk": cloud_newer,
        "disk_newer_than_cloud": disk_newer,
        "cloud_epoch": cloud_epoch,
        "disk_epoch": disk_epoch,
        "restore_source": restore_source,
        "sync_skip_reason": skip_reason,
        "autosave_blocked": blocked,
        "last_save_cloud": last_save_cloud,
        "last_save_disk": last_save_disk,
        "last_autosave_reason": str(ss.get("_suite_persist_last_save_reason") or ""),
        "disk_shell_skipped_for_cloud": bool(ss.get("_ami_disk_shell_skipped_for_cloud")),
        "startup_overwrite_risk": risk,
        "startup_overwrite_reason": risk_reason,
    }


def _activity_emit_diagnostics(st: Any) -> dict[str, Any]:
    ss = st.session_state
    last = ss.get("_ami_last_activity_emit")
    if not isinstance(last, dict):
        last = {}
    trace: dict[str, Any] = {}
    try:
        from suite_activity_client import last_record_trace

        trace = last_record_trace()
    except Exception:
        pass
    try:
        from suite_workspace import get_active_workspace_id, scoped_cloud_app_id

        expected_write_ns = scoped_cloud_app_id("applied_intelligence")
    except Exception:
        expected_write_ns = "applied_intelligence"
    return {
        "last_emitted": last,
        "last_record_trace": trace,
        "expected_activity_write_namespace": expected_write_ns,
        "trace_write_namespace": trace.get("write_namespace") or trace.get("app") or "",
        "namespace_match": str(trace.get("write_namespace") or trace.get("app") or "") in {
            expected_write_ns,
            "applied_intelligence",
        },
    }


def build_ami_cloud_sync_snapshot(st: Any) -> dict[str, Any]:
    """Compare account/workspace namespaces, cloud vs disk payloads, overwrite risk."""
    ss = st.session_state
    try:
        from suite_workspace import get_active_workspace_id, workspace_persistence_meta

        meta = workspace_persistence_meta(APP_ID, st=st)
        workspace_id = get_active_workspace_id(st)
    except Exception:
        meta = {"active_workspace_id": "?", "local_state_path": "?", "cloud_app_key": "?"}
        workspace_id = "?"

    disk_path = Path(str(meta.get("local_state_path") or ""))
    disk_meta = _read_disk_meta(disk_path)
    cloud_meta = _cloud_row_meta(APP_ID)
    identity = _account_identity()

    cloud_ts = str(cloud_meta.get("updated_at") or "")
    disk_ts = str(disk_meta.get("saved_at") or "")
    try:
        from suite_cloud_state import parse_persist_timestamp

        cloud_epoch = parse_persist_timestamp(cloud_ts)
        disk_epoch = parse_persist_timestamp(disk_ts)
    except Exception:
        cloud_epoch = 0.0
        disk_epoch = 0.0

    overwrite = _startup_overwrite_analysis(
        st, cloud_ts=cloud_ts, disk_ts=disk_ts, cloud_epoch=cloud_epoch, disk_epoch=disk_epoch
    )
    activity = _activity_emit_diagnostics(st)

    return {
        "workspace_id": workspace_id,
        "suite_user_id": identity.get("suite_user_id"),
        "account_user_id": identity.get("account_user_id"),
        "account_mode": identity.get("account_mode"),
        "cloud_read_namespace": cloud_meta.get("read_namespace"),
        "cloud_write_namespace": cloud_meta.get("write_namespace"),
        "cloud_enabled": cloud_meta.get("cloud_enabled"),
        "cloud_row_found": cloud_meta.get("row_found"),
        "cloud_updated_at": cloud_ts,
        "cloud_page": cloud_meta.get("page"),
        "cloud_summary": cloud_meta.get("summary"),
        "cloud_ui_key_count": cloud_meta.get("ui_key_count"),
        "cloud_view_mode": cloud_meta.get("view_mode"),
        "cloud_has_ami_ui_state": int(cloud_meta.get("ui_key_count") or 0) > 0,
        "disk_path": str(disk_path),
        "disk_saved_at": disk_ts,
        "disk_ui_key_count": disk_meta.get("ui_key_count"),
        "disk_view_mode": disk_meta.get("view_mode"),
        "disk_has_ami_ui_state": int(disk_meta.get("ui_key_count") or 0) > 0,
        "persisted_workspace_file": str(Path("data/suite_active_workspace.json")),
        "startup_overwrite": overwrite,
        "activity": activity,
        "session_flags": {
            "workspace_prepared": bool(ss.get("_applied_intelligence_workspace_prepared")),
            "disk_shell_had_state": bool(ss.get("_applied_intelligence_disk_shell_had_state")),
            "cloud_sync_overwrote_disk": bool(ss.get("_cloud_workspace_restored_this_run")),
        },
    }
