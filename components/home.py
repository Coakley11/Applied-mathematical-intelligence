"""Clear, guided Home page."""

import html

import streamlit as st

from content.platform_meta import NUM_PRACTICAL_LABS, VERSION
from content.practical_labs import ACTION_DESCRIPTIONS, PRACTICAL_LAB_NAMES, PRACTICAL_LABS


def _action_card(lab_name: str) -> str:
    lab = PRACTICAL_LABS[lab_name]
    desc = ACTION_DESCRIPTIONS.get(lab_name, lab["tagline"])
    return f"""
    <div class="ami-action-card">
        <div class="ami-action-icon">{html.escape(lab["icon"])}</div>
        <div class="ami-action-label">{html.escape(lab["action"])}</div>
        <h3>{html.escape(lab_name)}</h3>
        <p>{html.escape(desc)}</p>
    </div>
    """


def render_home() -> None:
    st.markdown(
        """
        <div class="ami-hero ami-hero-action">
            <h1>Applied Mathematical Intelligence</h1>
            <p class="ami-tagline">A hands-on mathematical decision lab.</p>
            <p class="ami-purpose">
                Choose a real-world problem, change the assumptions, run simulations, and see how
                calculus, probability, statistics, and optimization help explain what happens.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="ami-section-title">What do you want to do?</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ami-section-sub">Pick a card below or use the sidebar. Each lab guides you step by step.</p>',
        unsafe_allow_html=True,
    )

    # 3 + 3 + 1 layout for 7 labs
    rows = [PRACTICAL_LAB_NAMES[:3], PRACTICAL_LAB_NAMES[3:6], PRACTICAL_LAB_NAMES[6:]]
    for row in rows:
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            with col:
                st.markdown(_action_card(name), unsafe_allow_html=True)

    st.caption(f"v{VERSION} · {NUM_PRACTICAL_LABS} guided labs · Educational simulations only")

    with st.expander("How this app works", expanded=False):
        st.markdown(
            """
            1. **Pick a lab** — betting, sports, medicine, AI, weather, space, or math concepts.
            2. **Read the plain-language intro** — what the tool does and why it matters.
            3. **Change the sliders** — run the simulation and see what happens.
            4. **Read the result** — the app explains how to interpret what you see.
            5. **Go deeper (optional)** — expand "Show the math behind this" or "Try the math yourself."
            """
        )

    with st.expander("Advanced reference library (optional)", expanded=False):
        st.markdown(
            "32 domain case studies, portfolio project specs, and full math theme write-ups "
            "live under **Advanced reference** in the sidebar — only when you want encyclopedia depth."
        )

    st.info("**New here?** Open **Analyze a Bet** or **Model a Disease** from the sidebar and follow the guided steps.")
