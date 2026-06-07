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
    # Conclusion engine — answer-first UX
    conclusion: str = ""
    confidence_pct: int | None = None
    confidence_label: str = ""
    reasons: list[str] = field(default_factory=list)
    pivot_assumption: str = ""
    sensitivity_rows: list[dict[str, str]] = field(default_factory=list)
    model_note: str = ""
    data_would_improve: list[str] = field(default_factory=list)

    # Legacy alias — older code/tests referenced problem_detected
    @property
    def problem_detected(self) -> str:
        if self.problem_type and self.question:
            return f"{self.problem_type}: {self.question}"
        return self.problem_type or self.question


def _cap_data_used(lines: list[str], limit: int = 5) -> list[str]:
    return [ln for ln in lines if ln][:limit]


def _confidence_label(pct: int) -> str:
    if pct >= 75:
        return "High"
    if pct >= 55:
        return "Medium"
    return "Low"


def _route_confidence_pct(route: ProblemRoute, partial: bool, missing_count: int) -> int:
    base = float(route.confidence)
    if partial:
        base = max(0.25, base - 0.12 * max(1, missing_count))
    return int(round(base * 100))


def _verdict_to_conclusion(verdict: str) -> str:
    low = verdict.lower()
    if "likely" in low and "unlikely" not in low:
        return "Likely yes"
    if "unlikely" in low:
        return "Likely no"
    if "toss-up" in low or "borderline" in low or "uncertain" in low:
        return "Uncertain — too close to call"
    if "rebalance" in low and "no action" not in low and "monitor" not in low:
        return "Yes — rebalance"
    if "monitor" in low:
        return "Not yet — monitor drift"
    if "no action" in low:
        return "No — within tolerance"
    if "meaningful" in low and "not meaningful" not in low and "weak" not in low:
        return "Yes — trend looks meaningful"
    if "noisy" in low:
        return "Uncertain — noisy trend"
    if "weak" in low:
        return "No — trend too weak to trust"
    if low.startswith("yes"):
        return "Yes"
    if low.startswith("no"):
        return "No"
    return verdict.split("—")[0].strip() if "—" in verdict else verdict


def _nba_pass_confidence(required: float | None, expected: float | None) -> int | None:
    if required is None or expected is None or required <= 0:
        return None
    ratio = expected / required
    if ratio >= 1.15:
        return 88
    if ratio >= 1.05:
        return 78
    if ratio >= 0.95:
        return 62
    if ratio >= 0.85:
        return 48
    return 32


