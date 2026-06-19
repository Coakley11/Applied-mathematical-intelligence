"""Streamlit UI for rule-based Applied Math solvers."""

from __future__ import annotations

import json
from typing import Any

from components.applied_math_problem_router import (
    BASEBALL_DRAFT,
    BASEBALL_FUTURE_ACCUMULATION,
    BASEBALL_GENERIC,
    BASEBALL_PLAYER_COMPARE,
    BASEBALL_PROJECTION,
    BASEBALL_TREND,
    GENERIC_INTERACTIVE,
    INVESTMENT_CONCENTRATION,
    INVESTMENT_DRAWDOWN_ATTRIBUTION,
    INVESTMENT_GENERIC,
    INVESTMENT_MACRO,
    INVESTMENT_REBALANCE,
    INVESTMENT_RISK_RETURN,
    NBA_GENERIC,
    NBA_INVERSE_STAT_CHASE,
    NBA_MATCHUP_EDGE,
    NBA_STAT_CHASE,
    NBA_WIN_PROBABILITY,
    ProblemRoute,
    route_suite_question,
)
from components.applied_math_problem_interpreter import CORRECTION_OPTIONS
from components.applied_math_problem_interpreter import (
    PURPOSE_COMPARE,
    PURPOSE_DECIDE,
    PURPOSE_ESTIMATE_PROBABILITY,
    PURPOSE_ESTIMATE_RATE,
    PURPOSE_EVALUATE_RISK,
    PURPOSE_EXPLAIN_WHY,
    PURPOSE_FORECAST,
    PURPOSE_MEASURE_SENSITIVITY,
    PURPOSE_TEST_SIGNIFICANCE,
    PURPOSE_ATTRIBUTE,
)
from components.applied_math_solver_trace import SolverRunTrace
from components.applied_math_solvers import SolverResult, _route_confidence_pct, solve_suite_question


def render_applied_math_build_sidebar(st: Any) -> None:
    """Developer Mode: confirm deployed solver build."""
    try:
        from components.applied_math_context_diagnostics import applied_math_developer_mode_enabled
        from applied_math_build_info import build_info_lines

        if not applied_math_developer_mode_enabled(st):
            return
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Applied Math Solver Build**")
        for line in build_info_lines():
            st.sidebar.caption(line)
    except Exception:
        pass


def _fallback_solver_result(
    question: str,
    source_app: str,
    ctx: dict[str, Any],
    *,
    error: Exception | None = None,
) -> tuple[ProblemRoute, SolverResult]:
    """Safe fallback when routing/dispatch fails — still answer-first."""
    route = route_suite_question(question, source_app=source_app, context=ctx)
    missing = list(route.missing_fields)
    model_note = "The closest model we can use is a threshold/decision problem once numeric context is attached."
    answer = ""
    assumptions: list[str] = []
    problem = route.problem_type
    calc = "Partial — missing inputs for a full calculation."
    reasons: list[str] = []

    try:
        from components.applied_math_first_pass_analysis import analyze_suite_question

        fp = analyze_suite_question(question, source_app=source_app, context=ctx)
        answer = fp.answer or ""
        assumptions = list(fp.assumptions)
        missing = list(fp.data_needed) or missing
        problem = fp.problem_type
        calc = fp.method or calc
        if missing:
            reasons = [f"Missing **{missing[0]}** — cannot compute a firm verdict yet."]
    except Exception:
        answer = "We can model this once numeric context is attached from the source app."
        reasons = ["Solver dispatch failed and first-pass analysis could not run."]

    if error is not None:
        reasons.append(f"Error: {type(error).__name__}: {error}")

    if not reasons and missing:
        reasons = [f"Missing **{', '.join(missing[:3])}** from the source app."]

    conf = max(25, _route_confidence_pct(route, True, len(missing)) - 10)
    data_improve = [f"**{m}**" for m in missing[:4]] or [
        "Return to the source app and re-send with the page loaded (filters/selections applied)."
    ]

    return route, SolverResult(
        question=question.strip(),
        problem_type=problem,
        math_idea=model_note,
        variables="variable · baseline · threshold",
        data_used=[f"Source: **{route.source_app}**"],
        calculation=calc,
        result="Partial — uncertain",
        interpretation=answer,
        assumptions=assumptions or ["Context from the source app reflects the user's current view."],
        sensitivity_notes="Re-send from the source app after the relevant page has loaded fully.",
        missing_fields=missing,
        partial=True,
        problem_type_id=route.problem_type_id,
        conclusion="Partial / uncertain",
        confidence_pct=conf,
        confidence_label="Low",
        reasons=reasons[:4],
        model_note=model_note,
        data_would_improve=data_improve,
        pivot_assumption=(
            f"Adding **{missing[0]}** would change this from uncertain to a quantitative verdict."
            if missing
            else ""
        ),
        computed={"fallback": True},
    )


def _is_generic_route(route: ProblemRoute) -> bool:
    pid = route.problem_type_id
    return pid in (GENERIC_INTERACTIVE, "generic_fallback") or pid.endswith("_generic")


def _purpose_correction_key(question: str) -> str:
    qhash = abs(hash(question.strip().lower())) % 10_000_000
    return f"ami_purpose_override_{qhash}"


def resolve_suite_solver(
    question: str,
    *,
    source_app: str,
    context: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    purpose_override: str = "",
) -> tuple[ProblemRoute, SolverResult]:
    """Route + dispatch — same path as the UI; returns fallback on failure."""
    ctx = dict(context or {})
    try:
        route, result = solve_suite_question(
            question,
            source_app=source_app,
            context=ctx,
            params=params,
            purpose_override=purpose_override,
        )
        if not isinstance(result, SolverResult):
            raise TypeError(f"expected SolverResult, got {type(result)!r}")
        return route, result
    except Exception as exc:
        return _fallback_solver_result(question, source_app, ctx, error=exc)


def _control_key(problem_type_id: str, name: str) -> str:
    return f"ami_solver_{problem_type_id}_{name}"


