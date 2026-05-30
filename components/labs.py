"""Interactive Labs hub and lab page renderer."""

import html

import streamlit as st

from content.interactive_labs import INTERACTIVE_LABS, LAB_NAMES
from simulations.labs import LAB_RUNNERS


def _lab_card(name: str, lab: dict) -> str:
    return f"""
    <div class="ami-card ami-card-lab">
        <span class="ami-lab-icon">{html.escape(lab["icon"])}</span>
        <span class="ami-badge">{html.escape(lab["badge"])}</span>
        <h4>{html.escape(name)}</h4>
        <p>{html.escape(lab["tagline"])}</p>
    </div>
    """


def render_labs_hub() -> None:
    st.markdown(
        """
        <div class="ami-hero ami-hero-labs">
            <h1>Interactive Labs</h1>
            <p class="ami-tagline">Do the math — don't just read about it.</p>
            <p class="ami-purpose">
                Hands-on modules for poker decisions, sports EV, portfolio risk, forecasting,
                optimization, and AI training. Pick a lab below or use the sidebar.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="ami-section-title">Choose a lab</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ami-section-sub">Each lab follows the same flow: goal → math → controls → result → challenge.</p>',
        unsafe_allow_html=True,
    )

    rows = [LAB_NAMES[i : i + 3] for i in range(0, len(LAB_NAMES), 3)]
    for row in rows:
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            lab = INTERACTIVE_LABS[name]
            with col:
                st.markdown(_lab_card(name, lab), unsafe_allow_html=True)

    st.info(
        "Select a lab in the **sidebar** to open the interactive workspace. "
        "All labs include educational disclaimers — not financial or gambling advice."
    )


def render_lab_page(lab_name: str) -> None:
    lab = INTERACTIVE_LABS[lab_name]
    runner_id = lab["runner_id"]
    runner = LAB_RUNNERS.get(runner_id)

    st.markdown(
        f"""
        <div class="ami-lab-header">
            <span class="ami-lab-icon-lg">{html.escape(lab["icon"])}</span>
            <div>
                <span class="ami-badge">{html.escape(lab["badge"])}</span>
                <h2 style="margin:0.25rem 0 0 0;">{html.escape(lab_name)}</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_page_summary(
        what=lab["tagline"],
        why=lab["math_idea"].replace("**", ""),
        do_here="Use the controls below to test scenarios and see mathematical recommendations.",
        skill=lab["skill"],
    )

    st.markdown("---")

    with st.container(border=True):
        st.markdown("##### What you are trying to do")
        st.markdown(lab["goal"])

    with st.container(border=True):
        st.markdown("##### Math idea used")
        st.markdown(lab["math_idea"])

    st.markdown("##### Interactive workspace")
    if runner:
        runner()
    else:
        st.warning("Lab simulation is not available.")

    with st.expander("Practice challenge", expanded=False):
        st.markdown(lab["practice_challenge"])

    with st.expander("Portfolio project idea", expanded=False):
        st.markdown(lab["portfolio_project"])


def render_page_summary(what: str, why: str, do_here: str, skill: str) -> None:
    """Four quick-answer cards used on lab, theme, and domain pages."""
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
