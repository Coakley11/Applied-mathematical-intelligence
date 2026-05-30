"""Clear, guided Home page — problem-first action cards."""

import streamlit as st

from components.nav import render_action_grid
from content.platform_meta import VERSION


def render_home() -> None:
    st.markdown(
        """
        <div class="ami-hero ami-hero-action">
            <h1>What do you want to do?</h1>
            <p class="ami-tagline">Pick a problem. Run a simulation. See what the math says.</p>
            <p class="ami-purpose">
                No textbook — just hands-on tools for bets, games, medicine, AI, decisions, and ideas.
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
            1. **Pick a card** — each one is a standalone tool.
            2. **Follow Start here** — plain English, no prerequisites.
            3. **Run the simulation** — change sliders, see results.
            4. **Go deeper** — optional expanders for the math behind it.
            """
        )

    with st.expander("Looking for encyclopedia depth?", expanded=False):
        st.markdown(
            "Extra labs (weather, space) and 32 domain write-ups live under "
            "**Advanced reference** at the bottom of the sidebar — completely optional."
        )
