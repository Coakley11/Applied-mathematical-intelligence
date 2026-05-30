"""Shared problem-thinking prompts integrated into every lab."""

import streamlit as st

from content.problem_solving import LAB_THINKING_PROMPTS


def render_lab_thinking_gate(lab_name: str, key_prefix: str) -> None:
    """Ask thinking questions before simulations — optional but encouraged."""
    config = LAB_THINKING_PROMPTS.get(lab_name)
    if not config:
        return

    with st.container(border=True):
        st.markdown('<p class="ami-start-label">Think first</p>', unsafe_allow_html=True)
        st.markdown(f"**{config['lead_question']}**")
        for i, (question, hint) in enumerate(config["prompts"]):
            answer = st.text_input(
                question,
                placeholder=hint,
                key=f"{key_prefix}_think_{i}",
            )
            if answer.strip():
                st.caption(f"→ {hint}")
