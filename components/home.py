"""Clear, guided Home page — Solve a Problem as flagship."""

import streamlit as st

from components.nav import render_action_grid
from content.platform_meta import VERSION


def render_home() -> None:
    st.markdown(
        """
        <div class="ami-hero ami-hero-action ami-hero-flagship">
            <h1>What's your problem?</h1>
            <p class="ami-tagline">Quantitative questions in seven real-world areas.</p>
            <p class="ami-purpose">
                Betting, sports, medicine, AI, space, forecasting — plus abstract structure.
                Short analyst framing, then hands-on math and labs.
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
            1. **Solve a Problem** — pick an area, ask a quantitative question, work the math.
            2. **Open a lab** — simulate, predict, or train hands-on.
            3. **Mathematical thinking** — abstraction and modeling (separate tab).
            """
        )
