# streamlit_app.py — Applied Mathematical Intelligence Platform

import streamlit as st

from components.home import render_home
from components.practical_labs import render_practical_lab
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

PRIMARY_NAV = ["Home"] + [ACTION_LABELS[name] for name in PRACTICAL_LAB_NAMES] + ["Advanced reference"]

NAV_HELP = {
    "Home": "Pick a real-world problem and start experimenting.",
    "Analyze a Bet": "Expected value, pot odds, and casino edge — is the decision worth it?",
    "Predict a Game": "Sports probabilities, odds, ratings, and trend forecasting.",
    "Model a Disease": "Disease spread, tumor growth, and drug concentration.",
    "Train an AI": "Gradient descent and neural network training.",
    "Forecast Weather": "Uncertainty cones and trend forecasting.",
    "Explore Space Motion": "Orbits, planet detection, and trajectories.",
    "Understand the Math": "Calculus, probability, statistics, optimization, and simulation.",
    "Advanced reference": "Optional — 32 domain case studies and portfolio specs.",
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

ref_lens = "Statistics / Pattern Detection"
ref_depth = "Professional Overview"
if view_mode == "Advanced reference":
    st.sidebar.markdown("---")
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
    )
    ref_depth = st.sidebar.radio(
        "Depth",
        ["Professional Overview", "Technical Explanation", "Portfolio / Interview Framing"],
    )

st.sidebar.markdown("---")
st.sidebar.caption("Guided decision lab · not professional advice")

# =====================================================
# MAIN CONTENT
# =====================================================

if view_mode == "Home":
    render_home()

elif view_mode == "Advanced reference":
    render_reference_library(run_simulation, ref_lens, ref_depth)

elif view_mode in ACTION_TO_LAB:
    render_practical_lab(ACTION_TO_LAB[view_mode])

st.markdown("---")
st.caption(
    f"Applied Mathematical Intelligence v{VERSION} | "
    "Choose a problem → run a simulation → read the result."
)
