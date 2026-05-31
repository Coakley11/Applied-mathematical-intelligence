"""Clear, guided Home page — Solve a Problem as flagship."""

import streamlit as st

from components.nav import render_action_grid
from content.platform_meta import VERSION


def render_home() -> None:
    st.markdown(
        """
        <div class="ami-hero ami-hero-action ami-hero-flagship">
            <h1>Applied mathematical intelligence</h1>
            <p class="ami-tagline">Two directions: real-world questions ↔ math ideas.</p>
            <p class="ami-purpose">
                <strong>Solve a Problem</strong> — betting, sports, medicine, AI, and more.
                <strong>Explore a Math Idea</strong> — derivative, expected value, quadratics — see where they live in reality.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("##### Start here")
    render_action_grid()

    st.caption(f"v{VERSION} · Educational quantitative analysis · Not professional advice")

    with st.expander("How this works", expanded=False):
        st.markdown(
            """
            1. **Solve a Problem** — real-world question → math tools.
            2. **Explore a Math Idea** — math concept → real-world applications.
            3. **Labs** — simulate, predict, train hands-on.
            """
        )
