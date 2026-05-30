"""Mathematical Thinking signature page renderer."""

import streamlit as st

from components.layout import bullet_block, section


def render_mathematical_thinking(content: dict) -> None:
    section(content["title"])
    st.markdown(content["tagline"])
    st.markdown(content["introduction"])

    st.subheader("The Ten Pillars of Quantitative Intelligence")
    for pillar in content["pillars"]:
        with st.expander(f"**{pillar['name']}**", expanded=False):
            st.markdown(pillar["summary"])
            st.markdown(f"*Cross-domain:* {pillar['domains']}")
            st.info(pillar["insight"])

    st.subheader("Unified Synthesis")
    st.markdown(content["synthesis"])

    st.subheader("Questions Professionals Ask")
    bullet_block(content["professional_questions"])

    st.success(
        "Use **Mathematical Themes** for system depth, **Applied Domains** for field-specific case studies, "
        "and **Portfolio Lab** to turn this thinking into demonstrable artifacts."
    )
