"""Developer Mode diagnostics for suite Applied Math context hydration."""

from __future__ import annotations

import json
from typing import Any

from applied_math_quality_validation import (
    audit_context,
    context_json_size,
    expected_fields_for_page,
)


def applied_math_developer_mode_enabled(st: Any) -> bool:
    return bool(st.session_state.get("app_developer_mode", False))


def render_developer_mode_sidebar_toggle(st: Any) -> None:
    st.session_state.setdefault("app_developer_mode", False)
    st.sidebar.checkbox(
        "Developer Mode",
        value=False,
        key="app_developer_mode",
        help="Show Applied Math context diagnostics (question id, fields received, missing fields).",
    )


def _query_param(st: Any, name: str) -> str:
    try:
        raw = st.query_params.get(name)
    except Exception:
        return ""
    if raw is None:
        return ""
    if isinstance(raw, list):
        return str(raw[0] or "").strip()
    return str(raw).strip()


def build_load_identity_diagnostics(
    st: Any,
    *,
    context: dict[str, Any],
    question_id: str,
) -> dict[str, Any]:
    try:
        from applied_math_build_info import GIT_COMMIT, SOLVER_BUILD_MARKER
    except ImportError:
        SOLVER_BUILD_MARKER, GIT_COMMIT = "unknown", "unknown"

    blob_meta = st.session_state.get("_suite_ai_blob_meta")
    meta = dict(blob_meta) if isinstance(blob_meta, dict) else {}
    url_qid = _query_param(st, "suite_ai_question_id") or meta.get("url_question_id") or ""
    loaded_qid = str(question_id or st.session_state.get("_suite_ai_question_id") or meta.get("loaded_question_id") or "").strip()
    payload_qid = str(meta.get("payload_question_id") or "").strip()

    snap = context.get("draft_snapshot") if isinstance(context.get("draft_snapshot"), dict) else {}
    avail = context.get("available_players") or snap.get("available_players") or []
    best = context.get("best_available") or snap.get("best_available_players") or []

    try:
        from suite_analytical_question import _context_payload_hash

        loaded_context_hash = _context_payload_hash(context) if context else meta.get("loaded_context_hash")
    except Exception:
        loaded_context_hash = meta.get("loaded_context_hash")

    hash_match = bool(meta.get("blob_payload_hash") and loaded_context_hash == meta.get("blob_payload_hash"))

    ctx_raw = str(st.session_state.get("_suite_ai_context") or "")
    try:
        from suite_cloud_state import list_active_resume_query_params

        query_params_present = list_active_resume_query_params(st, "applied_intelligence")
    except Exception:
        query_params_present = []

    return {
        "deploy_build": SOLVER_BUILD_MARKER,
        "deploy_commit": GIT_COMMIT,
        "url_question_id": url_qid or None,
        "loaded_question_id": loaded_qid or None,
        "payload_question_id": payload_qid or None,
        "question_id_match": bool(url_qid and loaded_qid and url_qid == loaded_qid == (payload_qid or loaded_qid)),
        "blob_load_source": meta.get("blob_load_source") or st.session_state.get("_suite_ai_hydrate_source"),
        "blob_store_app": meta.get("blob_store_app"),
        "blob_load_error": meta.get("blob_load_error"),
        "blob_updated_at": meta.get("blob_updated_at"),
        "blob_payload_hash": meta.get("blob_payload_hash"),
        "loaded_context_hash": loaded_context_hash,
        "payload_hash_matches_loaded_context": hash_match,
        "query_params_present": query_params_present,
        "context_json_length": len(ctx_raw),
        "available_players_count_hydrated": len(avail) if isinstance(avail, list) else 0,
        "draft_snapshot_available_players_count": len(snap.get("available_players") or [])
        if isinstance(snap.get("available_players"), list)
        else 0,
        "best_available_count": len(best) if isinstance(best, list) else 0,
        "current_pick": context.get("current_pick") or snap.get("current_pick"),
        "blob_load_candidates": meta.get("blob_load_candidates"),
    }


