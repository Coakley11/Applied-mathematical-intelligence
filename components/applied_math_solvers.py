"""Rule-based mathematical solvers for suite Applied Math questions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from components.applied_math_problem_router import (
    BASEBALL_DRAFT,
    BASEBALL_GENERIC,
    BASEBALL_HISTORICAL,
    BASEBALL_PLAYER_COMPARE,
    BASEBALL_TREND,
    GENERIC_FALLBACK,
    INVESTMENT_CONCENTRATION,
    INVESTMENT_GENERIC,
    INVESTMENT_MACRO,
    INVESTMENT_REBALANCE,
    INVESTMENT_RISK_RETURN,
    NBA_GENERIC,
    NBA_LEGACY_COMPARISON,
    NBA_MATCHUP_EDGE,
    NBA_STAT_CHASE,
    NBA_WIN_PROBABILITY,
    ProblemRoute,
    route_suite_question,
)


@dataclass
class SolverResult:
    question: str = ""
    problem_type: str = ""
    math_idea: str = ""
    variables: str = ""
    data_used: list[str] = field(default_factory=list)
    calculation: str = ""
    result: str = ""
    interpretation: str = ""
    assumptions: list[str] = field(default_factory=list)
    sensitivity_notes: str = ""
    missing_fields: list[str] = field(default_factory=list)
    partial: bool = False
    problem_type_id: str = ""
    computed: dict[str, Any] = field(default_factory=dict)
    default_controls: dict[str, Any] = field(default_factory=dict)

    # Legacy alias — older code/tests referenced problem_detected
    @property
    def problem_detected(self) -> str:
        if self.problem_type and self.question:
            return f"{self.problem_type}: {self.question}"
        return self.problem_type or self.question


def _cap_data_used(lines: list[str], limit: int = 5) -> list[str]:
    return [ln for ln in lines if ln][:limit]


def _coach_result(
    *,
    question: str,
    problem_type: str,
    math_idea: str,
    variables: str,
    data_used: list[str],
    calculation: str,
    result: str,
    interpretation: str,
    assumptions: list[str],
    sensitivity_notes: str,
    problem_type_id: str,
    computed: dict[str, Any] | None = None,
    default_controls: dict[str, Any] | None = None,
    missing_fields: list[str] | None = None,
    partial: bool = False,
) -> SolverResult:
    return SolverResult(
        question=question.strip(),
        problem_type=problem_type,
        math_idea=math_idea,
        variables=variables,
        data_used=_cap_data_used(data_used),
        calculation=calculation,
        result=result,
        interpretation=interpretation,
        assumptions=assumptions,
        sensitivity_notes=sensitivity_notes,
        missing_fields=missing_fields or [],
        partial=partial,
        problem_type_id=problem_type_id,
        computed=computed or {},
        default_controls=default_controls or {},
    )


def _num(val: Any) -> float | None:
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(",", "")
    m = re.search(r"-?[\d.]+", s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def _parse_pp(val: Any) -> float | None:
    """Parse drift strings like '+5.0pp' or '-3.2pp' into percentage points."""
    n = _num(val)
    if n is None:
        return None
    return n


def _parse_rate(val: Any) -> float | None:
    return _num(val)


def _ctx_list(val: Any) -> list[str]:
    if isinstance(val, list):
        return [str(v).strip() for v in val if str(v).strip()]
    if val:
        return [str(val).strip()]
    return []


def solve_nba_stat_chase(
    ctx: dict[str, Any],
    question: str,
    *,
    games_remaining: int | None = None,
    expected_rate: float | None = None,
    target_value: float | None = None,
) -> SolverResult:
    gap_ctx = ctx.get("stat_gap") if isinstance(ctx.get("stat_gap"), dict) else {}
    player = str(gap_ctx.get("player") or ctx.get("player") or "Challenger").strip()
    target_name = str(gap_ctx.get("comparison") or "Leader").strip()
    stat = str(gap_ctx.get("stat") or "stat").strip()

    current = _num(gap_ctx.get("current_value"))
    target = _num(target_value if target_value is not None else gap_ctx.get("target_value"))
    gap = _num(gap_ctx.get("gap"))
    if gap is None and current is not None and target is not None:
        gap = target - current

    games = games_remaining
    if games is None:
        gr = gap_ctx.get("games_remaining") if gap_ctx else None
        games = int(gr) if gr is not None else _num(ctx.get("games_remaining"))
        games = int(games) if games is not None else None

    context_rate = _parse_rate(gap_ctx.get("rate_needed") or ctx.get("rate_needed"))
    exp_rate = expected_rate if expected_rate is not None else context_rate

    missing: list[str] = []
    if gap is None:
        missing.append("stat_gap.gap (or current_value and target_value)")
    if games is None:
        missing.append("games_remaining")

    data_used = [
        x
        for x in (
            f"Gap: **{gap:g}** {stat}" if gap is not None else "",
            f"Games remaining: **{games}**" if games is not None else "",
            f"Expected {stat}/game: **{exp_rate:g}**" if exp_rate is not None else "",
            f"Chase: **{player}** → **{target_name}**",
        )
        if x
    ]

    math_idea = "Rate-needed problem — can the challenger produce enough per game to close the gap?"
    variables = (
        "gap = target total − current total\n"
        "games_remaining = g\n"
        "required_rate = gap ÷ g\n"
        "expected_rate = recent production per game"
    )

    required_rate: float | None = None
    calc = ""
    if gap is not None and games and games > 0:
        required_rate = gap / games
        calc = (
            f"**required_rate** = gap ÷ games_remaining\n\n"
            f"= {gap:g} ÷ {games} = **{required_rate:.2f}** {stat}/game"
        )
        if exp_rate is not None:
            calc += f"\n\nCompare to expected **{exp_rate:g}** {stat}/game."
    elif gap is not None:
        calc = f"gap = **{gap:g}**. Set games remaining to compute required_rate."

    verdict = "Insufficient data"
    interpretation = ""
    if required_rate is not None and exp_rate is not None:
        cushion = exp_rate - required_rate
        if exp_rate >= required_rate * 1.05:
            verdict = "Likely — on pace to pass"
        elif exp_rate >= required_rate * 0.85:
            verdict = "Toss-up — close to required pace"
        else:
            verdict = "Unlikely — required pace is too high"
        interpretation = (
            f"If only **{games}** games remain, {player} needs **{required_rate:.1f}** {stat}/game. "
            f"At **{exp_rate:.1f}**/game (cushion **{cushion:+.1f}**), the chase looks **{verdict.split('—')[0].strip().lower()}**."
        )
    elif required_rate is not None:
        interpretation = (
            f"Required pace is **{required_rate:.2f}** {stat}/game. "
            "Adjust expected rate below to see if the chase is realistic."
        )
    elif missing:
        interpretation = (
            "We can model this as a rate-needed problem, but need gap and games remaining "
            "before computing required_rate."
        )

    sensitivity = (
        "**Games remaining** is the strongest lever — fewer games means a higher required_rate. "
        "**Expected rate** shifts the conclusion between Likely and Unlikely."
    )
    if required_rate and games:
        alt_games = max(1, games - 1)
        alt_req = gap / alt_games if gap else None
        if alt_req:
            sensitivity += f" At {alt_games} games left, required_rate rises to **{alt_req:.2f}**/game."

    return _coach_result(
        question=question,
        problem_type="NBA stat chase",
        math_idea=math_idea,
        variables=variables,
        data_used=data_used,
        calculation=calc,
        result=verdict if not missing or required_rate else "Partial — set missing inputs",
        interpretation=interpretation,
        assumptions=[
            f"{player} maintains recent minutes and role.",
            f"{target_name} may also add {stat} in remaining games (static gap model).",
            "Injury/rest can reduce effective games below the games-remaining input.",
        ],
        sensitivity_notes=sensitivity,
        missing_fields=missing,
        partial=bool(missing),
        problem_type_id=NBA_STAT_CHASE,
        computed={
            "gap": gap,
            "games_remaining": games,
            "required_rate": required_rate,
            "expected_rate": exp_rate,
            "verdict": verdict,
        },
        default_controls={
            "games_remaining": games if games is not None else 4,
            "expected_rate": exp_rate if exp_rate is not None else 3.0,
            "target_value": target if target is not None else 0.0,
        },
    )


def solve_baseball_trend(
    ctx: dict[str, Any],
    question: str,
    *,
    min_slope: float = 0.5,
    min_r2: float = 0.35,
) -> SolverResult:
    trend = ctx.get("trend_summary") if isinstance(ctx.get("trend_summary"), dict) else {}
    player = str(trend.get("player") or ctx.get("player") or "Player").strip()
    metrics = _ctx_list(ctx.get("metrics"))
    stat = str(trend.get("stat") or (metrics[0] if metrics else "stat")).strip()

    slope = _num(trend.get("slope"))
    r2 = _num(trend.get("r2"))
    delta = _num(trend.get("delta"))
    direction = str(trend.get("direction") or "unknown").strip()
    latest = trend.get("latest")
    previous = trend.get("previous")

    missing: list[str] = []
    if slope is None:
        missing.append("trend_summary.slope")
    if r2 is None:
        missing.append("trend_summary.r2")

    strength = "unknown"
    noise = "unknown"
    meaningful = False
    if slope is not None and r2 is not None:
        abs_slope = abs(slope)
        if abs_slope >= min_slope and r2 >= min_r2:
            strength = "strong"
            noise = "low"
            meaningful = True
        elif abs_slope >= min_slope * 0.5 and r2 < min_r2:
            strength = "noisy"
            noise = "high"
        else:
            strength = "weak"
            noise = "moderate" if r2 >= min_r2 else "high"

    data_used = [
        x
        for x in (
            f"Slope: **{slope:g}** {stat}/season" if slope is not None else "",
            f"R²: **{r2:g}**" if r2 is not None else "",
            f"Direction: **{direction}**" if direction != "unknown" else "",
            f"Player: **{player}**",
            f"Thresholds: slope ≥ {min_slope}, R² ≥ {min_r2}",
        )
        if x
    ]

    math_idea = "Trend strength vs noise — is the slope real or year-to-year randomness?"
    variables = (
        "slope = yearly change in the stat\n"
        "R² = consistency of the linear fit (0–1)\n"
        "delta = total change over the trend window"
    )

    calc = (
        f"Meaningful if |slope| ≥ **{min_slope}** and R² ≥ **{min_r2}**\n\n"
        + (
            f"|slope| = **{abs(slope):g}**, R² = **{r2:g}**"
            if slope is not None and r2 is not None
            else "Need slope and R² from the Trends page."
        )
    )
    if delta is not None:
        calc += f"\n\nNet change (delta) = **{delta:g}** over the window."

    if meaningful:
        result = f"Meaningful {direction} trend on {stat}"
        interp = (
            f"Slope **{slope:g}**/year with R² **{r2:g}** exceeds your thresholds — "
            "more than a one-year spike, but confirm sample size and playing time."
        )
    elif strength == "noisy":
        result = "Noisy trend — direction without consistent fit"
        interp = (
            f"Direction is {direction}, but R² **{r2:g}** < **{min_r2}** — "
            "year-to-year noise may dominate. Monitor, don't overreact."
        )
    elif strength == "weak":
        result = "Weak trend — not meaningful for decisions"
        interp = (
            f"|slope| or delta on {stat} is small vs thresholds — not strong evidence of real change."
        )
    else:
        result = "Partial — need slope and R²"
        interp = (
            f"We can model this as trend vs noise on {stat}, but need regression output from Baseball Trends."
        )

    sensitivity = (
        "**R² threshold** is the main filter for noise — raising it demands a cleaner fit. "
        "**Slope threshold** filters gradual vs sharp trends."
    )

    return _coach_result(
        question=question,
        problem_type="Trend significance",
        math_idea=math_idea,
        variables=variables,
        data_used=data_used,
        calculation=calc,
        result=result,
        interpretation=interp,
        assumptions=[
            "Seasons in the window are comparable (role, health, league environment).",
            f"{stat} is measured on similar playing-time opportunity each year.",
        ],
        sensitivity_notes=sensitivity,
        missing_fields=missing,
        partial=bool(missing),
        problem_type_id=BASEBALL_TREND,
        computed={
            "slope": slope,
            "r2": r2,
            "strength": strength,
            "noise": noise,
            "meaningful": meaningful,
        },
        default_controls={"min_slope": min_slope, "min_r2": min_r2},
    )


def solve_investment_rebalance(
    ctx: dict[str, Any],
    question: str,
    *,
    drift_threshold: float = 5.0,
    risk_tolerance: str = "moderate",
) -> SolverResult:
    drift_raw = ctx.get("rebalance_drift") if isinstance(ctx.get("rebalance_drift"), dict) else {}
    current_w = ctx.get("current_weights") if isinstance(ctx.get("current_weights"), dict) else {}
    target_w = ctx.get("target_weights") if isinstance(ctx.get("target_weights"), dict) else {}
    parsed: dict[str, float] = {}
    for ticker, val in drift_raw.items():
        n = _parse_pp(val)
        if n is not None:
            parsed[str(ticker)] = n

    health = ctx.get("health_score")
    objective = str(ctx.get("objective") or ctx.get("portfolio_objective") or "").strip()

    missing: list[str] = []
    if not parsed:
        missing.append("rebalance_drift")

    overweight = underweight = None
    max_drift = 0.0
    if parsed:
        overweight = max(parsed.items(), key=lambda x: x[1])
        underweight = min(parsed.items(), key=lambda x: x[1])
        max_drift = max(abs(v) for v in parsed.values())

    largest = ""
    if overweight:
        largest = f"Largest drift: **{overweight[0]}** {overweight[1]:+.1f}pp"
    data_used = [
        x
        for x in (
            f"Health score: **{health}**" if health is not None else "",
            largest,
            f"Rebalance threshold: **{drift_threshold:g}pp**",
            f"Goal: **{objective}**" if objective else "",
            f"Risk tolerance: **{risk_tolerance}**",
        )
        if x
    ]

    math_idea = "Threshold / drift problem — compare each holding's weight to its target."
    variables = (
        "current_weight_i = portfolio weight today\n"
        "target_weight_i = policy target\n"
        "drift_i = current_weight_i − target_weight_i\n"
        "threshold = max acceptable |drift| before rebalancing"
    )

    calc_lines = [f"**drift_i** = current − target (percentage points)", f"**threshold** = {drift_threshold:g}pp"]
    for ticker, d in sorted(parsed.items(), key=lambda x: abs(x[1]), reverse=True)[:3]:
        cur = current_w.get(ticker, "—")
        tgt = target_w.get(ticker, "—")
        calc_lines.append(f"**{ticker}**: {cur} current, {tgt} target → drift **{d:+.1f}pp**")
    if parsed:
        calc_lines.append(f"\nMax |drift| = **{max_drift:.1f}pp**")
    calc = "\n".join(calc_lines)

    if max_drift >= drift_threshold:
        action = "Rebalance — drift exceeds threshold"
    elif max_drift >= drift_threshold * 0.6:
        action = "Monitor — material drift but below threshold"
    else:
        action = "No action — within tolerance"

    if risk_tolerance.lower() in ("low", "conservative") and max_drift >= drift_threshold * 0.8:
        action = "Rebalance — conservative tolerance lowers effective threshold"

    interp = action + "."
    if overweight and underweight:
        interp += (
            f" **{overweight[0]}** is {overweight[1]:+.1f}pp overweight; "
            f"**{underweight[0]}** is {underweight[1]:+.1f}pp underweight."
        )
    interp += " Taxes and trading costs may change the practical decision."

    sensitivity = (
        "**Drift threshold** is the main lever — lower threshold → rebalance sooner. "
        "**Risk tolerance** shifts how aggressively you act on the same drift."
    )

    return _coach_result(
        question=question,
        problem_type="Portfolio drift / threshold decision",
        math_idea=math_idea,
        variables=variables,
        data_used=data_used,
        calculation=calc,
        result=action,
        interpretation=interp,
        assumptions=[
            "Target weights reflect your stated objective and horizon.",
            "Does not include tax lot or transaction cost analysis.",
        ],
        sensitivity_notes=sensitivity,
        missing_fields=missing,
        partial=bool(missing),
        problem_type_id=INVESTMENT_REBALANCE,
        computed={
            "max_drift_pp": max_drift,
            "overweight": overweight,
            "underweight": underweight,
            "action": action,
        },
        default_controls={"drift_threshold": drift_threshold, "risk_tolerance": risk_tolerance},
    )


def solve_investment_risk_return(
    ctx: dict[str, Any],
    question: str,
    *,
    min_sharpe: float = 0.5,
    max_volatility: float = 15.0,
    acceptable_volatility: float | None = None,
) -> SolverResult:
    exp_ret = _num(ctx.get("expected_return"))
    vol = _num(ctx.get("volatility"))
    sharpe = _num(ctx.get("sharpe_ratio"))
    drawdown = _num(ctx.get("max_drawdown"))
    health = ctx.get("health_score")
    holdings = _ctx_list(ctx.get("holdings"))
    risk_level = str(ctx.get("risk_level") or "moderate").strip()

    max_vol = acceptable_volatility if acceptable_volatility is not None else max_volatility

    missing: list[str] = []
    if exp_ret is None:
        missing.append("expected_return")
    if vol is None:
        missing.append("volatility")

    data_used = [
        x
        for x in (
            f"Expected return: **{exp_ret:g}%**" if exp_ret is not None else "",
            f"Volatility: **{vol:g}%**" if vol is not None else "",
            f"Sharpe ratio: **{sharpe:g}**" if sharpe is not None else "",
            f"Max drawdown: **{drawdown:g}%**" if drawdown is not None else "",
            f"Acceptable volatility: **{max_vol:g}%**",
        )
        if x
    ]

    math_idea = "Return per unit of risk — is the portfolio compensated for volatility?"
    variables = (
        "Sharpe ≈ (return − risk_free) / volatility\n"
        "max_drawdown = worst peak-to-trough loss\n"
        "acceptable_volatility = your risk ceiling"
    )

    calc_parts = ["**Sharpe** ≈ return / volatility (simplified, no risk-free rate subtracted)"]
    if sharpe is not None:
        calc_parts.append(f"Sharpe = **{sharpe:g}**")
    elif exp_ret is not None and vol and vol > 0:
        implied = exp_ret / vol
        calc_parts.append(f"Rough return/vol ratio ≈ **{implied:.2f}** (no risk-free rate subtracted)")
        sharpe = implied

    verdict = "Insufficient data"
    warnings: list[str] = []
    if vol is not None and vol > max_vol:
        warnings.append(f"Volatility **{vol:g}%** exceeds your **{max_vol:g}%** tolerance.")
    if drawdown is not None and drawdown < -25:
        warnings.append(f"Max drawdown **{drawdown:g}%** is severe.")
    if sharpe is not None:
        if sharpe >= min_sharpe and (vol is None or vol <= max_vol):
            verdict = "Yes — return appears worth the risk for your thresholds"
        elif sharpe >= min_sharpe * 0.8:
            verdict = "Borderline — return is close to your risk tolerance"
        else:
            verdict = "No — return does not compensate for volatility at your Sharpe floor"

    interp_parts = [verdict]
    if warnings:
        interp_parts.append(" ".join(warnings))
    if exp_ret is not None and vol is not None:
        interp_parts.append(
            f"You earn **{exp_ret:g}%** expected return for **{vol:g}%** volatility ({risk_level} profile)."
        )

    sensitivity = (
        "**Acceptable volatility** is the strongest filter — lower it and the same portfolio looks riskier. "
        "**Minimum Sharpe** sets how much return per unit risk you demand."
    )

    assumptions = [
        f"Risk profile: {risk_level}.",
        "Return and volatility are historical estimates unless noted forward.",
    ]

    return _coach_result(
        question=question,
        problem_type="Risk-return tradeoff",
        math_idea=math_idea,
        variables=variables,
        data_used=data_used,
        calculation="\n\n".join(calc_parts),
        result=verdict,
        interpretation=" ".join(interp_parts),
        assumptions=assumptions,
        sensitivity_notes=sensitivity,
        missing_fields=missing,
        partial=bool(missing),
        problem_type_id=INVESTMENT_RISK_RETURN,
        computed={
            "expected_return": exp_ret,
            "volatility": vol,
            "sharpe": sharpe,
            "drawdown": drawdown,
            "verdict": verdict,
        },
        default_controls={
            "min_sharpe": min_sharpe,
            "max_volatility": max_vol,
            "acceptable_volatility": max_vol,
        },
    )


def _generic_solver(route: ProblemRoute, question: str, ctx: dict[str, Any]) -> SolverResult:
    missing_note = ""
    if route.missing_fields:
        missing_note = (
            "We can model this as a threshold/decision problem, but need: "
            + ", ".join(route.missing_fields)
            + "."
        )
    return _coach_result(
        question=question,
        problem_type=route.problem_type,
        math_idea="Define the measurable quantity, baseline, and decision threshold.",
        variables="variable = what you measure\nbaseline = comparison point\nthreshold = decision cutoff",
        data_used=[f"Source: **{route.source_app}**"],
        calculation="State the claim as one number, then compare to baseline ± uncertainty.",
        result="Framework — attach numeric context from the source app",
        interpretation=missing_note or "Translate the question into one measurable quantity.",
        assumptions=["Context from the source app reflects the user's current view."],
        sensitivity_notes="Adding missing fields enables a domain-specific solver.",
        missing_fields=list(route.missing_fields),
        partial=True,
        problem_type_id=route.problem_type_id,
    )


def dispatch_solver(
    route: ProblemRoute,
    question: str,
    ctx: dict[str, Any],
    params: dict[str, Any] | None = None,
) -> SolverResult:
    p = dict(params or {})
    pid = route.problem_type_id

    if pid == NBA_STAT_CHASE:
        return solve_nba_stat_chase(
            ctx,
            question,
            games_remaining=p.get("games_remaining"),
            expected_rate=p.get("expected_rate"),
            target_value=p.get("target_value"),
        )
    if pid == BASEBALL_TREND:
        return solve_baseball_trend(
            ctx,
            question,
            min_slope=float(p.get("min_slope", 0.5)),
            min_r2=float(p.get("min_r2", 0.35)),
        )
    if pid == INVESTMENT_REBALANCE:
        return solve_investment_rebalance(
            ctx,
            question,
            drift_threshold=float(p.get("drift_threshold", 5.0)),
            risk_tolerance=str(p.get("risk_tolerance", "moderate")),
        )
    if pid == INVESTMENT_RISK_RETURN:
        return solve_investment_risk_return(
            ctx,
            question,
            min_sharpe=float(p.get("min_sharpe", 0.5)),
            max_volatility=float(p.get("max_volatility", 15.0)),
            acceptable_volatility=p.get("acceptable_volatility"),
        )

    # Non-primary types reuse closest solver or generic
    if pid in (NBA_WIN_PROBABILITY, NBA_LEGACY_COMPARISON):
        wp = ctx.get("win_probability") or ctx.get("series_probability")
        return _coach_result(
            question=question,
            problem_type=route.problem_type,
            math_idea="Probability reasonableness — does the quoted chance match the setup?",
            variables="p = quoted win/series probability\nprior = strength-model baseline",
            data_used=[f"Quoted probability: **{wp}**"] if wp else [],
            calculation="Compare p to prior ±10pp; list what must be true if gap is large.",
            result=str(wp) if wp else "Attach win/series probability",
            interpretation=(
                f"If **{wp}** is >15pp from a simple strength prior, stress-test injuries and matchups."
                if wp
                else "Load Live Game Center or Matchup Intelligence for a numeric probability."
            ),
            assumptions=["Probability refers to the same event horizon (game vs series)."],
            sensitivity_notes="Star minutes ±10% shifts playoff probability materially.",
            missing_fields=route.missing_fields,
            partial=bool(route.missing_fields),
            problem_type_id=pid,
            computed={"probability": wp},
        )

    if pid == NBA_MATCHUP_EDGE:
        team = str(ctx.get("team") or "").strip()
        opp = str(ctx.get("opponent") or "").strip()
        adv = ctx.get("matchup_advantages")
        adv_text = str(adv[0])[:120] if isinstance(adv, list) and adv else ""
        inj = str(ctx.get("injury_summary") or "").strip()
        wp = ctx.get("win_probability") or ctx.get("series_probability")
        return _coach_result(
            question=question,
            problem_type=route.problem_type,
            math_idea="Matchup edge — weight injuries and schematic advantages vs model probability.",
            variables="edge = injury + positional mismatches\np = model series probability",
            data_used=_cap_data_used([
                f"**{team}** vs **{opp}**",
                f"Scouting edge: {adv_text}" if adv_text else "",
                f"Injuries: {inj}" if inj else "",
                f"Model probability: **{wp}**" if wp else "",
            ]),
            calculation="Large p without matching edge → optimism; injury downgrade → lower p.",
            result="Matchup assessed" if adv_text or inj else "Load matchup advantages",
            interpretation=" ".join(
                x
                for x in (
                    f"Edge for **{team}** vs **{opp}**.",
                    f"Advantage: {adv_text}" if adv_text else "",
                    f"Injury: {inj}" if inj else "",
                )
                if x
            ),
            assumptions=["Matchup summaries reflect the loaded scouting board."],
            sensitivity_notes="Injury downgrades or hot shooting swing probability ±10–15 pp.",
            missing_fields=route.missing_fields,
            partial=bool(route.missing_fields),
            problem_type_id=pid,
            computed={"advantages": adv},
        )

    if pid == BASEBALL_HISTORICAL:
        snap = ctx.get("historical_snapshot") if isinstance(ctx.get("historical_snapshot"), dict) else {}
        player = str(ctx.get("player") or "").strip()
        sort_stat = str(snap.get("sort_stat") or "stat")
        rows = snap.get("top_rows") if isinstance(snap.get("top_rows"), list) else []
        row_bits = []
        for row in rows[:3]:
            if not isinstance(row, dict):
                continue
            name = str(row.get("player") or "").strip()
            val = row.get(sort_stat) or row.get(str(sort_stat))
            if name and val is not None:
                row_bits.append(f"{name}: {sort_stat}={val}")
        calc_detail = "; ".join(row_bits[:3])
        return _coach_result(
            question=question,
            problem_type=route.problem_type,
            math_idea="Outlier check — is this row unusual vs peers in the filter window?",
            variables="x = stat value\npeers = neighboring rows in the filtered table",
            data_used=_cap_data_used([f"Sort stat: **{sort_stat}**", f"Player: **{player}**"] + row_bits[:2]),
            calculation=f"Compare **{sort_stat}** to next-ranked rows. Outlier if >1.5× next rank.\n\n{calc_detail}",
            result=f"Snapshot on **{sort_stat}**" if row_bits else "Attach historical_snapshot.top_rows",
            interpretation=(
                f"Top rows: {calc_detail}." if row_bits else f"Compare {player}'s row to neighbors."
            ),
            assumptions=[f"Filters: {ctx.get('filters_applied') or snap.get('year_range') or 'see snapshot'}"],
            sensitivity_notes="Rate stats need playing-time context; counting stats need AB/PA.",
            missing_fields=route.missing_fields,
            partial=not row_bits,
            problem_type_id=pid,
            computed={"top_rows": rows[:3]},
        )

    if pid == BASEBALL_PLAYER_COMPARE:
        pa, pb = ctx.get("player_a"), ctx.get("player_b")
        return _coach_result(
            question=question,
            problem_type="Player comparison",
            math_idea="Value gap = rate-stat difference adjusted for playing time and scarcity.",
            variables="value_i = rate stats per PA × playing-time projection",
            data_used=[f"**{pa}** vs **{pb}**"] if pa and pb else [],
            calculation="Subtract rate-based value scores; weight scarce categories.",
            result="Compare rate stats per PA with replacement baseline",
            interpretation="If gaps are within one standard error, call it too close to call.",
            assumptions=["Same position eligibility matters for roster fit."],
            sensitivity_notes="Weight scarce categories (SB, HR) higher in category leagues.",
            missing_fields=route.missing_fields,
            partial=bool(route.missing_fields),
            problem_type_id=pid,
        )

    if pid == INVESTMENT_MACRO:
        macro = ctx.get("macro_outlook") or ctx.get("macro_summary")
        fwd = str(ctx.get("context_note_forward") or "").strip()
        hist = str(ctx.get("context_note_historical") or "").strip()
        return _coach_result(
            question=question,
            problem_type="Macro sensitivity",
            math_idea="Stress-test return/vol assumptions under a macro scenario.",
            variables="scenario = macro outlook\nforward_return vs historical_return",
            data_used=_cap_data_used([f"Macro outlook: **{macro}**"] if macro else []),
            calculation="Compare base-case return/vol to recession or rate-shock scenario.",
            result=str(macro) if macro else "Attach macro outlook",
            interpretation=(fwd or "Forward returns may diverge from historical metrics.") + (f" {hist}" if hist else ""),
            assumptions=[str(macro or "Macro assumptions not attached.") + (f" {fwd}" if fwd else "")],
            sensitivity_notes="Recession probability shifts bond/equity correlation.",
            missing_fields=route.missing_fields,
            partial=True,
            problem_type_id=pid,
        )

    return _generic_solver(route, question, ctx)


def solve_suite_question(
    question: str,
    *,
    source_app: str = "",
    context: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> tuple[ProblemRoute, SolverResult]:
    ctx = dict(context or {})
    route = route_suite_question(question, source_app=source_app, context=ctx)
    result = dispatch_solver(route, question, ctx, params)
    if result is None:
        raise ValueError("dispatch_solver returned None")
    return route, result