def _seed_control_defaults(st: Any, route: ProblemRoute, defaults: dict[str, Any]) -> dict[str, Any]:
    """Read solver params from session state (widgets from prior rerun) or defaults."""
    pid = route.problem_type_id
    params: dict[str, Any] = {}

    if pid == NBA_STAT_CHASE:
        gk = _control_key(pid, "games")
        rk = _control_key(pid, "rate")
        tk = _control_key(pid, "target")
        if gk not in st.session_state:
            st.session_state[gk] = int(defaults.get("games_remaining", 4))
        if rk not in st.session_state:
            st.session_state[rk] = float(defaults.get("expected_rate", 3.0))
        if tk not in st.session_state:
            st.session_state[tk] = float(defaults.get("target_value", 0.0))
        params["games_remaining"] = int(st.session_state[gk])
        params["expected_rate"] = float(st.session_state[rk])
        tv = float(st.session_state[tk])
        if tv > 0:
            params["target_value"] = tv
    elif pid == NBA_INVERSE_STAT_CHASE:
        rk = _control_key(pid, "rate")
        tk = _control_key(pid, "target")
        if rk not in st.session_state:
            st.session_state[rk] = float(defaults.get("expected_rate", 4.0))
        if tk not in st.session_state:
            st.session_state[tk] = float(defaults.get("target_value", 0.0))
        params["expected_rate"] = float(st.session_state[rk])
        tv = float(st.session_state[tk])
        if tv > 0:
            params["target_value"] = tv
    elif pid == BASEBALL_TREND:
        sk = _control_key(pid, "slope")
        rk = _control_key(pid, "r2")
        if sk not in st.session_state:
            st.session_state[sk] = float(defaults.get("min_slope", 0.5))
        if rk not in st.session_state:
            st.session_state[rk] = float(defaults.get("min_r2", 0.35))
        params["min_slope"] = float(st.session_state[sk])
        params["min_r2"] = float(st.session_state[rk])
    elif pid == INVESTMENT_REBALANCE:
        dk = _control_key(pid, "drift")
        rk = _control_key(pid, "risk")
        if dk not in st.session_state:
            st.session_state[dk] = float(defaults.get("drift_threshold", 5.0))
        if rk not in st.session_state:
            st.session_state[rk] = str(defaults.get("risk_tolerance", "moderate"))
        params["drift_threshold"] = float(st.session_state[dk])
        params["risk_tolerance"] = str(st.session_state[rk])
    elif pid == INVESTMENT_RISK_RETURN:
        sk = _control_key(pid, "sharpe")
        vk = _control_key(pid, "vol")
        if sk not in st.session_state:
            st.session_state[sk] = float(defaults.get("min_sharpe", 0.5))
        if vk not in st.session_state:
            st.session_state[vk] = float(defaults.get("acceptable_volatility", 15.0))
        params["min_sharpe"] = float(st.session_state[sk])
        params["acceptable_volatility"] = float(st.session_state[vk])
    elif pid == INVESTMENT_CONCENTRATION:
        sk = _control_key(pid, "single")
        tk = _control_key(pid, "top3")
        if sk not in st.session_state:
            st.session_state[sk] = float(defaults.get("max_single_pct", 25.0))
        if tk not in st.session_state:
            st.session_state[tk] = float(defaults.get("max_top3_pct", 60.0))
        params["max_single_pct"] = float(st.session_state[sk])
        params["max_top3_pct"] = float(st.session_state[tk])
    elif pid == BASEBALL_PLAYER_COMPARE:
        for name, key in (
            ("weight_rate", "wr"),
            ("weight_power", "wp"),
            ("weight_career", "wc"),
            ("weight_peak", "wk"),
        ):
            ck = _control_key(pid, key)
            if ck not in st.session_state:
                st.session_state[ck] = float(defaults.get(name, 1.0 if "rate" in name or "power" in name else 0.5))
            params[name] = float(st.session_state[ck])
    elif pid == INVESTMENT_MACRO:
        rk = _control_key(pid, "ret")
        vk = _control_key(pid, "vsh")
        pk = _control_key(pid, "prob")
        if rk not in st.session_state:
            st.session_state[rk] = float(defaults.get("return_shock", -3.0))
        if vk not in st.session_state:
            st.session_state[vk] = float(defaults.get("vol_shock", 4.0))
        if pk not in st.session_state:
            st.session_state[pk] = float(defaults.get("recession_prob", 30.0))
        params["return_shock"] = float(st.session_state[rk])
        params["vol_shock"] = float(st.session_state[vk])
        params["recession_prob"] = float(st.session_state[pk])
    elif pid == BASEBALL_PROJECTION:
        rk = _control_key(pid, "recent")
        ck = _control_key(pid, "career")
        if rk not in st.session_state:
            st.session_state[rk] = float(defaults.get("max_above_recent_pct", 25.0))
        if ck not in st.session_state:
            st.session_state[ck] = float(defaults.get("max_above_career_pct", 35.0))
        params["max_above_recent_pct"] = float(st.session_state[rk])
        params["max_above_career_pct"] = float(st.session_state[ck])
    elif pid == BASEBALL_FUTURE_ACCUMULATION:
        for name, key, default in (
            ("seasons_a", "sa", 10),
            ("seasons_b", "sb", 10),
            ("rate_a", "ra", 90.0),
            ("rate_b", "rb", 100.0),
        ):
            ck = _control_key(pid, key)
            if ck not in st.session_state:
                st.session_state[ck] = float(defaults.get(name, default)) if "rate" in name else int(defaults.get(name, default))
            params[name] = float(st.session_state[ck]) if "rate" in name else int(st.session_state[ck])
        for name, key, default in (
            ("decline_a", "da", 0.02),
            ("decline_b", "db", 0.03),
        ):
            ck = _control_key(pid, key)
            if ck not in st.session_state:
                st.session_state[ck] = float(defaults.get(name, default))
            params[name] = float(st.session_state[ck])
    elif pid == INVESTMENT_DRAWDOWN_ATTRIBUTION:
        mk = _control_key(pid, "mkt")
        ck = _control_key(pid, "corr")
        if mk not in st.session_state:
            st.session_state[mk] = float(defaults.get("market_decline", -20.0))
        if ck not in st.session_state:
            st.session_state[ck] = float(defaults.get("equity_correlation", 0.85))
        params["market_decline"] = float(st.session_state[mk])
        params["equity_correlation"] = float(st.session_state[ck])
    elif pid == BASEBALL_DRAFT:
        for name, key, default in (
            ("current_pick", "pick", 18),
            ("adp", "adp", 22.0),
            ("projected_rank", "rank", 18),
            ("replacement_value", "rep", 50.0),
        ):
            ck = _control_key(pid, key)
            if ck not in st.session_state:
                st.session_state[ck] = float(defaults.get(name, default)) if name != "current_pick" else int(defaults.get(name, default))
            params[name] = float(st.session_state[ck]) if name != "current_pick" else int(st.session_state[ck])
        rk = _control_key(pid, "risk")
        if rk not in st.session_state:
            st.session_state[rk] = str(defaults.get("risk_tolerance", "moderate"))
        params["risk_tolerance"] = str(st.session_state[rk])
    elif pid == NBA_MATCHUP_EDGE:
        for name, key, default in (
            ("injury_adjustment_pp", "inj", 5.0),
            ("prob_threshold_pp", "thr", 8.0),
            ("stat_gap_weight", "wgt", 0.4),
        ):
            ck = _control_key(pid, key)
            if ck not in st.session_state:
                st.session_state[ck] = float(defaults.get(name, default))
            params[name] = float(st.session_state[ck])
    elif _is_generic_route(route):
        purpose = route.math_purpose or PURPOSE_COMPARE
        gpid = "generic_interactive"
        if purpose == PURPOSE_FORECAST:
            for name, key, default in (
                ("generic_rate_a", "gra", 90.0),
                ("generic_rate_b", "grb", 100.0),
                ("generic_seasons_a", "gsa", 10.0),
                ("generic_seasons_b", "gsb", 8.0),
                ("generic_decline_a", "gda", 0.02),
                ("generic_decline_b", "gdb", 0.03),
            ):
                ck = _control_key(gpid, key)
                if ck not in st.session_state:
                    st.session_state[ck] = float(defaults.get(name, default))
                params[name] = float(st.session_state[ck])
        elif purpose == PURPOSE_COMPARE:
            for name, key, default in (("generic_score_a", "sca", 55.0), ("generic_score_b", "scb", 45.0)):
                ck = _control_key(gpid, key)
                if ck not in st.session_state:
                    st.session_state[ck] = float(defaults.get(name, default))
                params[name] = float(st.session_state[ck])
        elif purpose == PURPOSE_ESTIMATE_RATE:
            for name, key, default in (
                ("generic_gap", "gap", 100.0),
                ("generic_periods", "per", 20.0),
                ("generic_expected_rate", "exp", 4.5),
            ):
                ck = _control_key(gpid, key)
                if ck not in st.session_state:
                    st.session_state[ck] = float(defaults.get(name, default))
                params[name] = float(st.session_state[ck])
        elif purpose == PURPOSE_TEST_SIGNIFICANCE:
            for name, key, default in (
                ("generic_slope", "sl", 0.8),
                ("generic_r2", "r2", 0.42),
                ("min_slope", "msl", 0.5),
                ("min_r2", "mr2", 0.35),
            ):
                ck = _control_key(gpid, key)
                if ck not in st.session_state:
                    st.session_state[ck] = float(defaults.get(name, default))
                params[name] = float(st.session_state[ck])
        elif purpose in (PURPOSE_EVALUATE_RISK, PURPOSE_EXPLAIN_WHY, PURPOSE_ATTRIBUTE):
            for name, key, default in (
                ("generic_return", "ret", 8.0),
                ("generic_volatility", "vol", 14.0),
                ("generic_weight", "wgt", 40.0),
            ):
                ck = _control_key(gpid, key)
                if ck not in st.session_state:
                    st.session_state[ck] = float(defaults.get(name, default))
                params[name] = float(st.session_state[ck])
        elif purpose == PURPOSE_DECIDE:
            for name, key, default in (("generic_drift", "drf", 6.0), ("generic_threshold", "thr", 5.0)):
                ck = _control_key(gpid, key)
                if ck not in st.session_state:
                    st.session_state[ck] = float(defaults.get(name, default))
                params[name] = float(st.session_state[ck])
        elif purpose == PURPOSE_ESTIMATE_PROBABILITY:
            for name, key, default in (("generic_probability", "prob", 62.0), ("generic_prior", "prior", 52.0)):
                ck = _control_key(gpid, key)
                if ck not in st.session_state:
                    st.session_state[ck] = float(defaults.get(name, default))
                params[name] = float(st.session_state[ck])
        elif purpose == PURPOSE_MEASURE_SENSITIVITY:
            for name, key, default in (
                ("generic_base_return", "bret", 8.0),
                ("generic_return_shock", "rsh", -3.0),
                ("generic_base_vol", "bvol", 12.0),
                ("generic_vol_shock", "vsh", 4.0),
            ):
                ck = _control_key(gpid, key)
                if ck not in st.session_state:
                    st.session_state[ck] = float(defaults.get(name, default))
                params[name] = float(st.session_state[ck])

    return params


