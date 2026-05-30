# streamlit_app.py — Applied Mathematical Intelligence Platform

import streamlit as st

from components.layout import render_domain_page, render_home, render_portfolio_lab, render_theme_page
from content.domains import DOMAINS, DOMAIN_NAMES
from content.portfolio import PORTFOLIO_PROBLEMS
from content.themes import THEMES, THEME_NAMES
from simulations.runner import run_simulation

st.set_page_config(
    page_title="Applied Mathematical Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Lens → domain filter keywords (substring match on primary_lenses)
LENS_FILTER = {
    "Calculus / Accumulation": "Calculus",
    "Probability / Uncertainty": "Probability",
    "Statistics / Pattern Detection": "Statistics",
    "Optimization / Improvement": "Optimization",
    "Simulation / Alternate Futures": "Simulation",
    "AI / Learning Systems": "AI",
}

# =====================================================
# HEADER
# =====================================================

st.title("Applied Mathematical Intelligence")
st.subheader("Quantitative Reasoning Laboratory for Real-World Systems")

st.markdown("""
Explore how **calculus, probability, statistics, optimization, simulation, and learning systems**
power prediction, invention, and high-stakes decisions — from drug development to climate policy,
from hedge funds to autonomous vehicles.

This is not a textbook. It is an **applied mathematics intelligence explorer**.
""")

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Navigation")

view_mode = st.sidebar.radio(
    "Explore",
    ["Home", "Mathematical Themes", "Applied Domains", "Portfolio Lab"],
    label_visibility="collapsed",
)

math_lens = st.sidebar.selectbox(
    "Mathematical lens",
    list(LENS_FILTER.keys()),
)

depth = st.sidebar.radio(
    "Depth level",
    ["Professional Overview", "Technical Explanation", "Portfolio / Interview Framing"],
)

selection = None

if view_mode == "Mathematical Themes":
    selection = st.sidebar.selectbox("Theme", THEME_NAMES)
elif view_mode == "Applied Domains":
    lens_key = LENS_FILTER[math_lens]
    filtered = [d for d in DOMAIN_NAMES if lens_key in " ".join(DOMAINS[d]["primary_lenses"])]
    if not filtered:
        filtered = DOMAIN_NAMES
    show_all = st.sidebar.checkbox("Show all domains", value=len(filtered) == len(DOMAIN_NAMES))
    domain_list = DOMAIN_NAMES if show_all else filtered
    if not show_all and len(filtered) < len(DOMAIN_NAMES):
        st.sidebar.caption(f"Showing {len(filtered)} domains strong in {math_lens}.")
    selection = st.sidebar.selectbox("Domain", domain_list)
elif view_mode == "Portfolio Lab":
    st.sidebar.caption("Interview-ready project scaffolds across domains.")

st.sidebar.markdown("---")
st.sidebar.caption("Applied Mathematical Intelligence Platform")

# =====================================================
# MAIN CONTENT
# =====================================================

if view_mode == "Home":
    render_home()
    st.markdown("---")
    st.subheader("Start Exploring")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Mathematical Themes**")
        st.markdown(f"{len(THEME_NAMES)} deep systems — accumulation, uncertainty, patterns, optimization, simulation, AI.")
    with c2:
        st.markdown("**Applied Domains**")
        st.markdown(f"{len(DOMAIN_NAMES)} professional fields — finance, epidemiology, robotics, cryptography, and more.")
    with c3:
        st.markdown("**Portfolio Lab**")
        st.markdown(f"{len(PORTFOLIO_PROBLEMS)} project briefs for Excel, Python, and interviews.")

elif view_mode == "Mathematical Themes" and selection:
    render_theme_page(THEMES[selection], depth)

elif view_mode == "Applied Domains" and selection:
    render_domain_page(
        DOMAINS[selection],
        depth,
        math_lens,
        run_simulation,
    )

elif view_mode == "Portfolio Lab":
    render_portfolio_lab(PORTFOLIO_PROBLEMS)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")
st.caption(
    "Applied Mathematical Intelligence | Quantitative modeling explorer — "
    "conceptual demonstrations, not professional advice."
)
