"""Reusable section headers and Start here blocks."""

import html

import streamlit as st


def render_section_header(icon: str, action: str, tagline: str) -> None:
    """Action-first header — no internal lab or academic names."""
    st.markdown(
        f"""
        <div class="ami-lab-header">
            <span class="ami-lab-icon-lg">{html.escape(icon)}</span>
            <div>
                <h2 style="margin:0;">{html.escape(action)}</h2>
                <p style="margin:0.35rem 0 0 0;color:#64748b;font-size:0.95rem;">
                    {html.escape(tagline)}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_start_here(intro: str, steps: list[str] | None = None) -> None:
    """Plain-English entry point for every section."""
    with st.container(border=True):
        st.markdown('<p class="ami-start-label">Start here</p>', unsafe_allow_html=True)
        st.markdown(intro)
        if steps:
            for i, step in enumerate(steps, 1):
                st.markdown(f"{i}. {step}")
