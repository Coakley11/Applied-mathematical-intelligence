"""Mathematical Problem Solving Lab — interactive thinking partner."""

import re

import streamlit as st

from components.section_intro import render_section_header, render_start_here
from components.thinking_lab import render_thinking_topics_panel
from content.problem_solving import (
    EXAMPLE_PROBLEMS,
    MATHEMATICIAN_MODE_TOPICS,
    MATH_TOOLS,
    PROBLEM_BREAKDOWN_STEPS,
    PROBLEM_CATEGORIES,
    PROBLEM_PATTERNS,
    PROBLEM_SOLVING_LAB,
    QUESTION_INTENTS,
    DEFAULT_PATTERN,
)


def _match_pattern(text: str) -> dict:
    lower = text.lower()
    for pattern, data in PROBLEM_PATTERNS.items():
        if re.search(pattern, lower):
            return data
    return DEFAULT_PATTERN


def _init_session() -> None:
    defaults = {
        "ps_problem": "",
        "ps_step": 0,
        "ps_intents": [],
        "ps_categories": [],
        "ps_tools": [],
        "ps_answers": {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_problem_solving_lab() -> None:
    _init_session()

    render_section_header(
        PROBLEM_SOLVING_LAB["icon"],
        PROBLEM_SOLVING_LAB["action"],
        PROBLEM_SOLVING_LAB["tagline"],
    )

    render_start_here(
        "Describe your problem below. The app asks follow-up questions — like a consultant "
        "walking you through the reasoning, not jumping to formulas.",
        [
            "Enter or pick an example problem.",
            "Answer the guided questions step by step.",
            "Review your structured breakdown and try a suggested lab.",
        ],
    )

    tab_solve, tab_mathematician, tab_topics = st.tabs(
        ["Solve your problem", "Think like a mathematician", "Thinking topics"]
    )

    with tab_solve:
        _render_interactive_solver()

    with tab_mathematician:
        _render_mathematician_mode()

    with tab_topics:
        render_thinking_topics_panel()


def _render_interactive_solver() -> None:
    st.markdown("#### Describe your problem")

    example = st.selectbox("Start from an example", EXAMPLE_PROBLEMS, key="ps_example")
    custom = ""
    if example == "Custom problem (describe below)":
        custom = st.text_area(
            "Your problem",
            placeholder="Describe what you're trying to figure out or improve…",
            key="ps_custom",
        )

    problem = custom.strip() if custom.strip() else example
    if problem == "Custom problem (describe below)":
        st.info("Describe your problem above to begin.")
        return

    st.session_state.ps_problem = problem
    pattern = _match_pattern(problem)

    with st.container(border=True):
        st.markdown("**What I'm hearing**")
        st.markdown(f"*Problem:* {problem}")
        st.markdown(f"*Likely focus:* {', '.join(pattern['categories'])}")
        st.markdown(f"*Suggested next lab:* **{pattern['suggested_lab']}**")

    st.markdown("---")
    st.markdown("#### Work through the problem")

    # Step 0: What is the actual question?
    st.markdown("**1. What is the actual question?**")
    st.caption("What are you trying to do — predict, optimize, estimate, classify, or explain?")
    intent_labels = [label for _, label in QUESTION_INTENTS]
    default_intents = [
        label for key, label in QUESTION_INTENTS if key in pattern.get("intents", [])
    ]
    selected_intents = st.multiselect(
        "Select all that apply",
        intent_labels,
        default=default_intents[:2],
        key="ps_intent_select",
    )
    st.session_state.ps_intents = selected_intents

    # Step 2: Problem type
    st.markdown("**2. What type of problem is this?**")
    cat_labels = [label for _, label in PROBLEM_CATEGORIES]
    default_cats = [
        label for key, label in PROBLEM_CATEGORIES if key in pattern.get("categories", [])
    ]
    selected_cats = st.multiselect(
        "Problem types",
        cat_labels,
        default=default_cats[:2],
        key="ps_cat_select",
    )
    st.session_state.ps_categories = selected_cats

    # Coaching from pattern
    with st.expander("Consultant notes for your problem", expanded=True):
        st.markdown(f"**Important variables:** {pattern['variables']}")
        st.markdown(f"**Constraints:** {pattern['constraints']}")
        st.markdown(f"**Uncertainty:** {pattern['uncertainty']}")
        st.markdown(f"**Data needed:** {pattern['data']}")
        st.markdown(f"**Tradeoff to watch:** {pattern['tradeoff']}")

    # Interactive 8-step breakdown
    st.markdown("---")
    st.markdown("#### Problem breakdown")
    st.caption("Answer each step — refine your thinking as you go.")

    answers: dict[int, str] = {}
    for step in PROBLEM_BREAKDOWN_STEPS:
        with st.expander(f"Step {step['num']}: {step['title']}", expanded=step["num"] <= 2):
            st.markdown(f"*{step['prompt']}*")
            st.caption(step["coach"])
            default_hint = ""
            if step["num"] == 2:
                default_hint = pattern["variables"]
            elif step["num"] == 3:
                default_hint = pattern["constraints"]
            elif step["num"] == 4:
                default_hint = pattern["uncertainty"]
            elif step["num"] == 5:
                default_hint = pattern["data"]
            elif step["num"] == 6:
                default_hint = pattern["simple_model"]

            answers[step["num"]] = st.text_area(
                step["question"],
                value=st.session_state.ps_answers.get(step["num"], default_hint),
                key=f"ps_step_{step['num']}",
                height=80,
            )

    st.session_state.ps_answers = answers

    # Mathematical tools
    st.markdown("**3. What mathematical tools might help?**")
    tool_defaults = pattern.get("tools", [])
    selected_tools = st.multiselect(
        "Select tools",
        MATH_TOOLS,
        default=[t for t in MATH_TOOLS if any(d in t for d in tool_defaults)],
        key="ps_tools_select",
    )

    # Summary
    st.markdown("---")
    st.markdown("#### Your problem structure")
    if any(answers.values()) or selected_intents:
        with st.container(border=True):
            if selected_intents:
                st.markdown(f"**Question type:** {', '.join(selected_intents)}")
            if selected_cats:
                st.markdown(f"**Problem category:** {', '.join(selected_cats)}")
            if answers.get(1):
                st.markdown(f"**Objective:** {answers[1]}")
            if answers.get(6):
                st.markdown(f"**Simple model:** {answers[6]}")
            if selected_tools:
                st.markdown(f"**Tools to explore:** {', '.join(selected_tools[:3])}")
            st.success(
                f"**Try next:** Open **{pattern['suggested_lab']}** in the sidebar to run a simulation "
                f"connected to this problem."
            )
            if answers.get(8):
                st.info(f"**How you'll use results:** {answers[8]}")

    with st.expander("Go deeper — assumptions & modeling (optional)", expanded=False):
        st.markdown("**What assumptions are you making?**")
        st.text_area(
            "List assumptions explicitly",
            placeholder="e.g. Win rate is stable, opponents don't adapt, sample size is large enough…",
            key="ps_assumptions",
        )
        st.markdown("**What could be modeled?**")
        st.text_area(
            "Describe a simple model",
            value=pattern["simple_model"],
            key="ps_model_deep",
        )


def _render_mathematician_mode() -> None:
    st.markdown("#### Think like a mathematician")
    st.caption(
        "Not formulas — habits of mind. Pick a concept, read the idea, then apply the prompt to your own problem."
    )

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
        st.success(
            "Good — you've started abstract thinking. Compare your answer to the example. "
            "What did you strip away? What structure remains?"
        )

    st.markdown("---")
    st.caption("All eight habits at a glance:")
    cols = st.columns(2)
    for i, t in enumerate(MATHEMATICIAN_MODE_TOPICS):
        with cols[i % 2]:
            st.markdown(f"**{t['name']}** — {t['idea']}")
