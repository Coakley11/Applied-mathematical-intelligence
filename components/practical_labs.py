"""Practical lab hub and guided workspace renderer."""

import html

import streamlit as st

from components.lab_guide import render_guided_tool
from content.domains import DOMAINS
from content.practical_labs import (
    ACTION_DESCRIPTIONS,
    ACTION_LABELS,
    PRACTICAL_LABS,
    PRACTICAL_LAB_NAMES,
)
from content.themes import THEMES, THEME_NAMES


def _action_card(lab_name: str) -> str:
    lab = PRACTICAL_LABS[lab_name]
    desc = ACTION_DESCRIPTIONS.get(lab_name, lab["tagline"])
    return f"""
    <div class="ami-action-card">
        <div class="ami-action-icon">{html.escape(lab["icon"])}</div>
        <div class="ami-action-label">{html.escape(lab["action"])}</div>
        <h3>{html.escape(lab_name)}</h3>
        <p>{html.escape(desc)}</p>
    </div>
    """


def render_practical_lab(lab_name: str) -> None:
    lab = PRACTICAL_LABS[lab_name]
    tools = lab["tools"]

    st.markdown(
        f"""
        <div class="ami-lab-header">
            <span class="ami-lab-icon-lg">{html.escape(lab["icon"])}</span>
            <div>
                <span class="ami-badge">{html.escape(lab["action"])}</span>
                <h2 style="margin:0.25rem 0 0 0;">{html.escape(lab_name)}</h2>
                <p style="margin:0.35rem 0 0 0;color:#64748b;font-size:0.95rem;">{html.escape(lab["tagline"])}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(lab["intro"])

    if lab.get("is_math_hub"):
        _render_math_systems_overview()

    if len(tools) == 1:
        render_guided_tool(tools[0]["runner_id"])
    else:
        tool_names = [t["name"] for t in tools]
        tabs = st.tabs(tool_names)
        for tab, tool in zip(tabs, tools):
            with tab:
                render_guided_tool(tool["runner_id"])

    related = [d for d in lab.get("related_domains", []) if d in DOMAINS]
    if related:
        with st.expander("Related topics (advanced reading)", expanded=False):
            st.caption("Optional depth — open Reference library in the sidebar for full write-ups.")
            for d in related:
                tag = DOMAINS[d]["tagline"].replace("**", "")[:90]
                st.markdown(f"**{d}** — {tag}…")

    st.warning(
        "Educational simulation only — not medical, gambling, or forecasting advice."
    )


def _render_math_systems_overview() -> None:
    st.markdown("#### Six systems that power these labs")
    cols = st.columns(3)
    systems = [
        ("Accumulation", "Calculus", "Small rates of change compound into large outcomes — drug decay, tumor growth, trajectories."),
        ("Uncertainty", "Probability", "Expected value and odds for decisions when outcomes are not certain."),
        ("Pattern Detection", "Statistics", "Separate signal from noise — regression, shrinkage, forecasting."),
        ("Optimization", "Constraints", "Find the best choice when you cannot have everything."),
        ("Simulation", "Monte Carlo", "Run many possible futures when formulas alone are not enough."),
        ("Learning", "AI / Gradients", "Minimize error by following the slope — how AI trains."),
    ]
    for i, (name, badge, desc) in enumerate(systems):
        with cols[i % 3]:
            st.markdown(f"**{name}** ({badge})")
            st.caption(desc)

    with st.expander("Browse all six math themes (advanced)", expanded=False):
        choice = st.selectbox("Theme", THEME_NAMES, key="math_hub_theme")
        theme = THEMES[choice]
        st.markdown(theme["tagline"])
        st.markdown(theme["why_matters"][:400] + "…")


def render_page_summary(what: str, why: str, do_here: str, skill: str) -> None:
    """Four quick-answer cards used on reference pages."""
    st.markdown(
        f"""
        <div class="ami-summary-grid">
            <div class="ami-summary-card">
                <div class="ami-summary-label">What is this?</div>
                <div class="ami-summary-text">{html.escape(what)}</div>
            </div>
            <div class="ami-summary-card">
                <div class="ami-summary-label">Why does the math matter?</div>
                <div class="ami-summary-text">{html.escape(why[:220] + ("…" if len(why) > 220 else ""))}</div>
            </div>
            <div class="ami-summary-card">
                <div class="ami-summary-label">What can I do here?</div>
                <div class="ami-summary-text">{html.escape(do_here)}</div>
            </div>
            <div class="ami-summary-card">
                <div class="ami-summary-label">Skill you build</div>
                <div class="ami-summary-text">{html.escape(skill)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
