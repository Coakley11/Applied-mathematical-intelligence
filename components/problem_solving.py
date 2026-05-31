"""Solve a Problem — quantitative analyst flow (hands-on, not interview)."""

import re

import streamlit as st

from components.problem_analyst import (
    render_analyst_brief,
    render_interactive_analysis,
    render_show_math,
    render_try_yourself,
)
from components.problem_coach import render_problem_library
from components.section_intro import render_section_header
from components.thinking_lab import render_thinking_topics_panel
from content.problem_solving import (
    DEFAULT_PATTERN,
    EXAMPLE_PROBLEMS,
    MATHEMATICIAN_MODE_TOPICS,
    PROBLEM_PATTERNS,
    PROBLEM_SOLVING_LAB,
)


def _match_pattern(text: str) -> dict:
    lower = text.lower()
    for pattern, data in PROBLEM_PATTERNS.items():
        if re.search(pattern, lower):
            return data
    return DEFAULT_PATTERN


def _load_library_problem(problem: str) -> None:
    st.session_state.ps_library_problem = problem
    st.session_state.ps_example = "Custom question (describe below)"
    st.rerun()


def render_problem_solving_lab() -> None:
    render_section_header(
        PROBLEM_SOLVING_LAB["icon"],
        PROBLEM_SOLVING_LAB["action"],
        PROBLEM_SOLVING_LAB["tagline"],
    )

    tab_solve, tab_examples, tab_thinking = st.tabs(
        ["Solve a problem", "Example questions", "Mathematical thinking"]
    )

    with tab_solve:
        _render_solve_flow()

    with tab_examples:
        render_problem_library(_load_library_problem)

    with tab_thinking:
        _render_mathematical_thinking()


def _render_solve_flow() -> None:
    st.markdown("#### Enter a quantitative question")
    st.caption(
        "Bring a specific question — odds, predictions, models, strategies — not general life advice."
    )

    library_problem = st.session_state.get("ps_library_problem", "")
    example = st.selectbox("Example question", EXAMPLE_PROBLEMS, key="ps_example")
    custom = ""
    if example == "Custom question (describe below)":
        custom = st.text_area(
            "Your question",
            value=library_problem,
            placeholder="e.g. Is this bet at +150 worth it if I estimate a 45% win chance?",
            key="ps_custom",
        )

    problem = custom.strip() if custom.strip() else example
    if problem == "Custom question (describe below)":
        st.info("Type a specific quantitative question above.")
        return

    pattern = _match_pattern(problem)
    pattern_id = pattern.get("id", "default")
    key_prefix = f"ps_{pattern_id}"

    st.markdown("---")
    render_analyst_brief(pattern, problem, pattern_id)

    st.markdown("---")
    render_interactive_analysis(pattern_id, key_prefix)

    st.markdown("---")
    render_show_math(pattern_id)

    st.markdown("---")
    render_try_yourself(pattern)


def _render_mathematical_thinking() -> None:
    """Separate from solve flow — how mathematicians think."""
    st.markdown("#### How do mathematicians think?")
    st.caption("Habits of mind for quantitative problems — study separately from solving.")

    sub_habits, sub_topics = st.tabs(["Core ideas", "Topic library"])

    with sub_habits:
        topic_names = [t["name"] for t in MATHEMATICIAN_MODE_TOPICS]
        choice = st.selectbox("Concept", topic_names, key="ps_math_mode_topic")
        topic = next(t for t in MATHEMATICIAN_MODE_TOPICS if t["name"] == choice)

        with st.container(border=True):
            st.markdown(f"**{topic['name']}**")
            st.markdown(topic["idea"])
            st.info(f"Example: {topic['example']}")

        st.text_area(
            topic["prompt"],
            placeholder="Apply this to a quantitative question you're working on…",
            key=f"ps_mode_{topic['id']}",
            height=80,
        )

    with sub_topics:
        render_thinking_topics_panel()