def _render_controls(st: Any, route: ProblemRoute) -> None:
    pid = route.problem_type_id

    if pid == NBA_STAT_CHASE:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Games remaining", min_value=1, max_value=20, key=_control_key(pid, "games"))
        with c2:
            st.number_input(
                "Expected stat per game",
                min_value=0.0,
                max_value=30.0,
                step=0.5,
                key=_control_key(pid, "rate"),
            )
        with c3:
            st.number_input(
                "Target total (leader)",
                min_value=0.0,
                max_value=500.0,
                step=1.0,
                key=_control_key(pid, "target"),
                help="0 = use value from context.",
            )
    elif pid == NBA_INVERSE_STAT_CHASE:
        c1, c2 = st.columns(2)
        with c1:
            st.number_input(
                "Expected stat per game",
                min_value=0.5,
                max_value=30.0,
                step=0.5,
                key=_control_key(pid, "rate"),
            )
        with c2:
            st.number_input(
                "Target total (leader)",
                min_value=0.0,
                max_value=500.0,
                step=1.0,
                key=_control_key(pid, "target"),
                help="0 = use value from context.",
            )
    elif pid == BASEBALL_TREND:
        c1, c2 = st.columns(2)
        with c1:
            st.slider(
                "Minimum meaningful slope (per season)",
                min_value=0.1,
                max_value=3.0,
                step=0.1,
                key=_control_key(pid, "slope"),
            )
        with c2:
            st.slider(
                "Minimum R² threshold",
                min_value=0.05,
                max_value=0.95,
                step=0.05,
                key=_control_key(pid, "r2"),
            )
    elif pid == INVESTMENT_REBALANCE:
        c1, c2 = st.columns(2)
        with c1:
            st.slider(
                "Drift threshold (pp)",
                min_value=1.0,
                max_value=15.0,
                step=0.5,
                key=_control_key(pid, "drift"),
            )
        with c2:
            st.selectbox(
                "Risk tolerance",
                ["conservative", "moderate", "aggressive"],
                key=_control_key(pid, "risk"),
            )
    elif pid == INVESTMENT_RISK_RETURN:
        c1, c2 = st.columns(2)
        with c1:
            st.slider(
                "Minimum Sharpe ratio",
                min_value=0.0,
                max_value=2.0,
                step=0.05,
                key=_control_key(pid, "sharpe"),
            )
        with c2:
            st.slider(
                "Acceptable volatility (%)",
                min_value=5.0,
                max_value=40.0,
                step=0.5,
                key=_control_key(pid, "vol"),
            )
    elif pid == INVESTMENT_CONCENTRATION:
        c1, c2 = st.columns(2)
        with c1:
            st.slider(
                "Max single holding (%)",
                min_value=5.0,
                max_value=50.0,
                step=1.0,
                key=_control_key(pid, "single"),
            )
        with c2:
            st.slider(
                "Max top-3 combined (%)",
                min_value=20.0,
                max_value=90.0,
                step=1.0,
                key=_control_key(pid, "top3"),
            )
    elif pid == BASEBALL_PLAYER_COMPARE:
        c1, c2 = st.columns(2)
        with c1:
            st.slider("Weight rate stats", 0.0, 2.0, key=_control_key(pid, "wr"))
            st.slider("Weight power stats", 0.0, 2.0, key=_control_key(pid, "wp"))
        with c2:
            st.slider("Weight career totals", 0.0, 2.0, key=_control_key(pid, "wc"))
            st.slider("Weight peak seasons", 0.0, 2.0, key=_control_key(pid, "wk"))
    elif pid == INVESTMENT_MACRO:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.slider("Return shock (pp)", -10.0, 0.0, key=_control_key(pid, "ret"))
        with c2:
            st.slider("Volatility shock (pp)", 0.0, 15.0, key=_control_key(pid, "vsh"))
        with c3:
            st.slider("Recession probability (%)", 0.0, 80.0, key=_control_key(pid, "prob"))
    elif pid == BASEBALL_PROJECTION:
        c1, c2 = st.columns(2)
        with c1:
            st.slider(
                "Max % above recent season",
                min_value=5.0,
                max_value=60.0,
                step=1.0,
                key=_control_key(pid, "recent"),
            )
        with c2:
            st.slider(
                "Max % above career avg",
                min_value=10.0,
                max_value=80.0,
                step=1.0,
                key=_control_key(pid, "career"),
            )
    elif pid == BASEBALL_FUTURE_ACCUMULATION:
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Rate per season (player A)", min_value=0.0, max_value=200.0, key=_control_key(pid, "ra"))
            st.number_input("Seasons remaining (player A)", min_value=1, max_value=20, key=_control_key(pid, "sa"))
            st.slider("Decline rate A (per season)", 0.0, 0.15, key=_control_key(pid, "da"))
        with c2:
            st.number_input("Rate per season (player B)", min_value=0.0, max_value=200.0, key=_control_key(pid, "rb"))
            st.number_input("Seasons remaining (player B)", min_value=1, max_value=20, key=_control_key(pid, "sb"))
            st.slider("Decline rate B (per season)", 0.0, 0.15, key=_control_key(pid, "db"))
    elif pid == INVESTMENT_DRAWDOWN_ATTRIBUTION:
        c1, c2 = st.columns(2)
        with c1:
            st.slider("Assumed market decline (%)", -40.0, -5.0, key=_control_key(pid, "mkt"))
        with c2:
            st.slider("Equity correlation", 0.5, 1.0, key=_control_key(pid, "corr"))
    elif pid == BASEBALL_DRAFT:
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Current pick (overall)", min_value=1, max_value=300, key=_control_key(pid, "pick"))
            st.number_input("ADP", min_value=1.0, max_value=300.0, step=0.5, key=_control_key(pid, "adp"))
        with c2:
            st.number_input("Projected rank", min_value=1, max_value=300, key=_control_key(pid, "rank"))
            st.number_input("Replacement value", min_value=0.0, max_value=100.0, key=_control_key(pid, "rep"))
        st.selectbox("Risk tolerance", ["conservative", "moderate", "aggressive"], key=_control_key(pid, "risk"))
    elif pid == NBA_MATCHUP_EDGE:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.slider("Injury penalty (pp)", 0.0, 15.0, key=_control_key(pid, "inj"))
        with c2:
            st.slider("Edge threshold (pp)", 3.0, 20.0, key=_control_key(pid, "thr"))
        with c3:
            st.slider("Stat gap weight", 0.1, 0.8, key=_control_key(pid, "wgt"))
    elif _is_generic_route(route):
        gpid = "generic_interactive"
        purpose = route.math_purpose or PURPOSE_COMPARE
        if purpose == PURPOSE_FORECAST:
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Rate per season (A)", min_value=0.0, max_value=200.0, key=_control_key(gpid, "gra"))
                st.number_input("Seasons remaining (A)", min_value=1, max_value=20, key=_control_key(gpid, "gsa"))
                st.slider("Decline rate A", 0.0, 0.15, key=_control_key(gpid, "gda"))
            with c2:
                st.number_input("Rate per season (B)", min_value=0.0, max_value=200.0, key=_control_key(gpid, "grb"))
                st.number_input("Seasons remaining (B)", min_value=1, max_value=20, key=_control_key(gpid, "gsb"))
                st.slider("Decline rate B", 0.0, 0.15, key=_control_key(gpid, "gdb"))
        elif purpose == PURPOSE_COMPARE:
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Score A", min_value=0.0, max_value=200.0, key=_control_key(gpid, "sca"))
            with c2:
                st.number_input("Score B", min_value=0.0, max_value=200.0, key=_control_key(gpid, "scb"))
        elif purpose == PURPOSE_ESTIMATE_RATE:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.number_input("Gap to close", min_value=0.0, key=_control_key(gpid, "gap"))
            with c2:
                st.number_input("Periods remaining", min_value=1, key=_control_key(gpid, "per"))
            with c3:
                st.number_input("Expected rate", min_value=0.0, step=0.1, key=_control_key(gpid, "exp"))
        elif purpose == PURPOSE_TEST_SIGNIFICANCE:
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Trend slope", step=0.1, key=_control_key(gpid, "sl"))
                st.slider("Min slope", 0.1, 3.0, key=_control_key(gpid, "msl"))
            with c2:
                st.number_input("R²", min_value=0.0, max_value=1.0, step=0.05, key=_control_key(gpid, "r2"))
                st.slider("Min R²", 0.05, 0.95, key=_control_key(gpid, "mr2"))
        elif purpose in (PURPOSE_EVALUATE_RISK, PURPOSE_EXPLAIN_WHY, PURPOSE_ATTRIBUTE):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.number_input("Return (%)", key=_control_key(gpid, "ret"))
            with c2:
                st.number_input("Volatility (%)", key=_control_key(gpid, "vol"))
            with c3:
                st.number_input("Weight (%)", key=_control_key(gpid, "wgt"))
        elif purpose == PURPOSE_DECIDE:
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Drift (%)", key=_control_key(gpid, "drf"))
            with c2:
                st.number_input("Threshold (%)", key=_control_key(gpid, "thr"))
        elif purpose == PURPOSE_ESTIMATE_PROBABILITY:
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Quoted probability (%)", key=_control_key(gpid, "prob"))
            with c2:
                st.number_input("Prior (%)", key=_control_key(gpid, "prior"))
        elif purpose == PURPOSE_MEASURE_SENSITIVITY:
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Base return (%)", key=_control_key(gpid, "bret"))
                st.number_input("Return shock (pp)", key=_control_key(gpid, "rsh"))
            with c2:
                st.number_input("Base vol (%)", key=_control_key(gpid, "bvol"))
                st.number_input("Vol shock (pp)", key=_control_key(gpid, "vsh"))
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Baseline", key=_control_key(gpid, "base"))
            with c2:
                st.number_input("Threshold", key=_control_key(gpid, "thr2"))
    else:
        st.caption("No assumption controls for this problem type yet.")


