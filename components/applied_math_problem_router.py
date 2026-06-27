"""Classify suite Applied Math questions into solvable problem types."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from components.applied_math_question_intent import (
    INTENT_IS_MEANINGFUL,
    INTENT_SHOULD_I,
    INTENT_WHAT_IF,
    INTENT_WHY,
    INTENT_WILL_HAPPEN,
    INTENT_WHO_IS_BETTER,
    QuestionIntent,
    classify_question_intent,
)
from components.applied_math_problem_interpreter import (
    PURPOSE_ATTRIBUTE,
    PURPOSE_FORECAST,
    ProblemInterpretation,
    interpret_suite_question,
)
from components.draft_market_question import (
    is_draft_head_to_head_question,
    is_draft_market_prediction_question,
    is_draft_review_question,
    is_draft_timing_question,
    is_player_explanation_question,
    is_position_best_available_question,
    is_roster_needs_question,
)

# Stable IDs consumed by solvers and tests.
NBA_STAT_CHASE = "nba_stat_chase"
NBA_INVERSE_STAT_CHASE = "nba_inverse_stat_chase"
NBA_WIN_PROBABILITY = "nba_win_probability"
NBA_MATCHUP_EDGE = "nba_matchup_edge"
NBA_LEGACY_COMPARISON = "nba_legacy_comparison"
NBA_GENERIC = "nba_generic"

BASEBALL_TREND = "baseball_trend_significance"
BASEBALL_PLAYER_COMPARE = "baseball_player_comparison"
BASEBALL_FUTURE_ACCUMULATION = "baseball_future_accumulation"
BASEBALL_HISTORICAL = "baseball_historical_comparison"
BASEBALL_DRAFT = "baseball_draft_decision"
BASEBALL_PROJECTION = "baseball_projection_realism"
BASEBALL_VALUATION = "baseball_valuation"
BASEBALL_HOF_CASE = "baseball_hof_case"
BASEBALL_GENERIC = "baseball_generic"

INVESTMENT_REBALANCE = "investment_rebalance"
INVESTMENT_RISK_RETURN = "investment_risk_return"
INVESTMENT_CONCENTRATION = "investment_concentration"
INVESTMENT_DRAWDOWN_ATTRIBUTION = "investment_drawdown_attribution"
INVESTMENT_MACRO = "investment_macro_sensitivity"
INVESTMENT_GENERIC = "investment_generic"

GENERIC_FALLBACK = "generic_fallback"
GENERIC_INTERACTIVE = "generic_interactive"

MUSIC_PRACTICE_PLAN = "music_practice_plan"
MUSIC_SECTION_FOCUS = "music_section_focus"
MUSIC_CHORD_TRANSITION = "music_chord_transition"
MUSIC_TEMPO_KEY = "music_tempo_key"
MUSIC_BACKING_TRACK = "music_backing_track"
MUSIC_SKILL_TECHNIQUE = "music_skill_technique"
MUSIC_GENERIC = "music_generic"

_MUSIC_INTENT_TO_PID: dict[str, str] = {
    "practice_plan": MUSIC_PRACTICE_PLAN,
    "chord_transition": MUSIC_CHORD_TRANSITION,
    "section_focus": MUSIC_SECTION_FOCUS,
    "tempo_key": MUSIC_TEMPO_KEY,
    "backing_track": MUSIC_BACKING_TRACK,
    "skill_technique": MUSIC_SKILL_TECHNIQUE,
    "difficulty": MUSIC_SKILL_TECHNIQUE,
}

_MUSIC_PID_LABELS: dict[str, str] = {
    MUSIC_PRACTICE_PLAN: "Music practice plan",
    MUSIC_SECTION_FOCUS: "Music section focus",
    MUSIC_CHORD_TRANSITION: "Music chord transitions",
    MUSIC_TEMPO_KEY: "Music tempo & key",
    MUSIC_BACKING_TRACK: "Music backing track practice",
    MUSIC_SKILL_TECHNIQUE: "Music technique & readiness",
    MUSIC_GENERIC: "Music practice coaching",
}

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


MODEL_ID_TO_ROUTE: dict[str, tuple[str, str, tuple[str, ...]]] = {
    BASEBALL_FUTURE_ACCUMULATION: ("Future stat accumulation forecast", "baseball", ("player_a", "player_b")),
    BASEBALL_PLAYER_COMPARE: ("Player comparison", "baseball", ("player_a", "player_b")),
    BASEBALL_TREND: ("Trend significance", "baseball", FIELD_SPECS[BASEBALL_TREND]),
    BASEBALL_HISTORICAL: ("Historical stat comparison", "baseball", ("historical_snapshot", "player")),
    BASEBALL_DRAFT: ("Draft decision", "baseball", ("draft_snapshot", "player", "draft_projection")),
    BASEBALL_PROJECTION: ("Projection realism", "baseball", ("player", "projection")),
    BASEBALL_VALUATION: ("Player valuation", "baseball", ("valuation_snapshot", "player")),
    BASEBALL_HOF_CASE: ("Hall of Fame statistical case", "baseball", ("hof_case_packet", "player")),
    BASEBALL_GENERIC: ("Baseball decision analysis", "baseball", ("player", "metrics")),
    NBA_STAT_CHASE: ("NBA stat chase / rate needed", "nba", FIELD_SPECS[NBA_STAT_CHASE]),
    NBA_INVERSE_STAT_CHASE: ("NBA inverse stat chase (games needed)", "nba", FIELD_SPECS[NBA_STAT_CHASE]),
    NBA_WIN_PROBABILITY: ("Win probability reasonableness", "nba", ("win_probability", "team")),
    NBA_MATCHUP_EDGE: ("Matchup edge", "nba", ("team", "opponent", "matchup_advantages")),
    NBA_LEGACY_COMPARISON: ("Legacy / historical comparison", "nba", ("stat_gap",)),
    NBA_GENERIC: ("NBA quantitative decision", "nba", ("team", "player")),
    INVESTMENT_REBALANCE: ("Rebalance decision", "investment", FIELD_SPECS[INVESTMENT_REBALANCE]),
    INVESTMENT_RISK_RETURN: ("Risk-return tradeoff", "investment", FIELD_SPECS[INVESTMENT_RISK_RETURN]),
    INVESTMENT_CONCENTRATION: ("Portfolio concentration", "investment", ("holdings", "current_weights")),
    INVESTMENT_DRAWDOWN_ATTRIBUTION: ("Drawdown risk attribution", "investment", ("current_weights",)),
    INVESTMENT_MACRO: ("Macro sensitivity", "investment", ("macro_outlook", "expected_return", "volatility")),
    INVESTMENT_GENERIC: ("Portfolio analysis", "investment", ("holdings", "health_score")),
    MUSIC_PRACTICE_PLAN: ("Music practice plan", "music", ("instrument", "song", "question")),
    MUSIC_SECTION_FOCUS: ("Music section focus", "music", ("practice_focus_section", "song")),
    MUSIC_CHORD_TRANSITION: ("Music chord transitions", "music", ("instrument", "song")),
    MUSIC_TEMPO_KEY: ("Music tempo & key", "music", ("display_key", "bpm")),
    MUSIC_BACKING_TRACK: ("Music backing track practice", "music", ("practice_focus_section",)),
    MUSIC_SKILL_TECHNIQUE: ("Music technique coaching", "music", ("instrument", "level")),
    MUSIC_GENERIC: ("Music practice coaching", "music", ("question",)),
    GENERIC_INTERACTIVE: ("Interactive partial model", "unknown", ("question",)),
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
        "sleeper": ("sleeper", "sleepers", "upside pick", "late round"),
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
    question_intent: str = ""
    intent_label: str = ""
    intent_restatement: str = ""
    math_purpose: str = ""
    purpose_label: str = ""
    model_name: str = ""
    model_rationale: str = ""
    model_variables: str = ""
    solvability: str = "partial"
    data_relevant: list[str] = field(default_factory=list)
    data_missing_interp: list[str] = field(default_factory=list)


def _with_intent(route: ProblemRoute, intent: QuestionIntent) -> ProblemRoute:
    route.question_intent = intent.intent_id
    route.intent_label = intent.label
    if not route.intent_restatement:
        route.intent_restatement = intent.restatement
    return route


def _attach_interpretation(route: ProblemRoute, interp: ProblemInterpretation) -> ProblemRoute:
    route = _with_intent(route, interp.intent)
    is_music = route.problem_type_id.startswith("music_")
    if not is_music:
        route.intent_restatement = interp.restatement
        route.math_purpose = interp.math_purpose
        route.purpose_label = interp.purpose_label
        route.model_name = interp.model_name
        route.model_rationale = interp.model_rationale
        route.model_variables = interp.model_variables
        route.solvability = interp.solvability
        route.data_relevant = list(interp.data_relevant)
        route.data_missing_interp = list(interp.data_missing)
    if interp.confidence > route.confidence and not is_music:
        route.confidence = interp.confidence
    return route


def _route_from_model_id(
    model_id: str,
    *,
    source_app: str,
    ctx: dict[str, Any],
    interp: ProblemInterpretation,
) -> ProblemRoute:
    spec = MODEL_ID_TO_ROUTE.get(model_id)
    if spec:
        label, default_app, req = spec
        avail, miss = _audit_fields(ctx, req)
        app = source_app or default_app
        conf = 0.75 if not miss else 0.5 if avail else 0.4
        if model_id == GENERIC_INTERACTIVE:
            conf = max(0.35, interp.confidence - 0.1)
        return ProblemRoute(
            problem_type_id=model_id,
            problem_type=label,
            confidence=conf,
            source_app=app,
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    return ProblemRoute(
        problem_type_id=GENERIC_INTERACTIVE,
        problem_type="Interactive partial model",
        confidence=0.35,
        source_app=source_app or "unknown",
        required_fields=["question"],
        available_fields=["question"] if interp.question else [],
        missing_fields=[] if interp.question else ["question"],
    )


def _route_aligns(domain: ProblemRoute, interp: ProblemInterpretation) -> bool:
    if domain.problem_type_id.endswith("_generic"):
        return False
    if domain.problem_type_id in (GENERIC_FALLBACK, GENERIC_INTERACTIVE):
        return False
    if domain.problem_type_id == interp.model_id:
        return True
    if domain.problem_type_id == BASEBALL_TREND:
        return True
    if interp.math_purpose == PURPOSE_FORECAST and domain.problem_type_id == BASEBALL_PLAYER_COMPARE:
        return False
    if interp.math_purpose == PURPOSE_ATTRIBUTE and domain.problem_type_id == INVESTMENT_MACRO:
        return False
    if interp.intent.intent_id == INTENT_WHY and domain.problem_type_id == INVESTMENT_MACRO:
        return False
    # Draft-market questions must not fall through to future accumulation via interpreter.
    if domain.problem_type_id == BASEBALL_DRAFT and domain.problem_type == "Draft market prediction":
        return True
    if domain.problem_type_id == BASEBALL_DRAFT and domain.problem_type == "Draft player compare":
        return True
    if domain.problem_type_id.startswith("music_"):
        return True
    return domain.confidence >= 0.65


def _route_music(question: str, ctx: dict[str, Any]) -> ProblemRoute:
    from components.music_ami_intent import detect_music_send_intent, minutes_from_question

    coach_page = str(ctx.get("coach_page") or ctx.get("source_page") or "").strip().lower()
    intent = detect_music_send_intent(question, coach_page, ctx)
    pid = _MUSIC_INTENT_TO_PID.get(intent, MUSIC_PRACTICE_PLAN)
    if intent == "music_general":
        low = question.lower()
        if any(p in low for p in ("practice", "song", "chorus", "verse", "chord", "tempo", "groove")):
            pid = MUSIC_PRACTICE_PLAN
    label = _MUSIC_PID_LABELS.get(pid, "Music practice coaching")
    avail, miss = _audit_fields(ctx, ("instrument", "song", "question"))
    if question.strip() and "question" not in avail:
        avail = list(avail) + ["question"]
    restatement = "You're asking for a **practice coaching plan** for your current song and session."
    parsed_minutes = minutes_from_question(question)
    if parsed_minutes is not None:
        restatement = (
            f"You're asking how to use **{parsed_minutes} minutes** of practice time on this song."
        )
    return ProblemRoute(
        problem_type_id=pid,
        problem_type=label,
        confidence=0.92,
        source_app="music",
        required_fields=["question"],
        available_fields=avail,
        missing_fields=miss,
        intent_restatement=restatement,
        math_purpose="practice_coaching",
        purpose_label="Music practice coaching",
        model_name=label,
        model_rationale=f"Music intent `{intent}` routed to {pid}.",
        solvability="approximate" if miss else "exact",
    )


def route_suite_question(
    question: str,
    *,
    source_app: str = "",
    context: dict[str, Any] | None = None,
    purpose_override: str = "",
) -> ProblemRoute:
    ctx = dict(context or {})
    app = str(source_app or ctx.get("source_app") or "").strip().lower()
    topics = _topics(question)
    workflow = str(ctx.get("workflow") or "").lower()
    page = str(ctx.get("page") or "").lower()
    source_page = str(ctx.get("source_page") or page or "").lower()
    low = question.lower()
    interp = interpret_suite_question(
        question,
        source_app=app,
        context=ctx,
        purpose_override=purpose_override,
    )

    if purpose_override:
        route = _route_from_model_id(
            interp.model_id,
            source_app=app,
            ctx=ctx,
            interp=interp,
        )
        return _attach_interpretation(route, interp)

    if "baseball" in app:
        domain = _route_baseball(question, ctx, topics, workflow, page, interp.intent, source_page=source_page)
    elif "nba" in app:
        domain = _route_nba(question, ctx, topics, workflow, low, interp.intent)
    elif "investment" in app:
        domain = _route_investment(question, ctx, topics, low, interp.intent)
    elif "music" in app or "music practice" in workflow:
        domain = _route_music(question, ctx)
    else:
        domain = ProblemRoute(
            problem_type_id=GENERIC_INTERACTIVE,
            problem_type="Interactive partial model",
            confidence=0.3,
            source_app=app or "unknown",
            required_fields=["question"],
            available_fields=["question"] if question.strip() else [],
            missing_fields=[] if question.strip() else ["question"],
        )

    if _route_aligns(domain, interp):
        route = domain
    elif interp.model_id in MODEL_ID_TO_ROUTE and not interp.model_id.endswith("_generic"):
        route = _route_from_model_id(interp.model_id, source_app=app, ctx=ctx, interp=interp)
    elif domain.problem_type_id.endswith("_generic") or domain.confidence < 0.5:
        route = _route_from_model_id(
            interp.model_id if interp.model_id != "baseball_generic" else GENERIC_INTERACTIVE,
            source_app=app,
            ctx=ctx,
            interp=interp,
        )
    else:
        route = domain

    route = _attach_interpretation(route, interp)
    _refine_baseball_restatement(route, ctx)
    return route


def _refine_baseball_restatement(route: ProblemRoute, ctx: dict[str, Any]) -> None:
    """Align the human-readable restatement with the final routed workflow.

    The interpreter restatement is computed before final routing and can lag the
    chosen workflow (e.g. say "who is better today" for an age-window historical
    question, or "trend projection" for a two-player comparison). Rewrite it so the
    displayed Interpretation matches what the solver will actually do.
    """
    pid = route.problem_type_id
    pa = str(ctx.get("player_a") or "").strip()
    pb = str(ctx.get("player_b") or "").strip()
    age = str(ctx.get("comparison_age_range") or "").strip()
    season = str(ctx.get("comparison_season_range") or "").strip()

    if pid == BASEBALL_HISTORICAL and pa and pb:
        if age:
            route.intent_restatement = (
                f"You're asking who was the better player between **{pa}** and **{pb}** "
                f"during the **ages {age}** window — an age-matched historical comparison."
            )
        elif season:
            route.intent_restatement = (
                f"You're asking who was better between **{pa}** and **{pb}** during "
                f"**{season}** — a season-matched historical comparison."
            )
    elif pid == BASEBALL_PLAYER_COMPARE and pa and pb:
        if ctx.get("trend_comparison_mode"):
            route.intent_restatement = (
                f"You're comparing the recent statistical **trends** of **{pa}** and "
                f"**{pb}** to decide who is the better pick."
            )
        else:
            route.intent_restatement = (
                f"You're asking who is the better pick between **{pa}** and **{pb}** "
                f"across their attached stats."
            )


def _has_draft_context(ctx: dict[str, Any]) -> bool:
    snap = ctx.get("draft_snapshot")
    if isinstance(snap, dict) and snap:
        return True
    return _has_value(ctx.get("roster")) or _has_value(ctx.get("recommended_players"))


def _route_baseball(
    question: str,
    ctx: dict[str, Any],
    topics: set[str],
    workflow: str,
    page: str,
    intent: QuestionIntent,
    *,
    source_page: str = "",
) -> ProblemRoute:
    low = question.lower()
    low_page = (source_page or page).lower()
    routing_hint = str(ctx.get("routing_hint") or ctx.get("intent") or "").lower()
    packet = ctx.get("hof_case_packet") if isinstance(ctx.get("hof_case_packet"), dict) else {}
    if routing_hint == "hof_case_analysis" or (
        isinstance(packet, dict) and packet.get("mode") == "hall_of_fame_case"
    ):
        req = ("hof_case_packet", "player")
        avail, miss = _audit_fields(ctx, req)
        if "hof_case_packet" not in avail and packet:
            avail = list(avail) + ["hof_case_packet"]
            miss = [m for m in miss if m != "hof_case_packet"]
        return ProblemRoute(
            problem_type_id=BASEBALL_HOF_CASE,
            problem_type="Hall of Fame statistical case",
            confidence=0.96 if "hof_case_packet" in avail else 0.82,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    is_trend_page = "trend" in low_page
    trend_q = any(
        w in low
        for w in (
            "trend",
            "slope",
            "sustainable",
            "regression",
            "breakout",
            "expected stat",
            "projection",
            "2026",
            "based on these trend",
            "meaningful",
            "noise",
        )
    )
    # Trend page with two named players + comparison phrasing → player comparison, not trend significance.
    # The trend solver handles one-player stat analysis; multi-player questions need the compare solver.
    _trend_pa = str(ctx.get("player_a") or "").strip()
    _trend_pb = str(ctx.get("player_b") or "").strip()
    if is_trend_page and _trend_pa and _trend_pb and (
        "better" in low
        or "compare" in low
        or " vs " in low
        or intent.intent_id == INTENT_WHO_IS_BETTER
    ):
        req = ("player_a", "player_b", "comparison_stats")
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=BASEBALL_PLAYER_COMPARE,
            problem_type="Player comparison",
            confidence=0.87 if "player_a" in avail and "player_b" in avail else 0.62,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )

    if is_trend_page and trend_q:
        trend_sum = ctx.get("trend_summary")
        has_trend_ctx = isinstance(trend_sum, dict) and bool(trend_sum)
        players = ctx.get("players") if isinstance(ctx.get("players"), list) else []
        has_trend_player = bool(
            str(ctx.get("player") or ctx.get("question_player") or (trend_sum or {}).get("player") or "").strip()
            or (players and str(players[0] or "").strip())
        )
        req = FIELD_SPECS[BASEBALL_TREND]
        avail, miss = _audit_fields(ctx, req)
        conf = 0.94 if has_trend_ctx and not miss else 0.88 if has_trend_player else 0.72
        return ProblemRoute(
            problem_type_id=BASEBALL_TREND,
            problem_type="Trend significance",
            confidence=conf,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if is_player_explanation_question(question):
        req = ("draft_snapshot", "question_player")
        avail, miss = _audit_fields(ctx, req)
        has_draft_page = _has_draft_context(ctx) or "draft" in topics or "draft" in workflow or "draft" in page.lower()
        if "draft_snapshot" in avail:
            conf = 0.9
        elif avail:
            conf = 0.78
        elif has_draft_page:
            conf = 0.58
        else:
            conf = 0.45
        return ProblemRoute(
            problem_type_id=BASEBALL_DRAFT,
            problem_type="Draft player explanation",
            confidence=conf,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if is_position_best_available_question(question):
        req = ("draft_snapshot", "available_players")
        avail, miss = _audit_fields(ctx, req)
        has_draft_page = _has_draft_context(ctx) or "draft" in topics or "draft" in workflow or "draft" in page.lower()
        if "draft_snapshot" in avail:
            conf = 0.91
        elif avail:
            conf = 0.8
        elif has_draft_page:
            conf = 0.58
        else:
            conf = 0.45
        return ProblemRoute(
            problem_type_id=BASEBALL_DRAFT,
            problem_type="Draft position best available",
            confidence=conf,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if is_draft_timing_question(question):
        req = ("draft_snapshot", "available_players")
        avail, miss = _audit_fields(ctx, req)
        conf = 0.9 if "draft_snapshot" in avail else 0.72 if avail else 0.55
        return ProblemRoute(
            problem_type_id=BASEBALL_DRAFT,
            problem_type="Draft timing decision",
            confidence=conf,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if is_draft_review_question(question):
        req = ("draft_snapshot", "user_roster")
        avail, miss = _audit_fields(ctx, req)
        conf = 0.88 if "draft_snapshot" in avail else 0.7 if avail else 0.52
        return ProblemRoute(
            problem_type_id=BASEBALL_DRAFT,
            problem_type="Draft review",
            confidence=conf,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if is_roster_needs_question(question):
        req = ("draft_snapshot", "needed_positions")
        avail, miss = _audit_fields(ctx, req)
        conf = 0.88 if avail else 0.55
        return ProblemRoute(
            problem_type_id=BASEBALL_DRAFT,
            problem_type="Roster needs",
            confidence=conf,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if is_draft_market_prediction_question(question):
        req = ("draft_snapshot", "drafted_players", "available_players")
        avail, miss = _audit_fields(ctx, req)
        has_draft_page = _has_draft_context(ctx) or "draft" in topics or "draft" in workflow or "draft" in page.lower()
        if "draft_snapshot" in avail:
            conf = 0.92
        elif avail:
            conf = 0.78
        elif has_draft_page:
            conf = 0.55
        else:
            conf = 0.42
        return ProblemRoute(
            problem_type_id=BASEBALL_DRAFT,
            problem_type="Draft market prediction",
            confidence=conf,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    trend_sum = ctx.get("trend_summary")
    has_trend_ctx = isinstance(trend_sum, dict) and bool(trend_sum)
    players = ctx.get("players") if isinstance(ctx.get("players"), list) else []
    has_trend_player = bool(
        str(ctx.get("player") or ctx.get("question_player") or (trend_sum or {}).get("player") or "").strip()
        or (players and str(players[0] or "").strip())
    )
    if has_trend_ctx and (
        "trend" in topics
        or "trend" in workflow
        or intent.intent_id == INTENT_IS_MEANINGFUL
        or any(w in low for w in ("trend", "slope", "doubles", "next season"))
    ):
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
    # Future accumulation beats static compare when user asks about next N seasons.
    if not is_trend_page and (
        intent.intent_id == INTENT_WILL_HAPPEN
        or (intent.intent_id == INTENT_WHO_IS_BETTER and intent.horizon)
    ):
        req = ("player_a", "player_b")
        avail, miss = _audit_fields(ctx, req)
        has_rates = bool(
            ctx.get("_ami_comparison_context")
            or ctx.get("comparison_stats")
            or ctx.get("comparison_differences")
        )
        if not has_rates:
            miss = list(miss) + ["comparison_stats (rate for focus stat)"]
        return ProblemRoute(
            problem_type_id=BASEBALL_FUTURE_ACCUMULATION,
            problem_type="Future stat accumulation forecast",
            confidence=0.82 if has_rates and not miss else 0.52,
            source_app="baseball",
            required_fields=list(req) + ["comparison_stats"],
            available_fields=avail + (["comparison_stats"] if has_rates else []),
            missing_fields=miss,
        )
    if "trend" in topics or "trend" in workflow or intent.intent_id == INTENT_IS_MEANINGFUL:
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
    if ("compare" in topics or "comparison" in workflow) and intent.intent_id == INTENT_WHO_IS_BETTER:
        if is_trend_page:
            req = FIELD_SPECS[BASEBALL_TREND]
            avail, miss = _audit_fields(ctx, req)
            return ProblemRoute(
                problem_type_id=BASEBALL_TREND,
                problem_type="Trend significance",
                confidence=0.86 if has_trend_ctx or has_trend_player else 0.68,
                source_app="baseball",
                required_fields=list(req),
                available_fields=avail,
                missing_fields=miss,
            )
        if _has_draft_context(ctx) and is_draft_head_to_head_question(question):
            req = ("draft_snapshot", "player_a", "player_b")
            avail, miss = _audit_fields(ctx, req)
            return ProblemRoute(
                problem_type_id=BASEBALL_DRAFT,
                problem_type="Draft player compare",
                confidence=0.85 if avail else 0.55,
                source_app="baseball",
                required_fields=list(req),
                available_fields=avail,
                missing_fields=miss,
            )
        if _has_draft_context(ctx) and re.search(
            r"safest.*upside|upside.*safest|highest.upside|safest pick|on the clock",
            low,
        ):
            req = ("draft_snapshot", "recommended_players")
            avail, miss = _audit_fields(ctx, req)
            return ProblemRoute(
                problem_type_id=BASEBALL_DRAFT,
                problem_type="Draft decision",
                confidence=0.82 if avail else 0.55,
                source_app="baseball",
                required_fields=list(req),
                available_fields=avail,
                missing_fields=miss,
            )
        # Age/season range constraint on a two-player comparison → historical age-window solver.
        # comparison_age_range or historical_comparison flag is set by the Comparison Tool send hook.
        if (
            ctx.get("comparison_age_range")
            or ctx.get("historical_comparison")
            or ctx.get("peak_comparison_mode")
        ):
            req = ("player_a", "player_b", "comparison_age_range")
            avail, miss = _audit_fields(ctx, req)
            return ProblemRoute(
                problem_type_id=BASEBALL_HISTORICAL,
                problem_type="Historical stat comparison",
                confidence=0.88 if "player_a" in avail and "player_b" in avail else 0.65,
                source_app="baseball",
                required_fields=list(req),
                available_fields=avail,
                missing_fields=miss,
            )
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
    val_snap = ctx.get("valuation_snapshot")
    if isinstance(val_snap, dict) and val_snap and (
        "valuation" in page.lower()
        or val_snap.get("top_valuation_players")
        or any(w in low for w in ("overvalued", "undervalued", "valuation score", "worth drafting"))
    ):
        req = ("valuation_snapshot", "player")
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=BASEBALL_VALUATION,
            problem_type="Player valuation",
            confidence=0.85 if not miss else 0.55,
            source_app="baseball",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if (
        "draft" in topics
        or "sleeper" in topics
        or "draft" in workflow
        or _has_draft_context(ctx)
        or (intent.intent_id == INTENT_SHOULD_I and ("draft" in low or _has_draft_context(ctx)))
    ):
        if _has_draft_context(ctx):
            req = ("draft_snapshot", "current_pick", "roster", "recommended_players")
            avail, miss = _audit_fields(ctx, req)
            conf = 0.88 if "draft_snapshot" in avail else 0.72 if avail else 0.45
        else:
            req = ("player", "draft_projection")
            avail, miss = _audit_fields(ctx, req)
            conf = 0.65 if avail else 0.4
        return ProblemRoute(
            problem_type_id=BASEBALL_DRAFT,
            problem_type="Draft decision",
            confidence=conf,
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
    intent: QuestionIntent,
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
    if "matchup" in workflow or (isinstance(matchup_adv, list) and matchup_adv) or (
        intent.intent_id == INTENT_IS_MEANINGFUL and "edge" in low
    ):
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
    intent: QuestionIntent,
) -> ProblemRoute:
    # WHY + drawdown/risk → attribution first, not stress test.
    if intent.intent_id == INTENT_WHY and (
        "drawdown" in low
        or ("risk" in low and ("why" in low or "create" in low or "cause" in low))
        or "expos" in low
    ):
        req = ("current_weights",)
        avail, miss = _audit_fields(ctx, req)
        return ProblemRoute(
            problem_type_id=INVESTMENT_DRAWDOWN_ATTRIBUTION,
            problem_type="Drawdown risk attribution",
            confidence=0.8 if avail else 0.48,
            source_app="investment",
            required_fields=list(req),
            available_fields=avail,
            missing_fields=miss,
        )
    if "rebalance" in topics or "rebalance" in low or (
        intent.intent_id == INTENT_SHOULD_I and "rebalance" in low
    ):
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
    if intent.intent_id == INTENT_WHAT_IF or (
        ("macro" in topics or ctx.get("macro_outlook") or ctx.get("macro_summary"))
        and intent.intent_id != INTENT_WHY
    ):
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
