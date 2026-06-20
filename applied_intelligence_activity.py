"""
Command Center activity hooks — completed learning work only.
"""

from __future__ import annotations

from typing import Any


APP_ID = "applied_intelligence"
_LAST_EMIT_KEY = "_ami_last_activity_emit"


def _store_activity_emit_diagnostics(
    *,
    event: str,
    page: str,
    metrics: dict[str, Any],
    summary: str,
    resume_key: str,
) -> None:
    try:
        import streamlit as st

        from suite_workspace import get_active_workspace_id, scoped_cloud_app_id

        ws = get_active_workspace_id()
        write_ns = scoped_cloud_app_id("applied_intelligence", ws)
    except Exception:
        st = None
        ws = metrics.get("workspace_id", "")
        write_ns = "applied_intelligence"
    trace: dict[str, Any] = {}
    try:
        from suite_activity_client import last_record_trace

        trace = last_record_trace()
    except Exception:
        pass
    payload = {
        "event": event,
        "page": page,
        "workspace_id": ws,
        "write_namespace": write_ns,
        "metrics_workspace_id": metrics.get("workspace_id"),
        "summary": summary[:120],
        "resume_key": resume_key,
        "record_trace": trace,
    }
    try:
        import streamlit as st

        st.session_state[_LAST_EMIT_KEY] = payload
    except Exception:
        pass


def _record(
    event: str,
    *,
    page: str = "",
    metrics: dict[str, Any] | None = None,
    summary: str = "",
    resume_key: str = "",
    resume_title: str = "",
    resume_subtitle: str = "",
    action_url: str = "",
) -> None:
    try:
        from suite_activity_client import record_activity

        payload = dict(metrics or {})
        try:
            from suite_workspace import get_active_workspace_id

            payload.setdefault("workspace_id", get_active_workspace_id())
        except ImportError:
            pass
        record_activity(
            "applied_intelligence",
            event,
            page=page or "Applied Intelligence",
            metrics=payload,
            summary=summary,
            resume_key=resume_key,
            resume_title=resume_title,
            resume_subtitle=resume_subtitle,
            action_url=action_url,
            local_state={"page": page, "lesson": payload.get("lesson", page)},
        )
        _store_activity_emit_diagnostics(
            event=event,
            page=page or "Applied Intelligence",
            metrics=payload,
            summary=summary,
            resume_key=resume_key,
        )
    except Exception:
        pass


def log_ami_session_activity(*, page: str, summary: str = "", metrics: dict[str, Any] | None = None) -> None:
    """Log AMI page/settings activity for Command Center feed and current-state row."""
    label = str(page or "Applied Intelligence").strip()
    payload = dict(metrics or {})
    payload.setdefault("view_mode", label)
    payload.setdefault("lesson", summary or label)
    _record(
        "session_activity",
        page=label,
        metrics=payload,
        summary=summary or f"Applied Intelligence: {label}",
        resume_key=f"ami:page:{label[:40]}",
        resume_title=f"Continue: {label[:48]}",
        resume_subtitle="Applied Mathematical Intelligence",
    )


def log_ami_workflow_activity(
    *,
    question: str,
    area_id: str = "",
    area_name: str = "",
    interactive: str = "",
) -> None:
    """Log standalone AMI workflow for Command Center Continue, recent questions, and feed."""
    q = str(question or "").strip()
    if not q:
        return
    try:
        from suite_analytical_question import (
            analytical_question_continue_copy,
            build_applied_math_resume_url,
            build_question_payload,
            metrics_for_applied_math_resume,
            _upsert_applied_intelligence_resume,
        )

        ctx: dict[str, Any] = {}
        if area_name:
            ctx["area"] = area_name
        if area_id:
            ctx["quant_area"] = area_id
        payload = build_question_payload(
            source_app="applied_intelligence",
            source_page="Solve a Problem",
            question=q,
            context=ctx,
            quant_area=area_id,
        )
        action_url = build_applied_math_resume_url(payload)
        metrics = metrics_for_applied_math_resume(payload)
        if interactive:
            metrics["interactive"] = interactive
        if area_name:
            metrics["topic"] = area_name
        resume_key = str(payload.get("resume_key") or "")
        card_title, card_subtitle, _ = analytical_question_continue_copy(payload)
        _record(
            "analytical_question",
            page="Solve a Problem",
            metrics=metrics,
            summary=f"Applied Math: {q[:80]}",
            resume_key=resume_key,
            resume_title=card_title,
            resume_subtitle=card_subtitle,
            action_url=action_url,
        )
        _upsert_applied_intelligence_resume(payload, action_url=action_url)
    except Exception:
        log_problem_solved(topic=q, area=area_name, interactive=interactive)