def _render_live_dashboard(st: Any, result: SolverResult, *, max_metrics: int = 3) -> None:
    """Show key computed values — capped for cleaner layout."""
    if not result.live_metrics:
        return
    items = list(result.live_metrics.items())[:max_metrics]
    cols = st.columns(len(items))
    for i, (label, value) in enumerate(items):
        with cols[i]:
            st.metric(label, value)


def _render_baseball_draft_analyst_sections(st: Any, result: SolverResult) -> bool:
    """Six-part baseball analyst answer when solver produced coach_sections."""
    coach = result.computed.get("coach_sections") if isinstance(result.computed, dict) else None
    if not isinstance(coach, dict):
        return False

    with st.container(border=True):
        st.markdown("##### Direct answer")
        st.markdown(coach.get("direct_answer") or result.short_answer)

    with st.container(border=True):
        st.markdown("##### Analyst framing")
        st.markdown(coach.get("analyst_framing") or result.why or "—")

    key_vars = coach.get("key_variables")
    if isinstance(key_vars, list) and key_vars:
        with st.container(border=True):
            st.markdown("##### Key variables")
            for item in key_vars[:8]:
                st.markdown(f"- {item}")

    tradeoffs = str(coach.get("tradeoffs") or result.interpretation or "").strip()
    if tradeoffs:
        with st.container(border=True):
            st.markdown("##### Tradeoffs")
            st.markdown(tradeoffs)

    applied = str(coach.get("applied_math") or result.math_idea or "").strip()
    if applied:
        with st.container(border=True):
            st.markdown("##### Applied math")
            st.markdown(applied)

    what_if = coach.get("what_if")
    if isinstance(what_if, list) and what_if:
        with st.container(border=True):
            st.markdown("##### What-if scenarios")
            for line in what_if[:5]:
                st.markdown(f"- {line}")

    return True