def _finalize_result(route: ProblemRoute, result: SolverResult) -> SolverResult:
    """Fill conclusion-engine fields when solvers omit them."""
    if not result.conclusion and result.result:
        result.conclusion = _verdict_to_conclusion(result.result)
    if result.confidence_pct is None:
        result.confidence_pct = _route_confidence_pct(
            route, result.partial, len(result.missing_fields)
        )
    if not result.confidence_label:
        result.confidence_label = _confidence_label(result.confidence_pct)
    if not result.model_note and result.math_idea:
        result.model_note = f"We can model this as: {result.math_idea[0].lower() + result.math_idea[1:] if result.math_idea else ''}"
    if result.partial and not result.data_would_improve and result.missing_fields:
        result.data_would_improve = [
            f"Adding **{field}** would raise confidence above {result.confidence_pct}%."
            for field in result.missing_fields[:4]
        ]
    return result


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
    conclusion: str = "",
    confidence_pct: int | None = None,
    confidence_label: str = "",
    reasons: list[str] | None = None,
    pivot_assumption: str = "",
    sensitivity_rows: list[dict[str, str]] | None = None,
    model_note: str = "",
    data_would_improve: list[str] | None = None,
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
        conclusion=conclusion or _verdict_to_conclusion(result),
        confidence_pct=confidence_pct,
        confidence_label=confidence_label,
        reasons=reasons or [],
        pivot_assumption=pivot_assumption,
        sensitivity_rows=sensitivity_rows or [],
        model_note=model_note,
        data_would_improve=data_would_improve or [],
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

    conclusion = "Insufficient data to answer"
    reasons: list[str] = []
    pivot = ""
    conf_pct: int | None = None
    sens_rows: list[dict[str, str]] = []
    data_improve: list[str] = []
    model_note = "We can model this as a rate-needed chase — gap ÷ games remaining vs recent production."

    if required_rate is not None and exp_rate is not None:
        cushion = exp_rate - required_rate
        if exp_rate >= required_rate * 1.05:
            conclusion = f"Likely yes — {player} is on pace to pass {target_name} in {stat}."
        elif exp_rate >= required_rate * 0.85:
            conclusion = f"Uncertain — {player} is close to the pace needed to pass {target_name} in {stat}."
        else:
            conclusion = f"Unlikely — {player} would need an unsustainable {stat} pace to pass {target_name}."
        reasons = [
            f"He needs **{required_rate:.1f}** {stat}/game over **{games}** remaining games and is averaging **{exp_rate:.1f}**."
        ]
        if abs(cushion) >= 0.1:
            reasons.append(
                f"That is a **{cushion:+.1f}** {stat}/game cushion vs the required pace."
            )
        conf_pct = _nba_pass_confidence(required_rate, exp_rate)
        if games is not None and games <= 5:
            pivot = (
                f"This answer changes dramatically if **games remaining** drops below **{games}** "
                f"(required rate rises above **{required_rate:.1f}**/game)."
            )
        elif required_rate and exp_rate:
            pivot = (
                f"This answer flips if expected {stat}/game falls below **{required_rate:.1f}** "
                f"(currently **{exp_rate:.1f}**)."
            )
    elif required_rate is not None:
        reasons = [f"Required pace is **{required_rate:.1f}** {stat}/game — set expected rate to judge likelihood."]
        conf_pct = 45
    elif missing:
        data_improve = [f"**{m}**" for m in missing]

    if gap is not None and games and games > 0:
        for g in range(max(1, games - 2), games + 3):
            req_g = gap / g
            if exp_rate is not None:
                out = _verdict_to_conclusion(
                    "Likely — on pace to pass"
                    if exp_rate >= req_g * 1.05
                    else (
                        "Toss-up — close to required pace"
                        if exp_rate >= req_g * 0.85
                        else "Unlikely — required pace is too high"
                    )
                )
            else:
                out = f"Need {req_g:.1f}/game"
            sens_rows.append(
                {"Parameter": "Games remaining", "Scenario": str(g), "Outcome": out}
            )

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
        conclusion=conclusion,
        confidence_pct=conf_pct,
        reasons=reasons,
        pivot_assumption=pivot,
        sensitivity_rows=sens_rows,
        model_note=model_note,
        data_would_improve=data_improve,
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

    conclusion = "Insufficient data to answer"
    reasons: list[str] = []
    pivot = ""
    conf_pct: int | None = None
    sens_rows: list[dict[str, str]] = []
    data_improve: list[str] = []
    model_note = "We model this as a rate-needed chase: gap ÷ games remaining compared to recent production."

    if slope is not None and r2 is not None:
        if meaningful:
            conclusion = (
                f"The {stat} trend looks meaningful for {player} — strong enough to factor into decisions."
            )
            reasons = [
                f"Slope is **{slope:g}** {stat}/season with R² **{r2:g}**, above your thresholds (slope ≥ {min_slope}, R² ≥ {min_r2}).",
            ]
            if delta is not None:
                reasons.append(f"Net change over the window (delta) is **{delta:g}** {stat}.")
        elif strength == "noisy":
            conclusion = f"The {stat} trend looks moderately meaningful, but still noisy."
            reasons = [
                f"The slope is **{direction}** (**{slope:g}**/season) and R² is **{r2:g}**, but the fit is inconsistent — year-to-year noise may dominate.",
            ]
        elif strength == "weak":
            conclusion = f"The {stat} trend looks weak — not strong enough to rely on for decisions."
            reasons = [
                f"|slope| (**{abs(slope):g}**) or R² (**{r2:g}**) falls below meaningful thresholds for {stat}.",
            ]
        else:
            conclusion = f"The {stat} trend is inconclusive with the current data."
            reasons = [
                f"Slope **{slope:g}**/season, R² **{r2:g}** — review thresholds below.",
            ]
        conf_pct = 82 if meaningful else (58 if strength == "noisy" else 44)
        pivot = (
            f"This answer flips if R² falls below **{min_r2:.2f}** "
            f"(currently **{r2:g}**) or |slope| drops under **{min_slope}**."
        )
        for r2_try in (0.25, 0.35, 0.50, 0.65):
            ok = abs(slope) >= min_slope and r2 >= r2_try
            sens_rows.append(
                {
                    "Parameter": "R² threshold",
                    "Scenario": f"≥ {r2_try:.2f}",
                    "Outcome": "Meaningful trend" if ok else "Not meaningful",
                }
            )
    elif missing:
        data_improve = [f"**{m}** from Baseball Trends (Advanced Trend Intelligence)" for m in missing]
        conf_pct = 40
        conclusion = f"We cannot judge whether {player}'s {stat} trend is meaningful without regression output."
        reasons = ["Slope and R² from the Trends page are required before a quantitative verdict."]

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
        conclusion=conclusion,
        confidence_pct=conf_pct,
        reasons=reasons,
        pivot_assumption=pivot,
        sensitivity_rows=sens_rows,
        model_note=model_note,
        data_would_improve=data_improve,
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

    conclusion = "We need drift data from Portfolio Health before answering."
    reasons: list[str] = []
    pivot = ""
    conf_pct: int | None = None
    sens_rows: list[dict[str, str]] = []
    data_improve: list[str] = []
    model_note = "We model drift as current weight minus target weight, compared to your rebalance threshold."

    if parsed:
        n_over_thresh = sum(1 for v in parsed.values() if abs(v) >= drift_threshold)
        if max_drift >= drift_threshold:
            conclusion = f"Yes — rebalancing is mathematically justified at your **{drift_threshold:g}%** drift threshold."
            if overweight and underweight:
                reasons = [
                    f"**{overweight[0]}** is **{abs(overweight[1]):.0f}** percentage points above target and "
                    f"**{underweight[0]}** is **{abs(underweight[1]):.0f}** below target."
                ]
                if n_over_thresh >= 2:
                    reasons.insert(
                        0,
                        f"**{n_over_thresh}** holdings exceed the allowed drift threshold.",
                    )
            else:
                reasons = [f"Max drift is **{max_drift:.1f}pp**, above the **{drift_threshold:g}pp** threshold."]
        elif max_drift >= drift_threshold * 0.6:
            conclusion = "Monitor — drift is noticeable but still below your rebalance threshold."
            reasons = [
                f"Max drift is **{max_drift:.1f}pp** vs a **{drift_threshold:g}pp** threshold — watch before acting.",
            ]
        else:
            conclusion = "No — holdings are within your drift tolerance; rebalancing is not required yet."
            reasons = [
                f"Max drift is **{max_drift:.1f}pp**, below the **{drift_threshold:g}pp** threshold.",
            ]
        conf_pct = 86 if max_drift >= drift_threshold else (64 if max_drift >= drift_threshold * 0.6 else 72)
        pivot = (
            f"This answer changes if drift threshold is raised above **{max_drift:.1f}pp** "
            f"(current max drift) or lowered below **{drift_threshold:g}pp**."
        )
        for thresh in (3.0, 5.0, 7.0, 10.0):
            out = "Rebalance" if max_drift >= thresh else "Hold / monitor"
            sens_rows.append(
                {"Parameter": "Drift threshold (pp)", "Scenario": f"{thresh:g}", "Outcome": out}
            )
    elif missing:
        data_improve = ["**rebalance_drift** from Portfolio Health (run Analyze if needed)"]
        conf_pct = 38
        conclusion = "Unclear — rebalance drift data is missing from the transferred context."
        reasons = ["Run Portfolio Health in the Investment app, then re-send the question."]

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
        conclusion=conclusion,
        confidence_pct=conf_pct,
        reasons=reasons,
        pivot_assumption=pivot,
        sensitivity_rows=sens_rows,
        model_note=model_note,
        data_would_improve=data_improve,
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

    conclusion = "We need return and volatility from Portfolio Health before answering."
    reasons: list[str] = []
    pivot = ""
    conf_pct: int | None = None
    sens_rows: list[dict[str, str]] = []
    data_improve: list[str] = []
    model_note = "We model return per unit of risk — Sharpe ratio vs your volatility ceiling."

    if exp_ret is not None and vol is not None and sharpe is not None:
        if sharpe >= min_sharpe and vol <= max_vol:
            conclusion = (
                f"Yes — the **{exp_ret:g}%** expected return appears worth **{vol:g}%** volatility at your goal."
            )
        elif sharpe >= min_sharpe * 0.8:
            conclusion = (
                f"Unclear — **{exp_ret:g}%** return vs **{vol:g}%** volatility is borderline for your risk tolerance."
            )
        else:
            conclusion = (
                f"Too risky — **{vol:g}%** volatility is not justified by **{exp_ret:g}%** expected return at your Sharpe floor."
            )
        reasons = [
            f"Sharpe ratio is **{sharpe:g}** (your minimum is **{min_sharpe:g}**).",
        ]
        if drawdown is not None:
            reasons.append(f"Worst peak-to-trough drawdown is **{drawdown:g}%**.")
        conf_pct = 84 if sharpe >= min_sharpe and vol <= max_vol else (55 if sharpe >= min_sharpe * 0.8 else 48)
        pivot = (
            f"This answer becomes negative if volatility exceeds **{max_vol:g}%** "
            f"(currently **{vol:g}%**) or Sharpe falls below **{min_sharpe:g}**."
        )
        for vol_cap in (12.0, 15.0, 18.0, 22.0):
            if sharpe is not None:
                ok = sharpe >= min_sharpe and vol <= vol_cap
                out = "Worth the risk" if ok else "Too risky"
            else:
                out = f"Vol cap {vol_cap:g}%"
            sens_rows.append(
                {"Parameter": "Volatility cap (%)", "Scenario": f"{vol_cap:g}", "Outcome": out}
            )
    elif missing:
        data_improve = [f"**{m}** from Portfolio Health" for m in missing]
        conf_pct = 40
        conclusion = "Unclear — expected return and volatility are not in the transferred context."
        reasons = ["Run Analyze Portfolio in the Investment app, then re-send the question."]

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
        conclusion=conclusion,
        confidence_pct=conf_pct,
        reasons=reasons,
        pivot_assumption=pivot,
        sensitivity_rows=sens_rows,
        model_note=model_note,
        data_would_improve=data_improve,
    )


