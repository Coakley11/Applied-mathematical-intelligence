"""Quality validation helpers for suite Applied Math context → first-pass analysis."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from components.applied_math_first_pass_analysis import analyze_suite_question


@dataclass
class ValidationScenario:
    name: str
    source_app: str
    source_page: str
    question: str
    context: dict[str, Any]
    required_keys: tuple[str, ...] = ()
    nested_required: dict[str, tuple[str, ...]] = field(default_factory=dict)
    answer_must_contain: tuple[str, ...] = ()


@dataclass
class ValidationResult:
    scenario: str
    source_app: str
    context_received: list[str]
    context_missing: list[str]
    answer_snippet: str
    answer_uses_context: bool
    quality_rating: int
    notes: str = ""


def _has_value(val: Any) -> bool:
    if val is None or val == "":
        return False
    if isinstance(val, (list, dict)) and not val:
        return False
    return True


def audit_context(
    context: dict[str, Any],
    *,
    required_keys: tuple[str, ...],
    nested_required: dict[str, tuple[str, ...]] | None = None,
) -> tuple[list[str], list[str]]:
    """Return (present labels, missing labels) for required context fields."""
    present: list[str] = []
    missing: list[str] = []
    nested = nested_required or {}
    for key in required_keys:
        val = context.get(key)
        if _has_value(val):
            present.append(key)
        else:
            missing.append(key)
    for parent, subs in nested.items():
        block = context.get(parent)
        if not isinstance(block, dict):
            for sub in subs:
                missing.append(f"{parent}.{sub}")
            continue
        for sub in subs:
            label = f"{parent}.{sub}"
            if _has_value(block.get(sub)):
                present.append(label)
            else:
                missing.append(label)
    return present, missing


def context_json_size(context: dict[str, Any]) -> int:
    return len(json.dumps(context, ensure_ascii=False))


def answer_references_context(answer: str, *needles: str) -> bool:
    text = str(answer or "").lower()
    if not text:
        return False
    hits = sum(1 for n in needles if str(n).lower() in text)
    return hits >= max(1, len(needles) // 2) if needles else bool(text.strip())


def rate_quality(*, present_count: int, missing_count: int, answer_uses_context: bool) -> int:
    if missing_count == 0 and answer_uses_context:
        return 9
    if missing_count <= 1 and answer_uses_context:
        return 7
    if present_count >= 2 and not answer_uses_context:
        return 5
    if present_count >= 1:
        return 4
    return 2


def run_validation_scenario(scenario: ValidationScenario) -> ValidationResult:
    present, missing = audit_context(
        scenario.context,
        required_keys=scenario.required_keys,
        nested_required=scenario.nested_required,
    )
    analysis = analyze_suite_question(
        scenario.question,
        source_app=scenario.source_app,
        context=scenario.context,
    )
    answer = analysis.answer or ""
    uses = answer_references_context(answer, *scenario.answer_must_contain)
    rating = rate_quality(
        present_count=len(present),
        missing_count=len(missing),
        answer_uses_context=uses,
    )
    return ValidationResult(
        scenario=scenario.name,
        source_app=scenario.source_app,
        context_received=present,
        context_missing=missing,
        answer_snippet=answer[:280],
        answer_uses_context=uses,
        quality_rating=rating,
        notes="; ".join(analysis.data_needed[:3]) if analysis.data_needed else "",
    )


def expected_fields_for_page(source_app: str, source_page: str) -> tuple[tuple[str, ...], dict[str, tuple[str, ...]]]:
    """Developer diagnostics: expected keys by source app and page label."""
    app = str(source_app or "").strip().lower()
    page = str(source_page or "").strip().lower()
    if "baseball" in app:
        if "historical" in page:
            return (
                ("filters_applied", "metrics", "historical_snapshot"),
                {"historical_snapshot": ("top_rows", "sort_stat", "year_range")},
            )
        if "trend" in page:
            return (("player", "metrics", "trend_summary"), {"trend_summary": ("slope", "r2", "delta", "summary")})
        if "comparison" in page:
            return (("player_a", "player_b", "comparison_differences"), {})
    if "nba" in app:
        if "matchup" in page:
            return (("team", "opponent", "workflow"), {})
        if "live" in page or "game" in page:
            return (("team", "win_probability"), {})
        if "legacy" in page:
            return (("player", "stat_gap"), {"stat_gap": ("gap", "comparison")})
        return (("team",), {})
    if "investment" in app:
        if "macro" in page:
            return (("macro_outlook", "context_note_forward", "context_note_historical"), {})
        if "rebalance" in page:
            return (("rebalance_drift", "target_weights", "current_weights"), {})
        return (
            ("holdings", "current_weights", "health_score", "sharpe_ratio", "max_drawdown"),
            {},
        )
    return ((), {})


VALIDATION_SCENARIOS: tuple[ValidationScenario, ...] = (
    ValidationScenario(
        name="Baseball Historical Explorer",
        source_app="baseball",
        source_page="Historical Explorer",
        question="Is Mike Trout's 2019 season an outlier in this table?",
        context={
            "source_app": "Baseball",
            "page": "Historical Explorer",
            "player": "Mike Trout",
            "metrics": ["HR"],
            "filters_applied": "Years 2015–2019; sort HR",
            "historical_snapshot": {
                "sort_stat": "HR",
                "year_range": "2015–2019",
                "row_count": 120,
                "top_players": ["Mike Trout", "Aaron Judge"],
                "top_rows": [{"player": "Mike Trout", "year": 2019, "HR": 45}],
            },
        },
        required_keys=("player", "metrics", "filters_applied", "historical_snapshot"),
        nested_required={"historical_snapshot": ("top_rows", "sort_stat", "year_range")},
        answer_must_contain=("Mike Trout",),
    ),
    ValidationScenario(
        name="Baseball Trend Value",
        source_app="baseball",
        source_page="Trend Value",
        question="Is Lorenzo Cain's HR trend meaningful?",
        context={
            "player": "Lorenzo Cain",
            "metrics": ["HR"],
            "trend_summary": {
                "stat": "HR",
                "latest": 15,
                "delta": 6,
                "slope": 1.2,
                "r2": 0.64,
                "summary": "upward but noisy trend",
            },
        },
        required_keys=("player", "metrics", "trend_summary"),
        nested_required={"trend_summary": ("slope", "r2", "delta", "summary")},
        answer_must_contain=("1.2", "0.64"),
    ),
    ValidationScenario(
        name="Baseball Comparison Tool",
        source_app="baseball",
        source_page="Comparison Tool",
        question="Is Piazza better than Bagwell for my league?",
        context={
            "player_a": "Mike Piazza",
            "player_b": "Jeff Bagwell",
            "comparison_stats": ["OPS"],
            "comparison_differences": [
                {"player": "Mike Piazza", "Slope": 0.02},
                {"player": "Jeff Bagwell", "Slope": 0.01},
            ],
        },
        required_keys=("player_a", "player_b", "comparison_differences"),
        answer_must_contain=("Piazza", "Bagwell"),
    ),
    ValidationScenario(
        name="NBA Matchup",
        source_app="nba",
        source_page="Matchup Intelligence",
        question="How much does the injury gap matter?",
        context={
            "team": "New York Knicks",
            "opponent": "Boston Celtics",
            "workflow": "Matchup intelligence",
            "model_assumptions": "Knicks +4 health index",
        },
        required_keys=("team", "opponent", "workflow"),
        answer_must_contain=("Knicks",),
    ),
    ValidationScenario(
        name="NBA Probability",
        source_app="nba",
        source_page="Live Game Center",
        question="Is 62% win probability reasonable?",
        context={
            "team": "New York Knicks",
            "opponent": "Boston Celtics",
            "win_probability": "62%",
            "series_probability": "71%",
        },
        required_keys=("team", "win_probability", "series_probability"),
        answer_must_contain=("62%",),
    ),
    ValidationScenario(
        name="NBA Legacy Tracker",
        source_app="nba",
        source_page="Legacy Tracker",
        question="Will Jalen Brunson pass Allan Houston in playoff rebounds?",
        context={
            "player": "Jalen Brunson",
            "stat_gap": {
                "player": "Jalen Brunson",
                "comparison": "Allan Houston",
                "stat": "playoff rebounds",
                "gap": 12,
                "current_value": 8,
                "target_value": 20,
            },
            "games_remaining": 4,
            "rate_needed": "3.0 RPG",
        },
        required_keys=("player", "stat_gap", "games_remaining", "rate_needed"),
        nested_required={"stat_gap": ("gap", "comparison", "current_value", "target_value")},
        answer_must_contain=("4", "3.0"),
    ),
    ValidationScenario(
        name="Investment Portfolio Health",
        source_app="investment",
        source_page="Portfolio Health",
        question="Is my portfolio too risky?",
        context={
            "holdings": ["VTI", "BND"],
            "current_weights": {"VTI": "60.0%", "BND": "40.0%"},
            "health_score": 78.5,
            "sharpe_ratio": "0.68",
            "max_drawdown": "-18.3%",
            "expected_return": "8.2%",
            "volatility": "12.1%",
            "context_note_historical": "return/volatility are historical",
        },
        required_keys=("holdings", "current_weights", "health_score", "sharpe_ratio", "max_drawdown"),
        answer_must_contain=("78.5", "VTI"),
    ),
    ValidationScenario(
        name="Investment Rebalance",
        source_app="investment",
        source_page="Rebalance",
        question="Should I rebalance now?",
        context={
            "rebalance_drift": {"VTI": "+5.0pp", "BND": "-5.0pp"},
            "target_weights": {"VTI": "55%", "BND": "45%"},
            "current_weights": {"VTI": "60.0%", "BND": "40.0%"},
            "health_score": 72,
        },
        required_keys=("rebalance_drift", "target_weights", "current_weights"),
        answer_must_contain=("72",),
    ),
    ValidationScenario(
        name="Investment Macro",
        source_app="investment",
        source_page="Macro Outlook",
        question="How does recession risk affect my portfolio?",
        context={
            "macro_outlook": "Recession probability 25%; rates stable",
            "context_note_forward": "Macro outlook affects forward projections",
            "context_note_historical": "expected_return/volatility are historical",
            "health_score": 75,
        },
        required_keys=("macro_outlook", "context_note_forward", "context_note_historical"),
        answer_must_contain=("forward", "historical"),
    ),
)


def run_all_validations() -> list[ValidationResult]:
    return [run_validation_scenario(s) for s in VALIDATION_SCENARIOS]
