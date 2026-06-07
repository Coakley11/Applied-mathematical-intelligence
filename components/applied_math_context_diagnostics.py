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

    req_keys, nested = expected_fields_for_page(source_app, source_page)
    present, missing = audit_context(context, required_keys=req_keys, nested_required=nested)

    ctx_size = context_json_size(context)
    hydration = "session JSON"
    if not context and question_id:
        hydration = "empty — check question_id load"
    elif question_id and ctx_size > 400:
        hydration = "likely full blob (question_id or resume subtitle)"

    with st.expander("Context received (Developer Mode)", expanded=False):
        st.markdown(f"**Question ID:** `{question_id or '—'}`")
        st.markdown(f"**Source app:** {source_app or '—'}")
        st.markdown(f"**Source page:** {source_page or '—'}")
        st.markdown(f"**Context size:** {ctx_size} chars ({hydration})")
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
