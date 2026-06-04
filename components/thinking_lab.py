"""Mathematical thinking topics — used inside Problem Solving Lab."""

import streamlit as st

from components.thinking_workshop import render_thinking_quick_cards
from content.thinking_lab import THINKING_TOPICS


def render_thinking_topics_panel() -> None:
    """Topic library panel — frameworks for how quantitative thinkers approach problems."""
    st.markdown("#### Thinking topic library")
    st.caption(
        "Pick a topic, then try the questions on your problem — or use **Interactive workshop** "
        "for visuals and sliders."
    )
    render_thinking_quick_cards()
    st.markdown("---")

    topic_names = [t["name"] for t in THINKING_TOPICS]
    choice = st.selectbox("Pick a topic", topic_names, key="thinking_topic_select")

    topic = next(t for t in THINKING_TOPICS if t["name"] == choice)

    st.markdown(f"**{topic['name']}**")
    st.markdown(topic["summary"])

    with st.container(border=True):
        st.markdown("**The approach**")
        st.markdown(topic["approach"])
        st.markdown("**Questions to ask yourself**")
        for q in topic["questions"]:
            st.markdown(f"- {q}")
        st.info(f"**Example:** {topic['example']}")

    with st.expander("Why the math matters here (optional)", expanded=False):
        st.markdown(topic["math_connection"])

    user_problem = st.text_area(
        "Apply this to your problem",
        placeholder="Describe a problem, decision, or idea…",
        key=f"thinking_apply_{topic['id']}",
    )
    if user_problem.strip():
        st.markdown("**Try it yourself** — using this framework, ask:")
        for q in topic["questions"]:
            st.markdown(f"- {q}")
        st.caption("Open the **Interactive workshop** tab to walk through a thinking style with charts.")
