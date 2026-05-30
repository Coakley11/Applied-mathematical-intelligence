"""Reference library — domains, themes, secondary labs, and portfolio (advanced, optional)."""

import streamlit as st

from components.layout import render_domain_page, render_portfolio_lab, render_theme_page
from components.practical_labs import render_practical_lab
from components.thinking import render_mathematical_thinking
from content.domains import DOMAINS, DOMAIN_NAMES
from content.mathematical_thinking import MATHEMATICAL_THINKING
from content.portfolio import PORTFOLIO_PROBLEMS
from content.practical_labs import SECONDARY_LAB_NAMES
from content.themes import THEMES, THEME_NAMES


def render_reference_library(
    run_simulation,
    math_lens: str = "Statistics / Pattern Detection",
    depth: str = "Professional Overview",
) -> None:
    st.warning(
        "**Optional section** — you do not need this to use the main tools. "
        "Come here for extra labs, background reading, or interview project ideas."
    )

    st.markdown(
        """
        <div class="ami-hero ami-hero-ref">
            <h1>Advanced reference</h1>
            <p class="ami-tagline">Encyclopedia depth — for when you want to read, not just do.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section = st.selectbox(
        "What are you looking for?",
        [
            "Extra simulation labs",
            "Domain case studies",
            "Background reading on math ideas",
            "Full thinking framework",
            "Portfolio project specs",
        ],
    )

    if section == "Extra simulation labs":
        _render_secondary_labs()
    elif section == "Domain case studies":
        _render_domains_reference(run_simulation, math_lens, depth)
    elif section == "Background reading on math ideas":
        _render_themes_reference(depth)
    elif section == "Full thinking framework":
        st.caption(
            "The long-form version. For interactive problem-solving, use "
            "**Solve a Problem** in the main sidebar."
        )
        render_mathematical_thinking(MATHEMATICAL_THINKING)
    else:
        render_portfolio_lab(PORTFOLIO_PROBLEMS)


def _render_secondary_labs() -> None:
    st.caption("Weather, space, and core math tools — same guided format as the main sections.")
    choice = st.selectbox("Lab", SECONDARY_LAB_NAMES)
    render_practical_lab(choice)


def _render_domains_reference(run_simulation, math_lens: str, depth: str) -> None:
    st.caption(f"{len(DOMAIN_NAMES)} professional domains — run a simulation first, read later.")

    search = st.text_input("Search", placeholder="e.g. finance, epidemic, climate…")
    filtered = DOMAIN_NAMES
    if search.strip():
        q = search.strip().lower()
        filtered = [
            d for d in DOMAIN_NAMES
            if q in d.lower()
            or q in DOMAINS[d].get("tagline", "").lower()
            or any(q in c.lower() for c in DOMAINS[d].get("concepts", []))
        ]

    if not filtered:
        st.info("No domains match your search.")
        return

    choice = st.selectbox("Domain", filtered)
    domain = DOMAINS[choice]

    st.markdown(f"### {choice}")
    st.caption(domain["tagline"].replace("**", ""))

    st.markdown("#### Try the simulation")
    run_simulation(domain.get("simulation_id"))

    with st.expander("Why this field matters", expanded=False):
        st.markdown(domain["why_matters"])

    with st.expander("Concepts & applications", expanded=False):
        st.markdown("**Concepts:** " + ", ".join(domain["concepts"][:8]))
        st.markdown("**Applications:**")
        st.markdown("\n".join(f"- {a}" for a in domain["professional_applications"][:6]))

    case_studies = domain.get("case_studies", [])
    if case_studies:
        with st.expander(f"Case studies ({len(case_studies)})", expanded=False):
            for cs in case_studies:
                st.markdown(f"**{cs['title']}** — {cs.get('setting', '')}")
                st.caption(cs["lesson"])

    with st.expander("Full domain reference", expanded=False):
        render_domain_page(domain, depth, math_lens, run_simulation, skip_simulation=True)


def _render_themes_reference(depth: str) -> None:
    st.caption("Six big ideas behind the simulations — read when you're curious, not before you start.")
    choice = st.selectbox("Topic", THEME_NAMES)
    with st.expander("Full write-up", expanded=True):
        render_theme_page(THEMES[choice], depth)
