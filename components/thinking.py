"""Mathematical Thinking signature page renderer."""

import html

import streamlit as st

from components.layout import bullet_block, section


def render_mathematical_thinking(content: dict) -> None:
    st.markdown(
        f"""
        <div class="ami-hero">
            <h1>{html.escape(content["title"])}</h1>
            <p class="ami-tagline">{html.escape(content["tagline"].replace("**", ""))}</p>
            <p class="ami-purpose">The signature framework of this platform — how quantitative intelligence
            operates across finance, medicine, AI, climate, and every other domain you will explore here.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(content["introduction"])

    st.markdown(
        '<p class="ami-section-title">The Ten Pillars of Quantitative Intelligence</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="ami-section-sub">Each pillar appears repeatedly in professional work — only the domain vocabulary changes.</p>',
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    for i, pillar in enumerate(content["pillars"]):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"#### {pillar['name']}")
                st.markdown(pillar["summary"])
                st.caption(f"Cross-domain: {pillar['domains']}")
                st.markdown(f"*Insight:* {pillar['insight']}")

    st.markdown(
        '<p class="ami-section-title">Unified Synthesis</p>',
        unsafe_allow_html=True,
    )
    st.markdown(content["synthesis"])

    st.markdown(
        '<p class="ami-section-title">Questions Professionals Ask</p>',
        unsafe_allow_html=True,
    )
    bullet_block(content["professional_questions"])

    st.success(
        "This page is the conceptual backbone. Continue to **Mathematical Themes** for system depth, "
        "**Applied Domains** for case studies and simulations, and **Portfolio Lab** to build artifacts."
    )