def render_coach_answer(
    st: Any,
    route: ProblemRoute,
    result: SolverResult,
    *,
    question: str = "",
    source_app: str = "",
    source_page: str = "",
) -> bool:
    """Card-based learning layout — question → answer → math → try it → sensitivity."""
    q = (question or result.question or "").strip()
    short = (result.short_answer or result.conclusion or result.result or "").strip()
    if not short or short.lower().startswith("framework"):
        st.error(
            "We could not produce a clear answer for this question. "
            "Enable Developer Mode to inspect routing and context."
        )
        return False

    intent_txt = (result.intent_restatement or route.intent_restatement or "").strip()
    model_name = (result.model_name or route.model_name or route.problem_type or "").strip()
    model_rationale = (result.model_rationale or route.model_rationale or "").strip()
    why = (result.why or "").strip()
    if not why and result.reasons:
        why = result.reasons[0]
    conf_pct = result.confidence_pct
    conf_lbl = result.confidence_label or (f"{conf_pct}%" if conf_pct is not None else "")

    # 1 — Question card
    with st.container(border=True):
        st.markdown("##### Your question")
        if source_app:
            try:
                from suite_analytical_question import source_question_card_title

                src = source_question_card_title(source_app)
            except Exception:
                src = str(source_app or "").strip()
            st.caption(src + (f" · {source_page}" if source_page else ""))
        if q:
            st.markdown(f'*"{q}"*')
        if intent_txt:
            st.markdown(f"**What you're asking:** {intent_txt}")

    # 2 — Answer card (baseball draft uses six-part analyst layout)
    if result.problem_type_id == BASEBALL_DRAFT and isinstance(result.computed.get("coach_sections"), dict):
        _render_baseball_draft_analyst_sections(st, result)
        if conf_lbl:
            st.caption(f"Confidence: **{conf_lbl}**")
    else:
        with st.container(border=True):
            st.markdown("##### Answer")
            st.markdown(f"### {short}")
            if conf_lbl:
                st.caption(f"Confidence: **{conf_lbl}**")
            if why:
                st.markdown(f"**Main reason:** {why}")

    # 3 — Math card (formula details collapsed)
    skip_math_card = (
        result.problem_type_id == BASEBALL_DRAFT
        and isinstance(result.computed.get("coach_sections"), dict)
    )
    if not skip_math_card:
        with st.container(border=True):
            st.markdown("##### The math")
            if model_name:
                st.markdown(f"**Model:** {model_name}")
            if model_rationale:
                st.caption(model_rationale.replace("**", ""))
            if result.math_idea:
                st.markdown(result.math_idea)
            with st.expander("Variables & calculation", expanded=False):
                if result.variables:
                    st.markdown(f"```\n{result.variables.strip()}\n```")
                if result.calculation:
                    st.markdown(result.calculation)
            if result.partial and result.data_would_improve:
                st.caption(result.data_would_improve[0])
    elif result.calculation:
        with st.expander("Calculation details", expanded=False):
            if result.variables:
                st.markdown(f"```\n{result.variables.strip()}\n```")
            st.markdown(result.calculation)

    # 4 — Try it yourself
    with st.container(border=True):
        st.markdown("##### Try it yourself")
        st.caption("Adjust an assumption — the answer updates automatically.")
        _render_controls(st, route)
        _render_live_dashboard(st, result, max_metrics=3)

    # 5 — Sensitivity
    sens = (result.sensitivity_plain or result.pivot_assumption or result.sensitivity_notes or "").strip()
    if sens or result.sensitivity_rows:
        with st.container(border=True):
            st.markdown("##### What changes the answer?")
            if sens:
                st.markdown(sens)
            if result.sensitivity_rows:
                try:
                    import pandas as pd

                    st.dataframe(
                        pd.DataFrame(result.sensitivity_rows),
                        hide_index=True,
                        use_container_width=True,
                    )
                except Exception:
                    for row in result.sensitivity_rows[:4]:
                        st.markdown(
                            f"- **{row.get('Parameter', '')}** · {row.get('Scenario', '')} → {row.get('Outcome', '')}"
                        )

    # 6 — Details (assumptions + data audit)
    with st.expander("Details & assumptions", expanded=False):
        relevant = result.data_relevant or route.data_relevant
        missing = route.data_missing_interp or route.missing_fields
        if relevant:
            st.markdown("**Data used:** " + ", ".join(relevant[:8]))
        if missing:
            st.markdown("**Data missing:** " + ", ".join(str(m) for m in missing[:8]))
        solv = result.solvability or route.solvability
        if solv:
            st.caption(f"Solvability: {solv}")
        if result.assumptions:
            for a in result.assumptions:
                st.markdown(f"- {a}")

    return True


