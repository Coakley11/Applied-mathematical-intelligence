"""Clear, guided Home page — Solve a Problem as flagship."""

import streamlit as st

from components.nav import render_action_grid
from content.platform_meta import VERSION


def render_home() -> None:
    st.markdown(
        """
        <div class="ami-hero ami-hero-action ami-hero-flagship">
            <h1>What's your problem?</h1>
            <p class="ami-tagline">Quantitative thinking for real questions — not life coaching.</p>
            <p class="ami-purpose">
                Ask about odds, predictions, models, and strategies. Get analyst framing, interactive math,
                and a lab to try it yourself.
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
            1. **Solve a Problem** — enter a quantitative question, run a quick analysis, see the math.
            2. **Open a lab** — simulate, predict, or model hands-on.
            3. **Mathematical thinking** — abstraction, modeling, uncertainty (separate from solving).
            """
        )
