"""Mathematical Thinking Lab — interactive thinking frameworks."""

import html

import streamlit as st

from content.thinking_lab import THINKING_LAB, THINKING_TOPICS


def render_thinking_lab() -> None:
    st.markdown(
        f"""
        <div class="ami-lab-header">
            <span class="ami-lab-icon-lg">{html.escape(THINKING_LAB["icon"])}</span>
            <div>
                <span class="ami-badge">{html.escape(THINKING_LAB["action"])}</span>
                <h2 style="margin:0.25rem 0 0 0;">{html.escape(THINKING_LAB["title"])}</h2>
                <p style="margin:0.35rem 0 0 0;color:#64748b;font-size:0.95rem;">
                    {html.escape(THINKING_LAB["tagline"])}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(THINKING_LAB["intro"])

    st.markdown(
        '<p class="ami-section-title">Thinking topics</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="ami-section-sub">Not formulas — how quantitative thinkers approach problems.</p>',
        unsafe_allow_html=True,
    )

    topic_names = [t["name"] for t in THINKING_TOPICS]
    choice = st.selectbox("Choose a topic", topic_names, label_visibility="collapsed")

    topic = next(t for t in THINKING_TOPICS if t["name"] == choice)

    with st.container(border=True):
        st.markdown(f"### {topic['name']}")
        st.markdown(topic["summary"])
        st.markdown("#### The approach")
        st.markdown(topic["approach"])
        st.markdown("#### Questions to ask")
        for q in topic["questions"]:
            st.markdown(f"- {q}")
        st.info(f"**Example:** {topic['example']}")

    with st.expander("Show the math behind this", expanded=False):
        st.markdown(topic["math_connection"])
        st.markdown(
            "This is not a course in symbols — it explains *why* the mathematics is useful "
            "for this type of thinking, in the context of real decisions."
        )

    with st.expander("Try the math yourself", expanded=False):
        st.markdown("**Apply this thinking to your own problem:**")
        user_problem = st.text_area(
            "Describe a problem, decision, or idea",
            placeholder="e.g. Should I expand my business into a new market?",
            key=f"thinking_practice_{topic['id']}",
        )
        if user_problem.strip():
            st.markdown("**Using this framework, ask yourself:**")
            for q in topic["questions"]:
                st.markdown(f"- {q}")
            st.success(
                "Write your answers down — the act of framing the problem mathematically "
                "often reveals what data you need and which lab to explore next."
            )

    st.markdown("---")
    st.markdown("#### Browse all topics")
    cols = st.columns(2)
    for i, t in enumerate(THINKING_TOPICS):
        with cols[i % 2]:
            with st.expander(t["name"], expanded=False):
                st.caption(t["summary"])
                st.markdown(t["approach"][:300] + "…")
