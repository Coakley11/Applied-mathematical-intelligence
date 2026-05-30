"""Idea & Invention Analysis — mathematical brainstorming."""

import html
import re

import streamlit as st

from content.idea_analysis import (
    ANALYSIS_DIMENSIONS,
    DEFAULT_IDEA_HINTS,
    IDEA_ANALYSIS,
    IDEA_KEYWORDS,
)


def _match_idea_hints(text: str) -> dict:
    lower = text.lower()
    for pattern, hints in IDEA_KEYWORDS.items():
        if re.search(pattern, lower):
            return hints
    return DEFAULT_IDEA_HINTS


def render_idea_analysis() -> None:
    st.markdown(
        f"""
        <div class="ami-lab-header">
            <span class="ami-lab-icon-lg">{html.escape(IDEA_ANALYSIS["icon"])}</span>
            <div>
                <span class="ami-badge">{html.escape(IDEA_ANALYSIS["action"])}</span>
                <h2 style="margin:0.25rem 0 0 0;">{html.escape(IDEA_ANALYSIS["title"])}</h2>
                <p style="margin:0.35rem 0 0 0;color:#64748b;font-size:0.95rem;">
                    {html.escape(IDEA_ANALYSIS["tagline"])}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(IDEA_ANALYSIS["intro"])

    st.markdown("#### Describe your idea")
    idea = st.text_area(
        "Business idea, invention, strategy, machine, or system",
        placeholder=(
            "e.g. A mobile app that predicts sports outcomes using team statistics, "
            "or a new drug delivery mechanism for cancer treatment"
        ),
        height=120,
        key="idea_input",
    )

    idea_type = st.selectbox(
        "Category (optional — helps tailor analysis)",
        [
            "Auto-detect from description",
            "Business / Startup",
            "Invention / Product",
            "Strategy / System",
            "Machine / Engineering",
            "Medical / Health",
            "AI / Software",
            "Other",
        ],
    )

    if not idea.strip():
        st.info("Enter an idea above to start mathematical brainstorming.")
        _render_framework_preview()
        return

    hints = _match_idea_hints(idea)
    if idea_type != "Auto-detect from description":
        st.caption(f"Category: {idea_type} — analysis also uses keywords from your description.")

    st.markdown("---")
    st.markdown("#### Mathematical brainstorming")

    dimensions = [
        ("What variables matter?", hints["variables"], ANALYSIS_DIMENSIONS[0]),
        ("What data is needed?", hints["data"], ANALYSIS_DIMENSIONS[1]),
        ("What could be optimized?", hints["optimize"], ANALYSIS_DIMENSIONS[2]),
        ("What could be modeled?", hints["model"], ANALYSIS_DIMENSIONS[3]),
        ("What mathematical tools are useful?", hints["tools"], ANALYSIS_DIMENSIONS[4]),
    ]

    for title, tailored, dim in dimensions:
        with st.container(border=True):
            st.markdown(f"### {title}")
            st.caption(dim["description"])
            st.markdown(f"**For your idea:** {tailored}")
            with st.expander("Guiding questions", expanded=False):
                for p in dim["prompts"]:
                    st.markdown(f"- {p}")

    st.success(f"**Suggested labs to explore next:** {hints['labs']}")

    with st.expander("Show the math behind this analysis", expanded=False):
        st.markdown(
            """
            This brainstorming maps your idea to mathematical structures:

            - **Variables** identify what to measure (algebra, state vectors)
            - **Data** grounds estimates (statistics, experimental design)
            - **Optimization** finds best choices under constraints (linear programming, gradients)
            - **Modeling** represents system behavior (calculus, differential equations, simulation)
            - **Tools** match problem type to method (same stack used across all labs in this app)

            The goal is not a formula — it is clarity about what kind of mathematical thinking applies.
            """
        )

    with st.expander("Try the math yourself", expanded=False):
        st.markdown("**Define your core equation:**")
        st.markdown(
            "Complete this sentence: *To know if this idea works, I need to measure "
            "_______ as a function of _______ subject to _______.*"
        )
        col1, col2, col3 = st.columns(3)
        output_var = col1.text_input("Output (what you care about)", key="idea_out")
        input_var = col2.text_input("Inputs (what you control)", key="idea_in")
        constraint = col3.text_input("Constraints (limits)", key="idea_con")
        if output_var and input_var:
            st.markdown(
                f"**Your framework:** Optimize/measure **{output_var}** as a function of "
                f"**{input_var}** subject to **{constraint or 'your constraints'}**."
            )
            st.caption("If you can write this sentence, you have the skeleton of a mathematical model.")

    st.warning("Educational brainstorming only — not business, medical, or investment advice.")


def _render_framework_preview() -> None:
    st.markdown("---")
    st.markdown("#### The five analysis dimensions")
    for dim in ANALYSIS_DIMENSIONS:
        with st.expander(dim["title"], expanded=False):
            st.markdown(dim["description"])
            for p in dim["prompts"]:
                st.markdown(f"- {p}")
