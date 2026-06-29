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
    ("Executive Summary", "executive_summary"),
    ("Practice Activity", "practice_activity"),
    ("Upload Analysis Findings", "upload_analysis_findings"),
    ("Tone & Tuner Findings", "tone_tuner_findings"),
    ("Cross-Evidence Connections", "cross_evidence_connections"),
    ("Improvements", "improvements"),
    ("Needs Work", "needs_work"),
    ("Recommended Next Practice Plan", "recommended_next_practice_plan"),
    ("Evidence Used", "evidence_used"),
)


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


def _inline_md_to_html(text: str) -> str:
    """Minimal markdown (**bold**) → HTML for section bodies."""
    escaped = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


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
    safety = report.get("data_safety_confirmation") if isinstance(report.get("data_safety_confirmation"), dict) else {}
    if safety:
        lines.append("## Data Safety Confirmation")
        lines.append(
            f"- Raw audio excluded: **{safety.get('raw_audio_excluded', True)}** · "
            f"Base64 excluded: **{safety.get('base64_excluded', True)}** · "
            f"Deleted items excluded: **{safety.get('deleted_items_excluded', True)}**"
        )
    return "\n".join(lines).strip()


def render_progress_report_ui(st: Any, report: dict[str, Any]) -> None:
    """Render the 10-section report with bordered section cards for AMI."""
    title = str(report.get("title") or "Analyze My Practice — Progress Report").strip()
    st.markdown(f"## {title}")
    st.caption("Music Practice Log Analysis — synthesized from your saved practice evidence.")
    for heading, key in _SECTION_KEYS:
        items = _section_body_items(report.get(key))
        if not items:
            continue
        with st.container(border=True):
            st.markdown(f"#### {heading}")
            if key == "executive_summary":
                st.markdown(items[0])
            else:
                for item in items:
                    st.markdown(f"- {item}")
    safety = report.get("data_safety_confirmation") if isinstance(report.get("data_safety_confirmation"), dict) else {}
    if safety:
        with st.container(border=True):
            st.markdown("#### Data Safety Confirmation")
            st.markdown(
                f"- Raw audio excluded: **{safety.get('raw_audio_excluded', True)}** · "
                f"Base64 excluded: **{safety.get('base64_excluded', True)}** · "
                f"Deleted items excluded: **{safety.get('deleted_items_excluded', True)}**"
            )
