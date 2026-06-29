"""Format Music Practice Log progress_report blobs for AMI display."""

from __future__ import annotations

import html
import re
from typing import Any

_BARE_ORPHAN_TOKENS = frozenset(
    {
        "tone",
        "timing",
        "pitch",
        "groove",
        "technique",
        "intonation",
        "articulation",
        "dynamics",
        "musicality",
    }
)

_SECTION_KEYS: tuple[tuple[str, str], ...] = (
    ("Coach Summary", "executive_summary"),
    ("Practice Activity", "practice_activity"),
    ("Upload Analysis Findings", "upload_analysis_findings"),
    ("Tone & Tuner Findings", "tone_tuner_findings"),
    ("Cross-Evidence Connections", "cross_evidence_connections"),
    ("Improvements", "improvements"),
    ("Needs Work", "needs_work"),
    ("Recommended Next Practice Plan", "recommended_next_practice_plan"),
    ("Evidence Used", "evidence_used"),
)

_SECTION_ACCENTS: dict[str, str] = {
    "executive_summary": "#2563eb",
    "practice_activity": "#64748b",
    "upload_analysis_findings": "#7c3aed",
    "tone_tuner_findings": "#0891b2",
    "cross_evidence_connections": "#9333ea",
    "improvements": "#059669",
    "needs_work": "#dc2626",
    "recommended_next_practice_plan": "#d97706",
    "evidence_used": "#475569",
    "data_safety": "#64748b",
}


def _clean_item_text(item: Any) -> str:
    text = str(item or "").strip()
    if not text:
        return ""
    if text.lower() in _BARE_ORPHAN_TOKENS:
        return ""
    return text


def _section_body_items(body: Any) -> list[str]:
    if isinstance(body, list):
        return [line for line in (_clean_item_text(item) for item in body) if line]
    cleaned = _clean_item_text(body)
    return [cleaned] if cleaned else []


