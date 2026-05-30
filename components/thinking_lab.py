"""Mathematical Thinking Lab — interactive thinking frameworks."""

import streamlit as st

from components.section_intro import render_section_header, render_start_here
from content.thinking_lab import THINKING_LAB, THINKING_TOPICS


def render_thinking_lab() -> None:
    render_section_header(
        THINKING_LAB["icon"],
        THINKING_LAB["action"],
        THINKING_LAB["tagline"],
    )

    render_start_here(
        "Choose a topic below. Each one is a short framework — questions to ask, not formulas to memorize.",
        [
            "Pick a topic from the dropdown.",
            "Read the approach and example.",
            "Apply the questions to a problem you care about.",
        ],
    )

    topic_names = [t["name"] for t in THINKING_TOPICS]
    choice = st.selectbox("Pick a topic", topic_names, label_visibility="collapsed")

    topic = next(t for t in THINKING_TOPICS if t["name"] == choice)

    st.markdown(f"### {topic['name']}")
    st.markdown(topic["summary"])

    with st.container(border=True):
        st.markdown("**The approach**")
        st.markdown(topic["approach"])
        st.markdown("**Questions to ask yourself**")
        for q in topic["questions"]:
            st.markdown(f"- {q}")
        st.info(f"**Example:** {topic['example']}")

    with st.expander("Go deeper (optional)", expanded=False):
        st.markdown("**Why the math matters here**")
        st.markdown(topic["math_connection"])
        st.markdown("**Try it on your own problem**")
        user_problem = st.text_area(
            "Describe a problem, decision, or idea",
            placeholder="e.g. Should I expand my business into a new market?",
            key=f"thinking_practice_{topic['id']}",
        )
        if user_problem.strip():
            st.markdown("Using this framework, ask yourself:")
            for q in topic["questions"]:
                st.markdown(f"- {q}")

    with st.expander("All topics at a glance", expanded=False):
        for t in THINKING_TOPICS:
            st.markdown(f"**{t['name']}** — {t['summary']}")
