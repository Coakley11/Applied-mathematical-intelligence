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
        "Pick an example problem (or describe your own). Think through the objective first — "
        "then try the interactive optimizer.",
        [
            "Answer the thinking question below.",
            "Choose a problem type and read the quick analysis.",
            "Try the optimizer and compare your mix to the optimal one.",
        ],
    )

    with st.container(border=True):
        st.markdown('<p class="ami-start-label">Think first</p>', unsafe_allow_html=True)
        st.markdown("**What are we trying to optimize — and what tradeoff are we willing to make?**")
        st.text_input(
            "Your objective in plain language",
            placeholder="e.g. Maximize return without exceeding a risk limit",
            key="opt_think_objective",
        )

    problem_choice = st.selectbox("What do you want to improve?", EXAMPLE_PROBLEMS, key="opt_problem_choice")
    custom_problem = ""
    if problem_choice == "Custom problem (describe below)":
        custom_problem = st.text_area(
            "Describe it in one sentence",
            placeholder="e.g. Reduce wait times at my restaurant without hiring more staff",
            key="opt_custom_problem",
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
