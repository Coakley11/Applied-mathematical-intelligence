"""Mathematical Idea Explorer UI — math → real-world applications."""

import streamlit as st

from components.nav import navigate_to
from content.math_idea_explorer import (
    DOMAIN_LABELS,
    EXAMPLE_INPUTS,
    MATH_IDEA_EXPLORER,
    detect_concept,
)


def render_math_idea_explorer() -> None:
    from components.section_intro import render_section_header

    render_section_header(
        MATH_IDEA_EXPLORER["icon"],
        MATH_IDEA_EXPLORER["action"],
        MATH_IDEA_EXPLORER["tagline"],
    )
    st.caption(MATH_IDEA_EXPLORER["intro"])

    st.markdown("#### Enter a math idea")
    st.caption("Equation, concept, or phrase — we map structure to real-world uses.")

    example = st.selectbox("Examples", EXAMPLE_INPUTS, key="mie_example")
    custom = ""
    if example == "Custom input (type below)":
        custom = st.text_input(
            "Your math idea",
            placeholder="e.g. derivative, (x+3)^2 = 7, Bayes theorem…",
            key="mie_custom",
        )

    user_input = custom.strip() if custom.strip() else example
    if user_input == "Custom input (type below)" and not custom.strip():
        st.info("Pick an example or type your own idea above.")
        return

    concept = detect_concept(user_input)
    _render_concept_exploration(user_input, concept)


def render_math_idea_explorer_embedded() -> None:
    """Compact embed for tab inside Solve a Problem."""
    st.caption("Reverse direction: **math idea → where it appears in reality**.")
    example = st.selectbox("Math idea", EXAMPLE_INPUTS, key="mie_tab_example")
    custom = ""
    if example == "Custom input (type below)":
        custom = st.text_input("Your input", key="mie_tab_custom")
    user_input = custom.strip() if custom.strip() else example
    if user_input == "Custom input (type below)" and not custom.strip():
        return
    concept = detect_concept(user_input)
    _render_concept_exploration(user_input, concept)


def _render_concept_exploration(user_input: str, concept: dict) -> None:
    st.markdown("---")
    with st.container(border=True):
        st.markdown(f"**You entered:** `{user_input}`")
        st.markdown(f"**Recognized as:** {concept['plain_name']}")

    st.markdown("#### 1. What is this mathematically?")
    st.markdown(concept["mathematical_description"])

    st.markdown("#### 2. What is the deeper abstract idea?")
    st.markdown(concept["abstract_idea"])

    st.markdown("#### 3. Where does this show up in real life?")
    apps = concept.get("real_world_applications", {})
    cols = st.columns(2)
    items = list(apps.items())
    for i, (domain, text) in enumerate(items):
        with cols[i % 2]:
            label = DOMAIN_LABELS.get(domain, domain.replace("_", " ").title())
            st.markdown(f"**{label}**")
            st.caption(text)

    st.markdown("#### 4. Why does this matter?")
    st.markdown(concept["why_it_matters"])

    st.markdown("#### 5. Try a real-world version")
    st.info(concept["mini_example"])

    if concept.get("id") == "general" and concept.get("interpretation_questions"):
        st.markdown("**Quick structure check**")
        for q in concept["interpretation_questions"]:
            st.markdown(f"- {q}")

    _render_go_deeper(concept)

    _render_related_labs(concept)


def _render_go_deeper(concept: dict) -> None:
    with st.expander("#### 6. Go deeper (optional)", expanded=False):
        st.markdown(concept.get("deeper_math", ""))
        if concept.get("user_input"):
            st.caption(f"Your input: {concept['user_input']}")


def _render_related_labs(concept: dict) -> None:
    labs = concept.get("related_labs", [])
    if not labs:
        return
    st.markdown("---")
    st.markdown("#### Related in this app")
    for lab in labs:
        if st.button(f"Open **{lab}** →", key=f"mie_lab_{lab}_{concept.get('id', 'x')}"):
            navigate_to(lab)
