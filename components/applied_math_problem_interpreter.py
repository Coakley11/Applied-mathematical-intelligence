"""Layered problem interpretation: intent → entities → data → model selection."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from components.applied_math_question_intent import QuestionIntent, classify_question_intent

# Math-purpose taxonomy (Layer 1) — maps to solvers, not exact phrases.
PURPOSE_COMPARE = "compare"
PURPOSE_FORECAST = "forecast"
PURPOSE_EXPLAIN_WHY = "explain_why"
PURPOSE_EVALUATE_RISK = "evaluate_risk"
PURPOSE_TEST_SIGNIFICANCE = "test_significance"
PURPOSE_DECIDE = "decide"
PURPOSE_ESTIMATE_RATE = "estimate_rate"
PURPOSE_MEASURE_SENSITIVITY = "measure_sensitivity"
PURPOSE_CHECK_REALISM = "check_realism"
PURPOSE_ATTRIBUTE = "attribute"
PURPOSE_ESTIMATE_PROBABILITY = "estimate_probability"

PURPOSE_LABELS: dict[str, str] = {
    PURPOSE_COMPARE: "Compare (who is better today)",
    PURPOSE_FORECAST: "Forecast (future accumulation / will it happen)",
    PURPOSE_EXPLAIN_WHY: "Explain why (cause / attribution)",
    PURPOSE_EVALUATE_RISK: "Evaluate risk (return vs volatility)",
    PURPOSE_TEST_SIGNIFICANCE: "Test significance (signal vs noise)",
    PURPOSE_DECIDE: "Decide (should I / threshold)",
    PURPOSE_ESTIMATE_RATE: "Estimate required rate",
    PURPOSE_MEASURE_SENSITIVITY: "Measure sensitivity (what if)",
    PURPOSE_CHECK_REALISM: "Check realism (projection sanity)",
    PURPOSE_ATTRIBUTE: "Attribute contribution (drawdown / exposure)",
    PURPOSE_ESTIMATE_PROBABILITY: "Estimate probability (reasonableness)",
}

# User-facing problem-type correction options → internal purpose
CORRECTION_OPTIONS: dict[str, str] = {
    "Auto (detect from question)": "",
    "Comparison": PURPOSE_COMPARE,
    "Projection / forecast": PURPOSE_FORECAST,
    "Trend significance": PURPOSE_TEST_SIGNIFICANCE,
    "Risk / return": PURPOSE_EVALUATE_RISK,
    "Decision (should I)": PURPOSE_DECIDE,
    "Probability": PURPOSE_ESTIMATE_PROBABILITY,
    "Attribution (why)": PURPOSE_ATTRIBUTE,
    "Scenario (what if)": PURPOSE_MEASURE_SENSITIVITY,
    "Required rate": PURPOSE_ESTIMATE_RATE,
    "Projection realism": PURPOSE_CHECK_REALISM,
}

MODEL_INFO: dict[str, dict[str, str]] = {
    "baseball_future_accumulation": {
        "name": "Future accumulation comparison",
        "why": "The question is about **future totals over time**, not who is better in a single season.",
        "variables": "future total = rate per season × seasons remaining (with optional decline)",
    },
    "baseball_player_comparison": {
        "name": "Weighted stat comparison",
        "why": "The question compares **present production** on attached stats.",
        "variables": "score = weighted share of stats for each player",
    },
    "baseball_trend_significance": {
        "name": "Trend significance (slope vs R²)",
        "why": "The question asks whether a trend is **real or noise**.",
        "variables": "meaningful if |slope| and R² exceed thresholds",
    },
    "baseball_projection_realism": {
        "name": "Projection realism check",
        "why": "The question asks if a **forecast is believable** vs baselines.",
        "variables": "gap% = (projection − baseline) ÷ baseline",
    },
    "nba_stat_chase": {
        "name": "Rate-needed chase",
        "why": "The question is whether a player **will reach a target** at a given pace.",
        "variables": "required rate = gap ÷ games remaining",
    },
    "nba_inverse_stat_chase": {
        "name": "Inverse rate (games needed)",
        "why": "The question asks **how many games** are needed at an expected pace.",
        "variables": "games needed = ceil(gap ÷ expected rate)",
    },
    "nba_win_probability": {
        "name": "Probability reasonableness",
        "why": "The question asks if a **quoted probability is believable**.",
        "variables": "edge band from win probability %",
    },
    "investment_rebalance": {
        "name": "Drift threshold decision",
        "why": "The question is **should I rebalance** vs a drift threshold.",
        "variables": "rebalance if max |drift| ≥ threshold",
    },
    "investment_risk_return": {
        "name": "Risk-return tradeoff",
        "why": "The question is whether **return is worth the volatility**.",
        "variables": "Sharpe ≈ return ÷ volatility vs your floors",
    },
    "investment_concentration": {
        "name": "Concentration (HHI / top weights)",
        "why": "The question is about **portfolio concentration / diversification**.",
        "variables": "HHI = Σ weight²; top-3 sum vs limits",
    },
    "investment_drawdown_attribution": {
        "name": "Drawdown attribution",
        "why": "The question asks **why** a holding contributes to drawdown risk.",
        "variables": "contribution ≈ weight × decline × correlation",
    },
    "investment_macro_sensitivity": {
        "name": "Scenario stress test",
        "why": "The question is **what if** macro assumptions change.",
        "variables": "stressed return/vol = base + shock",
    },
    "baseball_draft_decision": {
        "name": "Draft value edge",
        "why": "The question is whether a pick is **worth it, fair, or a reach** vs ADP.",
        "variables": "rank_edge = ADP − current_pick",
    },
    "nba_matchup_edge": {
        "name": "Matchup edge score",
        "why": "The question asks whether the **matchup advantage is meaningful** vs probability and injuries.",
        "variables": "edge_score = prob_edge + stat_edge − injury_penalty",
    },
    "generic_interactive": {
        "name": "Interactive partial model",
        "why": "No exact solver matched, but we can still model the closest problem with your assumptions.",
        "variables": "depends on detected purpose",
    },
}


def _has_value(val: Any) -> bool:
    if val is None or val == "":
        return False
    if isinstance(val, (list, dict)) and not val:
        return False
    return True


def _intent_to_purpose(intent: QuestionIntent, question: str) -> str:
    low = question.lower()
    mapping = {
        "why": PURPOSE_EXPLAIN_WHY if "drawdown" not in low else PURPOSE_ATTRIBUTE,
        "what_if": PURPOSE_MEASURE_SENSITIVITY,
        "should_i": PURPOSE_DECIDE,
        "who_is_better": PURPOSE_COMPARE,
        "will_this_happen": PURPOSE_FORECAST,
        "is_this_meaningful": PURPOSE_TEST_SIGNIFICANCE,
    }
    if intent.intent_id == "why" and ("drawdown" in low or "expos" in low):
        return PURPOSE_ATTRIBUTE
    if "probability" in low or "believable" in low or "reasonable" in low:
        return PURPOSE_ESTIMATE_PROBABILITY
    if "how many games" in low or "rate" in low and "need" in low:
        return PURPOSE_ESTIMATE_RATE
    if "realistic" in low or "aggressive" in low or "believable" in low and "project" in low:
        return PURPOSE_CHECK_REALISM
    if "risk" in low and "worth" in low:
        return PURPOSE_EVALUATE_RISK
    return mapping.get(intent.intent_id, PURPOSE_COMPARE)


def _extract_entities(question: str, ctx: dict[str, Any]) -> dict[str, Any]:
    low = question.lower()
    entities: dict[str, Any] = {
        "player_a": ctx.get("player_a") or ctx.get("player"),
        "player_b": ctx.get("player_b"),
        "team": ctx.get("team"),
        "opponent": ctx.get("opponent"),
        "holdings": ctx.get("holdings"),
        "page": ctx.get("page") or ctx.get("source_page"),
        "workflow": ctx.get("workflow"),
    }
    intent = classify_question_intent(question)
    entities["horizon"] = intent.horizon
    entities["focus_stat"] = intent.focus_stat
    entities["attribution_target"] = intent.attribution_target
    # Tickers mentioned in question
    for t in re.findall(r"\b[A-Z]{2,5}\b", question):
        if t not in ("WHY", "NBA", "MLB", "ETF"):
            entities.setdefault("tickers", []).append(t)
    if "stat_gap" in ctx and isinstance(ctx["stat_gap"], dict):
        sg = ctx["stat_gap"]
        entities["target_value"] = sg.get("target_value")
        entities["current_value"] = sg.get("current_value")
        entities["gap"] = sg.get("gap")
    return {k: v for k, v in entities.items() if v}


def _audit_context(ctx: dict[str, Any], purpose: str) -> tuple[list[str], list[str], list[str]]:
    """Return (relevant, missing, secondary) context field labels."""
    relevant: list[str] = []
    missing: list[str] = []
    secondary: list[str] = []

    checks: list[tuple[str, str, bool]] = []
    if purpose in (PURPOSE_FORECAST, PURPOSE_COMPARE):
        checks = [
            ("player_a", "player A", True),
            ("player_b", "player B", True),
            ("_ami_comparison_context", "comparison stats", True),
            ("comparison_stats", "comparison stats", False),
            ("trend_summary", "trend data", False),
        ]
    elif purpose == PURPOSE_TEST_SIGNIFICANCE:
        checks = [
            ("trend_summary.slope", "trend slope", True),
            ("trend_summary.r2", "trend R²", True),
            ("player", "player", False),
        ]
    elif purpose == PURPOSE_ATTRIBUTE:
        checks = [
            ("current_weights", "portfolio weights", True),
            ("max_drawdown", "max drawdown", False),
        ]
    elif purpose == PURPOSE_DECIDE and "rebalance" in str(ctx.get("question", "")).lower():
        checks = [("rebalance_drift", "rebalance drift", True)]
    elif purpose == PURPOSE_EVALUATE_RISK:
        checks = [
            ("expected_return", "expected return", True),
            ("volatility", "volatility", True),
        ]
    elif purpose == PURPOSE_ESTIMATE_RATE:
        checks = [
            ("stat_gap.gap", "stat gap", True),
            ("stat_gap", "stat gap", False),
        ]
    elif purpose == PURPOSE_MEASURE_SENSITIVITY:
        checks = [
            ("expected_return", "return", False),
            ("macro_outlook", "macro outlook", False),
        ]

    for key, label, required in checks:
        if "." in key:
            parts = key.split(".")
            cur: Any = ctx
            for p in parts:
                cur = cur.get(p) if isinstance(cur, dict) else None
            val = cur
        else:
            val = ctx.get(key)
        if _has_value(val):
            relevant.append(label)
        elif required:
            missing.append(label)
        else:
            secondary.append(label)

    # Keys to ignore for display
    ignore = {"source_app", "suite_cloud_state", "question"}
    return relevant, missing, [k for k in ctx if k not in ignore and k not in relevant][:6]


def _select_model(source_app: str, purpose: str, ctx: dict[str, Any], question: str) -> str:
    app = source_app.lower()
    low = question.lower()

    if "baseball" in app:
        if purpose == PURPOSE_FORECAST:
            return "baseball_future_accumulation"
        if purpose == PURPOSE_TEST_SIGNIFICANCE:
            return "baseball_trend_significance"
        if purpose == PURPOSE_CHECK_REALISM:
            return "baseball_projection_realism"
        if purpose == PURPOSE_COMPARE:
            return "baseball_player_comparison"
        if purpose == PURPOSE_DECIDE and "draft" in low:
            return "baseball_draft_decision"
        if "trend" in low:
            return "baseball_trend_significance"
        if _has_value(ctx.get("player_a")) and _has_value(ctx.get("player_b")):
            if purpose == PURPOSE_FORECAST or classify_question_intent(question).horizon:
                return "baseball_future_accumulation"
            return "baseball_player_comparison"
        return "baseball_generic"

    if "nba" in app:
        if purpose == PURPOSE_ESTIMATE_RATE or "how many games" in low:
            return "nba_inverse_stat_chase"
        if purpose == PURPOSE_FORECAST or purpose == PURPOSE_ESTIMATE_RATE:
            if "games" in low:
                return "nba_inverse_stat_chase"
        if purpose == PURPOSE_ESTIMATE_PROBABILITY:
            return "nba_win_probability"
        if _has_value(ctx.get("stat_gap")):
            return "nba_stat_chase"
        if "matchup" in low or _has_value(ctx.get("matchup_advantages")):
            return "nba_matchup_edge"
        return "nba_generic"

    if "investment" in app:
        if purpose == PURPOSE_ATTRIBUTE:
            return "investment_drawdown_attribution"
        if purpose == PURPOSE_MEASURE_SENSITIVITY:
            return "investment_macro_sensitivity"
        if purpose == PURPOSE_DECIDE and "rebalance" in low:
            return "investment_rebalance"
        if purpose == PURPOSE_EVALUATE_RISK:
            return "investment_risk_return"
        if "concentrat" in low or "diversif" in low:
            return "investment_concentration"
        if "drawdown" in low and purpose == PURPOSE_EXPLAIN_WHY:
            return "investment_drawdown_attribution"
        if _has_value(ctx.get("rebalance_drift")):
            return "investment_rebalance"
        return "investment_generic"

    return "generic_interactive"


def _solvability(relevant: list[str], missing: list[str]) -> str:
    if not missing:
        return "exact"
    if relevant and len(missing) <= 2:
        return "approximate"
    return "partial"


def _build_restatement(question: str, intent: QuestionIntent, purpose: str, entities: dict[str, Any]) -> str:
    try:
        from components.draft_market_question import draft_question_restatement

        draft_rest = draft_question_restatement(question)
        if draft_rest:
            return draft_rest
    except ImportError:
        pass
    pa = entities.get("player_a") or "Player A"
    pb = entities.get("player_b") or "Player B"
    stat = entities.get("focus_stat") or "the stat"
    horizon = entities.get("horizon") or intent.horizon
    ticker = entities.get("attribution_target") or (entities.get("tickers") or [None])[0]

    if purpose == PURPOSE_FORECAST and pa and pb:
        h = f" over **{horizon}**" if horizon else " over the coming seasons"
        return f"You're asking whether **{pa}** is likely to accumulate more **{stat}** than **{pb}**{h}."
    if purpose == PURPOSE_ATTRIBUTE and ticker:
        return f"You're asking **why {ticker}** contributes to portfolio drawdown risk — cause first, not stress-test first."
    if purpose == PURPOSE_COMPARE and pa and pb:
        return f"You're asking who is **better today** on attached stats: **{pa}** vs **{pb}**."
    if purpose == PURPOSE_TEST_SIGNIFICANCE:
        return f"You're asking whether the **{stat or 'trend'}** is statistically meaningful vs noise."
    if purpose == PURPOSE_DECIDE:
        return "You're asking for a **decision** — action vs wait, against a threshold or value."
    if purpose == PURPOSE_MEASURE_SENSITIVITY:
        return "You're asking **what changes** if assumptions shift — scenario / sensitivity analysis."
    if purpose == PURPOSE_ESTIMATE_PROBABILITY:
        return "You're asking whether a **quoted probability is reasonable** for the setup."
    if purpose == PURPOSE_ESTIMATE_RATE:
        return "You're asking **what rate or how many periods** are needed to reach a target."
    if purpose == PURPOSE_EVALUATE_RISK:
        return "You're asking whether **return is worth the risk** at your tolerance."
    if purpose == PURPOSE_CHECK_REALISM:
        return "You're asking whether a **projection is realistic** vs recent and career baselines."
    return intent.restatement or "You're asking a quantitative question about the data on this page."


@dataclass
class ProblemInterpretation:
    question: str
    source_app: str
    intent: QuestionIntent
    math_purpose: str
    purpose_label: str
    restatement: str
    entities: dict[str, Any] = field(default_factory=dict)
    data_relevant: list[str] = field(default_factory=list)
    data_missing: list[str] = field(default_factory=list)
    data_secondary: list[str] = field(default_factory=list)
    model_id: str = ""
    model_name: str = ""
    model_rationale: str = ""
    model_variables: str = ""
    solvability: str = "partial"
    confidence: float = 0.5


def interpret_suite_question(
    question: str,
    *,
    source_app: str = "",
    context: dict[str, Any] | None = None,
    purpose_override: str = "",
) -> ProblemInterpretation:
    """Run Layers 1–4: intent, entities, data matching, model selection."""
    ctx = dict(context or {})
    q = (question or "").strip()
    intent = classify_question_intent(q)
    purpose = purpose_override or _intent_to_purpose(intent, q)
    entities = _extract_entities(q, ctx)
    relevant, missing, secondary = _audit_context(ctx, purpose)
    model_id = _select_model(source_app, purpose, ctx, q)
    info = MODEL_INFO.get(model_id, MODEL_INFO["generic_interactive"])
    solv = _solvability(relevant, missing)
    restatement = _build_restatement(q, intent, purpose, entities)

    conf = intent.confidence
    if missing:
        conf = max(0.35, conf - 0.08 * len(missing))
    if relevant:
        conf = min(0.95, conf + 0.05)

    return ProblemInterpretation(
        question=q,
        source_app=source_app,
        intent=intent,
        math_purpose=purpose,
        purpose_label=PURPOSE_LABELS.get(purpose, purpose),
        restatement=restatement,
        entities=entities,
        data_relevant=relevant,
        data_missing=missing,
        data_secondary=secondary,
        model_id=model_id,
        model_name=info["name"],
        model_rationale=info["why"],
        model_variables=info.get("variables", ""),
        solvability=solv,
        confidence=conf,
    )


def purpose_override_to_model_id(source_app: str, purpose: str) -> str:
    """Map correction-menu purpose to a model id for re-routing."""
    ctx: dict[str, Any] = {}
    return _select_model(source_app, purpose, ctx, "")
