"""Clear, guided Home page — Solve a Problem as flagship."""

import streamlit as st

from components.nav import render_action_grid
from content.platform_meta import VERSION


def render_home() -> None:
    st.markdown(
        """
        <div class="ami-hero ami-hero-action ami-hero-flagship">
            <h1>What's your problem?</h1>
            <p class="ami-tagline">A mathematical consultant — not a calculator.</p>
            <p class="ami-purpose">
                Describe any problem. Reframe what you're really solving, build a model in plain language,
                compare expert perspectives — before you touch a single formula.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("##### Start with the consultant")
    render_action_grid()

    st.caption(f"v{VERSION} · Educational mathematical consultant · Not professional advice")

    with st.expander("How this works", expanded=False):
        st.markdown(
            """
            1. **Solve a Problem** — discussion, model building, expert comparison, decision support.
            2. **Pick a lab** — run a simulation connected to your reasoning.
            3. **Go deeper** — math explained in context, never formulas first.
            """
        )
