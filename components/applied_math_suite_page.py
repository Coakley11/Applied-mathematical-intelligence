"""Polished page shell for suite questions in Applied Intelligence."""

from __future__ import annotations

from typing import Any

from components.section_intro import render_section_header
from content.problem_solving import PROBLEM_SOLVING_LAB

_SUITE_QUANT_AREA: dict[str, tuple[str, str]] = {
    "baseball": ("Sports Prediction", "🏈"),
    "nba": ("Sports Prediction", "🏈"),
    "investment": ("Forecasting & Uncertainty", "🌦"),
    "music": ("Music Practice Coaching", "🎵"),
}


def suite_quant_area_label(source_app: str) -> tuple[str, str]:
    app = str(source_app or "").strip().lower()
    if "baseball" in app:
        return _SUITE_QUANT_AREA["baseball"]
    if "nba" in app:
        return _SUITE_QUANT_AREA["nba"]
    if "investment" in app:
        return _SUITE_QUANT_AREA["investment"]
    if "music" in app:
        return _SUITE_QUANT_AREA["music"]
    return ("Modeling Real Systems", "📐")


def render_suite_question_page_header(
    st: Any,
    *,
    question: str,
    source_app: str,
    source_page: str = "",
) -> None:
    """Normal Applied Intelligence shell: area breadcrumb, Problem Solver, visible question."""
    st.markdown(
        '<p style="font-size:0.78rem;font-weight:600;color:#64748b;'
        'text-transform:uppercase;letter-spacing:0.06em;margin:0 0 0.35rem 0">'
        "Applied Mathematics</p>",
        unsafe_allow_html=True,
    )

    render_section_header(
        PROBLEM_SOLVING_LAB["icon"],
        "Problem Solver",
        "Learn the math behind your question — short answer first, then work through the calculation hands-on.",
    )

    area_name, area_icon = suite_quant_area_label(source_app)
    st.markdown(f"**Quantitative area:** {area_icon} {area_name}")

    try:
        from suite_analytical_question import source_app_label

        src_label = source_app_label(source_app) if source_app else "Suite app"
    except Exception:
        src_label = source_app or "Suite app"

    st.caption(f"From {src_label}" + (f" · {source_page}" if source_page else ""))
