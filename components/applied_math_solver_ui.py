"""Streamlit UI for rule-based Applied Math solvers."""

from __future__ import annotations

from typing import Any

from components.applied_math_problem_router import (
    BASEBALL_TREND,
    INVESTMENT_REBALANCE,
    INVESTMENT_RISK_RETURN,
    NBA_STAT_CHASE,
    ProblemRoute,
    route_suite_question,
)
from components.applied_math_solvers import SolverResult, solve_suite_question


def _fallback_solver_result(
    question: str,
    source_app: str,
    ctx: dict[str, Any],
    *,
    error: Exception | None = None,
) -> tuple[ProblemRoute, SolverResult]:
    """Safe fallback when routing/dispatch fails — never raises."""
    route = route_suite_question(question, source_app=source_app, context=ctx)
    answer = ""
    assumptions: list[str] = []
    missing: list[str] = list(route.missing_fields)
    try:
        from components.applied_math_first_pass_analysis import analyze_suite_question

        fp = analyze_suite_question(question, source_app=source_app, context=ctx)
        answer = fp.answer or ""
        assumptions = list(fp.assumptions)
        missing = list(fp.data_needed) or missing
        problem = fp.problem_type
        calc = fp.method
    except Exception:
        problem = route.problem_type
        calc = "Framework analysis"
        answer = "Attach numeric context from the source app for a computed answer."

    if error is not None:
        answer = f"{answer} (Solver unavailable: {error})".strip()

    data_used = [f"{k}: {ctx[k]}" for k in route.available_fields[:8] if ctx.get(k) is not None]
    return route, SolverResult(
        problem_detected=f"{problem}: {question.strip()}",
        data_used=data_used,
        calculation=calc,
        result="Fallback analysis — solver could not run",
        interpretation=answer,
        assumptions=assumptions or ["Context from the source app reflects the user's current view."],
        sensitivity_notes="Retry after redeploy or add missing context fields from the source app.",
        missing_fields=missing,
        partial=True,
        problem_type_id=route.problem_type_id,
        computed={},
        default_controls={},
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
    st.markdown("**7. Try changing this**")

    if pid == NBA_STAT_CHASE:
        st.number_input(
            "Games remaining",
            min_value=1,
            max_value=20,
            key=_control_key(pid, "games"),
        )
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
            help="Override leader total if not in context (0 = use context).",
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
        st.caption("No interactive controls for this problem type yet.")


def render_solver_sections(st: Any, route: ProblemRoute, result: SolverResult) -> None:
    st.markdown("### Applied Math answer")
    st.markdown(f"**1. Problem detected**  \n{result.problem_detected}")
    st.caption(
        f"Type: {route.problem_type} · confidence {route.confidence:.0%} · "
        f"id `{route.problem_type_id}`"
    )

    st.markdown("**2. Data used**")
    if result.data_used:
        for line in result.data_used:
            st.markdown(f"- {line}")
    else:
        st.markdown("- No numeric context attached yet.")

    if result.calculation:
        st.markdown("**3. Calculation**")
        st.markdown(result.calculation)

    st.markdown("**4. Result**")
    st.success(result.result)

    st.markdown("**5. Interpretation**")
    st.markdown(result.interpretation)

    st.markdown("**6. Assumptions**")
    for a in result.assumptions:
        st.markdown(f"- {a}")

    if result.partial and result.missing_fields:
        st.warning(
            "**Partial analysis** — missing: "
            + ", ".join(result.missing_fields)
            + ". Adjust controls below or return to the source app for full data."
        )
        st.markdown("**What would strengthen this answer**")
        for field in result.missing_fields:
            st.markdown(f"- `{field}` from the source app")


def render_suite_solver_answer(
    st: Any,
    *,
    question: str,
    source_app: str,
    context: dict[str, Any],
) -> None:
    """Route, solve, render interactive Applied Math answer for suite questions."""
    ctx = dict(context or {})
    try:
        route, seed_result = resolve_suite_solver(question, source_app=source_app, context=ctx)
        params = _seed_control_defaults(st, route, seed_result.default_controls)
        route, result = resolve_suite_solver(
            question,
            source_app=source_app,
            context=ctx,
            params=params,
        )
        render_solver_sections(st, route, result)
        _render_controls(st, route)
        st.markdown("**8. Sensitivity**")
        st.markdown(result.sensitivity_notes or "_No sensitivity notes._")
    except Exception as exc:
        route, result = _fallback_solver_result(question, source_app, ctx, error=exc)
        st.warning("Applied Math solver hit an error — showing fallback analysis instead of crashing.")
        render_solver_sections(st, route, result)
