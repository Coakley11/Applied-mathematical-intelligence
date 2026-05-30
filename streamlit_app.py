# streamlit_app.py — Applied Mathematical Intelligence Platform

import streamlit as st

from components.home import render_home
from components.layout import render_domain_page, render_portfolio_lab, render_theme_page
from components.styles import inject_platform_styles
from components.thinking import render_mathematical_thinking
from content.domains import DOMAINS, DOMAIN_NAMES
from content.mathematical_thinking import MATHEMATICAL_THINKING
from content.platform_meta import VERSION
from content.portfolio import PORTFOLIO_PROBLEMS
from content.themes import THEMES, THEME_NAMES
from simulations.registry import run_simulation

st.set_page_config(
    page_title="Applied Mathematical Intelligence",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_platform_styles()

LENS_FILTER = {
    "Calculus / Accumulation": "Calculus",
    "Probability / Uncertainty": "Probability",
    "Statistics / Pattern Detection": "Statistics",
    "Optimization / Improvement": "Optimization",
    "Simulation / Alternate Futures": "Simulation",
    "AI / Learning Systems": "AI",
}

NAV_OPTIONS = [
    "Home",
    "Mathematical Thinking",
    "Mathematical Themes",
    "Applied Domains",
    "Portfolio Lab",
]
NAV_LABELS = {
    "Home": "Home — platform overview",
    "Mathematical Thinking": "Mathematical Thinking — how quantitative intelligence works",
    "Mathematical Themes": "Mathematical Themes — deep math systems",
    "Applied Domains": "Applied Domains — real-world professional fields",
    "Portfolio Lab": "Portfolio Lab — Excel, Python & interview projects",
}
NAV_HELP = {
    "Home": "Landing page, featured domains, and orientation.",
    "Mathematical Thinking": "Cross-domain philosophy: modeling, uncertainty, optimization, and AI.",
    "Mathematical Themes": "Calculus, probability, statistics, optimization, simulation, and AI as systems.",
    "Applied Domains": "Finance, medicine, robotics, climate, elections, cryptography, and more.",
    "Portfolio Lab": "GitHub-ready project specifications with interview framing.",
}

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("Navigate")
st.sidebar.caption(f"Applied Mathematical Intelligence · v{VERSION}")

view_mode = st.sidebar.radio(
    "Section",
    NAV_OPTIONS,
    format_func=lambda x: NAV_LABELS[x],
    help="Themes = theory; Domains = practice; Thinking = unified framework; Portfolio = projects.",
)

st.sidebar.markdown(
    f"<p style='font-size:0.82rem;color:#64748b;margin:-0.5rem 0 1rem 0;'>{NAV_HELP[view_mode]}</p>",
    unsafe_allow_html=True,
)

math_lens = st.sidebar.selectbox(
    "Mathematical lens",
    list(LENS_FILTER.keys()),
    help="Frame domain content through a specific mathematical system.",
)

depth = st.sidebar.radio(
    "Depth level",
    ["Professional Overview", "Technical Explanation", "Portfolio / Interview Framing"],
    help="Overview = impact first; Technical = full structure; Portfolio = interview deliverables.",
)

selection = None

if view_mode == "Mathematical Themes":
    st.sidebar.markdown("**Select a mathematical system**")
    selection = st.sidebar.selectbox("Theme", THEME_NAMES, label_visibility="collapsed")
elif view_mode == "Applied Domains":
    st.sidebar.markdown("**Select a professional field**")
    lens_key = LENS_FILTER[math_lens]
    filtered = [d for d in DOMAIN_NAMES if lens_key in " ".join(DOMAINS[d]["primary_lenses"])]
    if not filtered:
        filtered = DOMAIN_NAMES
    show_all = st.sidebar.checkbox(
        "Show all domains",
        value=len(filtered) == len(DOMAIN_NAMES),
        help="Uncheck to see only domains strongly tied to your mathematical lens.",
    )
    domain_list = DOMAIN_NAMES if show_all else filtered
    if not show_all and len(filtered) < len(DOMAIN_NAMES):
        st.sidebar.caption(f"{len(filtered)} domains match **{math_lens}**.")
    selection = st.sidebar.selectbox("Domain", domain_list, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.caption("Develop on `dev` · release on `main`")

# =====================================================
# MAIN CONTENT
# =====================================================

if view_mode == "Home":
    render_home()

elif view_mode == "Mathematical Thinking":
    render_mathematical_thinking(MATHEMATICAL_THINKING)

elif view_mode == "Mathematical Themes":
    st.title("Mathematical Themes")
    st.caption("Deep mathematical intelligence systems — the theory layer.")
    if selection:
        render_theme_page(THEMES[selection], depth)

elif view_mode == "Applied Domains":
    st.title("Applied Domains")
    st.caption("Professional fields where mathematical systems drive predictions and decisions.")
    if selection:
        render_domain_page(DOMAINS[selection], depth, math_lens, run_simulation)

elif view_mode == "Portfolio Lab":
    st.title("Portfolio Lab")
    st.caption("Quantitative project specifications for Excel, Python, GitHub, and interviews.")
    render_portfolio_lab(PORTFOLIO_PROBLEMS)

st.markdown("---")
st.caption(
    f"Applied Mathematical Intelligence v{VERSION} | Quantitative systems laboratory — "
    "not professional advice."
)