def render_applied_math_context_diagnostics(
    st: Any,
    *,
    question: str,
    question_id: str,
    source_app: str,
    source_page: str,
    context: dict[str, Any],
) -> None:
    if not applied_math_developer_mode_enabled(st):
        return

    identity = build_load_identity_diagnostics(st, context=context, question_id=question_id)
    with st.expander("Blob identity (AMI load)", expanded=True):
        for key, val in identity.items():
            if val is None or val == "" or val == {} or val == []:
                continue
            st.text(f"{key}: {val}")
        if identity.get("blob_payload_hash") and identity.get("loaded_context_hash"):
            if not identity.get("payload_hash_matches_loaded_context"):
                st.warning("Loaded context hash does not match blob_payload_hash — stale or merged payload.")
        if identity.get("available_players_count_hydrated", 0) == 0 and identity.get("blob_load_source") == "resume_subtitle":
            st.warning("Loaded from resume subtitle fallback — not full saved blob.")

    req_keys, nested = expected_fields_for_page(source_app, source_page)
    present, missing = audit_context(context, required_keys=req_keys, nested_required=nested)

    ctx_size = context_json_size(context)
    hydrate = str(st.session_state.get("_suite_ai_hydrate_source") or "").strip()
    if hydrate == "question_id_blob":
        hydration = "question_id blob (full payload)"
    elif hydrate == "resume_subtitle":
        hydration = "resume subtitle (truncated fallback)"
    elif hydrate == "metrics":
        hydration = "resume metrics"
    elif hydrate == "url_query":
        hydration = "URL query (may be truncated)"
    elif hydrate == "session_json":
        hydration = "session JSON"
    elif not context and question_id:
        hydration = "empty — check question_id load"
    elif question_id and ctx_size > 400:
        hydration = "likely full blob (question_id or resume subtitle)"
    else:
        hydration = "session JSON"

    with st.expander("Context received (Developer Mode)", expanded=False):
        st.markdown(f"**Question ID:** `{question_id or '—'}`")
        st.markdown(f"**Source app:** {source_app or '—'}")
        st.markdown(f"**Source page:** {source_page or '—'}")
        st.markdown(f"**Context size:** {ctx_size} chars ({hydration})")
        if hydrate:
            st.markdown(f"**Hydrate source:** `{hydrate}`")
        blob_meta = st.session_state.get("_suite_ai_blob_meta")
        if isinstance(blob_meta, dict) and blob_meta:
            st.markdown("**Blob store (loaded)**")
            for key in (
                "blob_updated_at",
                "blob_payload_hash",
                "blob_store_app",
            ):
                if blob_meta.get(key):
                    st.markdown(f"- `{key}`: `{blob_meta[key]}`")
            diag = blob_meta.get("blob_diagnostics")
            if isinstance(diag, dict):
                for key, val in diag.items():
                    st.markdown(f"- `blob_{key}`: `{val}`")
        st.markdown(f"**Question:** {question[:200]}{'…' if len(question) > 200 else ''}")
        st.caption(
            "Normal view shows 3–5 key inputs only. This panel is the full transferred payload."
        )

        if present:
            st.markdown("**Fields received**")
            for key in present:
                val = context
                for part in key.split("."):
                    val = val.get(part) if isinstance(val, dict) else None
                preview = _preview_value(val)
                st.markdown(f"- `{key}`: {preview}")
        else:
            st.caption("No expected fields matched for this page — see raw JSON below.")

        if missing:
            st.markdown("**Missing (expected for this page)**")
            for key in missing:
                st.markdown(f"- `{key}`")

    draft_snap = context.get("draft_snapshot")
    if isinstance(draft_snap, dict) and draft_snap:
        st.markdown("**Draft snapshot (received)**")
        for key in (
            "current_pick",
            "draft_round",
            "user_roster",
            "recommended_players",
            "available_players",
            "sleepers",
            "scoring_settings",
        ):
            if key in draft_snap:
                st.markdown(f"- `{key}`: {_preview_value(draft_snap.get(key))}")

    try:
        from components.draft_context_diagnostics import build_draft_context_diagnostics, render_draft_context_diagnostics_block

        hydrate_src = str(st.session_state.get("_suite_ai_hydrate_source") or hydrate or "").strip()
        pool_diag = build_draft_context_diagnostics(context, hydrate_source=hydrate_src)
        with st.expander("Draft pool diagnostics (Developer Mode)", expanded=True):
            render_draft_context_diagnostics_block(st, pool_diag, title="Hydrated context (pre-solver)")
    except Exception:
        pass

    with st.expander("Raw context JSON", expanded=False):
        st.code(json.dumps(context, indent=2, ensure_ascii=False, default=str)[:12000])


def _preview_value(val: Any, limit: int = 120) -> str:
    if isinstance(val, dict):
        text = json.dumps(val, ensure_ascii=False, default=str)
    elif isinstance(val, list):
        text = ", ".join(str(v) for v in val[:6])
    else:
        text = str(val)
    if len(text) > limit:
        return text[: limit - 1] + "…"
    return text
