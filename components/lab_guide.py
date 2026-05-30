"""Guided tool renderer — plain-language intro, simulation, math expanders."""

import html

import streamlit as st

from components.math_practice import render_math_practice
from content.tool_guides import TOOL_GUIDES
from simulations.labs import LAB_RUNNERS
from simulations.registry import SIMULATION_RUNNERS


def run_tool(runner_id: str) -> None:
    runner = LAB_RUNNERS.get(runner_id) or SIMULATION_RUNNERS.get(runner_id)
    if runner:
        runner()
    else:
        st.warning(f"Tool not available: {runner_id}")


def render_guided_tool(runner_id: str) -> None:
    """Full guided flow for one simulation tool."""
    guide = TOOL_GUIDES.get(runner_id)
    if not guide:
        st.caption("Interactive simulation")
        run_tool(runner_id)
        return

    st.markdown(f"### {guide['plain_name']}")

    with st.container(border=True):
        st.markdown("#### What is this?")
        st.markdown(guide["what"])
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Why should I care?**")
            st.markdown(guide["why"])
        with c2:
            st.markdown("**What am I trying to figure out?**")
            st.markdown(guide["figuring_out"])
        st.markdown(f"**Math used:** {guide['math_used']}")
        st.markdown(f"**What you can change:** {guide['controls']}")

    st.markdown("---")
    st.markdown("#### Run the simulation")
    run_tool(runner_id)

    st.markdown("---")
    st.markdown("#### How to read the result")
    st.info(guide["interpret"])

    with st.expander("Show the math behind this", expanded=False):
        st.markdown(guide["math_behind"])

    with st.expander("Try the math yourself", expanded=False):
        practice_id = guide.get("practice_id", "")
        render_math_practice(
            practice_id,
            key_prefix=f"{runner_id}_{practice_id}",
        )

    with st.expander("Portfolio / advanced project idea", expanded=False):
        st.markdown(guide.get("portfolio_idea", "Build a Python notebook extending this simulation with real data."))
