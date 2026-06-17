"""Solve a Problem — seven quantitative areas, analyst flow."""

import hashlib
import json
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


def _url_query_param(name: str) -> str:
    try:
        raw = st.query_params.get(name)
    except Exception:
        return ""
    if raw is None:
        return ""
    if isinstance(raw, list):
        return str(raw[0] or "").strip()
    return str(raw).strip()


def _load_suite_context() -> tuple[str, str, str, dict]:
    preloaded = str(st.session_state.get("ps_library_problem") or "").strip()
    source = str(st.session_state.get("_suite_ai_source_app") or "").strip()
    source_page = str(st.session_state.get("_suite_ai_source_page") or "").strip()
    ctx_dict: dict = {}
    hydrate_source = str(st.session_state.get("_suite_ai_hydrate_source") or "").strip()

    try:
        from suite_resume_launch import resolve_url_suite_ai_question_id

        url_qid = resolve_url_suite_ai_question_id(st)
    except Exception:
        url_qid = _url_query_param("suite_ai_question_id")
    url_question = _url_query_param("suite_ai_question")
    if url_qid:
        st.session_state["_suite_ai_question_id"] = url_qid
        st.session_state["_suite_ai_url_question_id"] = url_qid
    if url_question:
        st.session_state["_suite_ai_question"] = url_question
        st.session_state["ps_library_problem"] = url_question
        preloaded = url_question

    qid = url_qid or str(st.session_state.get("_suite_ai_question_id") or "").strip()
    if qid:
        try:
            from suite_analytical_question import load_analytical_question_payload

            payload = load_analytical_question_payload(qid)
            blob_question = str(payload.get("question") or "").strip()
            if blob_question:
                preloaded = blob_question
                st.session_state["_suite_ai_question"] = blob_question
                st.session_state["ps_library_problem"] = blob_question
            blob_ctx = payload.get("context") if isinstance(payload.get("context"), dict) else {}
            instant = payload.get("instant_insight")
            if isinstance(instant, dict) and instant:
                blob_ctx = dict(blob_ctx)
                blob_ctx["instant_insight"] = instant
            if blob_ctx:
                ctx_dict = blob_ctx
                load_source = str(payload.get("blob_load_source") or "saved_items")
                hydrate_source = "resume_subtitle" if load_source == "resume_subtitle" else "question_id_blob"
                st.session_state["_suite_ai_context"] = json.dumps(ctx_dict, ensure_ascii=False)
                st.session_state["_suite_ai_hydrate_source"] = hydrate_source
                try:
                    from suite_analytical_question import _context_payload_hash

                    st.session_state["_suite_ai_blob_meta"] = {
                        "url_question_id": qid,
                        "loaded_question_id": qid,
                        "payload_question_id": payload.get("question_id"),
                        "blob_load_source": load_source,
                        "blob_updated_at": payload.get("blob_store_updated_at") or payload.get("saved_at"),
                        "blob_payload_hash": payload.get("payload_hash"),
                        "loaded_context_hash": _context_payload_hash(ctx_dict),
                        "blob_diagnostics": payload.get("blob_diagnostics"),
                        "blob_store_app": payload.get("blob_store_app"),
                        "blob_load_candidates": payload.get("blob_load_candidates"),
                    }
                except Exception:
                    pass
            elif qid:
                st.session_state.setdefault("_suite_ai_blob_meta", {})["blob_load_error"] = str(
                    payload.get("blob_load_error") or "no_blob_context_for_question_id"
                )
        except Exception as exc:
            if qid:
                st.session_state["_suite_ai_blob_meta"] = {
                    "url_question_id": qid,
                    "loaded_question_id": qid,
                    "blob_load_error": str(exc),
                }
            pass

    if not ctx_dict and qid and hydrate_source not in ("question_id_blob", "resume_subtitle"):
        ctx_raw = str(st.session_state.get("_suite_ai_context") or "").strip()
        if ctx_raw and not url_qid:
            try:
                parsed = json.loads(ctx_raw)
                if isinstance(parsed, dict) and parsed:
                    ctx_dict = parsed
                    if not hydrate_source:
                        hydrate_source = "session_json"
            except Exception:
                pass
    elif not ctx_dict:
        ctx_raw = str(st.session_state.get("_suite_ai_context") or "").strip()
        if ctx_raw:
            try:
                parsed = json.loads(ctx_raw)
                if isinstance(parsed, dict):
                    ctx_dict = parsed
                    if not hydrate_source:
                        hydrate_source = "session_json"
            except Exception:
                pass

    if not ctx_dict and qid:
        try:
            from suite_analytical_question import load_analytical_question_context

            ctx_dict = load_analytical_question_context(qid)
            if ctx_dict:
                hydrate_source = "question_id_blob"
                st.session_state["_suite_ai_context"] = json.dumps(ctx_dict, ensure_ascii=False)
                st.session_state["_suite_ai_hydrate_source"] = hydrate_source
        except Exception:
            pass

    if hydrate_source:
        st.session_state["_suite_ai_hydrate_source"] = hydrate_source
    if not source:
        raw = str(ctx_dict.get("source_app") or "").strip().lower()
        if "baseball" in raw:
            source = "baseball"
        elif "nba" in raw:
            source = "nba"
        elif "investment" in raw:
            source = "investment"
    return preloaded, source, source_page, ctx_dict


def _render_suite_question_view() -> None:
    """Suite-only path: normal page shell + solver answer."""
    preloaded, source, source_page, ctx_dict = _load_suite_context()
    if not preloaded:
        qid = str(st.session_state.get("_suite_ai_question_id") or "").strip()
        if qid:
            st.warning(f"Suite question id `{qid}` loaded but question text is empty — check blob_load_error in Dev Mode.")
        else:
            st.warning("Suite question loaded but text is empty.")
        return

    from components.applied_math_suite_page import render_suite_question_page_header

    render_suite_question_page_header(
        st,
        question=preloaded,
        source_app=source,
        source_page=source_page,
    )

    try:
        from components.applied_math_context_diagnostics import render_applied_math_context_diagnostics

        render_applied_math_context_diagnostics(
            st,
            question=preloaded,
            question_id=str(st.session_state.get("_suite_ai_question_id") or "").strip(),
            source_app=source,
            source_page=source_page,
            context=ctx_dict,
        )
    except Exception:
        pass

    from components.applied_math_solver_ui import render_suite_solver_answer

    render_suite_solver_answer(
        st,
        question=preloaded,
        source_app=source,
        source_page=source_page,
        context=ctx_dict,
    )


def render_problem_solving_lab() -> None:
    if st.session_state.get("_suite_ai_question") or st.session_state.get("_suite_ai_question_id"):
        _render_suite_question_view()
        return

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
