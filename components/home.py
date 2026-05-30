"""Action-first Home — what do you want to do?"""

import html

import streamlit as st

from content.platform_meta import NUM_PRACTICAL_LABS, NUM_SIMULATIONS, VERSION
from content.practical_labs import PRACTICAL_LAB_NAMES, PRACTICAL_LABS


def _action_card(lab_name: str) -> str:
    lab = PRACTICAL_LABS[lab_name]
    return f"""
    <div class="ami-action-card">
        <div class="ami-action-icon">{html.escape(lab["icon"])}</div>
        <div class="ami-action-label">{html.escape(lab["action"])}</div>
        <h3>{html.escape(lab_name)}</h3>
        <p>{html.escape(lab["tagline"])}</p>
    </div>
    """


def render_home() -> None:
    st.markdown(
        """
        <div class="ami-hero ami-hero-action">
            <h1>Applied Mathematical Intelligence</h1>
            <p class="ami-tagline">A decision laboratory — not a textbook.</p>
            <p class="ami-purpose">
                Invest, bet, forecast, train AI, or simulate systems.
                Use the tools first; probability, optimization, and statistics appear when they help you decide.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="ami-stat-row">
            <div class="ami-stat"><div class="ami-stat-num">{NUM_PRACTICAL_LABS}</div><div class="ami-stat-label">Practical labs</div></div>
            <div class="ami-stat"><div class="ami-stat-num">{NUM_SIMULATIONS}</div><div class="ami-stat-label">Simulation tools</div></div>
            <div class="ami-stat"><div class="ami-stat-num">32</div><div class="ami-stat-label">Reference domains</div></div>
        </div>
        <p style="text-align:center;color:#64748b;font-size:0.85rem;margin-top:-0.5rem;">v{VERSION}</p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="ami-section-title">What do you want to do?</p>', unsafe_allow_html=True)

    row1 = PRACTICAL_LAB_NAMES[:3]
    row2 = PRACTICAL_LAB_NAMES[3:]
    for row in (row1, row2):
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            with col:
                st.markdown(_action_card(name), unsafe_allow_html=True)

    st.caption("Use the sidebar to open any lab. Each lab has interactive tools — start experimenting.")

    with st.expander("Reference library (optional reading)", expanded=False):
        st.markdown(
            "Domain case studies, math themes, and portfolio project specs live under "
            "**Reference library** in the sidebar. They are there when you want depth — "
            "not required to use the labs."
        )

    st.info(
        "**Start here:** pick **Invest money**, **Analyze a bet**, or **Simulate a system** "
        "from the sidebar and run a scenario in under a minute."
    )
