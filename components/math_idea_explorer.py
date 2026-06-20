"""Mathematical Idea Explorer UI — math → real-world applications."""

import streamlit as st

from components.idea_interactives import render_idea_play
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
    st.caption("Equation, concept, or phrase — structure first, not just an answer.")

    example = st.selectbox("Examples", EXAMPLE_INPUTS, key="mie_example")
    custom = ""
    if example == "Custom input (type below)":
        custom = st.text_input(
            "Your math idea",
            placeholder="e.g. derivative, gradient descent, (x+3)^2 = 7…",
            key="mie_custom",
        )

    user_input = custom.strip() if custom.strip() else example
    if user_input == "Custom input (type below)" and not custom.strip():
        st.info("Pick an example or type your own idea above.")
        return

    concept = detect_concept(user_input)
    sig = (user_input, concept.get("id", ""))
    if st.session_state.get("_ami_mie_activity_sig") != sig:
        st.session_state["_ami_mie_activity_sig"] = sig
        try:
            from applied_intelligence_activity import log_ami_explore_activity

            log_ami_explore_activity(
                math_idea=user_input,
                concept_name=str(concept.get("plain_name") or ""),
                concept_id=str(concept.get("id") or ""),
            )
        except Exception:
            pass
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

    st.markdown("#### 2. What does it mean abstractly?")
    st.markdown(concept["abstract_idea"])

    representation = concept.get("representation")
    if representation:
        st.markdown("#### 3. How could it be represented?")
        st.markdown(representation)

    st.markdown("#### 4. Where does it apply in real life?")
    apps = concept.get("real_world_applications", {})
    cols = st.columns(2)
    items = list(apps.items())
    for i, (domain, text) in enumerate(items):
        with cols[i % 2]:
            label = DOMAIN_LABELS.get(domain, domain.replace("_", " ").title())
            st.markdown(f"**{label}**")
            st.caption(text)

    specific = concept.get("specific_examples", [])
    if specific:
        st.markdown("#### 5. Specific application examples")
        for ex in specific:
            st.markdown(f"- {ex}")

    st.markdown("#### 6. Why does this matter?")
    st.markdown(concept["why_it_matters"])

    st.markdown("#### 7. Try a real-world version")
    st.info(concept["mini_example"])

    if concept.get("id") == "general" and concept.get("interpretation_questions"):
        st.markdown("**Quick structure check**")
        for q in concept["interpretation_questions"]:
            st.markdown(f"- {q}")

    interactive = concept.get("interactive")
    if interactive:
        st.markdown("#### 8. Play with numbers")
        render_idea_play(interactive, f"mie_{concept.get('id', 'x')}", concept.get("interactive_defaults", {}))

    _render_go_deeper(concept)

    closing = concept.get("real_world_closing")
    if closing:
        st.markdown("---")
        st.markdown("#### How this helps you solve real problems")
        st.success(closing)

    _render_related_labs(concept)


def _render_go_deeper(concept: dict) -> None:
    with st.expander("Go deeper — formula, symbols, worked sketch", expanded=False):
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
