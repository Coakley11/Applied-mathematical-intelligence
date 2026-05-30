"""Clear, guided Home page — problem-first action cards."""

import streamlit as st

from components.nav import render_action_grid
from content.platform_meta import VERSION


def render_home() -> None:
    st.markdown(
        """
        <div class="ami-hero ami-hero-action">
            <h1>What problem are you working on?</h1>
            <p class="ami-tagline">Think it through first. Then simulate. Then go deeper.</p>
            <p class="ami-purpose">
                A mathematical thinking partner — not a formula reference. Start with
                <strong>Solve a Problem</strong>, or jump straight to a hands-on lab.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_action_grid()

    st.caption(f"v{VERSION} · Educational simulations only · Not professional advice")

    with st.expander("How this works (30 seconds)", expanded=False):
        st.markdown(
            """
            1. **Solve a Problem** — describe your situation, answer guided questions.
            2. **Pick a lab** — run a simulation connected to your reasoning.
            3. **Go deeper** — optional expanders for the math behind it.
            """
        )

    with st.expander("Looking for encyclopedia depth?", expanded=False):
        st.markdown(
            "Extra labs (weather, space) and 32 domain write-ups live under "
            "**Advanced reference** at the bottom of the sidebar — completely optional."
        )
