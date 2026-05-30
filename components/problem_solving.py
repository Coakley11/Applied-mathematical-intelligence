"""Mathematical Problem Solving Lab — adaptive thinking consultant."""

import re

import streamlit as st

from components.problem_coach import (
    compute_thinking_score,
    render_challenge_questions,
    render_conversational_adaptive,
    render_critical_pushback,
    render_decision_support,
    render_expert_comparison,
    render_model_builder,
    render_problem_library,
    render_problem_pipeline,
    render_real_problem_section,
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
        ["Your consultant", "Problem library", "Think like a mathematician", "Thinking topics"]
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
    st.markdown("#### Tell the consultant your problem")

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
        st.info("Describe your problem above — the consultant will adapt the discussion.")
        return

    pattern = _match_pattern(problem)
    pattern_id = pattern.get("id", "default")
    key_prefix = f"ps_{pattern_id}"

    st.markdown("---")
    with st.chat_message("assistant"):
        st.markdown(
            f"**Consultant:** I hear you working on: *{problem}*\n\n"
            f"This looks like a **{', '.join(pattern.get('categories', ['general']))}** problem. "
            f"Before any formulas — let's discuss, model, and decide together."
        )

    # What is the real problem?
    st.markdown("---")
    render_real_problem_section(problem, pattern_id)

    # Branching discussion
    st.markdown("---")
    adaptive = render_conversational_adaptive(pattern_id, key_prefix)

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
                st.markdown(f"**Consultant:** So you're {', '.join(parts)}. Good — let's stress-test that.")

    # Coach pushback
    st.markdown("---")
    render_critical_pushback(adaptive, pattern_id)

    # Problem structure
    st.markdown("---")
    st.markdown("#### Build your problem structure")
    st.caption("Answer in your own words — abstraction, assumptions, and uncertainty matter more than formulas.")

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

    # Expert comparison
    st.markdown("---")
    render_expert_comparison(pattern, problem)

    # Score
    st.markdown("---")
    total, dim_scores, strengths, weaknesses = compute_thinking_score(
        breakdown, adaptive, challenges
    )
    render_thinking_score(total, dim_scores, strengths, weaknesses)

    # Model builder
    st.markdown("---")
    model = render_model_builder(pattern_id, key_prefix)

    # Decision support
    st.markdown("---")
    render_decision_support(problem, breakdown, model, pattern)

    # Reasoning pipeline
    st.markdown("---")
    thinking_summary = breakdown.get(1, pattern.get("tradeoff", ""))
    model_summary = model.get("simplified_model") or breakdown.get(6, pattern.get("simple_model", ""))
    math_summary = (
        f"Tools that fit: {', '.join(pattern.get('tools', []))}. "
        f"Tradeoff: {pattern.get('tradeoff', '')}"
    )
    render_problem_pipeline(problem, thinking_summary, model_summary, math_summary)

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
                "**Consultant:** Good — you've started abstract thinking. What did you strip away? "
                "What structure remains? Could someone in a different field use the same structure?"
            )
