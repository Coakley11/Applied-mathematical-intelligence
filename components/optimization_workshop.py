"""Optimization Workshop — guided consultant flow with interactive tool."""

import streamlit as st

from components.lab_guide import render_guided_tool
from components.section_intro import render_section_header, render_start_here
from content.optimization_workshop import (
    EXAMPLE_PROBLEMS,
    OPTIMIZATION_WORKSHOP,
    PROBLEM_HINTS,
    WORKSHOP_STEPS,
)


def render_optimization_workshop() -> None:
    render_section_header(
        OPTIMIZATION_WORKSHOP["icon"],
        OPTIMIZATION_WORKSHOP["action"],
        OPTIMIZATION_WORKSHOP["tagline"],
    )

    render_start_here(
        "Pick an example problem (or describe your own), skim the quick analysis, "
        "then try the interactive optimizer at the bottom.",
        [
            "Choose a problem type from the dropdown.",
            "Read the suggested objective and constraints.",
            "Scroll to **Try the optimizer** and move the sliders.",
        ],
    )

    problem_choice = st.selectbox("What do you want to improve?", EXAMPLE_PROBLEMS)
    custom_problem = ""
    if problem_choice == "Custom problem (describe below)":
        custom_problem = st.text_area(
            "Describe it in one sentence",
            placeholder="e.g. Reduce wait times at my restaurant without hiring more staff",
        )

    hints = PROBLEM_HINTS.get(problem_choice, {})

    if hints:
        with st.container(border=True):
            st.markdown("**Quick read for this problem**")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Goal:** {hints['objective']}")
                st.markdown(f"**Levers:** {hints['variables']}")
            with c2:
                st.markdown(f"**Limits:** {hints['constraints']}")
                st.markdown(f"**Unknowns:** {hints['uncertainty']}")

    with st.expander("8-step framework (optional walkthrough)", expanded=False):
        for step in WORKSHOP_STEPS:
            with st.expander(f"Step {step['num']}: {step['title']}", expanded=False):
                st.markdown(f"*{step['prompt']}*")
                st.markdown(step["guidance"])
                if hints and step["num"] <= 5:
                    hint_key = {
                        1: "objective",
                        2: "variables",
                        3: "constraints",
                        4: "uncertainty",
                        5: "math",
                    }.get(step["num"])
                    if hint_key and hint_key in hints:
                        st.info(f"For your problem: {hints[hint_key]}")

    st.markdown("#### Try the optimizer")
    st.caption("Allocate a budget across projects — find the best mix within a risk limit.")
    render_guided_tool("lab_optimization")

    active = custom_problem.strip() or problem_choice
    if active and active != "Custom problem (describe below)" and hints:
        with st.expander("Your problem summary", expanded=False):
            st.markdown(f"**Problem:** {active}")
            st.markdown(f"**Goal:** {hints.get('objective', '—')}")

    st.caption("Educational framework only — not professional consulting or advice.")
