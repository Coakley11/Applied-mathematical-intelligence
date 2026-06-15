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

    try:
        from suite_resume_launch import resolve_url_suite_ai_question_id

        url_qid = resolve_url_suite_ai_question_id(st)
    except Exception:
        url_qid = _query_param(st, "suite_ai_question_id")

    blob_meta = st.session_state.get("_suite_ai_blob_meta")
    meta = dict(blob_meta) if isinstance(blob_meta, dict) else {}
    if not url_qid:
        url_qid = str(meta.get("url_question_id") or st.session_state.get("_suite_ai_url_question_id") or "").strip()
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
        "question_id_match": bool(
            url_qid and loaded_qid and url_qid == loaded_qid and (not payload_qid or payload_qid == loaded_qid)
        ),
        "blob_load_source": meta.get("blob_load_source") or st.session_state.get("_suite_ai_hydrate_source"),
        "blob_store_app": meta.get("blob_store_app"),
        "blob_load_error": meta.get("blob_load_error"),
        "blob_updated_at": meta.get("blob_updated_at"),
        "blob_payload_hash": meta.get("blob_payload_hash"),
        "loaded_context_hash": loaded_context_hash,
        "payload_hash_matches_loaded_context": hash_match,
        "query_params_present": query_params_present,
        "context_json_length": len(ctx_raw),
        "hydrate_attempted": st.session_state.get("_suite_ai_hydrate_attempted"),
        "hydrate_error": st.session_state.get("_suite_ai_hydrate_error"),
        "session_hydrate_source": st.session_state.get("_suite_ai_hydrate_source"),
        "available_players_count_hydrated": len(avail) if isinstance(avail, list) else 0,
        "draft_snapshot_available_players_count": len(snap.get("available_players") or [])
        if isinstance(snap.get("available_players"), list)
        else 0,
        "best_available_count": len(best) if isinstance(best, list) else 0,
        "current_pick": context.get("current_pick") or snap.get("current_pick"),
        "blob_load_candidates": meta.get("blob_load_candidates"),
    }


_BLOB_IDENTITY_ALWAYS_SHOW = (
    "deploy_build",
    "deploy_commit",
    "query_params_present",
    "url_question_id",
    "loaded_question_id",
    "payload_question_id",
    "question_id_match",
    "blob_load_source",
    "blob_store_app",
    "blob_load_error",
    "context_json_length",
    "hydrate_attempted",
    "hydrate_error",
)


def classify_ami_hydration_status(identity: dict[str, Any]) -> tuple[str, str]:
    """
    Classify hydration for Dev Mode.
    Returns (level, message) where level is error | warning | success | info.
    """
    url_qid = str(identity.get("url_question_id") or "").strip()
    hydrate_err = str(identity.get("hydrate_error") or "").strip()
    blob_err = str(identity.get("blob_load_error") or "").strip()
    hydrate_src = str(
        identity.get("blob_load_source") or identity.get("session_hydrate_source") or ""
    ).strip()
    attempted = bool(identity.get("hydrate_attempted"))
    avail = int(identity.get("available_players_count_hydrated") or 0)

    if hydrate_err:
        return ("error", f"Hydration error: {hydrate_err}")
    if not url_qid:
        return (
            "error",
            "URL question_id missing — Continue URL is wrong or stale. "
            "Send a new question from Baseball and open the new Command Center Continue card.",
        )
    if blob_err and blob_err not in {"", "no_blob_context_for_question_id"}:
        return ("error", f"Blob load failed: {blob_err}")
    if attempted and (not hydrate_src or hydrate_src == "none"):
        detail = blob_err or "no_blob_context_for_question_id"
        return ("error", f"Blob load failed: {detail}")
    if attempted and avail == 0 and hydrate_src in {"", "none", "resume_subtitle"}:
        if hydrate_src == "resume_subtitle":
            return (
                "warning",
                "Blob load used resume_subtitle fallback only — full draft pool was not restored.",
            )
        return ("error", f"Blob load failed: {blob_err or 'empty_context_after_load'}")
    if hydrate_src and hydrate_src != "none":
        return ("success", f"Hydrated from {hydrate_src} · {avail} available player(s) in context.")
    if not attempted:
        return ("info", "Hydration not attempted — open AMI via a Continue URL with suite_ai_question_id.")
    return ("warning", "Hydration status unclear — inspect fields below.")


def render_hydration_status_banner(st: Any, identity: dict[str, Any], *, context: str = "AMI") -> None:
    """Prominent Dev Mode banner: URL missing vs blob failure vs success."""
    level, message = classify_ami_hydration_status(identity)
    if level == "error":
        st.error(f"**{context}:** {message}")
    elif level == "warning":
        st.warning(f"**{context}:** {message}")
    elif level == "success":
        st.success(f"**{context}:** {message}")
    else:
        st.info(f"**{context}:** {message}")


def render_url_intake_sidebar_panel(st: Any) -> None:
    """Sidebar Dev Mode panel — URL/question_id intake before solver runs."""
    if not applied_math_developer_mode_enabled(st):
        return
    identity = build_load_identity_diagnostics(st, context={}, question_id="")
    identity["startup_error"] = st.session_state.get("_suite_ai_startup_error")
    with st.sidebar.expander("URL intake (AMI load)", expanded=True):
        render_hydration_status_banner(st, identity, context="Hydrated context")
        for key in _BLOB_IDENTITY_ALWAYS_SHOW:
            val = identity.get(key)
            st.text(f"{key}: {val if val is not None and val != '' else '—'}")
        if identity.get("startup_error"):
            st.text(f"startup_error: {identity['startup_error']}")


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
        render_hydration_status_banner(st, identity, context="Hydrated context")
        for key in _BLOB_IDENTITY_ALWAYS_SHOW:
            val = identity.get(key)
            st.text(f"{key}: {val if val is not None and val != '' else '—'}")
        for key, val in identity.items():
            if key in _BLOB_IDENTITY_ALWAYS_SHOW:
                continue
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
        try:
            from components.applied_math_context_diagnostics import (
                build_load_identity_diagnostics,
                render_hydration_status_banner,
            )

            intake_identity = build_load_identity_diagnostics(st, context=context, question_id=question_id)
            intake_identity.update(pool_diag)
        except Exception:
            intake_identity = dict(pool_diag)
        with st.expander("Draft pool diagnostics (Developer Mode)", expanded=True):
            render_hydration_status_banner(st, intake_identity, context="Hydrated context")
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
