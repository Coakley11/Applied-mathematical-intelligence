"""Solve a Problem — seven quantitative areas, analyst flow."""

import hashlib
import re

import streamlit as st

from components.problem_analyst import render_abstract_section, render_quantitative_flow
from components.section_intro import render_section_header
from components.thinking_lab import render_thinking_topics_panel
from components.thinking_workshop import render_thinking_workshop
from content.problem_solving import (
    DEFAULT_PATTERN,
    MATHEMATICIAN_MODE_TOPICS,
    PROBLEM_PATTERNS,
    PROBLEM_SOLVING_LAB,
)
from content.quant_areas import QUANT_AREAS, QUANT_AREA_BY_ID


def _match_pattern(text: str, area_pattern_id: str) -> dict:
    lower = text.lower()
    for pattern, data in PROBLEM_PATTERNS.items():
        if re.search(pattern, lower):
            matched = dict(data)
            if area_pattern_id == "abstract":
                matched["id"] = "abstract"
            return matched
    result = dict(DEFAULT_PATTERN)
    result["id"] = area_pattern_id if area_pattern_id != "default" else "default"
    return result


def render_problem_solving_lab() -> None:
    render_section_header(
        PROBLEM_SOLVING_LAB["icon"],
        PROBLEM_SOLVING_LAB["action"],
        PROBLEM_SOLVING_LAB["tagline"],
    )

    tab_areas, tab_ideas, tab_thinking = st.tabs(
        ["Quantitative areas", "Explore a math idea", "Mathematical thinking"]
    )

    with tab_areas:
        _render_area_hub()

    with tab_ideas:
        from components.math_idea_explorer import render_math_idea_explorer_embedded

        render_math_idea_explorer_embedded()

    with tab_thinking:
        _render_mathematical_thinking()


def _render_area_hub() -> None:
    st.markdown("#### Choose a real-world area")
    st.caption("Pick where your question lives — then ask something specific and quantitative.")

    preloaded = str(st.session_state.get("ps_library_problem") or "").strip()
    if preloaded and st.session_state.get("_suite_ai_question"):
        source = str(st.session_state.get("_suite_ai_source_app") or "").strip()
        source_page = str(st.session_state.get("_suite_ai_source_page") or "").strip()
        ctx_raw = str(st.session_state.get("_suite_ai_context") or "").strip()
        st.markdown("#### Applied Math question (from suite app)")
        st.markdown(f"**{preloaded}**")
        banner = f"From **{source or 'suite app'}**"
        if source_page:
            banner += f" · {source_page}"
        st.caption(banner)
        if ctx_raw:
            try:
                import json

                parsed = json.loads(ctx_raw)
                if isinstance(parsed, dict):
                    try:
                        from suite_analytical_question import format_context_lines

                        lines = format_context_lines(parsed)
                    except Exception:
                        lines = [f"{k}: {v}" for k, v in parsed.items() if v][:8]
                    if lines:
                        st.markdown("**Context**")
                        for line in lines:
                            st.markdown(f"- {line}")
                else:
                    st.caption(ctx_raw[:400])
            except Exception:
                if ctx_raw.startswith("Question:") or ctx_raw.startswith("Context:"):
                    st.markdown(ctx_raw.replace(" · ", "\n\n"))
                else:
                    st.caption(ctx_raw[:400])
        area_ids = [a["id"] for a in QUANT_AREAS]
        area_id = str(st.session_state.get("ps_area_id") or area_ids[0])
        if area_id not in area_ids:
            area_id = area_ids[0]
        area = QUANT_AREA_BY_ID[area_id]
        pattern_id = area["pattern_id"]
        pattern = _match_pattern(preloaded, pattern_id)
        slug = hashlib.md5(preloaded.encode("utf-8")).hexdigest()[:10]
        key_prefix = f"ps_{area['id']}_{slug}"
        st.markdown("---")
        render_quantitative_flow(preloaded, pattern, pattern_id, area, key_prefix)
        return

    area_ids = [a["id"] for a in QUANT_AREAS]
    default_id = st.session_state.get("ps_area_id", area_ids[0])
    if default_id not in area_ids:
        default_id = area_ids[0]

    area_id = st.selectbox(
        "Area",
        area_ids,
        index=area_ids.index(default_id),
        format_func=lambda aid: f"{QUANT_AREA_BY_ID[aid]['icon']} {QUANT_AREA_BY_ID[aid]['name']}",
        key="ps_area_select",
    )
    area = QUANT_AREA_BY_ID[area_id]
    st.session_state.ps_area_id = area_id

    st.markdown(f"*{area['tagline']}*")

    if area["id"] == "abstract":
        render_abstract_section()
        st.markdown("---")

    library_problem = st.session_state.get("ps_library_problem", "")
    examples = area["example_questions"]
    example = st.selectbox(
        "Pick an example (featured ones are first)",
        examples,
        key=f"ps_ex_{area['id']}",
    )

    custom = ""
    if example.endswith("Custom question (type below)"):
        custom = st.text_area(
            "Your question",
            value=library_problem if st.session_state.get("ps_area_id") == area["id"] else "",
            placeholder="Type a specific quantitative question…",
            key=f"ps_custom_{area['id']}",
        )

    problem = custom.strip() if custom.strip() else example
    if problem.endswith("Custom question (type below)") and not custom.strip():
        st.info("Pick a worked example above, or type your own quantitative question.")
        return

    pattern_id = area["pattern_id"]
    pattern = _match_pattern(problem, pattern_id)
    if pattern.get("id") not in (pattern_id, "abstract"):
        pattern_id = pattern.get("id", pattern_id)

    slug = hashlib.md5(problem.encode("utf-8")).hexdigest()[:10]
    key_prefix = f"ps_{area['id']}_{slug}"
    st.markdown("---")
    render_quantitative_flow(problem, pattern, pattern_id, area, key_prefix)


def _render_mathematical_thinking() -> None:
    st.markdown("#### How do mathematicians think?")
    st.caption(
        "Applied math laboratory — enter a scenario, pick a thinking style, play with sliders and visuals. "
        "Less reading, more experimenting."
    )

    sub_workshop, sub_core, sub_topics = st.tabs(
        ["Interactive workshop", "Quick reference", "Topic library"]
    )

    with sub_workshop:
        render_thinking_workshop()

    with sub_core:
        names = [t["name"] for t in MATHEMATICIAN_MODE_TOPICS]
        choice = st.selectbox("Concept", names, key="ps_math_mode_topic")
        topic = next(t for t in MATHEMATICIAN_MODE_TOPICS if t["name"] == choice)
        with st.container(border=True):
            st.markdown(f"**{topic['name']}** — {topic['idea']}")
            st.markdown(f"*{topic['prompt']}*")
            st.info(f"Example: {topic['example']}")
        st.caption("Use the **Interactive workshop** tab to apply this style to your own problem.")

    with sub_topics:
        render_thinking_topics_panel()
