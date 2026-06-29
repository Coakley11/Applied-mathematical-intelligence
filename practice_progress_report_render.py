"""Format Music Practice Log progress_report blobs for AMI display."""

from __future__ import annotations

from typing import Any


def format_progress_report_markdown(report: dict[str, Any]) -> str:
    """Render progress report sections as markdown (10-section Practice Analysis)."""
    sections = [
        ("Executive Summary", report.get("executive_summary")),
        ("Practice Activity", report.get("practice_activity")),
        ("Upload Analysis Findings", report.get("upload_analysis_findings")),
        ("Tone & Tuner Findings", report.get("tone_tuner_findings")),
        ("Cross-Evidence Connections", report.get("cross_evidence_connections")),
        ("Improvements", report.get("improvements")),
        ("Needs Work", report.get("needs_work")),
        ("Recommended Next Practice Plan", report.get("recommended_next_practice_plan")),
        ("Evidence Used", [report.get("evidence_used")]),
    ]
    lines = [f"# {report.get('title', 'Analyze My Practice — Progress Report')}", ""]
    for heading, body in sections:
        lines.append(f"## {heading}")
        if isinstance(body, list):
            for item in body:
                if item:
                    lines.append(f"- {item}")
        elif body:
            lines.append(str(body))
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
