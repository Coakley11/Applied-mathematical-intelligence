"""Idea & Invention Analysis — mathematical brainstorming."""

import re

import streamlit as st

from components.section_intro import render_section_header, render_start_here
from content.idea_analysis import (
    ANALYSIS_DIMENSIONS,
    DEFAULT_IDEA_HINTS,
    IDEA_ANALYSIS,
    IDEA_KEYWORDS,
)


def _match_idea_hints(text: str) -> dict:
    lower = text.lower()
    for pattern, hints in IDEA_KEYWORDS.items():
        if re.search(pattern, lower):
            return hints
    return DEFAULT_IDEA_HINTS


def render_idea_analysis() -> None:
    render_section_header(
        IDEA_ANALYSIS["icon"],
        IDEA_ANALYSIS["action"],
        IDEA_ANALYSIS["tagline"],
    )

    render_start_here(
        "Type your idea below. Before brainstorming variables, ask: "
        "**what question am I actually trying to answer?**",
        [
            "State the idea in one or two sentences.",
            "Answer the thinking prompt below.",
            "Read the structured breakdown and follow the suggested lab.",
        ],
    )

    with st.container(border=True):
        st.markdown('<p class="ami-start-label">Think first</p>', unsafe_allow_html=True)
        st.markdown("**What decision or prediction would change if you knew the answer?**")
        st.text_input(
            "The real question behind this idea",
            placeholder="e.g. Will this product be profitable within 12 months?",
            key="idea_think_question",
        )

    idea = st.text_area(
        "Your idea",
        placeholder=(
            "e.g. A sports prediction app, a new cancer treatment device, "
            "or a better poker strategy"
        ),
        height=100,
        key="idea_input",
        label_visibility="collapsed",
    )

    if not idea.strip():
        st.info("👆 Enter an idea above to get started.")
        return

    hints = _match_idea_hints(idea)

    st.markdown("#### What to think about")
    items = [
        ("What matters?", hints["variables"]),
        ("What data do you need?", hints["data"]),
        ("What could you improve?", hints["optimize"]),
        ("What could you simulate?", hints["model"]),
        ("What tools fit?", hints["tools"]),
    ]
    for title, answer in items:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.markdown(answer)

    st.success(f"**Try next:** {hints['labs']}")

    with st.expander("Go deeper (optional)", expanded=False):
        st.markdown("**Guiding questions**")
        for dim in ANALYSIS_DIMENSIONS:
            st.markdown(f"*{dim['title']}*")
            for p in dim["prompts"]:
                st.markdown(f"- {p}")
        st.markdown("---")
        st.markdown("**Frame your idea in one sentence**")
        col1, col2, col3 = st.columns(3)
        output_var = col1.text_input("What you care about", key="idea_out")
        input_var = col2.text_input("What you control", key="idea_in")
        constraint = col3.text_input("Your limits", key="idea_con")
        if output_var and input_var:
            st.markdown(
                f"Measure **{output_var}** as a function of **{input_var}**, "
                f"subject to **{constraint or 'your constraints'}**."
            )

    st.caption("Educational brainstorming only — not business, medical, or investment advice.")
