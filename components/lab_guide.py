"""Guided tool renderer — plain-language intro, simulation, optional depth."""

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
    """Lab-first guided flow — play with the simulation, then interpret."""
    guide = TOOL_GUIDES.get(runner_id)
    if not guide:
        st.caption("Interactive simulation — move the controls first.")
        run_tool(runner_id)
        return

    st.markdown(f"### {guide['plain_name']}")
    st.caption(guide["what"][:200] + ("…" if len(guide["what"]) > 200 else ""))

    st.markdown("#### Play with it")
    st.caption("Change sliders and inputs — watch the charts update. Read explanations after you explore.")
    run_tool(runner_id)

    st.markdown("#### What to look for")
    st.info(guide["interpret"])

    with st.expander("Why are we asking this? (after you explore)", expanded=False):
        st.markdown(guide["figuring_out"])
        st.markdown(f"*In context:* {guide['why']}")

    with st.expander("Go deeper (optional)", expanded=False):
        st.markdown("**Why this matters**")
        st.markdown(guide["why"])
        st.markdown("**What you're figuring out**")
        st.markdown(guide["figuring_out"])
        st.markdown("**What you can change**")
        st.markdown(guide["controls"])
        st.markdown("---")
        st.markdown("**The math behind this**")
        st.markdown(guide["math_behind"])
        st.caption(
            f"Connected to your problem: {guide['figuring_out'][:120]}… "
            f"Concepts: {guide['math_used']}"
        )
        st.markdown("---")
        st.markdown("**Try the math yourself**")
        practice_id = guide.get("practice_id", "")
        render_math_practice(
            practice_id,
            key_prefix=f"{runner_id}_{practice_id}",
        )
        if guide.get("portfolio_idea"):
            st.markdown("---")
            st.markdown("**Project idea**")
            st.markdown(guide["portfolio_idea"])
