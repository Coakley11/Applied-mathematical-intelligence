"""Mathematical Problem Solving Lab — adaptive thinking coach."""

import re

import streamlit as st

from components.problem_coach import (
    compute_thinking_score,
    render_adaptive_questions,
    render_challenge_questions,
    render_expert_perspectives,
    render_problem_library,
    render_problem_pipeline,
    render_thinking_score,
)
from components.section_intro import render_section_header
from components.thinking_lab import render_thinking_topics_panel
from content.problem_solving import (
    DEFAULT_PATTERN,
    EXAMPLE_PROBLEMS,
    MATHEMATICIAN_MODE_TOPICS,
    PROBLEM_BREAKDOWN_STEPS,
    PROBLEM_CATEGORIES,
    PROBLEM_PATTERNS,
    PROBLEM_SOLVING_LAB,
    QUESTION_INTENTS,
)


def _match_pattern(text: str) -> dict:
    lower = text.lower()
    for pattern, data in PROBLEM_PATTERNS.items():
        if re.search(pattern, lower):
            return data
    return DEFAULT_PATTERN


def _load_library_problem(problem: str) -> None:
    st.session_state.ps_library_problem = problem
    st.session_state.ps_example = "Custom problem (describe below)"
    st.rerun()


def render_problem_solving_lab() -> None:
    render_section_header(
        PROBLEM_SOLVING_LAB["icon"],
        PROBLEM_SOLVING_LAB["action"],
        PROBLEM_SOLVING_LAB["tagline"],
    )

    tab_coach, tab_library, tab_mathematician, tab_topics = st.tabs(
        ["Your coach", "Problem library", "Think like a mathematician", "Thinking topics"]
    )

    with tab_coach:
        _render_coaching_flow()

    with tab_library:
        render_problem_library(_load_library_problem)

    with tab_mathematician:
        _render_mathematician_mode()

    with tab_topics:
        render_thinking_topics_panel()


def _render_coaching_flow() -> None:
    st.markdown("#### Tell the coach your problem")

    library_problem = st.session_state.get("ps_library_problem", "")
    example = st.selectbox("Start from an example", EXAMPLE_PROBLEMS, key="ps_example")
    custom = ""
    if example == "Custom problem (describe below)":
        custom = st.text_area(
            "Your problem",
            value=library_problem,
            placeholder="e.g. I want to improve my sports betting system…",
            key="ps_custom",
        )

    problem = custom.strip() if custom.strip() else example
    if problem == "Custom problem (describe below)":
        st.info("Describe your problem above — the coach will adapt its questions.")
        return

    pattern = _match_pattern(problem)
    pattern_id = pattern.get("id", "default")
    key_prefix = f"ps_{pattern_id}"

    # Coach opening — conversational
    st.markdown("---")
    with st.chat_message("assistant"):
        st.markdown(
            f"**Coach:** I hear you working on: *{problem}*\n\n"
            f"This looks like a **{', '.join(pattern.get('categories', ['general']))}** problem. "
            f"Before any formulas — let's think it through together."
        )

    # Adaptive questions
    adaptive = render_adaptive_questions(pattern_id, key_prefix)

    # Reflect back adaptive answers
    if any(adaptive.values()):
        with st.chat_message("assistant"):
            parts = []
            if adaptive.get("optimizing"):
                parts.append(f"optimizing for **{adaptive['optimizing']}**")
            if adaptive.get("info_sources"):
                src = adaptive["info_sources"]
                if isinstance(src, list) and src:
                    parts.append(f"using **{', '.join(src)}**")
            if adaptive.get("challenge"):
                parts.append(f"where the main challenge is **{adaptive['challenge']}**")
            if parts:
                st.markdown(f"**Coach:** So you're {', '.join(parts)}. Let's structure that.")

    # Problem breakdown — conversational steps
    st.markdown("---")
    st.markdown("#### Build your problem structure")
    st.caption("Answer in your own words — the coach uses this to score your thinking.")

    breakdown: dict[int, str] = {}
    hints = {
        1: "Be specific — what would you measure to know you succeeded?",
        2: pattern.get("variables", ""),
        3: pattern.get("constraints", ""),
        4: pattern.get("uncertainty", ""),
        5: pattern.get("data", ""),
        6: pattern.get("simple_model", ""),
        7: "What assumption would you test first?",
        8: "What decision changes based on the answer?",
    }
    for step in PROBLEM_BREAKDOWN_STEPS:
        with st.expander(f"Step {step['num']}: {step['title']}", expanded=step["num"] <= 2):
            st.caption(step["coach"])
            breakdown[step["num"]] = st.text_area(
                step["question"],
                value=hints.get(step["num"], ""),
                key=f"{key_prefix}_step_{step['num']}",
                height=72,
            )

    # Challenge questions
    st.markdown("---")
    challenges = render_challenge_questions(key_prefix)

    # Expert perspectives
    st.markdown("---")
    render_expert_perspectives(pattern, problem)

    # Score
    st.markdown("---")
    total, dim_scores, strengths, weaknesses = compute_thinking_score(
        breakdown, adaptive, challenges
    )
    render_thinking_score(total, dim_scores, strengths, weaknesses)

    # Reasoning pipeline
    st.markdown("---")
    thinking_summary = breakdown.get(1, pattern.get("tradeoff", ""))
    model_summary = breakdown.get(6, pattern.get("simple_model", ""))
    math_summary = (
        f"Tools that fit: {', '.join(pattern.get('tools', []))}. "
        f"Tradeoff: {pattern.get('tradeoff', '')}"
    )
    render_problem_pipeline(problem, thinking_summary, model_summary, math_summary)

    # Next step
    st.success(
        f"**Ready to explore?** Open **{pattern['suggested_lab']}** in the sidebar to run a "
        f"simulation connected to this problem — with thinking first, math second."
    )

    with st.expander("Go deeper — math connected to your problem (optional)", expanded=False):
        st.markdown(f"**Why math helps here:** {pattern.get('tradeoff', '')}")
        st.markdown(f"**Variables:** {pattern.get('variables', '')}")
        st.markdown(f"**Uncertainty:** {pattern.get('uncertainty', '')}")
        st.caption("Formulas come after framing — never before.")


def _render_mathematician_mode() -> None:
    st.markdown("#### Think like a mathematician")
    st.caption("Abstraction, simplification, modeling — habits of mind, not memorization.")

    topic_names = [t["name"] for t in MATHEMATICIAN_MODE_TOPICS]
    choice = st.selectbox("Concept", topic_names, key="ps_math_mode_topic")
    topic = next(t for t in MATHEMATICIAN_MODE_TOPICS if t["name"] == choice)

    with st.container(border=True):
        st.markdown(f"**{topic['name']}**")
        st.markdown(topic["idea"])
        st.info(f"Example: {topic['example']}")

    user_apply = st.text_area(
        topic["prompt"],
        placeholder="Apply this to a problem you're working on…",
        key=f"ps_mode_{topic['id']}",
    )
    if user_apply.strip():
        with st.chat_message("assistant"):
            st.markdown(
                "**Coach:** Good — you've started abstract thinking. What did you strip away? "
                "What structure remains? Could someone in a different field use the same structure?"
            )
