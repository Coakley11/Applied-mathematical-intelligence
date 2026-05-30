# streamlit_app.py — Applied Mathematical Intelligence Platform

import streamlit as st

from components.home import render_home
from components.idea_analysis import render_idea_analysis
from components.optimization_workshop import render_optimization_workshop
from components.practical_labs import render_practical_lab
from components.reference import render_reference_library
from components.styles import inject_platform_styles
from components.thinking_lab import render_thinking_lab
from content.practical_labs import (
    ACTION_SECTION_TYPES,
    ACTION_TO_LAB,
    NAV_HELP,
    PRIMARY_ACTIONS,
)
from content.platform_meta import VERSION
from simulations.registry import run_simulation

st.set_page_config(
    page_title="Applied Mathematical Intelligence",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_platform_styles()

PRIMARY_NAV = ["Home"] + PRIMARY_ACTIONS + ["Advanced reference"]

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Home"

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("What do you want to do?")
st.sidebar.caption(f"Applied Mathematical Intelligence · v{VERSION}")

nav_index = (
    PRIMARY_NAV.index(st.session_state.view_mode)
    if st.session_state.view_mode in PRIMARY_NAV
    else 0
)

view_mode = st.sidebar.radio(
    "Choose",
    PRIMARY_NAV,
    index=nav_index,
    label_visibility="collapsed",
)

st.session_state.view_mode = view_mode

help_text = NAV_HELP.get(view_mode, "")
if help_text:
    st.sidebar.markdown(
        f"<p style='font-size:0.82rem;color:#64748b;margin:-0.25rem 0 1rem 0;'>{help_text}</p>",
        unsafe_allow_html=True,
    )

st.sidebar.caption("Items at the bottom of the list are optional reading.")

ref_lens = "Statistics / Pattern Detection"
ref_depth = "Professional Overview"
if view_mode == "Advanced reference":
    st.sidebar.markdown("---")
    st.sidebar.caption("Optional filters for background reading")
    ref_lens = st.sidebar.selectbox(
        "Focus area",
        [
            "Calculus / Accumulation",
            "Probability / Uncertainty",
            "Statistics / Pattern Detection",
            "Optimization / Improvement",
            "Simulation / Alternate Futures",
            "AI / Learning Systems",
        ],
        label_visibility="visible",
    )
    ref_depth = st.sidebar.radio(
        "Detail level",
        ["Professional Overview", "Technical Explanation", "Portfolio / Interview Framing"],
    )

st.sidebar.markdown("---")
st.sidebar.caption("Mathematical thinking lab · not professional advice")

# =====================================================
# MAIN CONTENT
# =====================================================

if view_mode == "Home":
    render_home()

elif view_mode == "Advanced reference":
    render_reference_library(run_simulation, ref_lens, ref_depth)

elif view_mode in ACTION_SECTION_TYPES:
    section_type = ACTION_SECTION_TYPES[view_mode]
    if section_type == "lab":
        render_practical_lab(ACTION_TO_LAB[view_mode])
    elif section_type == "optimization":
        render_optimization_workshop()
    elif section_type == "idea":
        render_idea_analysis()
    elif section_type == "thinking":
        render_thinking_lab()

st.markdown("---")
st.caption(
    f"Applied Mathematical Intelligence v{VERSION} | "
    "Choose a problem → think mathematically → run a simulation."
)