def render_conclusion_headline(st: Any, result: SolverResult) -> bool:
    """Legacy wrapper — prefer render_coach_answer."""
    short = (result.short_answer or result.conclusion or "").strip()
    if not short:
        return False
    with st.container(border=True):
        st.markdown(f"**Short answer:** {short}")
        if result.why:
            st.markdown(f"**Why:** {result.why}")
    return True


def render_solver_sections(
    st: Any,
    route: ProblemRoute,
    result: SolverResult,
    *,
    question: str = "",
    source_app: str = "",
    source_page: str = "",
) -> None:
    render_coach_answer(
        st,
        route,
        result,
        question=question,
        source_app=source_app,
        source_page=source_page,
    )


def render_solver_dev_diagnostics(
    st: Any,
    *,
    route: ProblemRoute,
    result: SolverResult,
    trace: SolverRunTrace | None = None,
    context: dict[str, Any] | None = None,
) -> None:
    try:
        from components.applied_math_context_diagnostics import applied_math_developer_mode_enabled
        from applied_math_build_info import build_info_lines
    except Exception:
        return
    if not applied_math_developer_mode_enabled(st):
        return

    ctx = dict(context or {})
    with st.expander("Solver diagnostics (Developer Mode)", expanded=True):
        st.markdown("**Applied Math Solver Build**")
        for line in build_info_lines():
            st.markdown(f"- {line}")

        if trace is not None:
            st.markdown("**Run trace**")
            for key, val in trace.to_dict().items():
                if isinstance(val, list):
                    st.markdown(f"- **{key}:** {', '.join(str(v) for v in val) if val else '—'}")
                else:
                    st.markdown(f"- **{key}:** `{val}`")

        st.markdown("**Router / solver**")
        st.markdown(f"- **problem_type_id:** `{route.problem_type_id}`")
        st.markdown(f"- **problem_type:** {route.problem_type}")
        st.markdown(f"- **router confidence:** {route.confidence:.0%}")
        st.markdown(f"- **solver_id:** `{result.problem_type_id}`")
        st.markdown(f"- **partial:** {result.partial}")
        st.markdown(f"- **conclusion:** {result.conclusion or result.result or '—'}")
        st.markdown(f"- **confidence_pct:** {result.confidence_pct}")
        st.markdown(f"- **reasons_count:** {len(result.reasons)}")

        if route.available_fields:
            st.markdown(f"- **fields available:** {', '.join(route.available_fields)}")
        if route.missing_fields:
            st.markdown(f"- **fields missing:** {', '.join(route.missing_fields)}")
        if ctx:
            st.markdown(f"- **context keys received:** {', '.join(sorted(ctx.keys())[:24])}")
        hydrate = str(st.session_state.get("_suite_ai_hydrate_source") or "").strip()
        if hydrate:
            st.markdown(f"- **hydrate_source:** `{hydrate}`")

        try:
            from components.applied_math_context_diagnostics import (
                build_load_identity_diagnostics,
                render_hydration_status_banner,
            )
            from components.draft_context_diagnostics import (
                build_draft_context_diagnostics,
                build_solver_bundle_diagnostics,
                render_draft_context_diagnostics_block,
            )

            ctx_debug = dict(ctx)
            ctx_debug["_debug_question"] = str(
                st.session_state.get("_suite_ai_question") or st.session_state.get("ps_library_problem") or ""
            )
            hydrate = str(st.session_state.get("_suite_ai_hydrate_source") or "").strip()
            intake_identity = build_load_identity_diagnostics(
                st, context=ctx_debug, question_id=str(st.session_state.get("_suite_ai_question_id") or "")
            )
            hydrated = build_draft_context_diagnostics(ctx_debug, hydrate_source=hydrate or intake_identity.get("blob_load_source") or "none")
            hydrated["hydrate_source"] = hydrate or hydrated.get("hydrate_source")
            hydrated["draft_context_source"] = hydrated["hydrate_source"]
            bundle = build_solver_bundle_diagnostics(ctx_debug)
            render_hydration_status_banner(st, {**intake_identity, **hydrated}, context="Hydrated context")
            render_draft_context_diagnostics_block(st, hydrated, title="Hydrated available pool")
            render_draft_context_diagnostics_block(st, bundle, title="Solver bundle (consumed)")
            if hydrated.get("available_players_count_hydrated", 0) > 0 and bundle.get("bundle_available_count", 0) == 0:
                st.warning("Hydrated pool has rows but solver bundle is empty — check draft_snapshot vs ctx merge.")
            if hydrated.get("available_players_count_hydrated", 0) == 0:
                st.warning("Hydrated available_players is empty — likely hydration (not Baseball packaging) if send had pool.")
            elif bundle.get("bundle_available_count", 0) > 0:
                st.info(
                    "Hydrated and bundle counts are both > 0. If the answer still says "
                    "'Fair price for the best player', 'pick 1', or '0 available names', classify as **C — reasoning/mode bug**."
                )
        except Exception as exc:
            st.markdown(f"- **draft_pool_diag_error:** `{exc}`")

        coach = result.computed.get("coach_sections") if isinstance(result.computed, dict) else None
        if isinstance(coach, dict):
            st.markdown(f"- **coach_sections:** {', '.join(sorted(coach.keys()))}")

        st.markdown("**Data used (solver)**")
        if result.data_used:
            for line in result.data_used[:8]:
                st.markdown(f"- {line}")

        with st.expander("Raw context JSON", expanded=False):
            st.code(json.dumps(ctx, indent=2, ensure_ascii=False, default=str)[:12000])


