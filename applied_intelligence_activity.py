"""
Command Center activity hooks — completed learning work only.
"""

from __future__ import annotations

from typing import Any


def _record(
    event: str,
    *,
    page: str = "",
    metrics: dict[str, Any] | None = None,
    summary: str = "",
    resume_key: str = "",
    resume_title: str = "",
    resume_subtitle: str = "",
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
            local_state={"page": page, "lesson": payload.get("lesson", page)},
        )
    except Exception:
        pass


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
