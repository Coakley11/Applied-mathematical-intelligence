"""Reference library — domains, themes, thinking, and portfolio (advanced, optional)."""

import streamlit as st

from components.layout import render_domain_page, render_portfolio_lab, render_theme_page
from components.thinking import render_mathematical_thinking
from content.domains import DOMAINS, DOMAIN_NAMES
from content.mathematical_thinking import MATHEMATICAL_THINKING
from content.portfolio import PORTFOLIO_PROBLEMS
from content.themes import THEMES, THEME_NAMES


def render_reference_library(
    run_simulation,
    math_lens: str = "Statistics / Pattern Detection",
    depth: str = "Professional Overview",
) -> None:
    st.markdown(
        """
        <div class="ami-hero ami-hero-ref">
            <h1>Reference Library</h1>
            <p class="ami-tagline">Optional depth — case studies, domain write-ups, and portfolio specs.</p>
            <p class="ami-purpose">The main experience is in the labs. Use this when you want background reading.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section = st.radio(
        "Browse",
        ["Domain case studies", "Math themes", "Mathematical thinking", "Portfolio projects"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if section == "Domain case studies":
        _render_domains_reference(run_simulation, math_lens, depth)
    elif section == "Math themes":
        _render_themes_reference(depth)
    elif section == "Mathematical thinking":
        render_mathematical_thinking(MATHEMATICAL_THINKING)
    else:
        render_portfolio_lab(PORTFOLIO_PROBLEMS)


def _render_domains_reference(run_simulation, math_lens: str, depth: str) -> None:
    st.caption(f"{len(DOMAIN_NAMES)} professional domains — simulation first, reading optional.")

    search = st.text_input("Search domains", placeholder="e.g. finance, epidemic, climate…")
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
    st.caption("Six mathematical systems — read when you want theory behind the labs.")
    choice = st.selectbox("Theme", THEME_NAMES)
    with st.expander("Full theme reference", expanded=True):
        render_theme_page(THEMES[choice], depth)
