"""Optimization Workshop — guided consultant flow with interactive tool."""

import html

import streamlit as st

from components.lab_guide import render_guided_tool
from content.optimization_workshop import (
    EXAMPLE_PROBLEMS,
    OPTIMIZATION_WORKSHOP,
    PROBLEM_HINTS,
    WORKSHOP_STEPS,
)


def render_optimization_workshop() -> None:
    st.markdown(
        f"""
        <div class="ami-lab-header">
            <span class="ami-lab-icon-lg">{html.escape(OPTIMIZATION_WORKSHOP["icon"])}</span>
            <div>
                <span class="ami-badge">{html.escape(OPTIMIZATION_WORKSHOP["action"])}</span>
                <h2 style="margin:0.25rem 0 0 0;">{html.escape(OPTIMIZATION_WORKSHOP["title"])}</h2>
                <p style="margin:0.35rem 0 0 0;color:#64748b;font-size:0.95rem;">
                    {html.escape(OPTIMIZATION_WORKSHOP["tagline"])}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(OPTIMIZATION_WORKSHOP["intro"])

    st.markdown("#### Step 0: Describe your problem")
    problem_choice = st.selectbox("Start from an example or describe your own", EXAMPLE_PROBLEMS)
    custom_problem = ""
    if problem_choice == "Custom problem (describe below)":
        custom_problem = st.text_area(
            "Describe what you want to improve",
            placeholder="e.g. Reduce wait times at my restaurant without hiring more staff",
        )

    active_problem = custom_problem.strip() if custom_problem.strip() else problem_choice
    hints = PROBLEM_HINTS.get(problem_choice, {})

    if hints:
        st.markdown("##### Quick analysis for this problem type")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Objective:** {hints['objective']}")
            st.markdown(f"**Variables:** {hints['variables']}")
        with c2:
            st.markdown(f"**Constraints:** {hints['constraints']}")
            st.markdown(f"**Uncertainty:** {hints['uncertainty']}")
        st.markdown(f"**Relevant math:** {hints['math']}")

    st.markdown("---")
    st.markdown("#### The 8-step optimization framework")

    for step in WORKSHOP_STEPS:
        with st.expander(f"Step {step['num']}: {step['title']}", expanded=step["num"] == 1):
            st.markdown(f"*{step['prompt']}*")
            st.markdown(step["guidance"])
            st.markdown("**Examples:**")
            for ex in step["examples"]:
                st.markdown(f"- {ex}")
            if hints and step["num"] <= 5:
                hint_key = {
                    1: "objective",
                    2: "variables",
                    3: "constraints",
                    4: "uncertainty",
                    5: "math",
                }.get(step["num"])
                if hint_key and hint_key in hints:
                    st.info(f"**For your problem:** {hints[hint_key]}")

    st.markdown("---")
    st.markdown("#### Try optimization yourself")
    st.caption("Interactive resource allocation — the same optimize-within-constraints pattern.")
    render_guided_tool("lab_optimization")

    if active_problem and active_problem != "Custom problem (describe below)":
        with st.expander("Your problem summary", expanded=False):
            st.markdown(f"**Problem:** {active_problem}")
            if hints:
                st.markdown(f"**Suggested objective:** {hints.get('objective', 'Define clearly')}")
                st.markdown(f"**Key variables:** {hints.get('variables', 'List your levers')}")
                st.markdown(f"**Main constraints:** {hints.get('constraints', 'What limits you?')}")

    st.warning("Educational framework only — not professional consulting or advice.")
