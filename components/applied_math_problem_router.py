"""Classify suite Applied Math questions into solvable problem types."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Stable IDs consumed by solvers and tests.
NBA_STAT_CHASE = "nba_stat_chase"
NBA_INVERSE_STAT_CHASE = "nba_inverse_stat_chase"
NBA_WIN_PROBABILITY = "nba_win_probability"
NBA_MATCHUP_EDGE = "nba_matchup_edge"
NBA_LEGACY_COMPARISON = "nba_legacy_comparison"
NBA_GENERIC = "nba_generic"

BASEBALL_TREND = "baseball_trend_significance"
BASEBALL_PLAYER_COMPARE = "baseball_player_comparison"
BASEBALL_HISTORICAL = "baseball_historical_comparison"
BASEBALL_DRAFT = "baseball_draft_decision"
BASEBALL_PROJECTION = "baseball_projection_realism"
BASEBALL_GENERIC = "baseball_generic"

INVESTMENT_REBALANCE = "investment_rebalance"
INVESTMENT_RISK_RETURN = "investment_risk_return"
INVESTMENT_CONCENTRATION = "investment_concentration"
INVESTMENT_MACRO = "investment_macro_sensitivity"
INVESTMENT_GENERIC = "investment_generic"

GENERIC_FALLBACK = "generic_fallback"

FIELD_SPECS: dict[str, tuple[str, ...]] = {
    NBA_STAT_CHASE: (
        "stat_gap.gap",
        "stat_gap.current_value",
        "stat_gap.target_value",
        "stat_gap.games_remaining",
    ),
    BASEBALL_TREND: ("trend_summary.slope", "trend_summary.r2", "player", "metrics"),
    INVESTMENT_REBALANCE: ("rebalance_drift",),
    INVESTMENT_RISK_RETURN: ("expected_return", "volatility"),
}


# Tokens that must match as whole words (avoid "rate" inside "concentrated").
_WHOLE_WORD_TOPICS: frozenset[str] = frozenset({"rate"})


def _contains_term(text: str, term: str) -> bool:
    low = text.lower()
    if term in _WHOLE_WORD_TOPICS:
        return bool(re.search(rf"\b{re.escape(term)}\b", low))
    return term in low


def _topics(question: str) -> set[str]:
    low = question.lower()
    out: set[str] = set()
    keys = {
        "trend": ("trend", "slope", "declin", "improv", "significant", "meaningful"),
        "compare": ("compare", "better", " vs ", "versus", "value", "pass"),
        "draft": ("draft", "round", "pick", "wait"),
        "probability": ("probability", "percent", "odds", "chance", "likely", "win"),
        "rebalance": ("rebalance", "allocat", "drift", "weight"),
        "risk": ("risk", "volatil", "concentration", "diversif", "sharpe", "drawdown", "worth"),
        "macro": ("recession", "macro", "rate", "inflation"),
        "record": ("record", "rebound", "pass", "catch", "overtake"),
        "projection": ("project", "realistic", "believable", "breakout", "forecast"),
    }
    for name, words in keys.items():
        if any(_contains_term(low, w) for w in words):
            out.add(name)
    return out


def _has_value(val: Any) -> bool:
    if val is None or val == "":
        return False
    if isinstance(val, (list, dict)) and not val:
        return False
    return True


def _nested_get(ctx: dict[str, Any], path: str) -> Any:
    parts = path.split(".")
    cur: Any = ctx
    for part in parts:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _audit_fields(ctx: dict[str, Any], required: tuple[str, ...]) -> tuple[list[str], list[str]]:
    available: list[str] = []
    missing: list[str] = []
    for path in required:
        if _has_value(_nested_get(ctx, path) if "." in path else ctx.get(path)):
            available.append(path)
        else:
            missing.append(path)
    return available, missing


@dataclass
class ProblemRoute:
    problem_type_id: str
    problem_type: str
    confidence: float
    source_app: str
    required_fields: list[str] = field(default_factory=list)
    available_fields: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)


def route_suite_question(
    question: str,
    *,
    source_app: str = "",
    context: dict[str, Any] | None = None,
) -> ProblemRoute:
    ctx = dict(context or {})
    app = str(source_app or ctx.get("source_app") or "").strip().lower()
    topics = _topics(question)
    workflow = str(ctx.get("workflow") or "").lower()
    page = str(ctx.get("page") or "").lower()
    low = question.lower()

    if "baseball" in app:
        return _route_baseball(question, ctx, topics, workflow, page)
    if "nba" in app:
        return _route_nba(question, ctx, topics, workflow, low)
    if "investment" in app:
        return _route_investment(question, ctx, topics, low)
    return ProblemRoute(
        problem_type_id=GENERIC_FALLBACK,
        problem_type="Quantitative decision (generic)",
        confidence=0.3,
        source_app=app or "unknown",
        required_fields=["question"],
        available_fields=["question"] if question.strip() else [],
        missing_fields=[] if question.strip() else ["question"],
    )


def _route_baseball(
    question: str,
    ctx: dict[str, Any],
    topics: set[str],
    workflow: str,
    page: str,
) -> ProblemRoute:
    if "trend" in topics or "trend" in workflow:
        req = FIELD_SPECS[BASEBALL_TREND]
        avail, miss = _audit_fields(ctx, req)
        conf = 0.9 if not miss else 0.55 if avail else 0.4
        return ProblemRoute(
            problem_type_id=BASEBALL_TREND,
            problem_type="Trend significance",
            confidence=conf,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if "compare" in topics or "comparison" in workflow:
        req = ("player_a", "player_b", "comparison_stats")
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=BASEBALL_PLAYER_COMPARE,
            problem_type="Player comparison",
            confidence=0.75 if avail else 0.45,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    snap = ctx.get("historical_snapshot")
    if isinstance(snap, dict) and snap and ("historical" in page or snap.get("top_rows")):
        req = ("historical_snapshot.top_rows", "player")
        avail, miss = _audit_fields(ctx, ("historical_snapshot", "player"))
        return ProblemRoute(
            problem_type_id=BASEBALL_HISTORICAL,
            problem_type="Historical stat comparison",
            confidence=0.8 if avail else 0.5,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if "draft" in topics or "draft" in workflow:
        req = ("player", "draft_projection")
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=BASEBALL_DRAFT,
            problem_type="Draft decision",
            confidence=0.65 if avail else 0.4,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    proj = ctx.get("projection")
    if "projection" in topics or (isinstance(proj, dict) and proj):
        req = ("player", "projection")
        avail, miss = _audit_fields(ctx, ("player", "projection"))
        if not isinstance(proj, dict):
            miss = list(miss) + ["projection"]
        return ProblemRoute(
            problem_type_id=BASEBALL_PROJECTION,
            problem_type="Projection realism",
            confidence=0.72 if not miss else 0.48,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    return ProblemRoute(
        problem_type_id=BASEBALL_GENERIC,
        problem_type="Baseball decision analysis",
        confidence=0.35,
        source_app="baseball",
        required_fields=["player", "metrics"],
        available_fields=[k for k in ("player", "metrics") if _has_value(ctx.get(k))],
        missing_fields=[k for k in ("player", "metrics") if not _has_value(ctx.get(k))],
    )


def _route_nba(
    question: str,
    ctx: dict[str, Any],
    topics: set[str],
    workflow: str,
    low: str,
) -> ProblemRoute:
    chase_words = ("pass", "rebound", "record", "catch", "overtake", "reach")
    inverse_phrases = (
        "how many games",
        "games would",
        "games does",
        "games needed",
        "games to pass",
        "games to catch",
    )
    has_gap = isinstance(ctx.get("stat_gap"), dict) and _has_value(ctx.get("stat_gap"))
    if any(p in low for p in inverse_phrases) and (has_gap or "record" in topics):
        req = FIELD_SPECS[NBA_STAT_CHASE]
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=NBA_INVERSE_STAT_CHASE,
            problem_type="NBA inverse stat chase (games needed)",
            confidence=0.88 if has_gap else 0.55,
            source_app="nba",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if "record" in topics or any(w in low for w in chase_words):
        req = FIELD_SPECS[NBA_STAT_CHASE]
        avail, miss = _audit_fields(ctx, req)
        gap = ctx.get("stat_gap")
        if isinstance(gap, dict) and _has_value(gap.get("gap")):
            conf = 0.92 if len(miss) <= 1 else 0.7
        else:
            conf = 0.5 if "record" in topics else 0.45
        return ProblemRoute(
            problem_type_id=NBA_STAT_CHASE,
            problem_type="NBA stat chase / rate needed",
            confidence=conf,
            source_app="nba",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    matchup_adv = ctx.get("matchup_advantages")
    if "matchup" in workflow or (isinstance(matchup_adv, list) and matchup_adv):
        req = ("team", "opponent", "matchup_advantages")
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=NBA_MATCHUP_EDGE,
            problem_type="Matchup edge",
            confidence=0.78 if avail else 0.5,
            source_app="nba",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if "probability" in topics or ctx.get("win_probability") or ctx.get("series_probability"):
        req = ("win_probability", "team")
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=NBA_WIN_PROBABILITY,
            problem_type="Win probability reasonableness",
            confidence=0.72 if avail else 0.48,
            source_app="nba",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if ctx.get("stat_gap") or ctx.get("historical_comparison"):
        req = ("stat_gap",)
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=NBA_LEGACY_COMPARISON,
            problem_type="Legacy / historical comparison",
            confidence=0.7 if avail else 0.45,
            source_app="nba",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    return ProblemRoute(
        problem_type_id=NBA_GENERIC,
        problem_type="NBA quantitative decision",
        confidence=0.35,
        source_app="nba",
        required_fields=["team", "player"],
        available_fields=[k for k in ("team", "player") if _has_value(ctx.get(k))],
        missing_fields=[k for k in ("team", "player") if not _has_value(ctx.get(k))],
    )


def _route_investment(
    question: str,
    ctx: dict[str, Any],
    topics: set[str],
    low: str,
) -> ProblemRoute:
    if "rebalance" in topics or "rebalance" in low:
        req = FIELD_SPECS[INVESTMENT_REBALANCE]
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=INVESTMENT_REBALANCE,
            problem_type="Rebalance decision",
            confidence=0.88 if not miss else 0.55,
            source_app="investment",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if (
        "concentration" in low
        or "concentrated" in low
        or "diversified" in low
        or "diversification" in low
        or "too heavy" in low
    ):
        req = ("holdings", "current_weights")
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=INVESTMENT_CONCENTRATION,
            problem_type="Portfolio concentration",
            confidence=0.65 if avail else 0.4,
            source_app="investment",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if "macro" in topics or ctx.get("macro_outlook") or ctx.get("macro_summary"):
        req = ("macro_outlook", "expected_return", "volatility")
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=INVESTMENT_MACRO,
            problem_type="Macro sensitivity",
            confidence=0.7 if avail else 0.45,
            source_app="investment",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    risk_words = ("volatil", "sharpe", "drawdown", "worth", "risk", "return")
    has_metrics = _has_value(ctx.get("expected_return")) and _has_value(ctx.get("volatility"))
    if "risk" in topics or any(w in low for w in risk_words) or has_metrics:
        req = FIELD_SPECS[INVESTMENT_RISK_RETURN]
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=INVESTMENT_RISK_RETURN,
            problem_type="Risk-return tradeoff",
            confidence=0.85 if not miss else 0.55,
            source_app="investment",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    return ProblemRoute(
        problem_type_id=INVESTMENT_GENERIC,
        problem_type="Portfolio analysis",
        confidence=0.4,
        source_app="investment",
        required_fields=["holdings", "health_score"],
        available_fields=[k for k in ("holdings", "health_score") if _has_value(ctx.get(k))],
        missing_fields=[k for k in ("holdings", "health_score") if not _has_value(ctx.get(k))],
    )
