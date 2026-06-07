"""Streamlit UI for rule-based Applied Math solvers."""

from __future__ import annotations

import json
from typing import Any

from components.applied_math_problem_router import (
    BASEBALL_TREND,
    INVESTMENT_REBALANCE,
    INVESTMENT_RISK_RETURN,
    NBA_STAT_CHASE,
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

    return params


def _render_controls(st: Any, route: ProblemRoute) -> None:
    pid = route.problem_type_id
    st.markdown("**Assumptions (adjust and watch the conclusion update)**")

    if pid == NBA_STAT_CHASE:
        st.number_input("Games remaining", min_value=1, max_value=20, key=_control_key(pid, "games"))
        st.number_input(
            "Expected stat per game",
            min_value=0.0,
            max_value=30.0,
            step=0.5,
            key=_control_key(pid, "rate"),
        )
        st.number_input(
            "Target total (leader)",
            min_value=0.0,
            max_value=500.0,
            step=1.0,
            key=_control_key(pid, "target"),
            help="0 = use value from context.",
        )
    elif pid == BASEBALL_TREND:
        st.slider(
            "Minimum meaningful slope (per season)",
            min_value=0.1,
            max_value=3.0,
            step=0.1,
            key=_control_key(pid, "slope"),
        )
        st.slider(
            "Minimum R² threshold",
            min_value=0.05,
            max_value=0.95,
            step=0.05,
            key=_control_key(pid, "r2"),
        )
    elif pid == INVESTMENT_REBALANCE:
        st.slider(
            "Drift threshold (pp)",
            min_value=1.0,
            max_value=15.0,
            step=0.5,
            key=_control_key(pid, "drift"),
        )
        st.selectbox(
            "Risk tolerance",
            ["conservative", "moderate", "aggressive"],
            key=_control_key(pid, "risk"),
        )
    elif pid == INVESTMENT_RISK_RETURN:
        st.slider(
            "Minimum Sharpe ratio",
            min_value=0.0,
            max_value=2.0,
            step=0.05,
            key=_control_key(pid, "sharpe"),
        )
        st.slider(
            "Acceptable volatility (%)",
            min_value=5.0,
            max_value=40.0,
            step=0.5,
            key=_control_key(pid, "vol"),
        )
    else:
        st.caption("No assumption controls for this problem type yet.")


def render_conclusion_headline(st: Any, result: SolverResult, *, route: ProblemRoute | None = None) -> bool:
    """First visible block — returns False if conclusion engine did not populate."""
    headline = (result.conclusion or "").strip()
    if not headline:
        headline = (result.result or "").strip()
    if not headline or headline.lower().startswith("framework"):
        st.error(
            "**Solver path did not produce a conclusion.** "
            "Enable Developer Mode → Solver diagnostics to inspect routing and context."
        )
        return False

    st.success(f"**Best conclusion:** {headline}")

    if result.confidence_pct is not None:
        label = result.confidence_label or ""
        label_txt = f" ({label})" if label else ""
        st.markdown(f"**Confidence:** {result.confidence_pct}%{label_txt}")

    if result.reasons:
        primary = result.reasons[0]
        st.markdown(f"**Main reason:** {primary}")
        if len(result.reasons) > 1:
            with st.expander("Additional reasons", expanded=False):
                for line in result.reasons[1:4]:
                    st.markdown(f"- {line}")
    elif result.interpretation:
        first = result.interpretation.split(".")[0].strip()
        if first:
            st.markdown(f"**Main reason:** {first}.")

    if route is not None:
        st.caption(
            f"Solver `{route.problem_type_id}` · router confidence {route.confidence:.0%}"
            + (" · partial data" if result.partial else "")
        )
    return True


def render_solver_sections(
    st: Any,
    route: ProblemRoute,
    result: SolverResult,
    *,
    question: str = "",
) -> None:
    render_conclusion_headline(st, result, route=route)

    if result.pivot_assumption:
        st.info(f"**What assumption matters most?** {result.pivot_assumption}")

    if result.partial and result.data_would_improve:
        st.markdown("**What would improve this answer:**")
        for item in result.data_would_improve[:4]:
            st.markdown(f"- {item}")

    if result.calculation:
        st.markdown("**Calculation**")
        st.markdown(result.calculation)

    if result.assumptions:
        st.markdown("**Assumptions**")
        for a in result.assumptions:
            st.markdown(f"- {a}")

    if result.sensitivity_rows:
        st.markdown("**Sensitivity**")
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
    elif result.sensitivity_notes:
        st.markdown("**What changes the answer?**")
        st.markdown(result.sensitivity_notes)

    q = (question or result.question or "").strip()
    with st.expander("Question, data, and math details", expanded=False):
        if q:
            st.markdown(f"**Question:** {q}")
        st.caption(f"Problem type: **{result.problem_type or route.problem_type}** (`{route.problem_type_id}`)")
        if result.model_note:
            st.markdown(result.model_note)
        if result.math_idea:
            st.markdown(f"**Mathematical idea:** {result.math_idea}")
        if result.variables:
            st.markdown("**Variables**")
            st.markdown(f"```\n{result.variables.strip()}\n```")
        st.markdown("**Data used**")
        if result.data_used:
            for line in result.data_used[:5]:
                st.markdown(f"- {line}")
        else:
            st.markdown("- No numeric inputs attached yet.")
        if result.interpretation:
            st.markdown("**Full interpretation**")
            st.markdown(result.interpretation)


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
    _render_controls(st, route)
    render_solver_dev_diagnostics(st, route=route, result=result, trace=trace, context=ctx)
    return trace