def _format_report_timestamp(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    try:
        from activity_time import format_eastern_time_label, parse_activity_timestamp

        dt = parse_activity_timestamp(text)
        if dt is not None:
            return format_eastern_time_label(dt)
    except Exception:
        pass
    return text[:19].replace("T", " ")


def _parse_evidence_chips(evidence_text: str) -> list[str]:
    text = str(evidence_text or "").strip()
    if not text:
        return []
    chips: list[str] = []
    patterns = [
        (r"(\d+)\s+practice logs?", "practice logs"),
        (r"(\d+)\s+saved upload analyses?", "upload analyses"),
        (r"(\d+)\s+tone takes?", "tone takes"),
        (r"(\d+)\s+saved export", "saved multitrack exports"),
        (r"(\d+)\s+linked analyzed export", "linked analyzed exports"),
    ]
    for pattern, label in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            chips.append(f"{match.group(1)} {label}")
    range_match = re.search(r"Date range:\s*(?:\*\*)?([^*.]+?)(?:\*\*)?(?:\.|$)", text, flags=re.IGNORECASE)
    if range_match:
        chips.append(f"Date range: {range_match.group(1).strip()}")
    return chips


def _render_section_card(st: Any, heading: str, key: str, body: Any, *, bullet: bool = True) -> None:
    items = _section_body_items(body)
    if not items:
        return
    accent = _SECTION_ACCENTS.get(key, "#64748b")
    st.markdown(
        f'<div style="border-left:4px solid {accent};border-radius:8px;padding-left:.35rem;margin:.4rem 0 .15rem;">',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown(f"#### {heading}")
        if key == "executive_summary":
            st.markdown(items[0])
        elif bullet:
            for item in items:
                st.markdown(f"- {item}")
        else:
            for item in items:
                st.markdown(item)


def _render_evidence_chips(st: Any, report: dict[str, Any]) -> None:
    evidence = str(report.get("evidence_used") or "").strip()
    chips = _parse_evidence_chips(evidence)
    if not chips:
        return
    html_chips = " ".join(
        f'<span style="display:inline-block;background:#f1f5f9;border:1px solid #cbd5e1;'
        f'border-radius:999px;padding:0.2rem 0.65rem;margin:0.15rem 0.35rem 0.15rem 0;'
        f'font-size:0.82rem;">{html.escape(chip)}</span>'
        for chip in chips
    )
    st.markdown(html_chips, unsafe_allow_html=True)


def _split_plan_step(text: str) -> tuple[str, str]:
    text = str(text).strip()
    match = re.match(r"^(\d+\s*min\s*[—\-]\s*[^:]+)(?::\s*(.+))?$", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip(), (match.group(2) or "").strip()
    return text, ""


def _render_plan_section(st: Any, items: list[str]) -> None:
    accent = _SECTION_ACCENTS["recommended_next_practice_plan"]
    st.markdown(
        f'<div style="border-left:4px solid {accent};border-radius:8px;padding-left:.35rem;margin:.4rem 0 .15rem;">',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown("#### Recommended Next Practice Plan")
        st.markdown("**Next 30-minute session**")
        step = 0
        for item in items:
            title, desc = _split_plan_step(item)
            if not title:
                continue
            if re.match(r"^\d+\s*min", title, flags=re.IGNORECASE):
                step += 1
                st.markdown(f"{step}. **{title}**")
                if desc:
                    st.markdown(f"   {desc}")
            else:
                st.markdown(f"- {title}")
                if desc:
                    st.markdown(f"   {desc}")


def format_progress_report_markdown(report: dict[str, Any]) -> str:
    """Render progress report sections as markdown (10-section Practice Analysis)."""
    lines = [f"# {report.get('title', 'Analyze My Practice — Progress Report')}", ""]
    for heading, key in _SECTION_KEYS:
        body = report.get(key)
        items = _section_body_items(body)
        if not items:
            continue
        lines.append(f"## {heading}")
        if key == "executive_summary":
            lines.append(items[0])
        else:
            for item in items:
                lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).strip()


def render_progress_report_ui(
    st: Any,
    report: dict[str, Any],
    *,
    dev_mode: bool = False,
    updated_at: str = "",
    skip_title: bool = False,
) -> None:
    """Render the 10-section report with bordered section cards for AMI."""
    if not skip_title:
        st.markdown("# Music Practice Log Analysis")
        st.caption(
            "Synthesized from your saved practice logs, upload analyses, tone takes, and multitrack evidence."
        )
        ts = _format_report_timestamp(updated_at)
        if ts:
            st.caption(f"Updated {ts}")

    summary = str(report.get("executive_summary") or "").strip()
    if summary:
        _render_section_card(st, "Coach Summary", "executive_summary", summary, bullet=False)
        _render_evidence_chips(st, report)

    for heading, key in _SECTION_KEYS:
        if key in {"executive_summary", "evidence_used", "recommended_next_practice_plan"}:
            continue
        _render_section_card(st, heading, key, report.get(key))

    plan_items = _section_body_items(report.get("recommended_next_practice_plan"))
    if plan_items:
        _render_plan_section(st, plan_items)

    evidence_items = _section_body_items(report.get("evidence_used"))
    if evidence_items:
        _render_section_card(st, "Evidence Used", "evidence_used", evidence_items, bullet=False)

    safety = report.get("data_safety_confirmation") if isinstance(report.get("data_safety_confirmation"), dict) else {}
    if dev_mode and safety:
        with st.container(border=True):
            st.markdown("#### Data Safety Confirmation")
            st.markdown(
                f"- Raw audio excluded: **{safety.get('raw_audio_excluded', True)}** · "
                f"Base64 excluded: **{safety.get('base64_excluded', True)}** · "
                f"Deleted items excluded: **{safety.get('deleted_items_excluded', True)}**"
            )
    elif not dev_mode:
        _render_section_card(
            st,
            "Data Safety",
            "data_safety",
            "This report used saved summaries and metadata only. Raw audio was not included.",
            bullet=False,
        )

    if dev_mode:
        with st.expander("Practice Log report payload (Developer Mode)", expanded=False):
            st.json(report)