def _generic_solver(route: ProblemRoute, question: str, ctx: dict[str, Any]) -> SolverResult:
    model_note = "We can model this as a threshold/decision problem once one measurable quantity is attached."
    data_improve = [f"**{f}**" for f in route.missing_fields[:4]]
    conclusion = "Best estimate unavailable — need numeric context"
    reasons: list[str] = []
    if route.missing_fields:
        reasons = [
            "The question needs at least one number from the source page before a quantitative verdict.",
        ]
    partial_conf = _route_confidence_pct(route, True, len(route.missing_fields))
    return _coach_result(
        question=question,
        problem_type=route.problem_type,
        math_idea="Define the measurable quantity, baseline, and decision threshold.",
        variables="variable = what you measure\nbaseline = comparison point\nthreshold = decision cutoff",
        data_used=[f"Source: **{route.source_app}**"],
        calculation="State the claim as one number, then compare to baseline ± uncertainty.",
        result="Partial — attach numeric context from the source app",
        interpretation=(
            "We can model this as a threshold/decision problem, but need: "
            + ", ".join(route.missing_fields)
            + "."
            if route.missing_fields
            else "Translate the question into one measurable quantity and re-send from the source app."
        ),
        assumptions=["Context from the source app reflects the user's current view."],
        sensitivity_notes="Adding missing fields enables a domain-specific solver with a firmer conclusion.",
        missing_fields=list(route.missing_fields),
        partial=True,
        problem_type_id=route.problem_type_id,
        conclusion=conclusion,
        confidence_pct=partial_conf,
        reasons=reasons,
        model_note=model_note,
        data_would_improve=data_improve,
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
        pa = str(ctx.get("player_a") or "").strip()
        pb = str(ctx.get("player_b") or "").strip()
        cmp_extra = ctx.get("_ami_comparison_context") or ctx.get("comparison_differences")
        diff_bits: list[str] = []
        if isinstance(cmp_extra, dict):
            for k, v in list(cmp_extra.items())[:4]:
                diff_bits.append(f"{k}: {v}")
        elif isinstance(cmp_extra, list):
            diff_bits = [str(x) for x in cmp_extra[:4]]

        surpass = any(w in question.lower() for w in ("surpass", "pass", "better", "beat"))
        model_note = "We can model this as rate-stat value gap per plate appearance, adjusted for playing time."
        if diff_bits:
            conclusion = f"**{pa}** leads on attached comparison stats" if pa else "Comparison favors one side on attached stats"
            reasons = diff_bits[:3]
            conf_pct = 68
            result_text = conclusion
            interp = " ".join(diff_bits)
            partial = False
        elif pa and pb:
            conclusion = "Possible but uncertain — rate stats not attached"
            reasons = [
                f"Comparing **{pa}** vs **{pb}** — rate production may be similar; projection depends on playing time and career length.",
            ]
            conf_pct = 58 if surpass else 52
            result_text = "Too close to call without rate comparison"
            interp = (
                f"For “{pa} vs {pb}”, attach OPS/SLG/WAR comparison from the Comparison Tool "
                "for a sharper quantitative verdict."
            )
            partial = bool(route.missing_fields)
        else:
            conclusion = "Need both players selected"
            reasons = []
            conf_pct = 35
            result_text = "Select two players in Comparison Tool"
            interp = "Open Comparison Tool, select both players, then re-send the question."
            partial = True

        data_improve = []
        if not diff_bits:
            data_improve = [
                "**comparison_stats** (OPS, SLG, WAR) from Comparison Tool",
                "**projections** for playing-time / career length questions",
            ]

        return _coach_result(
            question=question,
            problem_type="Player comparison",
            math_idea="Value gap = rate-stat difference adjusted for playing time and scarcity.",
            variables="value_i = rate stats per PA × playing-time projection",
            data_used=[f"**{pa}** vs **{pb}**"] if pa and pb else [],
            calculation="Subtract rate-based value scores; weight scarce categories.",
            result=result_text,
            interpretation=interp,
            assumptions=["Same position eligibility matters for roster fit."],
            sensitivity_notes="Weight scarce categories (SB, HR) higher in category leagues; career-length questions need projection inputs.",
            missing_fields=route.missing_fields,
            partial=partial,
            problem_type_id=pid,
            conclusion=conclusion,
            confidence_pct=conf_pct,
            reasons=reasons,
            model_note=model_note,
            data_would_improve=data_improve,
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
    return route, _finalize_result(route, result)
