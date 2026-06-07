# streamlit_app.py — Applied Mathematical Intelligence Platform

from typing import Any

import streamlit as st

from components.home import render_home
from components.idea_analysis import render_idea_analysis
from components.optimization_workshop import render_optimization_workshop
from components.practical_labs import render_practical_lab
from components.reference import render_reference_library
from components.styles import inject_platform_styles
from components.math_idea_explorer import render_math_idea_explorer
from components.problem_solving import render_problem_solving_lab
from content.practical_labs import (
    ACTION_SECTION_TYPES,
    ACTION_TO_LAB,
    NAV_HELP,
    PRIMARY_ACTIONS,
)
from content.platform_meta import VERSION
from simulations.registry import run_simulation
from suite_branding import PAGE_ICON
import portfolio_polish as pp
import portfolio_demo as pdemo

st.set_page_config(
    page_title="Applied Mathematical Intelligence",
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY_NAV = ["Home"] + PRIMARY_ACTIONS + ["Advanced reference"]

_PERSISTENCE_OK = False
try:
    from applied_intelligence_persistent_state import (
        VIEW_MODE_KEY,
        autosave_applied_intelligence_state,
        default_reset_applied_intelligence_session,
        ensure_applied_intelligence_view_from_restore,
        ensure_applied_intelligence_view_mode,
        restore_applied_intelligence_disk_state_once,
    )

    _PERSISTENCE_OK = True
except Exception:
    VIEW_MODE_KEY = "view_mode"

    def default_reset_applied_intelligence_session(st_obj: Any) -> None:
        st_obj.session_state.clear()
        st_obj.session_state[VIEW_MODE_KEY] = "Home"

    def restore_applied_intelligence_disk_state_once(_st: Any) -> bool:
        return False

    def autosave_applied_intelligence_state(_st: Any) -> None:
        return None

    def ensure_applied_intelligence_view_mode(st_obj: Any) -> None:
        if st_obj.session_state.get(VIEW_MODE_KEY) not in PRIMARY_NAV:
            st_obj.session_state[VIEW_MODE_KEY] = "Home"
        if st_obj.session_state.get("_suite_ai_question"):
            st_obj.session_state[VIEW_MODE_KEY] = "Solve a Problem"

    def ensure_applied_intelligence_view_from_restore(st_obj: Any) -> None:
        ensure_applied_intelligence_view_mode(st_obj)

if _PERSISTENCE_OK:
    try:
        if not st.session_state.get("_suite_ami_persistence_bootstrapped"):
            restore_applied_intelligence_disk_state_once(st)
            ensure_applied_intelligence_view_from_restore(st)
            st.session_state["_suite_ami_persistence_bootstrapped"] = True
    except Exception:
        pass

try:
    from suite_user_persistence import render_reset_controls, show_persistence_messages

    show_persistence_messages(st)
    render_reset_controls(
        st,
        "applied_intelligence",
        on_reset=default_reset_applied_intelligence_session,
        label="Reset to default",
        help_text="Clears saved page, problem area, and suite preload state for this app.",
        extra_reset_clear_prefixes=("_suite_ai_", "_ami_", "_cc_ai_"),
    )
except Exception:
    pass

try:
    from suite_resume_launch import apply_suite_resume_launch

    apply_suite_resume_launch(st, "applied_intelligence")
    ensure_applied_intelligence_view_from_restore(st)
except Exception:
    pass

inject_platform_styles()
pp.inject_polish_css(st, app_slug="applied-math")

ensure_applied_intelligence_view_mode(st)

# =====================================================
# SIDEBAR
# =====================================================

try:
    from suite_command_center_link import render_command_center_sidebar_link

    render_command_center_sidebar_link(st)
except Exception:
    pass

pp.render_sidebar_toggle(st)

st.sidebar.title("Applied Mathematical Intelligence")
st.sidebar.caption(f"Applied Mathematical Intelligence · v{VERSION}")

view_mode = st.sidebar.radio(
    "Choose",
    PRIMARY_NAV,
    key=VIEW_MODE_KEY,
    label_visibility="collapsed",
)

help_text = NAV_HELP.get(view_mode, "")
if help_text and not pp.is_screenshot_mode(st):
    st.sidebar.markdown(
        f"<p style='font-size:0.82rem;color:#64748b;margin:-0.25rem 0 1rem 0;'>{help_text}</p>",
        unsafe_allow_html=True,
    )

if not pp.is_screenshot_mode(st) and not pp.is_demo_mode(st):
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
st.sidebar.caption("Think first · simulate second · optional depth last")

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
    elif section_type == "problem_solving":
        render_problem_solving_lab()
    elif section_type == "math_idea_explorer":
        render_math_idea_explorer()

try:
    from applied_intelligence_persistent_state import autosave_applied_intelligence_state

    autosave_applied_intelligence_state(st)
except Exception:
    pass

st.markdown("---")
st.caption(
    f"Applied Mathematical Intelligence v{VERSION} | "
    "Enter a quantitative question → analyze → explore a math idea → try a lab."
)