def _build_trace(
    *,
    route: ProblemRoute,
    result: SolverResult,
    question: str,
    source_app: str,
    source_page: str,
    context: dict[str, Any],
    used_fallback: bool,
    fallback_error: str = "",
) -> SolverRunTrace:
    return SolverRunTrace(
        renderer_path="render_suite_solver_answer",
        used_fallback=used_fallback,
        fallback_error=fallback_error,
        generic_flow_rendered=False,
        source_app=source_app,
        source_page=source_page,
        question=question,
        problem_type_id=route.problem_type_id,
        problem_type=route.problem_type,
        router_confidence=route.confidence,
        solver_id=result.problem_type_id,
        fields_available=list(route.available_fields),
        fields_missing=list(route.missing_fields),
        context_keys=sorted(context.keys()),
        conclusion=result.conclusion or result.result or "",
        confidence_pct=result.confidence_pct,
        reasons_count=len(result.reasons),
        partial=result.partial,
    )


def _query_param(st: Any, name: str) -> str:
    try:
        raw = st.query_params.get(name)
    except Exception:
        return ""
    if raw is None:
        return ""
    if isinstance(raw, list):
        return str(raw[0] or "").strip()
    return str(raw).strip()


def _load_canonical_instant_insight(st: Any, context: dict[str, Any], *, source_app: str) -> dict[str, Any]:
    try:
        from applied_math_return_insight import resolve_canonical_instant_insight

        return resolve_canonical_instant_insight(st, context, source_app=source_app)
    except ImportError:
        return {}


def _load_canonical_music_insight(st: Any, context: dict[str, Any]) -> dict[str, Any]:
    return _load_canonical_instant_insight(st, context, source_app="music")


def _render_canonical_instant_answer(
    st: Any,
    *,
    question: str,
    source_app: str,
    source_page: str,
    context: dict[str, Any],
    canonical: dict[str, Any],
    caption: str,
    guidance_label: str,
    build_label: str,
    renderer_path: str,
    solver_id: str,
    problem_type: str,
    deep_dive: bool = False,
) -> SolverRunTrace:
    if caption:
        st.caption(caption)
    sections = canonical.get("analyst_sections")
    if isinstance(sections, dict) and sections:
        exp = str(context.get("experience_mode") or "").lower()
        beginner = "beginner" in exp
        try:
            from investment_ami_answer_format import render_ami_deep_dive_markdown

            body = render_ami_deep_dive_markdown(sections, beginner=beginner)
            if body:
                st.markdown(body)
                rendered = True
            else:
                rendered = False
        except ImportError:
            rendered = False
        if not rendered:
            section_order = (
                ("direct_answer", "Direct Answer"),
                ("portfolio_analyst_view", "What This Means" if beginner else "Portfolio Analyst View"),
                ("current_strengths", "Current Strengths"),
                ("current_weaknesses", "Current Weaknesses"),
                ("potential_increases", "Potential Increases"),
                ("potential_reductions", "Potential Reductions"),
                ("key_variables", "Key Numbers" if beginner else "Key Variables"),
                ("tradeoffs", "Tradeoffs"),
                ("what_if_scenarios", "What-If Scenarios"),
                ("recommended_actions", "What You Could Do" if beginner else "Recommended Actions"),
                ("risk_notes", "Important Notes" if beginner else "Risk Notes"),
            )
            if beginner:
                section_order = tuple(x for x in section_order if x[0] != "what_if_scenarios")
            rendered = False
            for key, label in section_order:
                body = str(sections.get(key) or "").strip()
                if body:
                    st.markdown(f"**{label}**\n\n{body}")
                    rendered = True
        if not rendered:
            st.markdown(str(canonical.get("conclusion") or ""))
    else:
        st.markdown(str(canonical.get("conclusion") or ""))
    method = str(canonical.get("method") or canonical.get("model_name") or "").strip()
    if method:
        st.markdown(f"**{guidance_label}:** {method}")
    assumptions = canonical.get("assumptions") or []
    if assumptions:
        st.markdown("**Assumptions:**")
        for line in assumptions[:8]:
            st.markdown(f"- {line}")
    conf = canonical.get("confidence")
    if conf:
        extra = f" ({canonical.get('confidence_pct')}%)" if canonical.get("confidence_pct") else ""
        st.caption(f"Confidence: **{conf}**{extra}")
    build_id = str(canonical.get("solver_build_id") or "").strip()
    if build_id:
        st.caption(f"{build_label}: `{build_id}`")
    trace = SolverRunTrace(
        renderer_path=renderer_path,
        used_fallback=False,
        fallback_error="",
        generic_flow_rendered=False,
        source_app=source_app,
        source_page=source_page,
        question=question,
        problem_type_id=problem_type,
        problem_type=problem_type,
        router_confidence=1.0,
        solver_id=solver_id,
        fields_available=[],
        fields_missing=[],
        context_keys=sorted(context.keys()),
        conclusion=str(canonical.get("conclusion") or ""),
        confidence_pct=canonical.get("confidence_pct"),
        reasons_count=0,
        partial=False,
    )
    st.session_state["_ami_last_solver_trace"] = trace.to_dict()
    return trace


