"""Clear, guided Home page — problem-first action cards."""

import streamlit as st

from components.nav import render_action_grid
from content.platform_meta import NUM_PRIMARY_ACTIONS, VERSION


def render_home() -> None:
    st.markdown(
        """
        <div class="ami-hero ami-hero-action">
            <h1>Applied Mathematical Intelligence</h1>
            <p class="ami-tagline">A Mathematical Thinking Lab — not a textbook.</p>
            <p class="ami-purpose">
                Bring a problem, decision, prediction, strategy, or idea. The app helps you
                think about it mathematically — through simulations, optimization, and guided reasoning.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="ami-section-title">What do you want to do?</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ami-section-sub">Pick a card below or use the sidebar. Each section guides you step by step.</p>',
        unsafe_allow_html=True,
    )

    render_action_grid()

    st.caption(
        f"v{VERSION} · {NUM_PRIMARY_ACTIONS} action labs · "
        "Educational simulations only"
    )

    with st.expander("How this app works", expanded=False):
        st.markdown(
            """
            1. **Pick a problem** — betting, sports, medicine, AI, optimization, ideas, or thinking frameworks.
            2. **Work through the guided steps** — define objectives, variables, and constraints.
            3. **Run simulations** — change assumptions and see what happens.
            4. **Show the math behind this** — optional expander explains why the mathematics matters.
            5. **Try the math yourself** — hands-on calculators and brainstorming prompts.
            """
        )

    with st.expander("More labs & advanced reference (optional)", expanded=False):
        st.markdown(
            """
            **Additional simulation labs** (Weather, Space, Math Systems) and **32 domain case studies**
            live under **Advanced reference** in the sidebar — open when you want encyclopedia depth.
            """
        )

    st.info(
        "**New here?** Click **Analyze a Bet** or **Explore Mathematical Thinking** above, "
        "or pick any card from the sidebar."
    )
