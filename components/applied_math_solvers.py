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
    problem_detected: str
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

    data_used: list[str] = []
    if current is not None:
        data_used.append(f"{player} current {stat}: **{current:g}**")
    if target is not None:
        data_used.append(f"{target_name} target total: **{target:g}**")
    if gap is not None:
        data_used.append(f"Gap to close: **{gap:g}** {stat}")
    if games is not None:
        data_used.append(f"Games remaining: **{games}**")
    if exp_rate is not None:
        data_used.append(f"Expected {stat} per game: **{exp_rate:g}**")

    required_rate: float | None = None
    calc = ""
    if gap is not None and games and games > 0:
        required_rate = gap / games
        calc = (
            f"**Required rate** = gap ÷ games remaining\n\n"
            f"= {gap:g} ÷ {games} = **{required_rate:.2f}** {stat}/game"
        )
    elif gap is not None:
        calc = f"Gap = **{gap:g}**. Set games remaining to compute required rate per game."

    verdict = "Insufficient data"
    interpretation = ""
    if required_rate is not None and exp_rate is not None:
        cushion = exp_rate - required_rate
        pct = (exp_rate / required_rate * 100) if required_rate > 0 else 0
        if exp_rate >= required_rate * 1.05:
            verdict = "**Likely** — expected rate exceeds required rate"
        elif exp_rate >= required_rate * 0.85:
            verdict = "**Toss-up** — expected rate is close to required rate"
        else:
            verdict = "**Unlikely** — expected rate falls short of required rate"
        interpretation = (
            f"{player} needs **{required_rate:.2f}** {stat}/game vs an expected **{exp_rate:.2f}** "
            f"(cushion **{cushion:+.2f}**/game, {pct:.0f}% of required pace). "
            f"{verdict.split('—')[0].strip()}."
        )
    elif required_rate is not None:
        interpretation = (
            f"Required pace is **{required_rate:.2f}** {stat}/game. "
            "Set expected rate per game below to compare likelihood."
        )
    elif missing:
        interpretation = (
            "We can partially analyze this chase, but need the missing fields below "
            "before computing required rate."
        )

    sensitivity = (
        "If **games remaining** drops, required rate rises (harder). "
        "If **expected rate** rises above required rate, conclusion shifts toward **Likely**."
    )
    if required_rate and games:
        alt_games = max(1, games - 1)
        alt_req = gap / alt_games if gap else None
        if alt_req:
            sensitivity += f" Example: at {alt_games} games, required rate = **{alt_req:.2f}**/game."

    return SolverResult(
        problem_detected=f"NBA stat chase: {question.strip()}",
        data_used=data_used,
        calculation=calc,
        result=verdict if not missing or required_rate else "Partial — set missing inputs",
        interpretation=interpretation,
        assumptions=[
            f"{player} maintains recent minutes and role.",
            f"{target_name} may also add {stat} in remaining games (this model uses a static gap).",
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

    data_used = [f"Player: **{player}**", f"Metric: **{stat}**"]
    if slope is not None:
        data_used.append(f"Slope: **{slope:g}**/season")
    if r2 is not None:
        data_used.append(f"R²: **{r2:g}**")
    if delta is not None:
        data_used.append(f"Net change (delta): **{delta:g}**")
    if direction != "unknown":
        data_used.append(f"Direction: **{direction}**")
    if latest is not None:
        data_used.append(f"Latest value: **{latest}**")

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

    calc = (
        f"**Trend test:** |slope| ≥ {min_slope} and R² ≥ {min_r2}\n\n"
        + (f"|slope| = **{abs(slope):g}**, R² = **{r2:g}**" if slope is not None and r2 is not None else "Need slope and R² from trend data.")
    )

    if meaningful:
        result = f"**Meaningful {direction} trend** on {stat}"
        interp = (
            f"The {stat} trend for {player} looks **meaningful**: slope magnitude and fit exceed your thresholds. "
            "Treat as signal, not noise — but confirm playing-time stability."
        )
    elif strength == "noisy":
        result = f"**Noisy trend** — slope present but low fit"
        interp = (
            f"{player}'s {stat} shows direction ({direction}) but **R² is below {min_r2}**, "
            "so year-to-year noise may dominate. **Monitor, don't overreact.**"
        )
    elif strength == "weak":
        result = f"**Weak trend** — not meaningful for decisions"
        interp = (
            f"Slope and/or delta on {stat} are small relative to thresholds. "
            "This is **not strong evidence** of a real change."
        )
    else:
        result = "Partial — attach trend_summary with slope and R²"
        interp = (
            f"Without season-by-season {stat} regression output, we cannot score trend strength numerically. "
            "Use the Baseball Trends page Advanced Trend Intelligence row."
        )

    sensitivity = (
        f"Raising **min R²** toward 0.5 makes fewer trends count as meaningful. "
        f"Raising **min slope** filters out gradual changes. "
        "What would make it meaningful: |slope| above threshold **and** R² above threshold **and** stable playing time."
    )

    return SolverResult(
        problem_detected=f"Baseball trend significance: {question.strip()}",
        data_used=data_used,
        calculation=calc,
        result=result,
        interpretation=interp,
        assumptions=[
            "Seasons in the trend window are comparable (role, health, league environment).",
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
    parsed: dict[str, float] = {}
    for ticker, val in drift_raw.items():
        n = _parse_pp(val)
        if n is not None:
            parsed[str(ticker)] = n

    health = ctx.get("health_score")
    total_d = str(ctx.get("total_drift") or "").strip()
    recs = _ctx_list(ctx.get("rebalance_recommendation"))

    missing: list[str] = []
    if not parsed:
        missing.append("rebalance_drift")

    data_used: list[str] = []
    if health is not None:
        data_used.append(f"Health score: **{health}**")
    if total_d:
        data_used.append(f"Total drift: **{total_d}**")
    for t, d in sorted(parsed.items(), key=lambda x: abs(x[1]), reverse=True)[:4]:
        data_used.append(f"{t}: drift **{d:+.1f}pp**")
    if recs:
        data_used.append(f"Recommendations: {', '.join(recs[:2])}")

    overweight = underweight = None
    max_drift = 0.0
    if parsed:
        overweight = max(parsed.items(), key=lambda x: x[1])
        underweight = min(parsed.items(), key=lambda x: x[1])
        max_drift = max(abs(v) for v in parsed.values())

    calc = (
        f"**Drift** = current weight − target weight (pp)\n\n"
        f"**Threshold** = {drift_threshold:g} pp\n\n"
        + (f"Max |drift| = **{max_drift:.1f}pp**" if parsed else "No drift table attached.")
    )

    if max_drift >= drift_threshold:
        action = "**Rebalance** — drift exceeds threshold"
    elif max_drift >= drift_threshold * 0.6:
        action = "**Monitor** — drift is material but below threshold"
    else:
        action = "**No action** — drift within tolerance"

    tol_note = f"Risk tolerance: **{risk_tolerance}**."
    if risk_tolerance.lower() in ("low", "conservative") and max_drift >= drift_threshold * 0.8:
        action = "**Rebalance** — conservative tolerance lowers effective threshold"
        tol_note += " Conservative profile triggers earlier."

    interp_parts = [action + "."]
    if overweight:
        interp_parts.append(f"Most overweight: **{overweight[0]}** ({overweight[1]:+.1f}pp).")
    if underweight:
        interp_parts.append(f"Most underweight: **{underweight[0]}** ({underweight[1]:+.1f}pp).")

    sensitivity = (
        f"Lower **drift threshold** → more frequent rebalance signals. "
        f"Higher threshold → fewer trades. "
        "Compare expected risk reduction to transaction costs and taxes before acting."
    )

    return SolverResult(
        problem_detected=f"Investment rebalance: {question.strip()}",
        data_used=data_used,
        calculation=calc,
        result=action.replace("**", ""),
        interpretation=" ".join(interp_parts),
        assumptions=[
            "Target weights reflect your stated objective and horizon.",
            tol_note,
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

    data_used: list[str] = []
    if exp_ret is not None:
        data_used.append(f"Expected return: **{exp_ret:g}%**")
    if vol is not None:
        data_used.append(f"Volatility: **{vol:g}%**")
    if sharpe is not None:
        data_used.append(f"Sharpe ratio: **{sharpe:g}**")
    if drawdown is not None:
        data_used.append(f"Max drawdown: **{drawdown:g}%**")
    if health is not None:
        data_used.append(f"Health score: **{health}**")
    if holdings:
        data_used.append(f"Holdings: {', '.join(holdings[:5])}")

    calc_parts = ["**Return per unit risk** ≈ Sharpe = (return − risk-free) / volatility"]
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
            verdict = "**Yes — return appears worth the risk** for your thresholds"
        elif sharpe >= min_sharpe * 0.8:
            verdict = "**Borderline — return is close to your risk tolerance**"
        else:
            verdict = "**No — return does not compensate for volatility** at your Sharpe floor"

    interp_parts = [verdict.replace("**", "")]
    if warnings:
        interp_parts.append(" ".join(warnings))
    if exp_ret is not None and vol is not None:
        interp_parts.append(f"You earn **{exp_ret:g}%** expected return for **{vol:g}%** volatility ({risk_level} profile).")

    sensitivity = (
        f"Lower **acceptable volatility** → harder to justify the portfolio. "
        f"Higher **minimum Sharpe** → stricter return-per-risk requirement. "
        "Macro shocks can raise volatility without changing long-run expected return."
    )

    macro = ctx.get("macro_outlook") or ctx.get("macro_summary")
    assumptions = [f"Risk profile: **{risk_level}**.", "Return/volatility are historical estimates unless noted forward."]
    if macro:
        assumptions.append(f"Macro outlook in context: {macro}")

    return SolverResult(
        problem_detected=f"Investment risk-return: {question.strip()}",
        data_used=data_used,
        calculation="\n\n".join(calc_parts),
        result=verdict.replace("**", ""),
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
    data_used = [f"Source: **{route.source_app}**"]
    for key in route.available_fields[:6]:
        val = ctx.get(key.split(".")[0])
        if val is not None:
            data_used.append(f"{key}: {val}")
    missing_note = ""
    if route.missing_fields:
        missing_note = (
            "We can partially analyze this, but the following data is missing: "
            + ", ".join(route.missing_fields)
            + ". State the claim as one measurable quantity and compare to a baseline."
        )
    return SolverResult(
        problem_detected=f"{route.problem_type}: {question.strip()}",
        data_used=data_used,
        calculation="Define **variable**, **baseline**, and **decision threshold** for this question.",
        result="Framework answer — attach numeric context from the source app",
        interpretation=missing_note or "Translate the question into a single number, then compare to what you'd give up.",
        assumptions=["Context from the source app reflects the user's current view."],
        sensitivity_notes="Adding the missing fields enables a domain-specific solver instead of this fallback.",
        missing_fields=list(route.missing_fields),
        partial=True,
        problem_type_id=route.problem_type_id,
        computed={},
        default_controls={},
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
        return SolverResult(
            problem_detected=f"{route.problem_type}: {question.strip()}",
            data_used=[f"Probability: **{wp}**"] if wp else [],
            calculation="Compare quoted probability to strength model ±10% injury/minutes sensitivity.",
            result=str(wp) if wp else "Attach win/series probability from NBA page",
            interpretation=(
                f"If **{wp}** is >15pp from a simple strength prior, list what must be true (injury edge, home court)."
                if wp
                else "Load Live Game Center or Matchup Intelligence for a numeric probability."
            ),
            assumptions=["Probability refers to the same event horizon (game vs series)."],
            sensitivity_notes="Shift star minutes ±10% to stress-test the probability.",
            missing_fields=route.missing_fields,
            partial=bool(route.missing_fields),
            problem_type_id=pid,
            computed={"probability": wp},
            default_controls={},
        )

    if pid == NBA_MATCHUP_EDGE:
        team = str(ctx.get("team") or "").strip()
        opp = str(ctx.get("opponent") or "").strip()
        adv = ctx.get("matchup_advantages")
        adv_text = str(adv[0])[:240] if isinstance(adv, list) and adv else ""
        inj = str(ctx.get("injury_summary") or "").strip()
        series_rec = str(ctx.get("series_record") or "").strip()
        wp = ctx.get("win_probability") or ctx.get("series_probability")
        data_used = [f"**{team}** vs **{opp}**"]
        if series_rec:
            data_used.append(f"Series record: **{series_rec}**")
        if adv_text:
            data_used.append(f"Edge: {adv_text}")
        if inj:
            data_used.append(f"Injuries: {inj}")
        if wp:
            data_used.append(f"Model probability: **{wp}**")
        interp_parts = [f"Matchup edge analysis for **{team}** vs **{opp}**."]
        if adv_text:
            interp_parts.append(f"Scouting advantage: {adv_text}")
        if inj:
            interp_parts.append(f"Injury factor: {inj}")
        if wp:
            interp_parts.append(f"Compare model **{wp}** to the stated advantages — large gaps imply optimism.")
        return SolverResult(
            problem_detected=f"{route.problem_type}: {question.strip()}",
            data_used=data_used,
            calculation="Edge score = injury availability + positional mismatches − series margin deficit.",
            result="Matchup edge assessed from scouting context" if adv_text or inj else "Load matchup advantages",
            interpretation=" ".join(interp_parts),
            assumptions=["Matchup summaries reflect the loaded scouting board."],
            sensitivity_notes="Injury downgrades or hot shooting can swing series probability ±10–15 pp.",
            missing_fields=route.missing_fields,
            partial=bool(route.missing_fields),
            problem_type_id=pid,
            computed={"advantages": adv},
            default_controls={},
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
                row_bits.append(f"**{name}**: {sort_stat}={val}")
        return SolverResult(
            problem_detected=f"{route.problem_type}: {question.strip()}",
            data_used=row_bits or [f"Player: **{player}**"],
            calculation=f"Compare **{sort_stat}** to peer rows — outlier if >1.5× next rank or z-score > ~2.",
            result=f"Snapshot rows on **{sort_stat}**" if row_bits else "Attach historical_snapshot.top_rows",
            interpretation=(
                "Top rows: " + "; ".join(row_bits) + "."
                if row_bits
                else f"Compare {player}'s row to neighbors in the Historical Explorer table."
            ),
            assumptions=[f"Filters: {ctx.get('filters_applied') or snap.get('year_range') or 'see snapshot'}"],
            sensitivity_notes="Rate stats need playing-time context; counting stats need AB/PA.",
            missing_fields=route.missing_fields,
            partial=not row_bits,
            problem_type_id=pid,
            computed={"top_rows": rows[:3]},
            default_controls={},
        )

    if pid == BASEBALL_PLAYER_COMPARE:
        pa, pb = ctx.get("player_a"), ctx.get("player_b")
        return SolverResult(
            problem_detected=f"Player comparison: {question.strip()}",
            data_used=[f"**{pa}** vs **{pb}**"] if pa and pb else [],
            calculation="Value gap ≈ rate-stat difference × playing-time projection, weighted by league scarcity.",
            result="Compare rate stats per PA with replacement-level baseline.",
            interpretation="If gaps are within one standard error of career rates, call it **too close to call**.",
            assumptions=["Same position eligibility matters for roster fit."],
            sensitivity_notes="Weight scarce categories (SB, HR) higher in category leagues.",
            missing_fields=route.missing_fields,
            partial=bool(route.missing_fields),
            problem_type_id=pid,
            computed={},
            default_controls={},
        )

    if pid == INVESTMENT_MACRO:
        macro = ctx.get("macro_outlook") or ctx.get("macro_summary")
        fwd = str(ctx.get("context_note_forward") or "").strip()
        hist = str(ctx.get("context_note_historical") or "").strip()
        assumption = str(macro or "Macro assumptions not attached.")
        if fwd:
            assumption += f" Forward note: {fwd}"
        return SolverResult(
            problem_detected=f"Macro sensitivity: {question.strip()}",
            data_used=[f"Macro: **{macro}**"] if macro else [],
            calculation="Stress portfolio return/vol under macro scenario vs base case.",
            result=str(macro) if macro else "Attach macro outlook from Macro tab",
            interpretation=(fwd or "Forward returns may diverge from historical metrics.") + (f" {hist}" if hist else ""),
            assumptions=[assumption],
            sensitivity_notes="Recession probability shifts bond/equity correlation assumptions.",
            missing_fields=route.missing_fields,
            partial=True,
            problem_type_id=pid,
            computed={},
            default_controls={},
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
    return route, result
