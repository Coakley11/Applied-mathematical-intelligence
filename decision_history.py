"""Persist imported decision problems to workspace history."""

from __future__ import annotations

import copy
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HISTORY_FILENAME = "ami_import_history.json"
_MAX_ENTRIES = 100


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _history_path(workspace_id: str | None = None) -> Path:
    from suite_workspace import resolve_workspace_id, workspace_dir

    ws = resolve_workspace_id(explicit=workspace_id) if workspace_id else resolve_workspace_id()
    path = workspace_dir(ws) / _HISTORY_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _read_history(workspace_id: str | None = None) -> list[dict[str, Any]]:
    path = _history_path(workspace_id)
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            return raw
    except (OSError, json.JSONDecodeError):
        pass
    return []


def _write_history(entries: list[dict[str, Any]], workspace_id: str | None = None) -> bool:
    path = _history_path(workspace_id)
    try:
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(entries[:_MAX_ENTRIES], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)
        return True
    except OSError:
        return False


def list_import_history(workspace_id: str | None = None) -> list[dict[str, Any]]:
    return _read_history(workspace_id)


def get_import_entry(entry_id: str, workspace_id: str | None = None) -> dict[str, Any] | None:
    for entry in _read_history(workspace_id):
        if str(entry.get("id")) == str(entry_id):
            return entry
    return None


def save_import_entry(
    *,
    source_type: str,
    decision_type: str,
    raw_input: str,
    fields: dict[str, Any],
    analysis: dict[str, Any] | None = None,
    completeness: dict[str, Any] | None = None,
    user_notes: str = "",
    workspace_id: str | None = None,
) -> dict[str, Any]:
    """Append an imported problem to workspace history."""
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": _utc_now(),
        "source_type": source_type,
        "decision_type": decision_type,
        "raw_input": raw_input[:4000],
        "fields": copy.deepcopy(fields),
        "analysis": copy.deepcopy(analysis) if analysis else None,
        "completeness": copy.deepcopy(completeness) if completeness else None,
        "user_notes": str(user_notes or "").strip(),
    }
    entries = _read_history(workspace_id)
    entries.insert(0, entry)
    _write_history(entries, workspace_id)
    return entry


def update_import_notes(entry_id: str, notes: str, workspace_id: str | None = None) -> bool:
    entries = _read_history(workspace_id)
    for entry in entries:
        if str(entry.get("id")) == str(entry_id):
            entry["user_notes"] = str(notes or "").strip()
            entry["updated_at"] = _utc_now()
            return _write_history(entries, workspace_id)
    return False


def delete_import_entry(entry_id: str, workspace_id: str | None = None) -> bool:
    entries = _read_history(workspace_id)
    filtered = [e for e in entries if str(e.get("id")) != str(entry_id)]
    if len(filtered) == len(entries):
        return False
    return _write_history(filtered, workspace_id)
