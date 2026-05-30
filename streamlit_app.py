# streamlit_app.py — Applied Mathematical Intelligence Platform

import streamlit as st

from components.home import render_home
from components.practical_labs import render_action_hub, render_practical_lab
from components.reference import render_reference_library
from components.styles import inject_platform_styles
from content.practical_labs import ACTION_LABELS, ACTION_TO_LAB, PRACTICAL_LAB_NAMES
from content.platform_meta import VERSION
from simulations.registry import run_simulation

st.set_page_config(
    page_title="Applied Mathematical Intelligence",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_platform_styles()

# Action-first navigation
PRIMARY_NAV = ["Home"] + [ACTION_LABELS[name] for name in PRACTICAL_LAB_NAMES] + ["Reference library"]

NAV_HELP = {
    "Home": "What do you want to do? Pick a goal and start experimenting.",
    "Invest money": "Portfolio simulator, Monte Carlo paths, risk and drawdown tools.",
    "Analyze a bet": "Poker EV, sports odds, pot odds, Kelly criterion, casino edge.",
    "Forecast the future": "Trend forecasting, elections, weather uncertainty, sports ratings.",
    "Train an AI": "Gradient descent, neural training, resource optimization.",
    "Simulate a system": "Epidemics, supply chains, insurance losses, Monte Carlo.",
    "Reference library": "Optional — domain case studies, themes, portfolio specs.",
}

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("What do you want to do?")
st.sidebar.caption(f"Applied Mathematical Intelligence · v{VERSION}")

view_mode = st.sidebar.radio(
    "Choose",
    PRIMARY_NAV,
    label_visibility="collapsed",
)

st.sidebar.markdown(
    f"<p style='font-size:0.82rem;color:#64748b;margin:-0.25rem 0 1rem 0;'>{NAV_HELP[view_mode]}</p>",
    unsafe_allow_html=True,
)

# Reference-only controls (hidden from main lab flow)
ref_lens = "Statistics / Pattern Detection"
ref_depth = "Professional Overview"
if view_mode == "Reference library":
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Reference options**")
    ref_lens = st.sidebar.selectbox(
        "Math lens",
        [
            "Calculus / Accumulation",
            "Probability / Uncertainty",
            "Statistics / Pattern Detection",
            "Optimization / Improvement",
            "Simulation / Alternate Futures",
            "AI / Learning Systems",
        ],
        help="Highlight concepts tied to a mathematical system.",
    )
    ref_depth = st.sidebar.radio(
        "Depth",
        ["Professional Overview", "Technical Explanation", "Portfolio / Interview Framing"],
    )

st.sidebar.markdown("---")
st.sidebar.caption("Decision laboratory · not professional advice")

# =====================================================
# MAIN CONTENT
# =====================================================

if view_mode == "Home":
    render_home()

elif view_mode == "Reference library":
    render_reference_library(run_simulation, ref_lens, ref_depth)

elif view_mode in ACTION_TO_LAB:
    render_practical_lab(ACTION_TO_LAB[view_mode])

st.markdown("---")
st.caption(
    f"Applied Mathematical Intelligence v{VERSION} | "
    "Experiment first — read when you need depth."
)