def log_ami_explore_activity(
    *,
    math_idea: str,
    concept_name: str = "",
    concept_id: str = "",
) -> None:
    """Log Explore a Math Idea workflow for Command Center (Ariel/Daniel scoped)."""
    idea = str(math_idea or "").strip()
    if not idea or idea == "Custom input (type below)":
        return
    try:
        from suite_analytical_question import (
            analytical_question_continue_copy,
            build_applied_math_resume_url,
            build_question_payload,
            metrics_for_applied_math_resume,
            _upsert_applied_intelligence_resume,
        )

        ctx: dict[str, Any] = {"math_idea": idea}
        if concept_name:
            ctx["concept"] = concept_name
        if concept_id:
            ctx["concept_id"] = concept_id
        payload = build_question_payload(
            source_app="applied_intelligence",
            source_page="Explore a Math Idea",
            question=idea,
            context=ctx,
            quant_area=concept_id or "math_idea",
        )
        action_url = build_applied_math_resume_url(payload)
        metrics = metrics_for_applied_math_resume(payload)
        metrics["view_mode"] = "Explore a Math Idea"
        if concept_name:
            metrics["topic"] = concept_name
        resume_key = str(payload.get("resume_key") or "")
        card_title, card_subtitle, _ = analytical_question_continue_copy(payload)
        _record(
            "analytical_question",
            page="Explore a Math Idea",
            metrics=metrics,
            summary=f"Math idea: {idea[:80]}",
            resume_key=resume_key,
            resume_title=card_title,
            resume_subtitle=card_subtitle,
            action_url=action_url,
        )
        _upsert_applied_intelligence_resume(payload, action_url=action_url)
        log_ami_session_activity(
            page="Explore a Math Idea",
            summary=f"Explored math idea: {idea[:80]}",
            metrics=metrics,
        )
    except Exception:
        _record(
            "problem_solved",
            page="Explore a Math Idea",
            metrics={"lesson": idea, "topic": concept_name or idea, "view_mode": "Explore a Math Idea"},
            summary=f"Explored math idea: {idea[:80]}",
            resume_key=f"ai:idea:{idea[:40]}",
            resume_title=f"Continue: {idea[:48]}",
            resume_subtitle="Explore a Math Idea",
        )


def log_problem_solved(*, topic: str, area: str = "", interactive: str = "") -> None:
    label = str(topic or area or "applied problem").strip()
    _record(
        "problem_solved",
        page="Solve a Problem",
        metrics={"lesson": label, "analysis": label, "topic": area, "interactive": interactive},
        summary=f"Solved applied problem: {label}",
        resume_key=f"ai:problem:{label[:40]}",
        resume_title=f"Continue: {label[:48]}",
        resume_subtitle="Problem-solving flow",
    )


def log_lesson_completed(*, lesson: str) -> None:
    label = str(lesson or "").strip()
    if not label:
        return
    _record(
        "lesson_completed",
        page=label,
        metrics={"lesson": label},
        summary=f"Completed AI lesson: {label}",
        resume_key=f"lesson:{label[:40]}",
        resume_title=f"Continue: {label}",
        resume_subtitle="Next exercise in sequence",
    )


def log_case_study_completed(*, title: str) -> None:
    label = str(title or "").strip()
    _record(
        "case_study_completed",
        page=label,
        metrics={"lesson": label, "topic": label},
        summary=f"Finished case study: {label}",
        resume_key=f"case:{label[:40]}",
        resume_title=f"Continue case study: {label[:40]}",
        resume_subtitle="Applied Intelligence",
    )


def log_module_completed(*, module: str) -> None:
    label = str(module or "").strip()
    _record(
        "module_completed",
        page=label,
        metrics={"lesson": label},
        summary=f"Finished learning module: {label}",
        resume_key=f"module:{label[:40]}",
        resume_title=f"Continue: {label}",
        resume_subtitle="Learning module",
    )


def log_reasoning_exercise_completed(*, exercise: str) -> None:
    label = str(exercise or "").strip()
    _record(
        "reasoning_exercise_completed",
        page=label,
        metrics={"lesson": label},
        summary=f"Completed reasoning exercise: {label}",
        resume_key=f"reasoning:{label[:40]}",
        resume_title=f"Continue: {label}",
        resume_subtitle="Reasoning practice",
    )
