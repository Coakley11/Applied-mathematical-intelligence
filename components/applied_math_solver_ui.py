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
    problem = route.problem_type
    calc = "Framework analysis"
    try:
        from components.applied_math_first_pass_analysis import analyze_suite_question

        fp = analyze_suite_question(question, source_app=source_app, context=ctx)
        answer = fp.answer or ""
        assumptions = list(fp.assumptions)
        missing = list(fp.data_needed) or missing
        problem = fp.problem_type
        calc = fp.method
    except Exception:
        answer = "We can model this once numeric context is attached from the source app."

    if error is not None:
        answer = f"{answer} (Solver unavailable: {error})".strip()

    return route, SolverResult(
        question=question.strip(),
        problem_type=problem,
        math_idea="Define the measurable quantity, baseline, and decision threshold.",
        variables="variable · baseline · threshold",
        data_used=[f"Source: **{route.source_app}**"],
        calculation=calc,
        result="Fallback analysis — solver could not run",
        interpretation=answer,
        assumptions=assumptions or ["Context from the source app reflects the user's current view."],
        sensitivity_notes="Enable Developer Mode to inspect the full context payload.",
        missing_fields=missing,
        partial=True,
        problem_type_id=route.problem_type_id,
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
    st.markdown("**7. Try changing assumptions**")

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


def render_solver_sections(
    st: Any,
    route: ProblemRoute,
    result: SolverResult,
    *,
    question: str = "",
) -> None:
    st.markdown("### Mathematical coach")
    q = (question or result.question or "").strip()
    if q:
        st.markdown(f"**1. The question**  \n{q}")
    st.caption(f"Problem type: **{result.problem_type or route.problem_type}**")

    if result.math_idea:
        st.markdown(f"**2. The mathematical idea**  \n{result.math_idea}")

    if result.variables:
        st.markdown("**3. Variables**")
        st.markdown(f"```\n{result.variables.strip()}\n```")

    st.markdown("**4. Data used**")
    st.caption("Key inputs only — full context is in Developer Mode.")
    if result.data_used:
        for line in result.data_used[:5]:
            st.markdown(f"- {line}")
    else:
        st.markdown("- No numeric inputs attached yet.")

    if result.calculation:
        st.markdown("**5. Calculation**")
        st.markdown(result.calculation)

    st.markdown("**6. Result**")
    st.success(result.result)

    st.markdown("**Interpretation**")
    st.markdown(result.interpretation)

    if result.assumptions:
        with st.expander("Assumptions", expanded=False):
            for a in result.assumptions:
                st.markdown(f"- {a}")

    if result.partial and result.missing_fields:
        st.info(
            "Partial analysis — missing: "
            + ", ".join(result.missing_fields)
            + ". Adjust assumptions below or return to the source app."
        )


def render_solver_dev_diagnostics(
    st: Any,
    *,
    route: ProblemRoute,
    result: SolverResult,
) -> None:
    try:
        from components.applied_math_context_diagnostics import applied_math_developer_mode_enabled
    except Exception:
        return
    if not applied_math_developer_mode_enabled(st):
        return
    with st.expander("Solver diagnostics (Developer Mode)", expanded=False):
        st.markdown(f"- **Route:** `{route.problem_type_id}` · confidence {route.confidence:.0%}")
        st.markdown(f"- **Solver:** `{result.problem_type_id}`")
        st.markdown(f"- **Partial:** {result.partial}")
        if route.available_fields:
            st.markdown(f"- **Fields used:** {', '.join(route.available_fields[:12])}")
        if route.missing_fields:
            st.markdown(f"- **Fields missing:** {', '.join(route.missing_fields)}")


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
        render_solver_sections(st, route, result, question=question)
        _render_controls(st, route)
        st.markdown("**8. What changes the answer?**")
        st.markdown(result.sensitivity_notes or "_Adjust the assumptions above to stress-test the conclusion._")
        render_solver_dev_diagnostics(st, route=route, result=result)
    except Exception as exc:
        route, result = _fallback_solver_result(question, source_app, ctx, error=exc)
        st.warning("Showing fallback analysis — the solver hit an unexpected error.")
        render_solver_sections(st, route, result, question=question)
