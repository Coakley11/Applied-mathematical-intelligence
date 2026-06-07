"""Streamlit UI for rule-based Applied Math solvers."""

from __future__ import annotations

import json
from typing import Any

from components.applied_math_problem_router import (
    BASEBALL_PLAYER_COMPARE,
    BASEBALL_PROJECTION,
    BASEBALL_TREND,
    INVESTMENT_CONCENTRATION,
    INVESTMENT_MACRO,
    INVESTMENT_REBALANCE,
    INVESTMENT_RISK_RETURN,
    NBA_INVERSE_STAT_CHASE,
    NBA_STAT_CHASE,
    NBA_WIN_PROBABILITY,
    ProblemRoute,
    route_suite_question,
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


def resolve_suite_solver(
    question: str,
    *,
    source_app: str,
    context: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> tuple[ProblemRoute, SolverResult]:
    """Route + dispatch — same path as the UI; returns fallback on failure."""
    ctx = dict(context or {})
    try:
        route, result = solve_suite_question(
            question,
            source_app=source_app,
            context=ctx,
            params=params,
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
    else:
        st.caption("No assumption controls for this problem type yet.")


def _render_live_dashboard(st: Any, result: SolverResult) -> None:
    """Show pass/fail and key computed values after hands-on controls."""
    if not result.live_metrics:
        return
    st.markdown("**At these assumptions:**")
    n = len(result.live_metrics)
    cols = st.columns(min(n, 4))
    for i, (label, value) in enumerate(result.live_metrics.items()):
        with cols[i % len(cols)]:
            st.metric(label, value)


def render_coach_answer(
    st: Any,
    route: ProblemRoute,
    result: SolverResult,
    *,
    question: str = "",
) -> bool:
    """Math-coach layout: question → short answer → why → math → calculation → controls → sensitivity."""
    q = (question or result.question or "").strip()
    short = (result.short_answer or result.conclusion or result.result or "").strip()
    if not short or short.lower().startswith("framework"):
        st.error(
            "We could not produce a clear answer for this question. "
            "Enable Developer Mode to inspect routing and context."
        )
        return False

    with st.container(border=True):
        st.markdown("#### 1. Your question")
        if q:
            st.markdown(f'*"{q}"*')
        else:
            st.caption("Question text unavailable.")

        st.markdown("#### 2. Short answer")
        st.markdown(short)

        why = (result.why or "").strip()
        if not why and result.reasons:
            why = result.reasons[0]
        if why:
            st.markdown("#### 3. Why")
            st.markdown(why)

    st.markdown("#### 4. The math idea")
    if result.math_idea:
        st.markdown(result.math_idea)

    if result.variables:
        st.markdown("#### 5. Variables")
        st.markdown(f"```\n{result.variables.strip()}\n```")

    if result.calculation:
        st.markdown("#### 6. Calculation")
        st.markdown(result.calculation)

    if result.partial and result.data_would_improve:
        for hint in result.data_would_improve[:2]:
            st.info(hint)

    st.markdown("#### 7. Hands-on controls")
    st.caption("Change an assumption — the answer and live result update automatically.")
    _render_controls(st, route)
    _render_live_dashboard(st, result)

    st.markdown("#### 8. What changes the answer?")
    sens = (result.sensitivity_plain or result.pivot_assumption or result.sensitivity_notes or "").strip()
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
            for row in result.sensitivity_rows:
                st.markdown(
                    f"- **{row.get('Parameter', '')}** · {row.get('Scenario', '')} → {row.get('Outcome', '')}"
                )

    if result.assumptions:
        with st.expander("Assumptions behind this model", expanded=False):
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
) -> None:
    render_coach_answer(st, route, result, question=question)


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
    used_fallback = False
    fallback_error = ""
    try:
        route, seed_result = resolve_suite_solver(question, source_app=source_app, context=ctx)
        params = _seed_control_defaults(st, route, seed_result.default_controls)
        route, result = resolve_suite_solver(
            question,
            source_app=source_app,
            context=ctx,
            params=params,
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

    render_solver_sections(st, route, result, question=question)
    render_solver_dev_diagnostics(st, route=route, result=result, trace=trace, context=ctx)
    return trace
