"""Practical lab hub and guided workspace renderer."""

import html

import streamlit as st

import portfolio_polish as pp
from components.problem_thinking import render_lab_thinking_gate
from components.lab_guide import render_guided_tool
from components.section_intro import render_section_header, render_start_here
from content.domains import DOMAINS
from content.practical_labs import PRACTICAL_LABS


def render_practical_lab(lab_name: str) -> None:
    lab = PRACTICAL_LABS[lab_name]
    tools = lab["tools"]

    render_section_header(lab["icon"], lab["action"], lab["tagline"])

    _lab_summaries = {
        "Betting & Poker Lab": (
            "Evaluate bets and poker decisions using expected value, pot odds, and probability trees.",
            "Separates mathematically sound wagers from negative-EV traps.",
            "EV metrics, implied probability comparison, edge charts, and plain-language verdicts.",
        ),
        "AI Learning Lab": (
            "Watch gradient descent train a model on a loss landscape in real time.",
            "Builds intuition for how learning rate and noise shape AI training outcomes.",
            "Loss surface visualization, training path, and step-by-step loss curve.",
        ),
    }
    if lab_name in _lab_summaries:
        what, why, outputs = _lab_summaries[lab_name]
        pp.render_executive_summary(st, what, why, outputs)
        if (pp.is_screenshot_mode(st) or pp.is_demo_mode(st)) and lab_name == "Betting & Poker Lab":
            pp.render_hero_banner(st, "Betting EV Analysis", "Compare your probability estimate to market odds and expected value.")
        if (pp.is_screenshot_mode(st) or pp.is_demo_mode(st)) and lab_name == "AI Learning Lab":
            pp.render_hero_banner(st, "Machine Learning Training Lab", "Interactive gradient descent on a 2D loss landscape.")
        if (pp.is_screenshot_mode(st) or pp.is_demo_mode(st)) and lab_name == "Medicine & Disease Lab":
            pp.render_hero_banner(st, "Disease Spread Simulation", "SIR epidemic dynamics with peak infectious load visible immediately.")

    if not pp.is_screenshot_mode(st) and not pp.is_demo_mode(st):
        st.markdown("#### Start experimenting")
        st.caption("Use the controls below first — this is a lab, not a chapter. Optional reading is collapsed.")

    if len(tools) == 1:
        render_guided_tool(tools[0]["runner_id"])
    else:
        tool_names = [t["name"] for t in tools]
        tabs = st.tabs(tool_names)
        for tab, tool in zip(tabs, tools):
            with tab:
                render_guided_tool(tool["runner_id"])

    if not pp.is_screenshot_mode(st):
        with st.expander("Before you started — quick thinking prompts (optional)", expanded=False):
            render_lab_thinking_gate(lab_name, key_prefix=lab_name.replace(" ", "_"))

    with st.expander("What is this lab? (optional)", expanded=pp.expander_default(st)):
        render_start_here(
            lab.get("start_here", lab["intro"]),
            lab.get("start_steps"),
        )
        if lab.get("is_math_hub"):
            _render_math_systems_overview()

    related = [d for d in lab.get("related_domains", []) if d in DOMAINS]
    if related:
        with st.expander("Background reading (optional)", expanded=False):
            st.caption("Full write-ups live under Advanced reference in the sidebar.")
            for d in related:
                tag = DOMAINS[d]["tagline"].replace("**", "")[:90]
                st.markdown(f"- **{d}** — {tag}…")

    if not pp.is_screenshot_mode(st) and not pp.is_demo_mode(st):
        st.caption("Educational simulation only — not medical, gambling, or forecasting advice.")


def render_page_summary(what: str, why: str, do_here: str, skill: str) -> None:
    """Four quick-answer cards used on reference pages."""
    import html

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


def _render_math_systems_overview() -> None:
    with st.expander("Six ideas behind these tools (optional)", expanded=False):
        cols = st.columns(3)
        systems = [
            ("Small changes add up", "Drug decay, tumor growth, trajectories."),
            ("Outcomes are uncertain", "Expected value and odds for decisions."),
            ("Separate signal from noise", "Forecasts, ratings, trends."),
            ("Find the best choice", "When you can't have everything."),
            ("Run many futures", "When one formula isn't enough."),
            ("Learn from data", "How AI improves step by step."),
        ]
        for i, (name, desc) in enumerate(systems):
            with cols[i % 3]:
                st.markdown(f"**{name}**")
                st.caption(desc)
