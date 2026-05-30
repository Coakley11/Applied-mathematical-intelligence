"""Practical lab hub and tool-first workspace renderer."""

import html

import streamlit as st

from content.domains import DOMAINS
from content.practical_labs import ACTION_LABELS, PRACTICAL_LABS, PRACTICAL_LAB_NAMES
from simulations.labs import LAB_RUNNERS
from simulations.registry import SIMULATION_RUNNERS


def _action_card(lab_name: str) -> str:
    lab = PRACTICAL_LABS[lab_name]
    tools_preview = " · ".join(t["name"] for t in lab["tools"][:3])
    return f"""
    <div class="ami-action-card">
        <div class="ami-action-icon">{html.escape(lab["icon"])}</div>
        <div class="ami-action-label">{html.escape(lab["action"])}</div>
        <h3>{html.escape(lab_name)}</h3>
        <p>{html.escape(lab["tagline"])}</p>
        <div class="ami-action-tools">{html.escape(tools_preview)}</div>
    </div>
    """


def run_tool(runner_id: str) -> None:
    runner = LAB_RUNNERS.get(runner_id) or SIMULATION_RUNNERS.get(runner_id)
    if runner:
        runner()
    else:
        st.warning(f"Tool not available: {runner_id}")


def render_action_hub() -> None:
    """Home-style hub: what do you want to do?"""
    st.markdown(
        """
        <div class="ami-hero ami-hero-action">
            <h1>What do you want to do?</h1>
            <p class="ami-tagline">Pick a goal. Use the tools. Math shows up when you need it.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    row1 = PRACTICAL_LAB_NAMES[:3]
    row2 = PRACTICAL_LAB_NAMES[3:]
    for row in (row1, row2):
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            with col:
                st.markdown(_action_card(name), unsafe_allow_html=True)

    st.caption("Select an action in the sidebar to open a lab workspace.")


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

    st.markdown(f"**Your goal:** {lab['goal']}")

    tool_names = [t["name"] for t in tools]
    tabs = st.tabs(tool_names)

    for tab, tool in zip(tabs, tools):
        with tab:
            st.caption(tool["description"])
            run_tool(tool["runner_id"])

    with st.expander("Math behind this lab", expanded=False):
        st.markdown("These tools use:")
        st.markdown("\n".join(f"- **{m}**" for m in lab["math_tools"]))
        st.caption("You do not need to master the formulas first — run a scenario, then read what the numbers mean.")

    with st.expander("Practice challenge", expanded=False):
        st.markdown(lab["practice_challenge"])

    related = [d for d in lab.get("related_domains", []) if d in DOMAINS]
    if related:
        with st.expander("Related reference topics (advanced)", expanded=False):
            st.caption("Deep domain write-ups live in Reference Library — not required to use this lab.")
            for d in related:
                tag = DOMAINS[d]["tagline"].replace("**", "")[:100]
                st.markdown(f"**{d}** — {tag}…")

    st.warning(
        "Educational simulation only — not financial, medical, gambling, or forecasting advice."
    )


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