def _render_canonical_music_answer(
    st: Any,
    *,
    question: str,
    source_app: str,
    source_page: str,
    context: dict[str, Any],
    canonical: dict[str, Any],
) -> SolverRunTrace:
    return _render_canonical_instant_answer(
        st,
        question=question,
        source_app=source_app,
        source_page=source_page,
        context=context,
        canonical=canonical,
        caption="Showing the same Music Coach answer from your practice page.",
        guidance_label="Coach guidance",
        build_label="Music Coach build",
        renderer_path="render_canonical_music_insight",
        solver_id="music_instant_canonical",
        problem_type=str(canonical.get("problem_type") or "music_canonical"),
    )


def _render_canonical_investment_answer(
    st: Any,
    *,
    question: str,
    source_app: str,
    source_page: str,
    context: dict[str, Any],
    canonical: dict[str, Any],
) -> SolverRunTrace:
    st.caption("Deep-dive analysis — explore assumptions, tradeoffs, and scenarios below.")
    try:
        from applied_math_return_insight import SESSION_PENDING_KEY
        from investment_ami_sliders import render_ami_assumption_controls

        slider_data = {
            **canonical,
            "source_app": "investment",
            "source_page": source_page,
            "question": question,
        }
        refreshed = render_ami_assumption_controls(st, slider_data)
        if refreshed:
            updated = st.session_state.get(SESSION_PENDING_KEY)
            if isinstance(updated, dict) and updated.get("conclusion"):
                canonical = updated
    except ImportError:
        pass
    except Exception as exc:
        st.warning(f"Assumption controls could not update the analysis ({exc}). Showing the last result.")
    return _render_canonical_instant_answer(
        st,
        question=question,
        source_app=source_app,
        source_page=source_page,
        context=context,
        canonical=canonical,
        caption="",
        guidance_label="Analyst framing",
        build_label="Investment AMI build",
        renderer_path="render_canonical_investment_insight",
        solver_id="investment_instant_canonical",
        problem_type=str(canonical.get("problem_type") or "investment_canonical"),
        deep_dive=True,
    )


def render_suite_solver_answer(
    st: Any,
    *,
    question: str,
    source_app: str,
    source_page: str = "",
    context: dict[str, Any],
) -> SolverRunTrace:
    """Route, solve, render interactive Applied Math answer for suite questions."""
    ctx = dict(context or {})
    app_key = str(source_app or ctx.get("source_app") or "").strip().lower()
    if app_key == "music":
        canonical = _load_canonical_music_insight(st, ctx)
        if canonical and str(canonical.get("conclusion") or "").strip():
            return _render_canonical_music_answer(
                st,
                question=question,
                source_app=source_app,
                source_page=source_page,
                context=ctx,
                canonical=canonical,
            )
    if app_key == "investment":
        canonical = _load_canonical_instant_insight(st, ctx, source_app="investment")
        if canonical and str(canonical.get("conclusion") or "").strip():
            return _render_canonical_investment_answer(
                st,
                question=question,
                source_app=source_app,
                source_page=source_page,
                context=ctx,
                canonical=canonical,
            )

    used_fallback = False
    fallback_error = ""
    corr_key = _purpose_correction_key(question)
    labels = list(CORRECTION_OPTIONS.keys())
    if corr_key not in st.session_state:
        st.session_state[corr_key] = labels[0]
    selected_label = st.selectbox(
        "Change problem type (if the interpretation is wrong)",
        labels,
        key=corr_key,
        help="Re-route to a different mathematical model without re-typing your question.",
    )
    purpose_override = CORRECTION_OPTIONS.get(selected_label, "")
    try:
        route, seed_result = resolve_suite_solver(
            question,
            source_app=source_app,
            context=ctx,
            purpose_override=purpose_override,
        )
        params = _seed_control_defaults(st, route, seed_result.default_controls)
        route, result = resolve_suite_solver(
            question,
            source_app=source_app,
            context=ctx,
            params=params,
            purpose_override=purpose_override,
        )
        used_fallback = bool(result.computed.get("fallback"))
    except Exception as exc:
        used_fallback = True
        fallback_error = f"{type(exc).__name__}: {exc}"
        route, result = _fallback_solver_result(question, source_app, ctx, error=exc)
        st.warning("Showing fallback analysis — the solver hit an unexpected error.")

    trace = _build_trace(
        route=route,
        result=result,
        question=question,
        source_app=source_app,
        source_page=source_page,
        context=ctx,
        used_fallback=used_fallback,
        fallback_error=fallback_error,
    )
    st.session_state["_ami_last_solver_trace"] = trace.to_dict()

    render_solver_sections(
        st,
        route,
        result,
        question=question,
        source_app=source_app,
        source_page=source_page,
    )

    from applied_math_return_insight import AMI_INSIGHT_STORE_VERSION, persist_suite_return_insight

    store_trace = persist_suite_return_insight(
        st,
        question=question,
        source_app=source_app,
        source_page=source_page,
        context=ctx,
        route=route,
        result=result,
    )
    st.session_state["_ami_insight_store_version"] = AMI_INSIGHT_STORE_VERSION
    if store_trace.get("store_exception"):
        st.warning(f"Return insight store issue: {store_trace.get('store_exception')}")

    render_solver_dev_diagnostics(st, route=route, result=result, trace=trace, context=ctx)
    return trace
