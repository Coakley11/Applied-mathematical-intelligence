"""Trace object for Applied Math suite solver runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SolverRunTrace:
    renderer_path: str = "render_suite_solver_answer"
    used_fallback: bool = False
    fallback_error: str = ""
    generic_flow_rendered: bool = False
    source_app: str = ""
    source_page: str = ""
    question: str = ""
    problem_type_id: str = ""
    problem_type: str = ""
    router_confidence: float = 0.0
    solver_id: str = ""
    fields_available: list[str] = field(default_factory=list)
    fields_missing: list[str] = field(default_factory=list)
    context_keys: list[str] = field(default_factory=list)
    conclusion: str = ""
    confidence_pct: int | None = None
    reasons_count: int = 0
    partial: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "renderer_path": self.renderer_path,
            "used_fallback": self.used_fallback,
            "fallback_error": self.fallback_error,
            "generic_flow_rendered": self.generic_flow_rendered,
            "source_app": self.source_app,
            "source_page": self.source_page,
            "question": self.question,
            "problem_type_id": self.problem_type_id,
            "problem_type": self.problem_type,
            "router_confidence": self.router_confidence,
            "solver_id": self.solver_id,
            "fields_available": self.fields_available,
            "fields_missing": self.fields_missing,
            "context_keys": self.context_keys,
            "conclusion": self.conclusion,
            "confidence_pct": self.confidence_pct,
            "reasons_count": self.reasons_count,
            "partial": self.partial,
        }
