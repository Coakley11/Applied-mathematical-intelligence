"""Rule-based mathematical solvers for suite Applied Math questions."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any

from components.applied_math_problem_router import (
    BASEBALL_DRAFT,
    BASEBALL_FUTURE_ACCUMULATION,
    BASEBALL_GENERIC,
    BASEBALL_HISTORICAL,
    BASEBALL_PLAYER_COMPARE,
    BASEBALL_PROJECTION,
    BASEBALL_TREND,
    BASEBALL_VALUATION,
    GENERIC_FALLBACK,
    GENERIC_INTERACTIVE,
    INVESTMENT_CONCENTRATION,
    INVESTMENT_DRAWDOWN_ATTRIBUTION,
    INVESTMENT_GENERIC,
    INVESTMENT_MACRO,
    INVESTMENT_REBALANCE,
    INVESTMENT_RISK_RETURN,
    NBA_GENERIC,
    NBA_INVERSE_STAT_CHASE,
    NBA_LEGACY_COMPARISON,
    NBA_MATCHUP_EDGE,
    NBA_STAT_CHASE,
    NBA_WIN_PROBABILITY,
    ProblemRoute,
    route_suite_question,
)
from components.applied_math_problem_interpreter import (
    PURPOSE_ATTRIBUTE,
    PURPOSE_COMPARE,
    PURPOSE_DECIDE,
    PURPOSE_ESTIMATE_PROBABILITY,
    PURPOSE_ESTIMATE_RATE,
    PURPOSE_EVALUATE_RISK,
    PURPOSE_EXPLAIN_WHY,
    PURPOSE_FORECAST,
    PURPOSE_MEASURE_SENSITIVITY,
    PURPOSE_TEST_SIGNIFICANCE,
)
from components.draft_market_question import (
    draft_question_restatement,
    extract_draft_compare_players,
    extract_draft_position_query,
    is_draft_head_to_head_question,
    is_draft_market_prediction_question,
    is_draft_review_question,
    is_draft_timing_question,
    is_player_explanation_question,
    is_position_best_available_question,
    is_roster_needs_question,
    position_matches_row,
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
    # Math coach — teach-and-solve UX
    short_answer: str = ""
    why: str = ""
    sensitivity_plain: str = ""
    live_metrics: dict[str, str] = field(default_factory=dict)
    question_intent: str = ""
    intent_restatement: str = ""
    math_purpose: str = ""
    model_name: str = ""
    model_rationale: str = ""
    model_variables: str = ""
    solvability: str = ""
    data_relevant: list[str] = field(default_factory=list)

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
    if not result.short_answer and result.conclusion:
        result.short_answer = result.conclusion
    if not result.why and result.reasons:
        result.why = result.reasons[0]
    if not result.sensitivity_plain and result.pivot_assumption:
        result.sensitivity_plain = result.pivot_assumption
    elif not result.sensitivity_plain and result.sensitivity_notes:
        result.sensitivity_plain = result.sensitivity_notes
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
            f"Use the controls below to enter **{field.split('.')[-1]}** and solve hands-on."
            for field in result.missing_fields[:4]
        ]
    if route.question_intent:
        result.question_intent = route.question_intent
    if route.intent_restatement:
        result.intent_restatement = route.intent_restatement
    if route.math_purpose:
        result.math_purpose = route.math_purpose
    if route.model_name:
        result.model_name = route.model_name
    if route.model_rationale:
        result.model_rationale = route.model_rationale
    if route.model_variables:
        result.model_variables = route.model_variables
    if route.solvability:
        result.solvability = route.solvability
    if route.data_relevant:
        result.data_relevant = list(route.data_relevant)
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
    short_answer: str = "",
    why: str = "",
    sensitivity_plain: str = "",
    live_metrics: dict[str, str] | None = None,
) -> SolverResult:
    resolved_conclusion = conclusion or _verdict_to_conclusion(result)
    resolved_why = why or ((reasons or [""])[0] if reasons else "")
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
        conclusion=resolved_conclusion,
        confidence_pct=confidence_pct,
        confidence_label=confidence_label,
        reasons=reasons or [],
        pivot_assumption=pivot_assumption,
        sensitivity_rows=sensitivity_rows or [],
        model_note=model_note,
        data_would_improve=data_would_improve or [],
        short_answer=short_answer or resolved_conclusion,
        why=resolved_why,
        sensitivity_plain=sensitivity_plain or pivot_assumption or sensitivity_notes,
        live_metrics=live_metrics or {},
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
        games = int(gr) if gr is not None else None
        if games is None:
            gr_num = _num(ctx.get("games_remaining"))
            games = int(gr_num) if gr_num is not None else None

    context_rate = _parse_rate(gap_ctx.get("rate_needed") or ctx.get("rate_needed"))
    exp_rate = expected_rate if expected_rate is not None else context_rate

    missing: list[str] = []
    if gap is None:
        missing.append("stat_gap.gap (or current_value and target_value)")
    if games is None:
        missing.append("games_remaining")
        games = 4  # hands-on default so the user can still explore

    # Only the numbers that matter for this question
    data_used = [
        x
        for x in (
            f"Gap to close: **{gap:g}** {stat}" if gap is not None else "",
            f"Games remaining: **{games}**" + (" _(adjust below)_" if "games_remaining" in missing else ""),
            f"Expected pace: **{exp_rate:g}** {stat}/game" if exp_rate is not None else "",
            f"Current total: **{current:g}** → target **{target:g}**"
            if current is not None and target is not None
            else "",
        )
        if x
    ]

    math_idea = (
        f"This is a **rate-needed** problem. We compare how many {stat} {player} still needs "
        f"to how many games he has left."
    )
    variables = (
        f"gap = target {stat} − current {stat}\n"
        f"games = games remaining\n"
        f"required rate = gap ÷ games\n"
        f"expected rate = recent {stat} per game"
    )

    required_rate: float | None = None
    calc = ""
    projected_total: float | None = None
    if gap is not None and games and games > 0:
        required_rate = gap / games
        calc = (
            f"gap = **{gap:g}** {stat}\n"
            f"games = **{games}**\n\n"
            f"required rate = gap ÷ games\n"
            f"= {gap:g} ÷ {games} = **{required_rate:.2f}** {stat}/game"
        )
        if exp_rate is not None:
            calc += f"\n\nexpected rate = **{exp_rate:g}** {stat}/game"
            if current is not None:
                projected_total = current + exp_rate * games
                calc += (
                    f"\n\nprojected final = current + (expected rate × games)\n"
                    f"= {current:g} + ({exp_rate:g} × {games}) = **{projected_total:.1f}** {stat}"
                )
    elif gap is not None:
        calc = f"gap = **{gap:g}** {stat}. Adjust **games remaining** below to compute required rate."

    verdict = "Insufficient data"
    interpretation = ""
    short_answer = "Adjust the controls below to explore this chase."
    why = ""
    sensitivity_plain = ""
    live_metrics: dict[str, str] = {}

    if required_rate is not None and exp_rate is not None:
        cushion = exp_rate - required_rate
        if exp_rate >= required_rate * 1.05:
            verdict = "Likely — on pace to pass"
            short_answer = f"Probably yes, if he has about **{games}** games left."
        elif exp_rate >= required_rate * 0.85:
            verdict = "Toss-up — close to required pace"
            short_answer = f"Uncertain — it depends on whether he keeps **{exp_rate:.1f}** {stat}/game."
        else:
            verdict = "Unlikely — required pace is too high"
            short_answer = f"Probably no — he would need **{required_rate:.1f}** {stat}/game but averages **{exp_rate:.1f}**."
        why = (
            f"He needs **{required_rate:.1f}** {stat}/game over **{games}** games; "
            f"recent pace is **{exp_rate:.1f}** ({cushion:+.1f} vs required)."
        )
        interpretation = why
        live_metrics = {
            "Required rate": f"{required_rate:.2f} {stat}/game",
            "Expected rate": f"{exp_rate:.1f} {stat}/game",
            "Pass at current pace?": "Yes ✓" if exp_rate >= required_rate * 0.85 else "No ✗",
        }
        if projected_total is not None and target is not None:
            live_metrics["Projected final"] = f"{projected_total:.1f} {stat}"
            live_metrics["Target to pass"] = f"{target:g} {stat}"
        half_g = max(1, games // 2) if games else 1
        if gap and half_g != games:
            sensitivity_plain = (
                f"If games remaining drops from **{games}** to **{half_g}**, "
                f"required rate rises from **{required_rate:.1f}** to **{gap / half_g:.1f}** {stat}/game."
            )
    elif required_rate is not None:
        short_answer = f"Set expected {stat}/game below — required pace is **{required_rate:.1f}**/game."
        why = f"With **{games}** games left, the math depends entirely on his per-game production."
        interpretation = why
        live_metrics = {"Required rate": f"{required_rate:.2f} {stat}/game"}
    elif gap is None:
        short_answer = "Enter a target value below — we can model this once the gap is known."
        why = "This is a rate-needed problem; gap = target − current."
        interpretation = why

    if not sensitivity_plain:
        sensitivity_plain = (
            "Fewer games remaining raises the required rate. "
            "Lower expected production makes passing less likely."
        )

    sensitivity = sensitivity_plain
    if required_rate and games:
        alt_games = max(1, games - 1)
        alt_req = gap / alt_games if gap else None
        if alt_req:
            sensitivity += f" At {alt_games} games left, required rate is **{alt_req:.2f}**/game."

    conclusion = short_answer
    reasons = [why] if why else []
    pivot = sensitivity_plain
    conf_pct: int | None = _nba_pass_confidence(required_rate, exp_rate) if required_rate and exp_rate else 45
    sens_rows: list[dict[str, str]] = []
    data_improve: list[str] = []
    if "games_remaining" in missing:
        data_improve.append("Use the **games remaining** control below.")
    if gap is None:
        data_improve.append("Use the **target total** control below.")

    if gap is not None and games and games > 0:
        for g in range(max(1, games - 2), games + 3):
            req_g = gap / g
            if exp_rate is not None:
                out = (
                    "Likely yes"
                    if exp_rate >= req_g * 1.05
                    else ("Uncertain" if exp_rate >= req_g * 0.85 else "Likely no")
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
        partial=bool(missing and (gap is None or "games_remaining" in missing)),
        problem_type_id=NBA_STAT_CHASE,
        computed={
            "gap": gap,
            "games_remaining": games,
            "required_rate": required_rate,
            "expected_rate": exp_rate,
            "verdict": verdict,
            "projected_total": projected_total,
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
        model_note=math_idea,
        data_would_improve=data_improve,
        short_answer=short_answer,
        why=why,
        sensitivity_plain=sensitivity_plain,
        live_metrics=live_metrics,
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
    low_q = question.lower()
    projection_q = any(w in low_q for w in ("expected stat", "projected", "projection", "2026", "forecast"))
    improve_q = any(w in low_q for w in ("improve", "next season", "future season"))
    if any(w in low_q for w in ("double", "doubles", "2b")):
        answer_stat = "2B"
    elif any(w in low_q for w in ("home run", " homer", " hr")):
        answer_stat = "HR"
    else:
        answer_stat = stat

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


    math_idea = (
        f"This is a **trend vs noise** problem. We ask whether {player}'s {stat} slope is "
        f"large enough and consistent enough (R²) to trust — or just year-to-year randomness."
    )
    variables = (
        "slope = change in stat per season\n"
        "R² = how consistently the stat follows a line (0–1)\n"
        "delta = total change over the trend window"
    )

    calc = (
        f"Meaningful if |slope| ≥ **{min_slope}** and R² ≥ **{min_r2}**\n\n"
        + (
            f"slope = **{slope:g}** {stat}/season\n"
            f"R² = **{r2:g}**"
            + (f"\ndelta = **{delta:g}** over the window" if delta is not None else "")
            if slope is not None and r2 is not None
            else "Enter slope and R² from Baseball Trends, or use the threshold sliders below."
        )
    )

    data_used = [
        x
        for x in (
            f"Slope: **{slope:g}** {stat}/season" if slope is not None else "",
            f"R²: **{r2:g}**" if r2 is not None else "",
            f"Direction: **{direction}**" if direction != "unknown" else "",
            f"Net change (delta): **{delta:g}**" if delta is not None else "",
        )
        if x
    ]

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

    short_answer = "Adjust slope and R² thresholds below to see if this trend is meaningful."
    why = ""
    sensitivity_plain = sensitivity
    live_metrics: dict[str, str] = {}

    conclusion = "Insufficient data to answer"
    reasons: list[str] = []
    pivot = ""
    conf_pct: int | None = None
    sens_rows: list[dict[str, str]] = []
    data_improve: list[str] = []
    model_note = math_idea

    if slope is not None and r2 is not None:
        if projection_q:
            proj_parts: list[str] = []
            for key, label in (
                ("proj_HR", "HR"),
                ("proj_OPS", "OPS"),
                ("proj_SB", "SB"),
                ("proj_RBI", "RBI"),
                ("proj_WAR", "WAR"),
            ):
                val = trend.get(key) if isinstance(trend, dict) else None
                if val is None:
                    val = ctx.get(key)
                if val is not None and str(val).strip():
                    proj_parts.append(f"**{label}** ~{val}")
            trend_read = f"**{direction}** {stat} trend (slope **{slope:g}**/yr, R² **{r2:g}**)"
            if meaningful:
                short_answer = (
                    f"**{player}** — {trend_read} supports a **{direction}** {answer_stat} outlook for 2026."
                )
            else:
                short_answer = (
                    f"**{player}** — {trend_read}; treat 2026 {answer_stat} as **{strength}**, not a lock."
                )
            if proj_parts:
                short_answer += " Projected line: " + ", ".join(proj_parts[:4]) + "."
            why = (
                f"Trend fit on **{stat}** (slope **{slope:g}**, R² **{r2:g}**) "
                f"{'supports' if meaningful else 'only weakly supports'} extrapolating {answer_stat} forward."
            )
        elif improve_q:
            if meaningful and str(direction).lower() in ("up", "positive", "rising"):
                short_answer = (
                    f"**{player}** is likely to **improve next season** — {answer_stat} trend is **{direction}** "
                    f"(slope **{slope:g}**/year, R² **{r2:g}**) above your thresholds."
                )
                why = (
                    f"The **{answer_stat}** slope (**{slope:g}**/season) and R² (**{r2:g}**) suggest real growth, "
                    f"not a one-year spike — monitor playing time and role stability."
                )
            elif strength == "noisy":
                short_answer = (
                    f"**{player}** may improve next season, but the **{answer_stat}** trend is **noisy** "
                    f"(R² **{r2:g}** vs **{min_r2}** floor) — treat improvement as possible, not probable."
                )
                why = (
                    f"Direction is **{direction}** (slope **{slope:g}**), but low R² means year-to-year variance "
                    f"could reverse the gain."
                )
            else:
                short_answer = (
                    f"**{player}** is **unlikely to improve much next season** — {answer_stat} trend is weak "
                    f"(slope **{slope:g}**, R² **{r2:g}**) vs your meaningful thresholds."
                )
                why = (
                    f"Without a consistent upward fit (R² **{r2:g}**), projecting **improvement** "
                    f"from this {answer_stat} line is not supported."
                )
            live_metrics = {
                "Player": player,
                "Next-season read": "Likely improve" if meaningful and str(direction).lower() in ("up", "positive", "rising") else "Uncertain",
                f"Slope ({stat}/season)": f"{slope:g}",
                "R²": f"{r2:g}",
            }
        elif meaningful:
            short_answer = f"Yes — **{player}**'s {direction} {answer_stat} trend looks meaningful at your thresholds."
            why = (
                f"|slope| = **{abs(slope):g}** ≥ **{min_slope}** and R² = **{r2:g}** ≥ **{min_r2}** — "
                f"the {answer_stat} line fits consistently enough to trust."
            )
            live_metrics = {
                "Trend verdict": "Meaningful ✓",
                "Noise level": "Low",
                f"Slope ({stat}/season)": f"{slope:g}",
                "R²": f"{r2:g}",
            }
        elif strength == "noisy":
            short_answer = (
                f"For **{player}**, the trend is **{direction}**, but only meaningful if R² is high enough — "
                f"currently **{r2:g}** vs your **{min_r2}** floor (likely **noise**)."
            )
            why = (
                f"**{player}**'s slope is **{slope:g}** {stat}/season ({direction}), but R² **{r2:g}** "
                f"is below **{min_r2}** — year-to-year noise may dominate."
            )
            live_metrics = {
                "Trend verdict": "Noisy — direction only",
                "Noise level": "High",
                f"Slope ({stat}/season)": f"{slope:g}",
                "R²": f"{r2:g}",
            }
        elif strength == "weak":
            short_answer = f"No — **{player}**'s {stat} trend is too weak to rely on for decisions."
            why = (
                f"|slope| (**{abs(slope):g}**) or R² (**{r2:g}**) falls below your thresholds "
                f"(slope ≥ **{min_slope}**, R² ≥ **{min_r2}**)."
            )
            live_metrics = {
                "Trend verdict": "Weak ✗",
                "Noise level": noise.capitalize(),
                f"Slope ({stat}/season)": f"{slope:g}",
                "R²": f"{r2:g}",
            }
        else:
            short_answer = f"Inconclusive for **{player}** — review slope **{slope:g}** and R² **{r2:g}** against your thresholds."
            why = f"**{player}**: slope **{slope:g}**/season, R² **{r2:g}** — adjust thresholds below to see when the verdict flips."
            live_metrics = {
                "Trend verdict": "Inconclusive",
                f"Slope ({stat}/season)": f"{slope:g}",
                "R²": f"{r2:g}",
            }

        if improve_q:
            conclusion = short_answer
            reasons = [why] if why else []
        elif meaningful:
            conclusion = short_answer
            reasons = [why] if why else [
                f"Slope is **{slope:g}** {stat}/season with R² **{r2:g}**, above your thresholds (slope ≥ {min_slope}, R² ≥ {min_r2}).",
            ]
            if delta is not None:
                reasons.append(f"Net change over the window (delta) is **{delta:g}** {stat}.")
        elif strength == "noisy":
            conclusion = short_answer
            reasons = [why] if why else [
                f"The slope is **{direction}** (**{slope:g}**/season) and R² is **{r2:g}**, but the fit is inconsistent — year-to-year noise may dominate.",
            ]
        elif strength == "weak":
            conclusion = short_answer
            reasons = [why] if why else [
                f"|slope| (**{abs(slope):g}**) or R² (**{r2:g}**) falls below meaningful thresholds for {stat}.",
            ]
        else:
            conclusion = short_answer
            reasons = [why] if why else [
                f"Slope **{slope:g}**/season, R² **{r2:g}** — review thresholds below.",
            ]
        conf_pct = 82 if meaningful else (58 if strength == "noisy" else 44)
        pivot = (
            f"This answer flips if R² falls below **{min_r2:.2f}** "
            f"(currently **{r2:g}**) or |slope| drops under **{min_slope}**."
        )
        sensitivity_plain = (
            f"If you raise the R² threshold from **{min_r2}** to **{min(min_r2 + 0.15, 0.95):.2f}**, "
            f"a trend with R² **{r2:g}** becomes "
            f"{'meaningful' if r2 >= min(min_r2 + 0.15, 0.95) else 'not meaningful'}."
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
        data_improve = ["Use the **threshold sliders** below, or re-send from Baseball Trends with slope and R² attached."]
        conf_pct = 40
        short_answer = f"We can model {player}'s {stat} trend — enter slope and R² from Baseball Trends, or adjust thresholds below."
        why = "This is a trend vs noise problem: meaningful if |slope| and R² both clear your thresholds."
        conclusion = short_answer
        reasons = [why]

    conclusion = short_answer if short_answer else conclusion
    if not reasons and why:
        reasons = [why]

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
            **{
                k: v
                for k, v in {
                    **(ctx.get("trend_send_diagnostics") or {}),
                    **(ctx.get("send_pipeline_diagnostics") or {}),
                    "source_page": ctx.get("source_page") or ctx.get("page"),
                    "trend_player": player,
                    "trend_mode_selected": "baseball_trend_significance",
                    "routing_reason": "trend_solver",
                    "player_a_present": bool(str(ctx.get("player_a") or "").strip()),
                    "player_b_present": bool(str(ctx.get("player_b") or "").strip()),
                }.items()
                if v is not None and v != "" and v != []
            },
        },
        default_controls={"min_slope": min_slope, "min_r2": min_r2},
        conclusion=conclusion,
        confidence_pct=conf_pct,
        reasons=reasons,
        pivot_assumption=pivot,
        sensitivity_rows=sens_rows,
        model_note=model_note,
        data_would_improve=data_improve,
        short_answer=short_answer,
        why=why,
        sensitivity_plain=sensitivity_plain,
        live_metrics=live_metrics,
    )


def solve_baseball_valuation(
    ctx: dict[str, Any],
    question: str,
    *,
    over_threshold: float = 0.72,
    under_threshold: float = 0.38,
) -> SolverResult:
    """Valuation over/under using Valuation_Score, Perf_Score, Trend_Score, and market edge."""
    snap = ctx.get("valuation_snapshot") if isinstance(ctx.get("valuation_snapshot"), dict) else {}
    player = str(snap.get("selected_player") or ctx.get("player") or "Player").strip()
    top_rows = snap.get("top_valuation_players") if isinstance(snap.get("top_valuation_players"), list) else []
    row = next((r for r in top_rows if isinstance(r, dict) and str(r.get("player", "")).lower() == player.lower()), None)
    if row is None and top_rows and isinstance(top_rows[0], dict):
        row = top_rows[0]
        player = str(row.get("player") or player)

    val_score = _num(row.get("Valuation_Score")) if row else None
    perf = _num(row.get("Perf_Score")) if row else None
    trend = _num(row.get("Trend_Score")) if row else None
    edge = _num(row.get("Fantasy Edge")) if row else None
    market = row.get("Market Rank") if row else None
    ds = ctx.get("draft_status") if isinstance(ctx.get("draft_status"), dict) else {}

    low = question.lower()
    why_rated = "why" in low and any(w in low for w in ("rated", "rating", "highly", "high"))
    if why_rated and val_score is not None:
        verdict = "explained"
        short = (
            f"**{player}** is **rated highly** (Valuation Score **{val_score:.2f}**) because "
            f"**Perf_Score {perf}** reflects recent production and **Trend_Score {trend}** captures momentum — "
            f"not just a single headline number."
        )
        if edge is not None and market is not None:
            short += f" Model Rank vs Market Rank (**{edge}** Fantasy Edge) adds upside vs ADP."
    elif val_score is not None:
        if val_score >= over_threshold or (edge is not None and edge < -10):
            verdict = "overvalued"
            short = f"**{player}** looks **overvalued** at Valuation Score **{val_score:.2f}** — market may be ahead of recent production/trend."
        elif val_score <= under_threshold or (edge is not None and edge > 15):
            verdict = "undervalued"
            short = f"**{player}** looks **undervalued** at Valuation Score **{val_score:.2f}** — model ranks him above market."
        else:
            verdict = "fair"
            short = f"**{player}** is **fairly valued** at Valuation Score **{val_score:.2f}** — near the middle of your filtered pool."
    else:
        verdict = "unknown"
        short = f"Attach **valuation_snapshot** with Valuation_Score for **{player}** to judge over/under vs market."

    why = (
        f"Valuation blends **Current Score** (**{perf}**) and **Trend Score** (**{trend}**) "
        f"with your page weights. Market Rank **{market}**, Fantasy Edge **{edge}**."
    )
    if why_rated and val_score is not None:
        why = (
            f"**Rated highly** because Perf_Score (**{perf}**) and Trend_Score (**{trend}**) "
            f"both contribute to Valuation Score **{val_score:.2f}** — "
            f"strong recent output plus positive momentum vs peers in your filtered pool."
        )
    if ds.get("is_drafted"):
        why += f" **{player}** is already drafted on your board."
    elif ds.get("on_user_roster"):
        why += f" **{player}** is on your roster."

    calc = (
        f"Player: **{player}**\n"
        f"Valuation Score: **{val_score}** (over ≥ **{over_threshold}**, under ≤ **{under_threshold}**)\n"
        f"Perf_Score: **{perf}** · Trend_Score: **{trend}**\n"
        f"Fantasy Edge: **{edge}** · Market Rank: **{market}**"
    )
    tradeoffs = (
        f"If you need safety → favor higher Perf_Score peers in top_valuation_players. "
        f"If you need upside → favor higher Trend_Score / positive Fantasy Edge names."
    )
    what_if = [
        "If you weight trend more → undervalued sleepers rise in Valuation Score.",
        "If you weight current production more → stable veterans rank higher.",
        f"If {player} is drafted before your pick → pivot to next name in valuation_snapshot.",
    ]

    return _coach_result(
        question=question,
        problem_type="Player valuation",
        math_idea="Valuation = weighted blend of recent production (Perf) and momentum (Trend) vs market rank/edge.",
        variables="Valuation_Score = f(Perf_Score, Trend_Score, weights)\nFantasy Edge = Model Rank − Market Rank",
        data_used=_cap_data_used([
            f"Valuation Score: **{val_score}**" if val_score is not None else "",
            f"Perf/Trend: **{perf}** / **{trend}**" if perf is not None else "",
            f"Draft status: {ds}" if ds else "",
        ]),
        calculation=calc,
        result=short,
        interpretation=why,
        assumptions=["Valuation uses the filtered player pool on the Valuation page, not generic rankings."],
        sensitivity_notes="Shift value_w_current vs value_w_trend weights to stress-test the score.",
        missing_fields=[] if val_score is not None else ["valuation_snapshot.Valuation_Score"],
        partial=val_score is None,
        problem_type_id=BASEBALL_VALUATION,
        computed={"verdict": verdict, "valuation_score": val_score, "coach_sections": {
            "direct_answer": short,
            "analyst_framing": why,
            "tradeoffs": tradeoffs,
            "what_if": what_if,
        }},
        short_answer=short,
        why=why,
        live_metrics=bool(val_score is not None),
    )


def solve_baseball_historical(ctx: dict[str, Any], question: str) -> SolverResult:
    """Explain historical leaderboard results — filters, comparison, and outlier rows."""
    snap = ctx.get("historical_snapshot") if isinstance(ctx.get("historical_snapshot"), dict) else {}
    player = str(ctx.get("player") or snap.get("selected_player") or "").strip()
    sort_stat = str(snap.get("sort_stat") or ctx.get("historical_sort_stat") or "stat").strip()
    filters = ctx.get("filters_applied") or snap.get("filters_applied") or snap.get("year_range") or "active filters"
    rows = snap.get("top_rows") if isinstance(snap.get("top_rows"), list) else []
    row_bits: list[str] = []
    for row in rows[:5]:
        if not isinstance(row, dict):
            continue
        name = str(row.get("player") or "").strip()
        val = row.get(sort_stat) or row.get(str(sort_stat))
        if name and val is not None:
            row_bits.append(f"**{name}** ({sort_stat}={val})")

    # Two-player age/season window comparison (from Comparison Tool with age or season constraint).
    # No historical_snapshot available — work from player names and the extracted age range.
    pa = str(ctx.get("player_a") or "").strip()
    pb = str(ctx.get("player_b") or "").strip()
    age_range = str(ctx.get("comparison_age_range") or "").strip()
    season_range = str(ctx.get("comparison_season_range") or "").strip()
    window_label = age_range or season_range
    if pa and pb and window_label and not row_bits:
        window_type = "ages" if age_range else "seasons"
        metrics_hint = _ctx_list(ctx.get("metrics")) or ["OPS", "WAR", "HR", "SLG", "OBP"]
        metrics_str = ", ".join(str(m) for m in metrics_hint[:5])
        short = (
            f"**{pa} vs {pb} — {window_type} {window_label}**: "
            f"To compare them in this window, filter the **Historical Explorer** to "
            f"{window_type} {window_label} and look at {metrics_str}. "
            f"Peak-age windows (e.g. ages 19–27) reveal who developed faster and peaked higher, "
            f"which differs significantly from career or current-day comparisons."
        )
        why = (
            f"Age-window comparisons isolate a specific career phase. "
            f"Between {window_type} {window_label}, look for: "
            f"rate-stat peaks (OPS+, SLG), power development (ISO, HR/PA), "
            f"contact quality, and walk/strikeout evolution. "
            f"One player may have been elite early while the other peaked later."
        )
        what_if = [
            f"If you widen the window beyond {window_label} → career totals may favor a different player.",
            "If you add era adjustment → raw stats need park/era context (OPS+ normalizes this).",
            "If you include postseason → peak-age playoff performance may shift the verdict.",
        ]
        return _coach_result(
            question=question,
            problem_type="Historical age-window comparison",
            math_idea=(
                f"Age-window comparison: isolate both players to {window_type} {window_label} "
                f"and compare peak-phase performance metrics."
            ),
            variables=(
                f"player_a = {pa}\nplayer_b = {pb}\nwindow = {window_type} {window_label}\n"
                "metrics = OPS, HR, WAR, SLG, OBP (era-adjusted preferred)"
            ),
            data_used=_cap_data_used([
                f"Player A: **{pa}**",
                f"Player B: **{pb}**",
                f"Window: {window_type} **{window_label}**",
            ]),
            calculation=f"Filter historical data to {window_type} {window_label}; compare {metrics_str}.",
            result=short,
            interpretation=why,
            assumptions=[
                f"Comparing {pa} and {pb} during {window_type} {window_label} only.",
                "Era and park adjustments improve accuracy for cross-generation comparisons.",
            ],
            sensitivity_notes="\n".join(what_if),
            missing_fields=["historical_snapshot.top_rows (filtered to age window)"],
            partial=True,
            problem_type_id=BASEBALL_HISTORICAL,
            computed={"player_a": pa, "player_b": pb, "window": window_label, "coach_sections": {
                "direct_answer": short,
                "why": why,
                "what_if": what_if,
            }},
            short_answer=short,
            why=why,
            sensitivity_plain=what_if[0] if what_if else "",
        )

    low = question.lower()
    comparison_q = "comparison" in low or ("what does" in low and "show" in low)
    filter_cause_q = "filter" in low and ("caus" in low or "outcome" in low)
    bonds_q = "bonds" in low or "why does" in low

    if comparison_q and row_bits:
        short = (
            f"This **historical comparison** shows top **{sort_stat}** seasons under **{filters}**: "
            + ", ".join(row_bits[:3])
            + f". It ranks who dominated **{sort_stat}** in that window — not a projection for today."
        )
    elif filter_cause_q and row_bits:
        short = (
            f"These **filters** (**{filters}**, sorted by **{sort_stat}**) surface extreme counting-stat seasons — "
            f"**{row_bits[0].split('(')[0].strip()}** leads because {sort_stat} totals rank highest in the filtered set."
        )
    elif bonds_q and row_bits:
        short = (
            f"**Barry Bonds** keeps appearing because your **filters** (**{filters}**) and **{sort_stat}** sort "
            f"favor his peak seasons ({row_bits[0] if row_bits else 'top HR totals'})."
        )
    elif row_bits:
        short = f"**Historical** snapshot on **{sort_stat}** under **{filters}**: " + ", ".join(row_bits[:3])
    else:
        short = "Attach **historical_snapshot.top_rows** with filters to interpret this leaderboard."

    why = (
        f"The table is sorted by **{sort_stat}** with filters **{filters}**. "
        + (
            f"Top rows: {', '.join(row_bits[:3])}."
            if row_bits
            else "Compare the selected player's row to neighbors in the filtered window."
        )
    )
    calc_detail = "; ".join(row_bits[:3])
    tradeoffs = (
        "Rate stats (OBP, SLG) need playing-time context; counting stats (HR) need era and park adjustments."
    )
    what_if = [
        f"If you widen the year range → different players may top **{sort_stat}**.",
        f"If you switch sort stat → **{player or 'top rows'}** may drop in rank.",
        "If you add PA/AB filters → small-sample outliers may disappear.",
    ]

    return _coach_result(
        question=question,
        problem_type="Historical comparison",
        math_idea="Leaderboard = filtered seasons ranked by sort stat; outliers reflect filters + era effects.",
        variables="sort_stat = ranking column\nfilters = year range + stat thresholds\npeers = neighboring rows",
        data_used=_cap_data_used([
            f"Sort stat: **{sort_stat}**",
            f"Filters: **{filters}**",
            f"Player: **{player}**" if player else "",
        ] + row_bits[:2]),
        calculation=f"Compare **{sort_stat}** across filtered rows.\n\n{calc_detail}",
        result=short,
        interpretation=why,
        assumptions=[f"Filters: {filters}"],
        sensitivity_notes="Changing year range or sort stat reshuffles who appears at the top.",
        missing_fields=[] if row_bits else ["historical_snapshot.top_rows"],
        partial=not row_bits,
        problem_type_id=BASEBALL_HISTORICAL,
        computed={"top_rows": rows[:5], "coach_sections": {
            "direct_answer": short,
            "analyst_framing": why,
            "tradeoffs": tradeoffs,
            "what_if": what_if,
        }},
        short_answer=short,
        why=why,
        live_metrics=bool(row_bits),
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
            largest,
            f"Drift threshold: **{drift_threshold:g}pp**",
            *[
                f"**{t}**: drift **{d:+.1f}pp**"
                for t, d in sorted(parsed.items(), key=lambda x: abs(x[1]), reverse=True)[:4]
            ],
        )
        if x
    ]

    math_idea = (
        "This is a **threshold / drift** problem. For each holding, "
        "drift = current weight − target weight; rebalance when |drift| exceeds your threshold."
    )
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

    short_answer = "Adjust the drift threshold below — we need holding drift data to compute a verdict."
    why = "Rebalance when any holding's |drift| exceeds your threshold."
    sensitivity_plain = sensitivity
    live_metrics: dict[str, str] = {}

    conclusion = "We need drift data from Portfolio Health before answering."
    reasons: list[str] = []
    pivot = ""
    conf_pct: int | None = None
    sens_rows: list[dict[str, str]] = []
    data_improve: list[str] = []
    model_note = math_idea

    if parsed:
        n_over_thresh = sum(1 for v in parsed.values() if abs(v) >= drift_threshold)
        over_list = ", ".join(t for t, v in parsed.items() if abs(v) >= drift_threshold)
        if max_drift >= drift_threshold:
            short_answer = f"Yes — rebalance if your threshold is **{drift_threshold:g}pp** (max drift **{max_drift:.1f}pp**)."
            why = (
                f"Max |drift| is **{max_drift:.1f}pp**, above your **{drift_threshold:g}pp** threshold"
                + (f" — **{n_over_thresh}** holding(s) over limit." if n_over_thresh else "")
                + "."
            )
            live_metrics = {
                "Action": "Rebalance ✓",
                "Max |drift|": f"{max_drift:.1f}pp",
                "Holdings over threshold": str(n_over_thresh) if n_over_thresh else over_list or "—",
                "Threshold": f"{drift_threshold:g}pp",
            }
        elif max_drift >= drift_threshold * 0.6:
            short_answer = f"Monitor — drift is **{max_drift:.1f}pp**, below your **{drift_threshold:g}pp** rebalance threshold."
            why = f"Noticeable drift but not yet over **{drift_threshold:g}pp** — watch before trading."
            live_metrics = {
                "Action": "Monitor",
                "Max |drift|": f"{max_drift:.1f}pp",
                "Threshold": f"{drift_threshold:g}pp",
            }
        else:
            short_answer = f"No — holdings are within **{drift_threshold:g}pp** drift tolerance."
            why = f"Max |drift| is **{max_drift:.1f}pp**, below the **{drift_threshold:g}pp** threshold."
            live_metrics = {
                "Action": "No action",
                "Max |drift|": f"{max_drift:.1f}pp",
                "Threshold": f"{drift_threshold:g}pp",
            }

        if max_drift >= drift_threshold:
            conclusion = short_answer
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
            conclusion = short_answer
            reasons = [why]
        else:
            conclusion = short_answer
            reasons = [why]
        conf_pct = 86 if max_drift >= drift_threshold else (64 if max_drift >= drift_threshold * 0.6 else 72)
        pivot = (
            f"This answer changes if drift threshold is raised above **{max_drift:.1f}pp** "
            f"(current max drift) or lowered below **{drift_threshold:g}pp**."
        )
        alt_thresh = max(1.0, drift_threshold - 2.0)
        sensitivity_plain = (
            f"If drift threshold drops from **{drift_threshold:g}pp** to **{alt_thresh:g}pp**, "
            f"max drift **{max_drift:.1f}pp** → "
            f"{'rebalance' if max_drift >= alt_thresh else 'hold/monitor'}."
        )
        for thresh in (3.0, 5.0, 7.0, 10.0):
            out = "Rebalance" if max_drift >= thresh else "Hold / monitor"
            sens_rows.append(
                {"Parameter": "Drift threshold (pp)", "Scenario": f"{thresh:g}", "Outcome": out}
            )
    elif missing:
        data_improve = ["Use the **drift threshold** slider below, or re-send from Portfolio Health with drift attached."]
        conf_pct = 38
        short_answer = "We can model this as drift vs threshold — enter drift from Portfolio Health or adjust the threshold below."
        why = "drift = current weight − target weight; rebalance when |drift| exceeds threshold."
        conclusion = short_answer
        reasons = [why]

    if not reasons and why:
        reasons = [why]

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
        short_answer=short_answer,
        why=why,
        sensitivity_plain=sensitivity_plain,
        live_metrics=live_metrics,
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
            f"Your Sharpe floor: **{min_sharpe:g}**",
            f"Your volatility cap: **{max_vol:g}%**",
        )
        if x
    ]

    math_idea = (
        "This is a **risk-return tradeoff** problem. Sharpe ≈ return ÷ volatility — "
        "does the portfolio earn enough return per unit of risk for your thresholds?"
    )
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

    short_answer = "Adjust Sharpe and volatility thresholds below to judge whether return is worth the risk."
    why = ""
    sensitivity_plain = sensitivity
    live_metrics: dict[str, str] = {}

    conclusion = "We need return and volatility from Portfolio Health before answering."
    reasons: list[str] = []
    pivot = ""
    conf_pct: int | None = None
    sens_rows: list[dict[str, str]] = []
    data_improve: list[str] = []
    model_note = "We model return per unit of risk — Sharpe ratio vs your volatility ceiling."

    if exp_ret is not None and vol is not None and sharpe is not None:
        passes = sharpe >= min_sharpe and vol <= max_vol
        if passes:
            short_answer = f"Yes — **{exp_ret:g}%** return looks worth **{vol:g}%** volatility at your thresholds."
            why = f"Sharpe **{sharpe:g}** ≥ **{min_sharpe:g}** and volatility **{vol:g}%** ≤ **{max_vol:g}%** cap."
            live_metrics = {
                "Verdict": "Pass ✓",
                "Sharpe": f"{sharpe:g}",
                "Volatility": f"{vol:g}%",
                f"Sharpe floor ({min_sharpe:g})": "Met" if sharpe >= min_sharpe else "Not met",
                f"Vol cap ({max_vol:g}%)": "Met" if vol <= max_vol else "Exceeded",
            }
        elif sharpe >= min_sharpe * 0.8:
            short_answer = f"Borderline — **{exp_ret:g}%** return vs **{vol:g}%** volatility is close to your limits."
            why = f"Sharpe **{sharpe:g}** is near your **{min_sharpe:g}** floor; volatility **{vol:g}%** vs **{max_vol:g}%** cap."
            live_metrics = {
                "Verdict": "Borderline",
                "Sharpe": f"{sharpe:g}",
                "Volatility": f"{vol:g}%",
            }
        else:
            short_answer = f"No — **{vol:g}%** volatility is not justified by **{exp_ret:g}%** return at your Sharpe floor."
            why = f"Sharpe **{sharpe:g}** < **{min_sharpe:g}** — not enough return per unit of risk."
            live_metrics = {
                "Verdict": "Fail ✗",
                "Sharpe": f"{sharpe:g}",
                "Volatility": f"{vol:g}%",
            }

        conclusion = short_answer
        reasons = [why]
        if drawdown is not None:
            reasons.append(f"Worst peak-to-trough drawdown is **{drawdown:g}%**.")
        conf_pct = 84 if passes else (55 if sharpe >= min_sharpe * 0.8 else 48)
        pivot = (
            f"This answer becomes negative if volatility exceeds **{max_vol:g}%** "
            f"(currently **{vol:g}%**) or Sharpe falls below **{min_sharpe:g}**."
        )
        tighter_vol = max(5.0, max_vol - 3.0)
        sensitivity_plain = (
            f"If acceptable volatility drops from **{max_vol:g}%** to **{tighter_vol:g}%**, "
            f"**{vol:g}%** actual volatility → {'pass' if vol <= tighter_vol else 'fail'}."
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
        data_improve = ["Use the **Sharpe / volatility sliders** below, or re-send from Portfolio Health with return and volatility attached."]
        conf_pct = 40
        short_answer = "We can model return vs risk — enter return and volatility from Portfolio Health, or set thresholds below."
        why = "Sharpe ≈ return ÷ volatility compared to your minimum Sharpe and volatility cap."
        conclusion = short_answer
        reasons = [why]

    if not reasons and why:
        reasons = [why]

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
        short_answer=short_answer,
        why=why,
        sensitivity_plain=sensitivity_plain,
        live_metrics=live_metrics,
    )


def _parse_pct(val: Any) -> float | None:
    """Parse probability as 0–100 percent."""
    n = _num(val)
    if n is None:
        return None
    if 0 <= n <= 1:
        return n * 100.0
    return n


def _parse_weight_fraction(val: Any) -> float | None:
    """Parse portfolio weight to 0–1 fraction."""
    n = _num(val)
    if n is None:
        return None
    if n > 1.0:
        return n / 100.0
    return n


def _parse_weights_map(raw: dict[str, Any]) -> dict[str, float]:
    out: dict[str, float] = {}
    for ticker, val in raw.items():
        w = _parse_weight_fraction(val)
        if w is not None and w >= 0:
            out[str(ticker)] = w
    return out


def _win_prob_edge_label(pct: float) -> tuple[str, str]:
    """Return (edge label, coach phrase) for win probability pct (0–100)."""
    if pct >= 75:
        return "heavy favorite", "They are a heavy favorite — but upsets still happen."
    if pct >= 65:
        return "strong edge", "They have a strong edge, but it is not a lock."
    if pct >= 55:
        return "solid edge", "The model says they are favored, but not a lock."
    if pct >= 50:
        return "slight edge", "They have a slight edge — essentially a toss-up with a lean."
    if pct >= 45:
        return "slight underdog", "They are a slight underdog — close enough that small swings matter."
    if pct >= 35:
        return "underdog", "They are an underdog; the model gives them a real but minority chance."
    return "long shot", "They are a long shot — would need several breaks to go their way."


def _extract_pair_values(text: str) -> tuple[float | None, float | None]:
    nums = [float(x) for x in re.findall(r"-?\d+\.?\d*", str(text))]
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], None
    return None, None


def _stat_category(stat: str) -> str:
    s = stat.lower()
    if any(k in s for k in ("hr", "slg", "power", "iso", "home run")):
        return "power"
    if any(k in s for k in ("ops", "wrc", "war", "obp", "avg", "rate", "woba")):
        return "rate"
    if any(k in s for k in ("career", "total", "counting", "rbi", "hit", "sb")):
        return "career"
    if any(k in s for k in ("peak", "season", "best")):
        return "peak"
    return "rate"


def _collect_comparison_rows(
    ctx: dict[str, Any],
    pa: str,
    pb: str,
) -> list[tuple[str, float, float]]:
    """Parse comparison stats into (name, value_a, value_b) rows."""
    rows: list[tuple[str, float, float]] = []
    cmp_extra = ctx.get("_ami_comparison_context") or ctx.get("comparison_differences")
    if isinstance(cmp_extra, dict):
        for stat, val in cmp_extra.items():
            a, b = _extract_pair_values(str(val))
            if a is not None and b is not None:
                rows.append((str(stat), a, b))
    elif isinstance(cmp_extra, list):
        for item in cmp_extra:
            if isinstance(item, dict):
                stat = str(item.get("stat") or item.get("metric") or "stat")
                a = _num(item.get(pa) or item.get("player_a") or item.get("a"))
                b = _num(item.get(pb) or item.get("player_b") or item.get("b"))
                if a is None or b is None:
                    a2, b2 = _extract_pair_values(str(item))
                    a = a if a is not None else a2
                    b = b if b is not None else b2
                if a is not None and b is not None:
                    rows.append((stat, a, b))
            else:
                a, b = _extract_pair_values(str(item))
                if a is not None and b is not None:
                    rows.append(("stat", a, b))
    stats_block = ctx.get("comparison_stats")
    if isinstance(stats_block, dict):
        for stat, val in stats_block.items():
            if isinstance(val, dict):
                a = _num(val.get(pa) or val.get("player_a"))
                b = _num(val.get(pb) or val.get("player_b"))
                if a is not None and b is not None:
                    rows.append((str(stat), a, b))
    return rows


def solve_nba_win_probability(ctx: dict[str, Any], question: str) -> SolverResult:
    team = str(ctx.get("team") or "Team").strip()
    wp_raw = ctx.get("win_probability") or ctx.get("series_probability")
    pct = _parse_pct(wp_raw)
    horizon = "series" if ctx.get("series_probability") and not ctx.get("win_probability") else "game"

    missing: list[str] = []
    if pct is None:
        missing.append("win_probability")

    edge = ""
    math_idea = (
        "This is a **probability calibration** problem. A win probability tells you how favored "
        "a team is — we classify the edge and note what would make the number look too high or low."
    )
    variables = (
        "p = quoted win probability (%)\n"
        "edge band: slight (50–55) · solid (55–65) · strong (65–75) · heavy (75+)"
    )

    short_answer = "Enter a win probability from Live Game Center to evaluate."
    why = ""
    calc = ""
    live_metrics: dict[str, str] = {}
    sens_rows: list[dict[str, str]] = []

    if pct is not None:
        edge, phrase = _win_prob_edge_label(pct)
        short_answer = f"At **{pct:g}%**, {phrase}"
        why = (
            f"**{pct:g}%** falls in the **{edge}** band "
            f"(50–55% slight · 55–65% solid · 65–75% strong · 75%+ heavy favorite)."
        )
        calc = (
            f"p = **{pct:g}%** ({horizon} win probability for **{team}**)\n\n"
            f"Edge classification: **{edge}**"
        )
        questionable = []
        if pct >= 70:
            questionable.append("Injuries, foul trouble, or cold shooting could pull this below 60%.")
        elif pct <= 40:
            questionable.append("Home court, star hot streak, or opponent foul trouble could push this up 10–15 pp.")
        else:
            questionable.append("A 10 pp swing in either direction is normal over a small sample of games.")
        calc += f"\n\nWhat could make this questionable: {questionable[0]}"
        live_metrics = {
            "Win probability": f"{pct:g}%",
            "Edge band": edge.replace("_", " ").title(),
            "Horizon": horizon,
        }
        for try_p in (45, 55, 62, 72):
            lbl, _ = _win_prob_edge_label(float(try_p))
            sens_rows.append({"Parameter": "Win probability", "Scenario": f"{try_p}%", "Outcome": lbl})

    data_used = [x for x in (f"Win probability: **{pct:g}%**" if pct else "", f"Team: **{team}**") if x]

    return _coach_result(
        question=question,
        problem_type="Win probability reasonableness",
        math_idea=math_idea,
        variables=variables,
        data_used=data_used,
        calculation=calc or "Load win_probability from Live Game Center.",
        result=short_answer,
        interpretation=why,
        assumptions=[f"Probability refers to the same {horizon} horizon as the source page."],
        sensitivity_notes="Star minutes ±10% or a key injury can shift playoff probability 10–15 percentage points.",
        missing_fields=missing,
        partial=bool(missing),
        problem_type_id=NBA_WIN_PROBABILITY,
        computed={"probability_pct": pct, "edge": edge if pct else None},
        conclusion=short_answer,
        confidence_pct=72 if pct else 40,
        reasons=[why] if why else [],
        short_answer=short_answer,
        why=why,
        sensitivity_plain=(
            f"If the true strength gap is smaller than the model assumes, **{pct:g}%** may be 5–10 pp too high."
            if pct and pct >= 60
            else (
                f"If **{team}** catches a hot stretch, a **{pct:g}%** line could rise toward 50%."
                if pct and pct < 50
                else "Attach a numeric probability to classify the edge band."
            )
        ),
        live_metrics=live_metrics,
        sensitivity_rows=sens_rows,
    )


def solve_nba_inverse_stat_chase(
    ctx: dict[str, Any],
    question: str,
    *,
    expected_rate: float | None = None,
    target_value: float | None = None,
) -> SolverResult:
    gap_ctx = ctx.get("stat_gap") if isinstance(ctx.get("stat_gap"), dict) else {}
    player = str(gap_ctx.get("player") or ctx.get("player") or "Player").strip()
    target_name = str(gap_ctx.get("comparison") or "Leader").strip()
    stat = str(gap_ctx.get("stat") or "stat").strip()

    current = _num(gap_ctx.get("current_value"))
    target = _num(target_value if target_value is not None else gap_ctx.get("target_value"))
    gap = _num(gap_ctx.get("gap"))
    if gap is None and current is not None and target is not None:
        gap = target - current

    exp_rate = expected_rate if expected_rate is not None else _parse_rate(
        gap_ctx.get("rate_needed") or ctx.get("rate_needed")
    )
    if exp_rate is None:
        exp_rate = 4.0

    missing: list[str] = []
    if gap is None:
        missing.append("stat_gap.gap")

    games_needed: int | None = None
    if gap is not None and exp_rate and exp_rate > 0:
        games_needed = max(1, math.ceil(gap / exp_rate))

    math_idea = (
        f"This is an **inverse rate** problem. Given the gap and expected {stat}/game, "
        f"how many games are needed to catch {target_name}?"
    )
    variables = (
        f"gap = target − current\n"
        f"expected rate = {stat} per game\n"
        f"games needed = ceil(gap ÷ expected rate)"
    )

    calc = ""
    if gap is not None and games_needed:
        calc = (
            f"gap = **{gap:g}** {stat}\n"
            f"expected rate = **{exp_rate:g}** {stat}/game\n\n"
            f"games needed = ceil(gap ÷ expected rate)\n"
            f"= ceil({gap:g} ÷ {exp_rate:g}) = **{games_needed}** games"
        )

    short_answer = (
        f"About **{games_needed}** games at **{exp_rate:g}** {stat}/game."
        if games_needed
        else "Set gap and expected rate below."
    )
    why = (
        f"To close a **{gap:g}**-{stat} gap at **{exp_rate:g}**/game, he needs at least **{games_needed}** games."
        if games_needed and gap
        else "games needed = ceil(gap ÷ expected rate)."
    )

    live_metrics: dict[str, str] = {}
    if games_needed:
        live_metrics = {
            "Games needed": str(games_needed),
            "Expected rate": f"{exp_rate:g} {stat}/game",
            "Gap": f"{gap:g} {stat}" if gap else "—",
        }

    sens_rows: list[dict[str, str]] = []
    if gap and gap > 0:
        for rate in (2.0, 3.0, 4.0, 5.0, 6.0):
            g = max(1, math.ceil(gap / rate))
            sens_rows.append(
                {"Parameter": "Expected rate", "Scenario": f"{rate:g}/game", "Outcome": f"{g} games needed"}
            )

    data_used = [
        x
        for x in (
            f"Gap: **{gap:g}** {stat}" if gap is not None else "",
            f"Expected rate: **{exp_rate:g}** {stat}/game",
            f"Target: **{target_name}** ({target:g})" if target is not None else "",
        )
        if x
    ]

    return _coach_result(
        question=question,
        problem_type="NBA inverse stat chase",
        math_idea=math_idea,
        variables=variables,
        data_used=data_used,
        calculation=calc or "Enter gap and expected rate.",
        result=short_answer,
        interpretation=why,
        assumptions=[
            f"{player} maintains **{exp_rate:g}** {stat}/game.",
            f"{target_name}'s total is held fixed (static gap model).",
        ],
        sensitivity_notes="Higher expected rate → fewer games needed; lower rate → more games.",
        missing_fields=missing,
        partial=bool(missing),
        problem_type_id=NBA_INVERSE_STAT_CHASE,
        computed={"gap": gap, "games_needed": games_needed, "expected_rate": exp_rate},
        default_controls={"expected_rate": exp_rate, "target_value": target or 0.0},
        conclusion=short_answer,
        confidence_pct=80 if games_needed else 45,
        reasons=[why],
        short_answer=short_answer,
        why=why,
        sensitivity_plain=(
            f"If expected rate drops from **{exp_rate:g}** to **{max(0.5, exp_rate - 1):g}**, "
            f"games needed rises from **{games_needed}** to **{max(1, math.ceil(gap / max(0.5, exp_rate - 1))) if gap else '?'}**."
            if games_needed and gap
            else "Lower expected production increases games needed."
        ),
        live_metrics=live_metrics,
        sensitivity_rows=sens_rows,
    )


def solve_investment_concentration(
    ctx: dict[str, Any],
    question: str,
    *,
    max_single_pct: float = 25.0,
    max_top3_pct: float = 60.0,
) -> SolverResult:
    weights_raw = ctx.get("current_weights") if isinstance(ctx.get("current_weights"), dict) else {}
    weights = _parse_weights_map(weights_raw)
    holdings = _ctx_list(ctx.get("holdings"))

    missing: list[str] = []
    if not weights:
        missing.append("current_weights")

    math_idea = (
        "This is a **concentration** problem. HHI = Σ(weight²) measures diversification; "
        "also check largest holding and top-3 weight sum vs your limits."
    )
    variables = (
        "weight_i = portfolio fraction (0–1)\n"
        "HHI = Σ weight_i²\n"
        "top1 = max weight · top3 = sum of 3 largest weights"
    )

    hhi = top1 = top3 = 0.0
    top_name = ""
    sorted_w: list[tuple[str, float]] = []
    if weights:
        sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        top_name, top1 = sorted_w[0]
        top1_pct = top1 * 100
        top3_pct = sum(w for _, w in sorted_w[:3]) * 100
        hhi = sum(w * w for w in weights.values())
        top3 = top3_pct
        top1 = top1_pct

    calc = ""
    verdict = "Insufficient data"
    short_answer = "Enter weights below or re-send from Portfolio Health."
    why = ""
    live_metrics: dict[str, str] = {}

    if weights:
        calc_lines = [f"HHI = Σ(weight²) = **{hhi:.3f}**"]
        for ticker, w in sorted_w[:4]:
            calc_lines.append(f"**{ticker}**: {w * 100:.1f}% → contributes {w * w:.4f} to HHI")
        calc_lines.append(f"\nTop holding: **{top_name}** at **{top1:.1f}%**")
        calc_lines.append(f"Top 3 combined: **{top3:.1f}%**")
        calc = "\n".join(calc_lines)

        over_single = top1 > max_single_pct
        over_top3 = top3 > max_top3_pct
        if over_single and over_top3:
            verdict = "Highly concentrated"
            short_answer = f"Yes — **{top_name}** at **{top1:.0f}%** and top-3 at **{top3:.0f}%** exceed your limits."
        elif over_single or over_top3:
            verdict = "Moderately concentrated"
            short_answer = f"Somewhat — {'top holding' if over_single else 'top-3 sum'} exceeds your **{max_single_pct if over_single else max_top3_pct:g}%** threshold."
        else:
            verdict = "Diversified"
            short_answer = f"No — top holding **{top1:.0f}%** and top-3 **{top3:.0f}%** are within your thresholds."
        why = (
            f"HHI **{hhi:.3f}** · top holding **{top1:.1f}%** (limit **{max_single_pct:g}%**) · "
            f"top-3 **{top3:.1f}%** (limit **{max_top3_pct:g}%)."
        )
        live_metrics = {
            "Verdict": verdict,
            "HHI": f"{hhi:.3f}",
            "Top holding": f"{top_name} {top1:.1f}%",
            "Top 3 sum": f"{top3:.1f}%",
        }

    data_used = [
        x
        for x in (
            *[f"**{t}**: {w * 100:.1f}%" for t, w in sorted_w[:4]],
            f"Holdings count: **{len(weights) or len(holdings)}**",
        )
        if x
    ]

    sens_rows: list[dict[str, str]] = []
    if weights:
        for thresh in (15.0, 20.0, 25.0, 30.0):
            out = "Over limit" if top1 > thresh else "OK"
            sens_rows.append({"Parameter": "Max single (%)", "Scenario": f"{thresh:g}", "Outcome": out})

    return _coach_result(
        question=question,
        problem_type="Portfolio concentration",
        math_idea=math_idea,
        variables=variables,
        data_used=data_used,
        calculation=calc or "Need current_weights from Portfolio Health.",
        result=verdict,
        interpretation=why,
        assumptions=["Weights reflect current market values.", "Thresholds are policy choices, not universal rules."],
        sensitivity_notes="Lowering max single-name % makes the same portfolio look more concentrated.",
        missing_fields=missing,
        partial=bool(missing),
        problem_type_id=INVESTMENT_CONCENTRATION,
        computed={"hhi": hhi, "top1_pct": top1, "top3_pct": top3, "verdict": verdict},
        default_controls={"max_single_pct": max_single_pct, "max_top3_pct": max_top3_pct},
        conclusion=short_answer,
        confidence_pct=78 if weights else 38,
        reasons=[why] if why else [],
        short_answer=short_answer,
        why=why,
        sensitivity_plain=(
            f"If max single holding drops from **{max_single_pct:g}%** to **{max(10, max_single_pct - 5):g}%**, "
            f"**{top_name}** at **{top1:.0f}%** → {'over limit' if top1 > max(10, max_single_pct - 5) else 'OK'}."
            if weights
            else "Adjust max single and top-3 thresholds below."
        ),
        live_metrics=live_metrics,
        sensitivity_rows=sens_rows,
        data_would_improve=["**current_weights** from Portfolio Health"] if missing else [],
    )


def solve_baseball_player_compare(
    ctx: dict[str, Any],
    question: str,
    *,
    weight_rate: float = 1.0,
    weight_power: float = 1.0,
    weight_career: float = 0.5,
    weight_peak: float = 0.5,
) -> SolverResult:
    pa = str(ctx.get("player_a") or "").strip()
    pb = str(ctx.get("player_b") or "").strip()
    rows = _collect_comparison_rows(ctx, pa, pb)

    cat_weights = {
        "rate": weight_rate,
        "power": weight_power,
        "career": weight_career,
        "peak": weight_peak,
    }

    math_idea = (
        "This is a **weighted stat comparison**. For each category, normalize who leads, "
        "then sum weighted points — higher total wins under your current weights."
    )
    variables = (
        "score_a = Σ weight_category × (stat_a / (stat_a + stat_b))\n"
        "score_b = Σ weight_category × (stat_b / (stat_a + stat_b))"
    )

    score_a = score_b = 0.0
    drivers: list[str] = []
    calc_lines: list[str] = []

    for stat, va, vb in rows:
        cat = _stat_category(stat)
        w = cat_weights.get(cat, weight_rate)
        share_a = va / (va + vb) if (va + vb) > 0 else 0.5
        share_b = vb / (va + vb) if (va + vb) > 0 else 0.5
        pts_a = w * share_a
        pts_b = w * share_b
        score_a += pts_a
        score_b += pts_b
        leader = pa if va > vb else pb if vb > va else "Tie"
        calc_lines.append(
            f"**{stat}**: {pa} **{va:g}** vs {pb} **{vb:g}** → {leader} (+{w:.1f}× {cat} weight)"
        )
        if abs(va - vb) / max(va, vb, 0.001) > 0.05:
            drivers.append(f"{stat} ({leader})")

    missing: list[str] = []
    if not pa or not pb:
        missing.append("player_a/player_b")
    if not rows:
        missing.append("comparison_stats")

    partial = bool(missing)
    short_answer = "Attach OPS/WAR/HR comparison from the Comparison Tool."
    why = ""
    live_metrics: dict[str, str] = {}

    if rows:
        if score_a > score_b * 1.02:
            winner, loser = pa, pb
            margin = score_a - score_b
        elif score_b > score_a * 1.02:
            winner, loser = pb, pa
            margin = score_b - score_a
        else:
            winner = ""
            margin = abs(score_a - score_b)
        if winner:
            short_answer = (
                f"**{winner}** leads **{loser}** under current weights "
                f"(score **{max(score_a, score_b):.2f}** vs **{min(score_a, score_b):.2f}**)."
            )
            why = f"Driven by: {', '.join(drivers[:3]) or 'attached stats'}."
        else:
            short_answer = (
                f"**{pa}** vs **{pb}** is too close to call — weighted scores "
                f"**{score_a:.2f}** vs **{score_b:.2f}**."
            )
            why = "Neither player leads by more than 2% on the weighted score."
        live_metrics = {
            f"{pa} score": f"{score_a:.2f}",
            f"{pb} score": f"{score_b:.2f}",
            "Leader": winner or "Toss-up",
        }

    calc = "\n".join(calc_lines) if calc_lines else "Subtract rate-based value scores with your category weights."

    return _coach_result(
        question=question,
        problem_type="Player comparison",
        math_idea=math_idea,
        variables=variables,
        data_used=[f"**{pa}** vs **{pb}**"] + [f"{s}: {va:g} vs {vb:g}" for s, va, vb in rows[:4]],
        calculation=calc,
        result=short_answer,
        interpretation=why,
        assumptions=["Rate stats are per-PA unless labeled as counting/career.", "Surpass questions need projection inputs not in this snapshot."],
        sensitivity_notes="Raising power weight shifts toward HR/SLG; raising rate weight favors OPS/WAR.",
        missing_fields=missing,
        partial=partial,
        problem_type_id=BASEBALL_PLAYER_COMPARE,
        computed={"score_a": score_a, "score_b": score_b, "rows": len(rows)},
        default_controls={
            "weight_rate": weight_rate,
            "weight_power": weight_power,
            "weight_career": weight_career,
            "weight_peak": weight_peak,
        },
        conclusion=short_answer,
        confidence_pct=72 if rows and abs(score_a - score_b) > 0.15 else (58 if rows else 40),
        reasons=[why] if why else [],
        short_answer=short_answer,
        why=why,
        sensitivity_plain="Increase rate-stat weight to favor OPS/WAR leaders; increase power weight for HR/SLG.",
        live_metrics=live_metrics,
        model_note=math_idea,
        data_would_improve=["**comparison_stats** (OPS, WAR, HR) from Comparison Tool"] if not rows else [],
    )


def solve_investment_macro_stress(
    ctx: dict[str, Any],
    question: str,
    *,
    return_shock: float = -3.0,
    vol_shock: float = 4.0,
    recession_prob: float = 30.0,
) -> SolverResult:
    exp_ret = _num(ctx.get("expected_return"))
    vol = _num(ctx.get("volatility"))
    health = _num(ctx.get("health_score"))
    macro = str(ctx.get("macro_outlook") or ctx.get("macro_summary") or "").strip()

    missing: list[str] = []
    if exp_ret is None:
        missing.append("expected_return")
    if vol is None:
        missing.append("volatility")

    math_idea = (
        "This is a **scenario stress test**. Start from base return/volatility, "
        "then apply recession shocks to see how far metrics move."
    )
    variables = (
        "return_stressed = return + return_shock\n"
        "vol_stressed = volatility + vol_shock\n"
        "recession_prob = your assigned recession probability (%)"
    )

    base_ret = exp_ret if exp_ret is not None else 8.0
    base_vol = vol if vol is not None else 12.0
    mild_ret_shock = return_shock * 0.5
    mild_vol_shock = vol_shock * 0.5
    severe_ret_shock = return_shock * 1.5
    severe_vol_shock = vol_shock * 1.5

    scenarios = [
        ("Base case", 0.0, 0.0),
        ("Mild recession", mild_ret_shock, mild_vol_shock),
        ("Severe recession", severe_ret_shock, severe_vol_shock),
    ]

    calc_lines: list[str] = []
    sens_rows: list[dict[str, str]] = []
    for name, r_sh, v_sh in scenarios:
        r_out = base_ret + r_sh
        v_out = base_vol + v_sh
        sharpe_approx = r_out / v_out if v_out > 0 else 0
        calc_lines.append(
            f"**{name}**: return **{r_out:.1f}%**, vol **{v_out:.1f}%**, Sharpe≈**{sharpe_approx:.2f}**"
        )
        sens_rows.append(
            {"Parameter": name, "Scenario": f"Δret {r_sh:+.1f}pp", "Outcome": f"vol {v_out:.1f}%"}
        )
    calc_lines.append(
        f"\n**Your shock settings**: return **{base_ret + return_shock:.1f}%**, vol **{base_vol + vol_shock:.1f}%**"
    )

    short_answer = (
        f"A **{abs(return_shock):g}pp** return hit and **+{vol_shock:g}pp** vol would bring return to "
        f"**{base_ret + return_shock:.1f}%** and vol to **{base_vol + vol_shock:.1f}**."
        if exp_ret is not None
        else "Set return/vol shocks below — base case uses portfolio Health metrics when attached."
    )
    why = (
        f"Base **{base_ret:g}%** return / **{base_vol:g}%** vol; "
        f"recession scenario applies **{return_shock:+.1f}pp** return and **+{vol_shock:g}pp** volatility."
    )
    health_note = ""
    if health is not None:
        stressed_health = max(0, health - abs(return_shock) * 2 - vol_shock)
        health_note = f" Qualitative health impact: **{health:.0f}** → ~**{stressed_health:.0f}** under severe stress."
        why += health_note

    live_metrics = {
        "Base return": f"{base_ret:g}%",
        "Stressed return": f"{base_ret + return_shock:.1f}%",
        "Base vol": f"{base_vol:g}%",
        "Stressed vol": f"{base_vol + vol_shock:.1f}%",
    }

    data_used = [
        x
        for x in (
            f"Base return: **{base_ret:g}%**",
            f"Base volatility: **{base_vol:g}%**",
            f"Macro: **{macro[:80]}**" if macro else "",
            f"Health score: **{health:g}**" if health is not None else "",
        )
        if x
    ]

    return _coach_result(
        question=question,
        problem_type="Macro sensitivity",
        math_idea=math_idea,
        variables=variables,
        data_used=data_used,
        calculation="\n".join(calc_lines),
        result=short_answer,
        interpretation=why,
        assumptions=[
            f"Recession probability assumption: **{recession_prob:g}%**.",
            "Shocks are illustrative — not a full factor model.",
        ],
        sensitivity_notes="Larger return shock or vol shock makes the portfolio look worse in recession.",
        missing_fields=missing,
        partial=bool(missing and exp_ret is None),
        problem_type_id=INVESTMENT_MACRO,
        computed={
            "base_return": base_ret,
            "stressed_return": base_ret + return_shock,
            "base_vol": base_vol,
            "stressed_vol": base_vol + vol_shock,
        },
        default_controls={
            "return_shock": return_shock,
            "vol_shock": vol_shock,
            "recession_prob": recession_prob,
        },
        conclusion=short_answer,
        confidence_pct=70 if exp_ret is not None else 48,
        reasons=[why],
        short_answer=short_answer,
        why=why,
        sensitivity_plain=(
            f"If return shock deepens from **{return_shock:g}pp** to **{return_shock * 1.5:g}pp**, "
            f"stressed return falls to **{base_ret + return_shock * 1.5:.1f}%**."
        ),
        live_metrics=live_metrics,
        sensitivity_rows=sens_rows,
        data_would_improve=["**expected_return** and **volatility** from Portfolio Health"] if missing else [],
    )


def solve_baseball_projection_realism(
    ctx: dict[str, Any],
    question: str,
    *,
    max_above_recent_pct: float = 25.0,
    max_above_career_pct: float = 35.0,
) -> SolverResult:
    player = str(ctx.get("player") or "Player").strip()
    proj = ctx.get("projection") if isinstance(ctx.get("projection"), dict) else {}
    trend = ctx.get("trend_summary") if isinstance(ctx.get("trend_summary"), dict) else {}

    projected = _num(proj.get("projected") or proj.get("value"))
    recent = _num(proj.get("previous") or proj.get("latest") or trend.get("latest"))
    career = _num(proj.get("career_avg") or proj.get("career_average"))
    stat = str(proj.get("stat") or trend.get("stat") or "stat").strip()
    slope = _num(trend.get("slope"))

    if projected is None and trend:
        projected = _num(trend.get("projected"))

    missing: list[str] = []
    if projected is None:
        missing.append("projection.projected")

    trend_implied = None
    if recent is not None and slope is not None:
        trend_implied = recent + slope

    baselines: list[tuple[str, float]] = []
    if recent is not None:
        baselines.append(("recent season", recent))
    if career is not None:
        baselines.append(("career average", career))
    if trend_implied is not None:
        baselines.append(("trend-implied", trend_implied))

    math_idea = (
        f"This is a **projection sanity check**. Compare the projected {stat} to recent average, "
        f"career baseline, and trend-implied value — large gaps need a story."
    )
    variables = (
        "projection = stated forecast\n"
        "baseline = recent / career / trend-implied\n"
        "gap_pct = (projection − baseline) ÷ baseline × 100"
    )

    calc_lines: list[str] = []
    verdict = "Insufficient data"
    short_answer = "Enter a projection value — we compare it to baselines from context."
    why = ""
    live_metrics: dict[str, str] = {}
    max_gap_pct = 0.0
    worst_baseline = ""

    if projected is not None and baselines:
        for label, base in baselines:
            if base <= 0:
                continue
            gap_pct = (projected - base) / base * 100
            calc_lines.append(
                f"vs **{label}** ({base:g}): projection **{projected:g}** → **{gap_pct:+.0f}%**"
            )
            if abs(gap_pct) > abs(max_gap_pct):
                max_gap_pct = gap_pct
                worst_baseline = label

        if max_gap_pct <= max_above_recent_pct * 0.5:
            verdict = "Realistic"
            short_answer = f"**Realistic** — projection **{projected:g}** {stat} is close to baselines."
        elif max_gap_pct <= max_above_recent_pct:
            verdict = "Aggressive"
            short_answer = f"**Aggressive** — **{projected:g}** {stat} is **{max_gap_pct:+.0f}%** above {worst_baseline}."
        else:
            verdict = "Unlikely"
            short_answer = f"**Unlikely** — **{projected:g}** {stat} is **{max_gap_pct:+.0f}%** above {worst_baseline} (>{max_above_recent_pct:g}% tolerance)."
        why = f"Largest gap vs **{worst_baseline}** is **{max_gap_pct:+.0f}%**; tolerance is **{max_above_recent_pct:g}%** above recent."
        live_metrics = {
            "Verdict": verdict,
            f"Projected {stat}": f"{projected:g}",
            "Largest gap": f"{max_gap_pct:+.0f}% vs {worst_baseline}",
        }

    calc = "\n".join(calc_lines) if calc_lines else "Compare projection to recent, career, and trend baselines."

    data_used = [
        x
        for x in (
            f"Projection: **{projected:g}** {stat}" if projected is not None else "",
            f"Recent: **{recent:g}**" if recent is not None else "",
            f"Career avg: **{career:g}**" if career is not None else "",
            f"Trend slope: **{slope:g}**/season" if slope is not None else "",
        )
        if x
    ]

    return _coach_result(
        question=question,
        problem_type="Projection realism",
        math_idea=math_idea,
        variables=variables,
        data_used=data_used,
        calculation=calc,
        result=verdict,
        interpretation=why,
        assumptions=[f"{player} playing time similar to recent seasons.", "Breakouts can exceed baselines — but need evidence."],
        sensitivity_notes="Tighter % tolerance above recent → more projections flagged unlikely.",
        missing_fields=missing,
        partial=bool(missing),
        problem_type_id=BASEBALL_PROJECTION,
        computed={"projected": projected, "max_gap_pct": max_gap_pct, "verdict": verdict},
        default_controls={
            "max_above_recent_pct": max_above_recent_pct,
            "max_above_career_pct": max_above_career_pct,
        },
        conclusion=short_answer,
        confidence_pct=74 if projected and baselines else 42,
        reasons=[why] if why else [],
        short_answer=short_answer,
        why=why,
        sensitivity_plain=(
            f"If tolerance drops from **{max_above_recent_pct:g}%** to **{max(10, max_above_recent_pct - 10):g}%**, "
            f"a **{max_gap_pct:+.0f}%** gap → {'unlikely' if max_gap_pct > max(10, max_above_recent_pct - 10) else 'aggressive'}."
            if projected
            else "Adjust tolerance sliders below."
        ),
        live_metrics=live_metrics,
        data_would_improve=["**projection.projected** from ML Projections page"] if missing else [],
    )


def _stat_row_for_focus(
    rows: list[tuple[str, float, float]],
    focus: str,
) -> tuple[str, float, float] | None:
    if not rows:
        return None
    focus_low = focus.lower()
    for stat, a, b in rows:
        if focus_low in stat.lower() or stat.lower() in focus_low:
            return stat, a, b
    # Prefer runs-like stats for forecast questions
    for stat, a, b in rows:
        if any(k in stat.lower() for k in ("run", "rbi", "hr", "hit")):
            return stat, a, b
    return rows[0]


def _accumulate_with_decline(rate: float, seasons: int, decline: float) -> float:
    """Total stat over seasons with per-season decline factor."""
    total = 0.0
    for t in range(seasons):
        total += rate * ((1.0 - decline) ** t)
    return total


def solve_baseball_future_accumulation(
    ctx: dict[str, Any],
    question: str,
    *,
    seasons_a: int | None = None,
    seasons_b: int | None = None,
    decline_a: float = 0.02,
    decline_b: float = 0.03,
    horizon_seasons: int = 10,
    rate_a_override: float | None = None,
    rate_b_override: float | None = None,
) -> SolverResult:
    from components.applied_math_question_intent import classify_question_intent

    intent = classify_question_intent(question)
    pa = str(ctx.get("player_a") or "Player A").strip()
    pb = str(ctx.get("player_b") or "Player B").strip()
    focus = intent.focus_stat or "runs"
    rows = _collect_comparison_rows(ctx, pa, pb)
    picked = _stat_row_for_focus(rows, focus)
    stat_name = picked[0] if picked else focus
    rate_a = picked[1] if picked else None
    rate_b = picked[2] if picked else None

    # Parse ages from context if present
    age_a = _num(ctx.get("player_a_age") or ctx.get("age_a"))
    age_b = _num(ctx.get("player_b_age") or ctx.get("age_b"))
    if isinstance(ctx.get("_ami_comparison_context"), dict):
        for k, v in ctx["_ami_comparison_context"].items():
            if "age" in k.lower() and pa.split()[-1].lower() in str(v).lower():
                age_a = age_a or _extract_pair_values(str(v))[0]
            if "age" in k.lower() and pb.split()[-1].lower() in str(v).lower():
                age_b = age_b or _extract_pair_values(str(v))[0]
        if "Age" in ctx["_ami_comparison_context"]:
            a_age, b_age = _extract_pair_values(str(ctx["_ami_comparison_context"]["Age"]))
            age_a = age_a or a_age
            age_b = age_b or b_age

    default_seasons = horizon_seasons
    if intent.horizon:
        m = re.search(r"(\d+)", intent.horizon)
        if m:
            default_seasons = int(m.group(1))

    sa = seasons_a if seasons_a is not None else default_seasons
    sb = seasons_b if seasons_b is not None else default_seasons
    # Younger player often projects more remaining seasons — rough default from age
    if age_a is not None and age_b is not None and seasons_a is None and seasons_b is None:
        if age_a < age_b:
            sa = default_seasons
            sb = max(1, default_seasons - int(age_b - age_a))
        elif age_b < age_a:
            sb = default_seasons
            sa = max(1, default_seasons - int(age_a - age_b))

    missing: list[str] = []
    rates_from_context = rate_a is not None and rate_b is not None
    if not rates_from_context:
        missing.append("comparison_stats (rate for focus stat)")
        rate_a = rate_a_override if rate_a_override is not None else 90.0
        rate_b = rate_b_override if rate_b_override is not None else 100.0

    math_idea = (
        f"This is a **future accumulation** forecast — not who is better today. "
        f"We project total **{stat_name}** as runs-per-season × remaining seasons, adjusted for decline."
    )
    variables = (
        f"rate = {stat_name} per season\n"
        f"seasons = projected seasons remaining\n"
        f"decline = yearly production decline (0–1)\n"
        f"total = Σ rate × (1 − decline)^t"
    )

    total_a = total_b = 0.0
    calc = ""
    if rate_a is not None and rate_b is not None:
        total_a = _accumulate_with_decline(rate_a, sa, decline_a)
        total_b = _accumulate_with_decline(rate_b, sb, decline_b)
        calc = (
            f"**{pa}**: {rate_a:g} {stat_name}/season × **{sa}** seasons (decline **{decline_a:.0%}/yr**)\n"
            f"→ projected total ≈ **{total_a:.0f}** {stat_name}\n\n"
            f"**{pb}**: {rate_b:g} {stat_name}/season × **{sb}** seasons (decline **{decline_b:.0%}/yr**)\n"
            f"→ projected total ≈ **{total_b:.0f}** {stat_name}"
        )

    short_answer = "Adjust per-season rates below to explore the forecast."
    why = ""
    live_metrics: dict[str, str] = {}

    if rate_a is not None and rate_b is not None:
        leader = pa if total_a > total_b * 1.02 else pb if total_b > total_a * 1.02 else ""
        if leader:
            short_answer = (
                f"**{leader}** projects to accumulate more **{stat_name}** over the horizon "
                f"({total_a:.0f} vs {total_b:.0f}), even though today's rate may differ."
            )
        else:
            short_answer = f"Too close to call — projected totals **{total_a:.0f}** vs **{total_b:.0f}** {stat_name}."
        if age_a is not None and age_b is not None and age_a != age_b:
            younger = pa if age_a < age_b else pb
            why = (
                f"**{younger}** is younger ({min(age_a, age_b):.0f} vs {max(age_a, age_b):.0f}), "
                f"so more projected seasons can outweigh a lower current rate."
            )
        else:
            why = (
                f"Future totals depend on rate × seasons × decline — "
                f"**{pa}** {rate_a:g}/yr for **{sa}** seasons vs **{pb}** {rate_b:g}/yr for **{sb}**."
            )
        live_metrics = {
            f"{pa} projected {stat_name}": f"{total_a:.0f}",
            f"{pb} projected {stat_name}": f"{total_b:.0f}",
            "Leader (forecast)": leader or "Toss-up",
        }

    data_used = [
        x
        for x in (
            f"Focus stat: **{stat_name}**",
            f"{pa} rate: **{rate_a:g}**/season" if rate_a is not None else "",
            f"{pb} rate: **{rate_b:g}**/season" if rate_b is not None else "",
            f"Horizon: **{default_seasons}** seasons",
            f"Ages: {pa} **{age_a:g}**, {pb} **{age_b:g}**" if age_a and age_b else "",
        )
        if x
    ]

    sens_rows: list[dict[str, str]] = []
    if rate_a and rate_b and sa:
        for s in (8, 10, 12):
            ta = _accumulate_with_decline(rate_a, s, decline_a)
            tb = _accumulate_with_decline(rate_b, s, decline_b)
            out = pa if ta > tb else pb if tb > ta else "Tie"
            sens_rows.append({"Parameter": f"{pa} seasons", "Scenario": str(s), "Outcome": f"{out} leads"})

    return _coach_result(
        question=question,
        problem_type="Future stat accumulation forecast",
        math_idea=math_idea,
        variables=variables,
        data_used=data_used,
        calculation=calc or "Need per-season rates from the comparison chart.",
        result=short_answer,
        interpretation=why,
        assumptions=[
            "Decline rates are illustrative aging curves, not injury-adjusted.",
            "Seasons remaining can differ by age and durability.",
        ],
        sensitivity_notes="More seasons for the younger player can flip the forecast even if their current rate is lower.",
        missing_fields=missing,
        partial=bool(missing),
        problem_type_id=BASEBALL_FUTURE_ACCUMULATION,
        computed={
            "total_a": total_a,
            "total_b": total_b,
            "rate_a": rate_a,
            "rate_b": rate_b,
            "seasons_a": sa,
            "seasons_b": sb,
            "rates_assumed": not rates_from_context,
        },
        default_controls={
            "seasons_a": sa,
            "seasons_b": sb,
            "decline_a": decline_a,
            "decline_b": decline_b,
            "rate_a": rate_a,
            "rate_b": rate_b,
            "horizon_seasons": default_seasons,
        },
        conclusion=short_answer,
        confidence_pct=76 if rate_a and rate_b else 44,
        reasons=[why] if why else [],
        short_answer=short_answer,
        why=why,
        sensitivity_plain="Adjust remaining seasons and decline rates — age advantage shows up in seasons, not just today's rate.",
        live_metrics=live_metrics,
        sensitivity_rows=sens_rows,
    )


def solve_investment_drawdown_attribution(
    ctx: dict[str, Any],
    question: str,
    *,
    focus_ticker: str = "",
    market_decline: float = -20.0,
    equity_correlation: float = 0.85,
) -> SolverResult:
    from components.applied_math_question_intent import classify_question_intent

    intent = classify_question_intent(question)
    ticker = (focus_ticker or intent.attribution_target or "VTI").strip().upper()
    weights = _parse_weights_map(ctx.get("current_weights") if isinstance(ctx.get("current_weights"), dict) else {})
    max_dd = _num(ctx.get("max_drawdown"))
    holdings = _ctx_list(ctx.get("holdings"))

    w = weights.get(ticker)
    if w is None:
        for k, v in weights.items():
            if k.upper() == ticker:
                w = v
                ticker = k
                break

    missing: list[str] = []
    if not weights:
        missing.append("current_weights")
    if w is None:
        missing.append(f"weight for {ticker}")

    math_idea = (
        f"This is **drawdown attribution** — why **{ticker}** contributes to portfolio drawdown risk. "
        f"Cause first: weight × exposure; stress scenarios come second."
    )
    variables = (
        "weight_i = portfolio fraction\n"
        "drawdown_contribution_i ≈ weight_i × market_decline × correlation\n"
        "concentration amplifies when one holding dominates equity exposure"
    )

    calc_lines: list[str] = []
    top_equity_share = 0.0
    if weights:
        sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        top_equity_share = sum(x[1] for x in sorted_w[:3])

    contrib_pct = 0.0
    if w is not None:
        contrib_pct = abs(w * market_decline * equity_correlation)
        calc_lines.append(f"**{ticker} weight** = **{w * 100:.1f}%**")
        calc_lines.append(f"Assumed market decline = **{market_decline:g}%**")
        calc_lines.append(f"Equity correlation ≈ **{equity_correlation:.2f}**")
        calc_lines.append(
            f"\nDrawdown contribution ≈ weight × decline × correlation\n"
            f"= {w * 100:.1f}% × {abs(market_decline):g}% × {equity_correlation:.2f} "
            f"≈ **{contrib_pct:.1f}pp** portfolio drawdown"
        )
        if max_dd is not None:
            calc_lines.append(f"\nObserved portfolio max drawdown: **{max_dd:g}%**")

    short_answer = f"Explain why **{ticker}** adds drawdown risk once weights are attached."
    why = ""
    live_metrics: dict[str, str] = {}

    if w is not None:
        if w >= 0.25:
            short_answer = (
                f"**{ticker}** creates drawdown risk because it is **{w * 100:.0f}%** of the portfolio — "
                f"a large equity slice moves the whole account when markets fall."
            )
        else:
            short_answer = (
                f"**{ticker}** contributes an estimated **{contrib_pct:.1f}pp** to drawdown "
                f"at **{w * 100:.0f}%** weight when equities drop **{abs(market_decline):g}%**."
            )
        why_parts = [
            f"High weight (**{w * 100:.1f}%**) means market moves hit a big share of assets.",
        ]
        if top_equity_share >= 0.6:
            why_parts.append(
                f"Top-3 holdings are **{top_equity_share * 100:.0f}%** of the book — equity concentration adds correlation risk."
            )
        why = " ".join(why_parts)
        live_metrics = {
            f"{ticker} weight": f"{w * 100:.1f}%",
            "Est. drawdown contribution": f"{contrib_pct:.1f}pp",
            "Top-3 weight share": f"{top_equity_share * 100:.0f}%",
        }

    stress_note = (
        f"\n\n**Then (what-if):** If markets fall **{abs(market_decline):g}%**, "
        f"this holding alone contributes roughly **{contrib_pct:.1f}pp** to portfolio drawdown."
        if w is not None
        else ""
    )

    data_used = [
        x
        for x in (
            f"**{ticker}** weight: **{w * 100:.1f}%**" if w is not None else "",
            f"Portfolio max drawdown: **{max_dd:g}%**" if max_dd is not None else "",
            f"Holdings: {', '.join(holdings[:4])}" if holdings else "",
        )
        if x
    ]

    return _coach_result(
        question=question,
        problem_type="Drawdown risk attribution",
        math_idea=math_idea,
        variables=variables,
        data_used=data_used,
        calculation="\n".join(calc_lines) + stress_note,
        result=short_answer,
        interpretation=why,
        assumptions=[
            f"{ticker} behaves like broad equity for correlation purposes.",
            "Attribution is illustrative — not a full factor decomposition.",
        ],
        sensitivity_notes=stress_note.strip() if stress_note else "Adjust market decline to see contribution change.",
        missing_fields=missing,
        partial=bool(missing),
        problem_type_id=INVESTMENT_DRAWDOWN_ATTRIBUTION,
        computed={
            "ticker": ticker,
            "weight": w,
            "contribution_pp": contrib_pct,
            "market_decline": market_decline,
        },
        default_controls={
            "focus_ticker": ticker,
            "market_decline": market_decline,
            "equity_correlation": equity_correlation,
        },
        conclusion=short_answer,
        confidence_pct=78 if w is not None else 42,
        reasons=[why] if why else [],
        short_answer=short_answer,
        why=why,
        sensitivity_plain=(
            f"If {ticker} weight drops from **{w * 100:.0f}%** to **{max(5, int(w * 100) - 10)}%**, "
            f"drawdown contribution falls roughly in proportion."
            if w is not None
            else "Attach portfolio weights to quantify contribution."
        ),
        live_metrics=live_metrics,
    )


def _player_adp_from_row(row: Any) -> float | None:
    if not isinstance(row, dict):
        return None
    for key in ("Market Rank", "market_rank", "ADP", "adp", "Model Rank", "model_rank"):
        v = _num(row.get(key))
        if v is not None and v >= 3:
            return float(v)
    return None


def _player_metric(row: Any, *keys: str) -> Any:
    if not isinstance(row, dict):
        return None
    for key in keys:
        val = row.get(key)
        if val is not None and str(val).strip() != "":
            return val
    return None


def _parse_draft_projection(val: Any) -> dict[str, Any]:
    """Extract ADP, round, pick from structured dict or projection string."""
    out: dict[str, Any] = {}
    if isinstance(val, dict):
        for key in ("adp", "current_pick", "draft_round", "projected_rank", "position_scarcity"):
            parsed = _num(val.get(key))
            if parsed is not None:
                out[key] = int(parsed) if key in ("current_pick", "draft_round", "projected_rank") else parsed
        top = val.get("top_pick")
        if isinstance(top, str) and top.strip():
            out["top_pick"] = top.strip()
        for rows_key in ("top_recommendations", "best_available", "available_players"):
            rows = val.get(rows_key)
            if isinstance(rows, list) and rows:
                adp_from_row = _player_adp_from_row(rows[0])
                if adp_from_row is not None and "adp" not in out:
                    out["adp"] = adp_from_row
                break
        return out

    low = str(val or "").lower()
    if low.startswith("{") and "current_pick" in low:
        return out
    m = re.search(r"\badp\s*[#:]?\s*(\d+(?:\.\d+)?)\b", low)
    if m:
        out["adp"] = float(m.group(1))
    m = re.search(r"\brank\s*[#:]?\s*(\d+)\b", low)
    if m:
        out["projected_rank"] = int(m.group(1))
    m = re.search(r"round\s*(\d+)", low)
    if m:
        out["projected_round"] = int(m.group(1))
    m = re.search(r"pick\s*(\d+)", low)
    if m:
        out["pick"] = int(m.group(1))
    if "adp" not in out:
        m = re.search(r"\badp\s*(\d+(?:\.\d+)?)\b", low)
        if m:
            out["adp"] = float(m.group(1))
    return out


def _parse_pct(val: Any) -> float | None:
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        v = float(val)
        return v if v <= 1 else v
    s = str(val).strip().replace("%", "")
    try:
        v = float(s)
        return v if v <= 1 else v
    except ValueError:
        return None


def _drafted_name_tokens(names: list[str] | None) -> set[str]:
    return {_player_name_token(str(n).split(" (")[0].strip()) for n in (names or []) if str(n).strip()}


def _filter_undrafted_player_rows(
    rows: list[dict[str, Any]],
    drafted_tokens: set[str],
) -> list[dict[str, Any]]:
    """Drop players already drafted — recommendations must never include off-board names."""
    if not drafted_tokens:
        return rows
    out: list[dict[str, Any]] = []
    for row in rows:
        name = _draft_player_name(row)
        if name and _player_name_token(name) in drafted_tokens:
            continue
        out.append(row)
    return out


def _draft_roster_note(bundle: dict[str, Any]) -> str:
    """Describe roster without implying drafted roster players are draft targets."""
    roster = bundle.get("roster") or []
    review_team = str(bundle.get("draft_review_team") or "").strip()
    if not roster:
        return f"**{review_team}**'s roster" if review_team else "your roster"
    drafted_tokens = _drafted_name_tokens(bundle.get("drafted_players"))
    parts: list[str] = []
    for name in roster[:4]:
        clean = str(name).split(" (")[0].strip()
        if _player_name_token(clean) in drafted_tokens:
            parts.append(f"**{clean}** (already drafted)")
        else:
            parts.append(f"**{clean}**")
    tail = "…" if len(roster) > 4 else ""
    owner = review_team or "your"
    if review_team:
        return f"**{review_team}**'s **{len(roster)}**-player roster ({', '.join(parts)}{tail})"
    return f"your **{len(roster)}**-player roster ({', '.join(parts)}{tail})"


def _hitter_pool_rows(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    drafted_tokens = _drafted_name_tokens(bundle.get("drafted_players"))
    hitters: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in _all_pool_rows(bundle):
        pos = str(_player_metric(row, "Primary Position", "position", "pos") or "").upper()
        if pos in ("SP", "RP", "P") or "PITCH" in pos:
            continue
        name = _draft_player_name(row)
        if not name or name.lower() in seen:
            continue
        if _player_name_token(name) in drafted_tokens:
            continue
        seen.add(name.lower())
        hitters.append(row)
    return sorted(hitters, key=_row_market_rank)


def _draft_player_name(row: Any) -> str:
    if isinstance(row, dict):
        return str(row.get("player") or row.get("Player") or row.get("fullName") or "").strip()
    return str(row or "").strip()


def _draft_player_rows(val: Any) -> list[dict[str, Any]]:
    if not isinstance(val, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in val:
        if isinstance(item, dict):
            rows.append(item)
        elif item:
            rows.append({"player": str(item).strip()})
    return rows


def _draft_context_bundle(ctx: dict[str, Any]) -> dict[str, Any]:
    snap = ctx.get("draft_snapshot") if isinstance(ctx.get("draft_snapshot"), dict) else {}
    sleepers_snap = ctx.get("sleepers_snapshot") if isinstance(ctx.get("sleepers_snapshot"), dict) else {}
    proj_raw = ctx.get("draft_projection")
    proj = proj_raw if isinstance(proj_raw, dict) else {}

    roster = _ctx_list(ctx.get("roster"))
    review_team = str(ctx.get("draft_review_team") or snap.get("draft_review_team") or "").strip()
    if not roster and not review_team:
        ur = snap.get("user_roster") or sleepers_snap.get("synced_roster")
        if isinstance(ur, list):
            roster = [str(x).strip() for x in ur if str(x).strip()]

    recommendations = _draft_player_rows(
        ctx.get("recommended_players") or snap.get("recommended_players") or proj.get("top_recommendations")
    )
    sleepers = _draft_player_rows(ctx.get("sleepers") or snap.get("sleepers"))
    sleeper_candidates = _draft_player_rows(
        ctx.get("sleeper_candidates") or sleepers_snap.get("sleeper_candidates")
    )
    if sleeper_candidates:
        sleepers = sleeper_candidates + [s for s in sleepers if _draft_player_name(s) not in {_draft_player_name(x) for x in sleeper_candidates}]

    available = _draft_player_rows(
        snap.get("available_players")
        or ctx.get("available_players")
        or proj.get("available_players")
        or ctx.get("best_available")
        or snap.get("best_available_players")
        or proj.get("best_available")
    )
    best_available = _draft_player_rows(
        ctx.get("best_available")
        or snap.get("best_available_players")
        or proj.get("best_available")
        or available
    )

    scoring = ctx.get("scoring_settings") if isinstance(ctx.get("scoring_settings"), dict) else {}
    if not scoring and isinstance(snap.get("scoring_settings"), dict):
        scoring = snap["scoring_settings"]

    rnd = _num(ctx.get("draft_round")) or _num(snap.get("draft_round")) or _num(proj.get("draft_round"))
    pick = _num(ctx.get("current_pick")) or _num(snap.get("current_pick")) or _num(proj.get("current_pick"))

    needed_positions = _ctx_list(ctx.get("needed_positions") or snap.get("needed_positions") or proj.get("needed_positions"))
    if not needed_positions:
        needed_positions = _ctx_list(ctx.get("roster_needs") or sleepers_snap.get("roster_needs"))
    category_needs = _ctx_list(ctx.get("category_needs") or snap.get("category_needs") or proj.get("category_needs"))

    drafted_players = _ctx_list(ctx.get("drafted_players") or snap.get("drafted_players") or proj.get("drafted_players"))
    if not drafted_players:
        drafted_players = _ctx_list(snap.get("canonical_drafted_players") or ctx.get("drafted_exclusions") or sleepers_snap.get("drafted_exclusions"))

    draft_queue = _ctx_list(ctx.get("draft_queue") or snap.get("draft_queue") or sleepers_snap.get("draft_queue"))
    watchlist = _ctx_list(ctx.get("watchlist") or snap.get("watchlist_focus") or sleepers_snap.get("watchlist_focus"))
    tracked_players = _ctx_list(ctx.get("tracked_players") or snap.get("tracked_players"))

    position_scarcity = _num(ctx.get("position_scarcity")) or _num(snap.get("position_scarcity")) or _num(proj.get("position_scarcity"))

    player = str(
        ctx.get("question_player")
        or ctx.get("player")
        or ((ctx.get("players") or [""])[0] if isinstance(ctx.get("players"), list) else "")
    ).strip()
    if not player and sleepers:
        player = _draft_player_name(sleepers[0])
    if not player and recommendations:
        player = _draft_player_name(recommendations[0])

    drafted_exclusions = _ctx_list(ctx.get("drafted_exclusions") or sleepers_snap.get("drafted_exclusions") or drafted_players)
    question_player_row = ctx.get("question_player_row") if isinstance(ctx.get("question_player_row"), dict) else None
    draft_status = ctx.get("draft_status") if isinstance(ctx.get("draft_status"), dict) else {}
    canonical_board = _draft_player_rows(
        snap.get("draft_room_board") or snap.get("canonical_draft_board") or ctx.get("draft_room_board")
    )
    board_rows = _draft_player_rows(
        snap.get("draft_room_board") or ctx.get("draft_room_board") or canonical_board
    )

    bundle: dict[str, Any] = {
        "snap": snap,
        "sleepers_snap": sleepers_snap,
        "proj": proj,
        "roster": roster,
        "recommendations": recommendations,
        "sleepers": sleepers,
        "sleeper_candidates": sleeper_candidates,
        "available": available,
        "best_available": best_available,
        "canonical_board": canonical_board,
        "board_rows": board_rows,
        "scoring": scoring,
        "round": int(rnd) if rnd is not None else None,
        "pick": int(pick) if pick is not None else None,
        "player": player,
        "player_a": str(ctx.get("player_a") or "").strip(),
        "player_b": str(ctx.get("player_b") or "").strip(),
        "question_player": str(ctx.get("question_player") or "").strip(),
        "question_player_row": question_player_row,
        "draft_status": draft_status,
        "guidance": str(ctx.get("ami_guidance") or "").strip(),
        "needed_positions": needed_positions,
        "category_needs": category_needs,
        "drafted_players": drafted_players,
        "drafted_exclusions": drafted_exclusions,
        "draft_queue": draft_queue,
        "watchlist": watchlist,
        "tracked_players": tracked_players,
        "position_scarcity": position_scarcity,
        "ami_answer_template": ctx.get("ami_answer_template") if isinstance(ctx.get("ami_answer_template"), list) else [],
        "my_next_pick": _num(snap.get("my_next_pick")) or _num(proj.get("my_next_pick")) or _num(ctx.get("my_next_pick")),
        "draft_review_team": str(ctx.get("draft_review_team") or snap.get("draft_review_team") or "").strip(),
    }
    _attach_player_position_index(bundle, ctx)
    return bundle


def _position_suffix_from_name(name: str) -> str:
    m = re.search(r"\(([^)]+)\)\s*$", str(name or "").strip())
    if not m:
        return ""
    token = m.group(1).strip().upper()
    if token in ("C", "1B", "2B", "3B", "SS", "OF", "SP", "RP", "DH", "P"):
        return token
    return ""


def _attach_player_position_index(bundle: dict[str, Any], ctx: dict[str, Any]) -> None:
    index: dict[str, str] = {}
    snap = bundle.get("snap") if isinstance(bundle.get("snap"), dict) else {}
    for src in (
        ctx.get("player_position_index"),
        ctx.get("player_position_lookup"),
        ctx.get("roster_position_index"),
        snap.get("player_position_index"),
        snap.get("player_position_lookup"),
        snap.get("roster_position_index"),
    ):
        if not isinstance(src, dict):
            continue
        for name, pos in src.items():
            token = _player_name_token(str(name))
            pos_val = str(pos or "").strip()
            if token and pos_val:
                index[token] = pos_val
    for row in snap.get("user_roster_detail") or []:
        if isinstance(row, dict):
            name = str(row.get("player") or row.get("Player") or "").strip()
            pos = _player_metric(row, "Primary Position", "position", "pos")
            if name and pos:
                index[_player_name_token(name)] = str(pos)
    ctx_snap = ctx.get("draft_snapshot")
    if isinstance(ctx_snap, dict):
        for row in ctx_snap.get("user_roster_detail") or []:
            if isinstance(row, dict):
                name = str(row.get("player") or row.get("Player") or "").strip()
                pos = _player_metric(row, "Primary Position", "position", "pos")
                if name and pos:
                    index[_player_name_token(name)] = str(pos)
    for pool_key in ("board_rows", "canonical_board", "available", "best_available", "recommendations"):
        for row in bundle.get(pool_key) or []:
            if not isinstance(row, dict):
                continue
            name = _draft_player_name(row)
            pos = _player_metric(row, "Primary Position", "position", "pos")
            if name and pos:
                index[_player_name_token(name)] = str(pos)
    for name in bundle.get("roster") or []:
        clean = str(name).split(" (")[0].strip()
        token = _player_name_token(clean)
        if not clean or token in index:
            continue
        for row in _all_pool_rows(bundle):
            if _player_name_token(_draft_player_name(row)) == token:
                pos = _player_metric(row, "Primary Position", "position", "pos")
                if pos:
                    index[token] = str(pos)
                    break
    bundle["_position_index"] = index


def _draft_num_teams(bundle: dict[str, Any], ctx: dict[str, Any], default: int = 12) -> int:
    scoring = bundle.get("scoring") if isinstance(bundle.get("scoring"), dict) else {}
    for key in ("room_team_count", "num_teams", "team_count"):
        val = _num(scoring.get(key)) or _num(ctx.get(key))
        if val is not None and int(val) > 0:
            return int(val)
    meta = bundle.get("snap", {}).get("canonical_draft_meta")
    if isinstance(meta, dict):
        val = _num(meta.get("team_count") or meta.get("num_teams"))
        if val is not None and int(val) > 0:
            return int(val)
    return default


def _resolve_draft_pick_round(
    bundle: dict[str, Any],
    ctx: dict[str, Any],
    parsed: dict[str, Any],
    *,
    num_teams: int = 12,
) -> tuple[int | None, int | None, bool, bool]:
    """Return pick, round, pick_known, round_known — never invent pick from formula."""
    pick = bundle.get("pick")
    rnd = bundle.get("round")
    pick_known = pick is not None
    round_known = rnd is not None
    if not pick_known:
        p = parsed.get("pick") or parsed.get("current_pick")
        if p is not None:
            pick = int(p)
            pick_known = True
    if not round_known:
        r = parsed.get("draft_round") or parsed.get("projected_round")
        if r is not None:
            rnd = int(r)
            round_known = True
    teams = _draft_num_teams(bundle, ctx, num_teams)
    snap = bundle.get("snap") if isinstance(bundle.get("snap"), dict) else {}
    snap_round = _num(snap.get("draft_round"))
    ctx_round = _num(ctx.get("draft_round"))
    bundle_round = _num(bundle.get("round"))
    explicit_round = ctx_round or snap_round or bundle_round
    if explicit_round is not None and int(explicit_round) > 0:
        rnd = int(explicit_round)
        round_known = True
    elif pick_known and pick is not None:
        rnd = (int(pick) - 1) // teams + 1
        round_known = True
    return (
        int(pick) if pick_known and pick is not None else None,
        int(rnd) if round_known and rnd is not None else None,
        pick_known,
        round_known,
    )


def _format_pick_note(pick: int | None, rnd: int | None, *, pick_known: bool, round_known: bool) -> str:
    if pick_known and round_known and pick is not None and rnd is not None:
        return f"pick **{pick}** (round **{rnd}**)"
    if pick_known and pick is not None:
        return f"pick **{pick}** (round not in context)"
    if round_known and rnd is not None:
        return f"round **{rnd}** (exact pick not in context)"
    return "pick and round not in saved board context"


def _enrich_row_from_canon(row: dict[str, Any], canon: list[dict[str, Any]]) -> dict[str, Any]:
    if _player_metric(row, "Primary Position", "position", "pos"):
        return row
    token = _player_name_token(_draft_player_name(row))
    for cr in canon:
        if _player_name_token(_draft_player_name(cr)) == token:
            merged = dict(cr)
            merged.update(row)
            return merged
    return row


def _all_pool_rows(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    canon = bundle.get("canonical_board") or []
    for pool_key in ("available", "best_available", "recommendations", "canonical_board", "board_rows"):
        for row in bundle.get(pool_key) or []:
            if not isinstance(row, dict):
                continue
            enriched = _enrich_row_from_canon(row, canon)
            name = _draft_player_name(enriched)
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            rows.append(enriched)
    return rows


def _sanitize_extracted_player_name(name: str) -> str:
    s = str(name or "").strip().strip("?,").strip()
    if not s:
        return ""
    s = re.sub(
        r"\s+at\s+(?:c\b|catcher|catchers|1b|2b|3b|ss|of|sp|rp|closer|shortstop|outfield|first base|second base|third base|starting pitcher|relief pitcher).*$",
        "",
        s,
        flags=re.I,
    )
    s = re.sub(r"\s+for\s+pick\s+\d+.*$", "", s, flags=re.I)
    s = re.sub(r"\s+now\s+or.*$", "", s, flags=re.I)
    return s.strip()


def _extract_player_from_question_text(question: str) -> str:
    q = str(question or "").strip()
    low = q.lower()
    patterns = (
        r"(?:should i )?(?:select|draft|take|grab)\s+(.+?)\s+at\s+(?:c\b|catcher|catchers|1b|2b|3b|ss|of|sp|rp)",
        r"(?:should i )?(?:select|draft|take|grab)\s+(.+?)\s+as a\s+",
        r"(?:should i )?(?:select|draft|take|grab)\s+(.+?)\s+now or wait",
        r"will (.+?) make it back",
        r"why is (.+?) the best",
        r"why is (.+?) a good",
        r"why is (.+?) worth",
        r"should i draft (.+?)(?:\?|\s+or|\s+as|\s*$)",
        r"is (.+?) (?:worth|available|the best)",
    )
    invalid_tokens = frozenset(
        {
            "should",
            "select",
            "draft",
            "take",
            "grab",
            "wait",
            "catcher",
            "now",
            "later",
            "round",
        }
    )
    for pat in patterns:
        m = re.search(pat, low, flags=re.I)
        if not m:
            continue
        name = q[m.start(1) : m.end(1)].strip().strip("?,").strip()
        parts = name.split()
        if len(parts) < 2 or len(name) > 48:
            continue
        if any(p.lower() in invalid_tokens for p in parts[:2]):
            continue
        if parts[0].lower() in ("should", "which", "what", "will", "can"):
            continue
        cleaned = _sanitize_extracted_player_name(name)
        if len(cleaned.split()) < 2:
            continue
        return cleaned
    return ""


def _normalize_position_query_for_pool(position_query: str) -> str:
    q = str(position_query or "").strip().lower()
    if q in ("c", "catcher", "catchers"):
        return "catcher"
    if q in ("ss", "shortstop", "shortstops"):
        return "shortstop"
    if q in ("of", "outfield", "outfielder", "outfielders"):
        return "outfield"
    if q in ("sp", "starter", "starters", "starting pitcher", "starting pitchers"):
        return "starting pitcher"
    if q in ("rp", "reliever", "relievers", "relief pitcher", "relief pitchers", "closer", "closers"):
        return "relief pitcher"
    return q


def _player_name_token(name: str) -> str:
    return str(name or "").split(" (")[0].strip().lower()


def _name_in_player_list(name: str, names: list[str]) -> bool:
    token = _player_name_token(name)
    return bool(token) and any(_player_name_token(n) == token for n in names)


def _find_player_row_in_bundle(name: str, bundle: dict[str, Any]) -> dict[str, Any] | None:
    qrow = bundle.get("question_player_row")
    if isinstance(qrow, dict) and _player_name_token(_draft_player_name(qrow)) == _player_name_token(name):
        return qrow
    token = _player_name_token(name)
    for pool_key in ("recommendations", "available", "best_available", "sleepers", "canonical_board"):
        for row in bundle.get(pool_key) or []:
            if isinstance(row, dict) and _player_name_token(_draft_player_name(row)) == token:
                return row
    return None


def _resolve_focus_player(question: str, ctx: dict[str, Any], bundle: dict[str, Any]) -> str:
    named = str(bundle.get("question_player") or ctx.get("question_player") or "").strip()
    if named:
        return _sanitize_extracted_player_name(named) or named
    parsed = _extract_player_from_question_text(question)
    if parsed:
        return parsed
    return str(bundle.get("player") or "").strip()


def _draft_question_mode(question: str) -> str:
    low = question.lower()
    if is_player_explanation_question(question):
        return "player_why"
    if is_position_best_available_question(question):
        return "position_best_available"
    if is_draft_timing_question(question):
        return "draft_timing_decision"
    if is_draft_review_question(question):
        return "draft_review"
    if is_roster_needs_question(question):
        return "roster_needs"
    if is_draft_market_prediction_question(question):
        return "draft_market_prediction"
    if is_draft_head_to_head_question(question):
        return "draft_player_compare"
    if re.search(r"hitter.*pitcher|pitcher.*hitter", low):
        return "hitter_pitcher"
    if "weakest" in low and "category" in low:
        return "weakest_category"
    if re.search(r"biggest\b.{0,30}\bweakness", low):
        return "roster_weakness"
    if re.search(r"\b(statistical|category|positional?|stat|roster)\b.{0,20}\bweakness", low):
        return "roster_weakness"
    if any(p in low for p in ("biggest roster weakness", "roster weakness", "biggest weakness", "weakest spot")):
        return "roster_weakness"
    if re.search(r"which hitter.*(fit|fits).*(roster|team)|hitter.*fits.*better", low):
        return "hitter_fit"
    if any(p in low for p in ("fits my team", "fit my team", "fits my roster", "who fits")):
        return "team_fit"
    if ("safest" in low and "upside" in low) or re.search(r"safest.*upside|upside.*safest", low):
        return "safety_upside"
    if re.search(r"why is .+ the best", low) or (
        "why is" in low and "best" in low and any(w in low for w in ("draft", "pick", "player"))
    ):
        return "player_why"
    if "why is" in low and any(w in low for w in ("good pick", "worth drafting", "right pick", "strong pick", "worth it")):
        return "player_why"
    if any(p in low for p in ("best values", "values left", "best value", "value left", "values available")):
        return "best_values"
    if "sleeper" in low and any(w in low for w in ("risk", "worth the risk", "how risky", "worth it")):
        return "sleeper_risk"
    if "sleeper" in low:
        return "sleeper"
    if any(w in low for w in ("risky", "take a risk", "risk in", "risk on", "how risky")):
        return "risk"
    if any(w in low for w in ("steal", "power", "category", "balance", "obp", "priorit", "upside", "safety", "pitching", "speed")):
        return "category"
    if any(p in low for p in ("who should", "draft next", "who to draft", "pick next", "draft first", "on the clock", "who should i take")):
        return "next_pick"
    if any(p in low for p in ("projection", "project", "what does this projection")):
        return "projection"
    return "value_edge"


def _draft_market_subtype(question: str) -> str:
    low = question.lower()
    if "make it back" in low:
        return "make_it_back"
    if "how long can i wait" in low or "wait on" in low:
        return "wait_timing"
    if re.search(r"which position", low) and "run" in low:
        return "position_run"
    if "run" in low and any(w in low for w in ("position", "catcher", "coming", "about to")):
        return "position_run"
    if "before my next pick" in low:
        return "before_next_pick"
    return "position_next"


def _infer_scarce_position_from_bundle(bundle: dict[str, Any]) -> str:
    needs = bundle.get("needed_positions") or []
    pos_map = {"C": "catcher", "SS": "shortstop", "OF": "outfield", "SP": "starting pitcher", "RP": "relief pitcher"}
    for need in needs:
        key = str(need).strip().upper()
        if key in pos_map:
            return pos_map[key]
        if str(need).strip():
            return str(need).strip().lower()
    return "catcher"


def _row_market_rank(row: dict[str, Any]) -> float:
    val = _player_metric(row, "Market Rank", "market_rank", "Model Rank", "model_rank")
    try:
        return float(val)
    except (TypeError, ValueError):
        return 9999.0


def _player_profile_bits(row: dict[str, Any]) -> str:
    if not isinstance(row, dict):
        return ""
    parts: list[str] = []
    for keys, label in (
        (("HR", "hr", "Projected HR", "projected_hr"), "HR"),
        (("RBI", "rbi", "Projected RBI", "projected_rbi"), "RBI"),
        (("AVG", "avg", "BA", "batting_avg"), "AVG"),
        (("OBP", "obp"), "OBP"),
        (("SB", "sb"), "SB"),
    ):
        val = _player_metric(row, *keys)
        if val is not None:
            parts.append(f"{label} **{val}**")
    return ", ".join(parts[:5])


def _position_alt_names(
    bundle: dict[str, Any],
    *,
    position_query: str,
    exclude_name: str,
    limit: int = 3,
) -> list[str]:
    pool = _pool_rows_by_position(bundle, position_query)
    focus_token = _player_name_token(exclude_name)
    names: list[str] = []
    for row in pool:
        name = _draft_player_name(row)
        if not name or _player_name_token(name) == focus_token:
            continue
        names.append(name)
        if len(names) >= limit:
            break
    return names


def _pool_rows_by_position(bundle: dict[str, Any], position_query: str) -> list[dict[str, Any]]:
    position_query = _normalize_position_query_for_pool(position_query)
    drafted_tokens = {
        _player_name_token(str(n).split(" (")[0].strip())
        for n in (bundle.get("drafted_players") or [])
    }
    pools: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in _all_pool_rows(bundle):
        name = _draft_player_name(row)
        if not name or name.lower() in seen:
            continue
        if _player_name_token(name) in drafted_tokens:
            continue
        pos = str(_player_metric(row, "Primary Position", "position", "pos") or "")
        if not pos:
            pos = str((bundle.get("_position_index") or {}).get(_player_name_token(name)) or "")
        if position_query and not position_matches_row(position_query, pos):
            continue
        seen.add(name.lower())
        pools.append(row)
    if not pools and position_query:
        index = bundle.get("_position_index") if isinstance(bundle.get("_position_index"), dict) else {}
        for pool_key in ("available", "best_available", "recommendations", "sleepers", "canonical_board"):
            for row in bundle.get(pool_key) or []:
                if not isinstance(row, dict):
                    continue
                name = _draft_player_name(row)
                token = _player_name_token(name)
                if not name or token in seen or token in drafted_tokens:
                    continue
                pos = str(_player_metric(row, "Primary Position", "position", "pos") or index.get(token) or "")
                if pos and position_matches_row(position_query, pos):
                    seen.add(name.lower())
                    pools.append(row)
    return sorted(pools, key=_row_market_rank)


def _player_position_from_pools(bundle: dict[str, Any], player_name: str) -> str:
    suffix = _position_suffix_from_name(player_name)
    if suffix:
        return suffix
    token = _player_name_token(player_name)
    index = bundle.get("_position_index")
    if isinstance(index, dict):
        pos = index.get(token)
        if pos:
            return str(pos)
    for row in _all_pool_rows(bundle):
        if _player_name_token(_draft_player_name(row)) == token:
            return str(_player_metric(row, "Primary Position", "position", "pos") or "")
    return ""


def _draft_scoring_label(scoring: dict[str, Any]) -> str:
    for key in ("draft_format", "draft_lab_scoring_type", "scoring_type", "room_format"):
        val = scoring.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return "standard"


def _format_need_list(positions: list[str], categories: list[str]) -> str:
    parts: list[str] = []
    if positions:
        parts.append("/".join(positions[:6]))
    if categories:
        parts.append(" + ".join(categories[:6]))
    return " · ".join(parts) if parts else "balanced coverage"


def _draft_context_notes(bundle: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    drafted = bundle.get("drafted_players") or []
    if drafted:
        notes.append(
            f"**{len(drafted)}** picks already on board (do not draft again: "
            f"{', '.join(drafted[:4])}{'…' if len(drafted) > 4 else ''})"
        )
    if bundle.get("draft_queue"):
        notes.append(f"Queue: **{', '.join(bundle['draft_queue'][:4])}**")
    if bundle.get("watchlist"):
        notes.append(f"Watchlist: **{', '.join(bundle['watchlist'][:4])}**")
    if bundle.get("tracked_players"):
        notes.append(f"Tracked: **{', '.join(bundle['tracked_players'][:4])}**")
    return notes


def _draft_scarcity_line(
    bundle: dict[str, Any],
    *,
    available_count: int | None = None,
    position_query: str = "",
) -> str:
    pool = available_count if available_count is not None else len(bundle.get("available") or [])
    if position_query:
        return _explain_position_scarcity(bundle, position_query=position_query, pool_count=int(pool))
    scarcity = bundle.get("position_scarcity")
    needs = _format_need_list(bundle.get("needed_positions") or [], bundle.get("category_needs") or [])
    if scarcity is not None:
        return (
            f"Position scarcity index **{scarcity:g}** at this pick; "
            f"**{pool}** available options tracked in context; prioritize scarce tiers (**{needs}**)."
        )
    return (
        f"Replacement value tightens as the draft progresses — "
        f"**{pool}** available names in context; roster gaps: **{needs}**."
    )


def _draft_risk_line(bundle: dict[str, Any], player: str, *, mode: str) -> str:
    target = player or (_draft_player_name(bundle["recommendations"][0]) if bundle.get("recommendations") else "this pick")
    row = next((r for r in bundle.get("recommendations") or [] if _draft_player_name(r) == target), None)
    edge = _player_metric(row, "Fantasy Edge", "fantasy_edge") if row else None
    sleeper_row = next((r for r in bundle.get("sleepers") or [] if _draft_player_name(r) == target), None)
    if edge is None and sleeper_row:
        edge = _player_metric(sleeper_row, "Fantasy Edge", "fantasy_edge")
    if mode == "sleeper":
        return (
            f"**{target}** is an upside/variance bet — Fantasy Edge **{edge}** when available; "
            "wider outcome swings than safe picks at this cost."
        )
    if edge is not None:
        return f"**{target}** carries projection edge **{edge}** with normal playing-time and role variance."
    return f"**{target}** balances floor and ceiling given your roster construction and category needs."


def _rank_value_players(rows: list[dict[str, Any]], *, limit: int = 5) -> list[str]:
    ranked: list[str] = []
    for row in rows[:limit]:
        name = _draft_player_name(row)
        if not name:
            continue
        edge = _player_metric(row, "Fantasy Edge", "fantasy_edge")
        market = _player_metric(row, "Market Rank", "market_rank")
        pos = _player_metric(row, "Primary Position", "position", "pos")
        bits = [f"**{name}**"]
        if pos:
            bits.append(str(pos))
        if edge is not None:
            bits.append(f"Fantasy Edge {edge}")
        if market is not None:
            bits.append(f"Market Rank {market}")
        ranked.append(" — ".join(bits))
    return ranked


def _explain_market_rank(rank: Any) -> str:
    try:
        val = float(rank)
    except (TypeError, ValueError):
        return ""
    if val <= 40:
        return f"market rank **{val:g}** (early-round tier)"
    if val <= 80:
        return f"market rank **{val:g}** (middle-round tier)"
    return f"market rank **{val:g}** (later-round tier)"


def _explain_fantasy_edge(edge: Any) -> str:
    try:
        val = float(edge)
    except (TypeError, ValueError):
        return ""
    if val >= 5:
        return f"model value **+{val:g}** vs ADP (clear surplus — strong buy at this slot)"
    if val >= 0:
        return f"model value **+{val:g}** vs ADP (fair to slight value)"
    if val >= -8:
        return (
            f"model value **{val:g}** vs ADP (small reach — you pay a modest premium for stability/upside)"
        )
    return f"model value **{val:g}** vs ADP (meaningful reach — only take if you must have the profile)"


def _position_need_phrase(bundle: dict[str, Any], position_query: str) -> str:
    """Roster-fit phrase scoped to the position in the question (not full need list)."""
    if not position_query:
        return ""
    needs = [str(n).strip().upper() for n in (bundle.get("needed_positions") or []) if str(n).strip()]
    pos_map = {
        "catcher": "C",
        "shortstop": "SS",
        "outfield": "OF",
        "first base": "1B",
        "second base": "2B",
        "third base": "3B",
    }
    code = pos_map.get(position_query.lower(), position_query.upper())
    if code in needs:
        return f"fills your open **{code}** roster slot"
    if position_query.lower() == "catcher":
        return "adds stable catcher production while the tier is still strong"
    return f"adds **{position_query.title()}** depth at this pick"


def _explain_position_scarcity(
    bundle: dict[str, Any],
    *,
    position_query: str,
    pool_count: int,
) -> str:
    pos_label = position_query.title() if position_query else "Position"
    scarcity = bundle.get("position_scarcity")
    if scarcity is not None:
        try:
            sval = float(scarcity)
        except (TypeError, ValueError):
            sval = None
        if sval is not None and sval >= 2.0:
            return (
                f"**{pos_label}** scarcity is elevated (index **{sval:g}**) — only **{pool_count}** "
                f"viable options remain, so waiting usually means a steep drop in production."
            )
    if pool_count <= 4:
        return (
            f"The **{pos_label}** pool is thin (**{pool_count}** left) — replacement production "
            "falls off quickly after the top names."
        )
    return (
        f"**{pool_count}** **{pos_label}** options remain in your board context; "
        "the practical risk is losing a tier before your next pick."
    )


def _peer_comparison_line(
    focus_name: str,
    focus_row: dict[str, Any],
    pos_pool: list[dict[str, Any]],
    *,
    limit: int = 2,
) -> str:
    focus_token = _player_name_token(focus_name)
    focus_market = _row_market_rank(focus_row) if focus_row else 9999.0
    peers: list[str] = []
    for row in pos_pool:
        name = _draft_player_name(row)
        if not name or _player_name_token(name) == focus_token:
            continue
        peer_market = _row_market_rank(row)
        edge_txt = _explain_fantasy_edge(_player_metric(row, "Fantasy Edge", "fantasy_edge"))
        profile = _player_profile_bits(row)
        rank_gap = int(peer_market - focus_market) if peer_market < 9990 and focus_market < 9990 else 0
        bit = f"**{name}** ({_explain_market_rank(peer_market)}"
        if edge_txt:
            bit += f"; {edge_txt}"
        if profile:
            bit += f"; {profile}"
        bit += ")"
        if rank_gap > 0:
            bit += f" trails **{focus_name}** by **{rank_gap}** market-rank spots"
        peers.append(bit)
        if len(peers) >= limit:
            break
    if not peers:
        return ""
    return " Compared with " + " and ".join(peers) + "."


def _drafted_names_at_position(bundle: dict[str, Any], position_query: str) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    drafted_tokens = _drafted_name_tokens(bundle.get("drafted_players"))

    def _maybe_add(clean: str, pos: str) -> None:
        token = _player_name_token(clean)
        if not clean or token in seen:
            return
        if not position_query:
            seen.add(token)
            names.append(clean)
            return
        if pos and position_matches_row(position_query, pos):
            seen.add(token)
            names.append(clean)
        elif not pos and position_query in clean.lower():
            seen.add(token)
            names.append(clean)

    for name in bundle.get("drafted_players") or []:
        clean = str(name).split(" (")[0].strip()
        if not clean:
            continue
        pos = _player_position_from_pools(bundle, clean)
        if drafted_tokens and _player_name_token(clean) not in drafted_tokens:
            continue
        _maybe_add(clean, pos)

    for row in bundle.get("board_rows") or bundle.get("canonical_board") or []:
        if not isinstance(row, dict):
            continue
        clean = _draft_player_name(row)
        if not clean:
            continue
        if drafted_tokens and _player_name_token(clean) not in drafted_tokens:
            continue
        pos = str(_player_metric(row, "Primary Position", "position", "pos") or "")
        _maybe_add(clean, pos)

    for name in bundle.get("roster") or []:
        clean = str(name).split(" (")[0].strip()
        if not clean:
            continue
        pos = _player_position_from_pools(bundle, clean)
        _maybe_add(clean, pos)

    return names


def _drafted_position_line(bundle: dict[str, Any], position_query: str) -> str:
    names = _drafted_names_at_position(bundle, position_query)
    pos_label = position_query.title() if position_query else "Position"
    if names:
        return (
            f"**{len(names)}** **{pos_label}** already drafted: "
            f"{', '.join(names[:4])}{'…' if len(names) > 4 else ''}."
        )
    return ""


def _position_label_from_code(pos: str) -> str:
    code = str(pos or "").strip().upper()
    labels = {
        "C": "Catcher",
        "1B": "First Base",
        "2B": "Second Base",
        "3B": "Third Base",
        "SS": "Shortstop",
        "OF": "Outfield",
        "DH": "Designated Hitter",
        "SP": "Starting Pitcher",
        "RP": "Relief Pitcher",
    }
    return labels.get(code, code or "Position")


def _roster_by_position(bundle: dict[str, Any]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    seen: set[str] = set()
    for name in bundle.get("roster") or []:
        clean = str(name).split(" (")[0].strip()
        token = _player_name_token(clean)
        if not clean or token in seen:
            continue
        seen.add(token)
        pos = str(_player_position_from_pools(bundle, clean) or "").strip().upper()
        if not pos:
            pos = "?"
        groups.setdefault(pos, []).append(clean)
    return groups


def _filled_roster_display_lines(bundle: dict[str, Any]) -> tuple[list[str], int]:
    groups = _roster_by_position(bundle)
    lines: list[str] = []
    tagged_groups = 0
    for pos in sorted(groups.keys(), key=lambda p: (p == "?", p)):
        names = groups[pos]
        if not names:
            continue
        if pos == "?":
            for name in names:
                lines.append(f"**?**: {name}")
        else:
            tagged_groups += 1
            lines.append(f"**{pos}**: {', '.join(names[:4])}{'…' if len(names) > 4 else ''}")
    return lines, tagged_groups


def _timing_survival_readout(
    focus_market: float,
    pick_num: int,
    picks_until_next: int,
    *,
    fallback_market: float | None = None,
) -> tuple[str, str, str]:
    """Heuristic survival readouts for timing decisions (plain language)."""
    gap = max(0.0, focus_market - float(pick_num))
    if gap <= max(1, picks_until_next - 1):
        focus_pct = "roughly **70–85%** he is gone before your next pick"
        rec = "draft now"
    elif gap <= picks_until_next * 2:
        focus_pct = "roughly **40–60%** he survives until your next pick"
        rec = "lean draft now if you need the position"
    else:
        focus_pct = "roughly **60–75%** he is still there if you wait one round"
        rec = "waiting is viable"
    if fallback_market is not None:
        fb_gap = max(0.0, fallback_market - float(pick_num))
        if fb_gap <= picks_until_next * 2:
            fallback_pct = "fallback option likely gone too if you wait"
        else:
            fallback_pct = "fallback should still be there if the top name goes"
    else:
        fallback_pct = "fallback tier depends on how fast the position runs"
    cost = (
        "expected cost of waiting: you may drop one tier at this position"
        if gap <= picks_until_next * 2
        else "expected cost of waiting: modest — you can likely pivot and still land value"
    )
    return focus_pct, fallback_pct, f"**{rec}** — {cost}"


def _fantasy_peer_names(pos_pool: list[dict[str, Any]], focus_name: str, *, limit: int = 3) -> list[str]:
    focus_token = _player_name_token(focus_name)
    names: list[str] = []
    for row in pos_pool:
        name = _draft_player_name(row)
        if not name or _player_name_token(name) == focus_token:
            continue
        names.append(name)
        if len(names) >= limit:
            break
    return names


def _replacement_rank_gap(bundle: dict[str, Any], position_query: str) -> int | None:
    pool = _pool_rows_by_position(bundle, position_query)
    if len(pool) < 2:
        return None
    gap = int(_row_market_rank(pool[1]) - _row_market_rank(pool[0]))
    return gap if gap > 0 else None


def _fantasy_analyst_player_why_direct(
    bundle: dict[str, Any],
    *,
    focus: str,
    pos_query: str,
    pos_label: str,
    pos_pool: list[dict[str, Any]],
    pick_note: str,
    drafted_line: str,
    profile: str,
) -> str:
    peers = _fantasy_peer_names(pos_pool, focus, limit=3)
    parts: list[str] = []
    if drafted_line:
        parts.append(drafted_line)
    parts.append(
        f"**{focus}** is the highest-ranked **{pos_label}** still available at {pick_note}."
    )
    if peers:
        peer_txt = ", ".join(f"**{p}**" for p in peers[:2])
        parts.append(f"He sits above {peer_txt} on your board.")
    pool_count = len(pos_pool)
    if pool_count <= 4:
        parts.append(
            f"**{pos_label}** depth begins to thin after this tier — only **{pool_count}** "
            "viable options remain in your board context."
        )
    elif pos_query == "catcher":
        parts.append(
            "Drafting him now secures one of the last catchers from the strongest remaining group."
        )
    else:
        parts.append(
            f"Taking **{focus}** here locks in a top **{pos_label}** before the tier drops."
        )
    need_phrase = _position_need_phrase(bundle, pos_query)
    if need_phrase:
        parts.append(f"Practically, he {need_phrase}.")
    if profile:
        parts.append(f"Production profile: {profile}.")
    return " ".join(parts)


def _position_query_from_code(pos_code: str) -> str:
    code = str(pos_code or "").strip().upper()
    mapping = {
        "C": "catcher",
        "1B": "first base",
        "2B": "second base",
        "3B": "third base",
        "SS": "shortstop",
        "OF": "outfield",
        "SP": "starting pitcher",
        "RP": "relief pitcher",
    }
    return mapping.get(code, code.lower())


def _head_to_head_analyst_direct(
    bundle: dict[str, Any],
    *,
    pa: str,
    pb: str,
    pos_a: str,
    pos_b: str,
    mkt_a: Any,
    mkt_b: Any,
    pick_note: str,
) -> str:
    try:
        rank_a = float(mkt_a) if mkt_a is not None else 9999.0
        rank_b = float(mkt_b) if mkt_b is not None else 9999.0
    except (TypeError, ValueError):
        rank_a = rank_b = 9999.0

    if rank_a < rank_b:
        winner, loser, win_pos, lose_pos, win_rank, lose_rank = pa, pb, pos_a, pos_b, rank_a, rank_b
    elif rank_b < rank_a:
        winner, loser, win_pos, lose_pos, win_rank, lose_rank = pb, pa, pos_b, pos_a, rank_b, rank_a
    else:
        return (
            f"**{pa}** ({pos_a}) and **{pb}** ({pos_b}) are close overall at {pick_note} — "
            f"choose based on which position gap matters more for your roster."
        )

    win_label = _position_label_from_code(win_pos)
    lose_label = _position_label_from_code(lose_pos)
    lose_query = _position_query_from_code(lose_pos)
    win_query = _position_query_from_code(win_pos)
    lose_pool = _pool_rows_by_position(bundle, lose_query) if lose_query else []
    lose_top = _draft_player_name(lose_pool[0]) if lose_pool else loser
    lose_is_top_at_pos = bool(
        lose_top and _player_name_token(lose_top) == _player_name_token(loser)
    )

    parts = [
        f"**{winner}** is the stronger overall value at {pick_note}.",
    ]
    if lose_is_top_at_pos and win_pos != lose_pos:
        parts.append(
            f"While **{loser}** is the best remaining **{lose_label}**, **{winner}** ranks "
            f"substantially higher overall and fills a premium **{win_pos}** slot."
        )
    elif win_pos != lose_pos:
        parts.append(
            f"**{winner}** gives you more overall draft capital at **{win_pos}** than **{loser}** does at **{lose_pos}**."
        )

    gap_win = _replacement_rank_gap(bundle, win_query) if win_query else None
    gap_lose = _replacement_rank_gap(bundle, lose_query) if lose_query else None
    if gap_win is not None and gap_lose is not None:
        if gap_win > gap_lose:
            parts.append(
                f"The drop-off after **{winner}** at **{win_label}** is steeper than the drop-off "
                f"after **{loser}** at **{lose_label}**, so waiting on **{win_label}** costs more."
            )
        elif gap_lose > gap_win:
            parts.append(
                f"**{lose_label}** depth thins faster than **{win_label}** on your board — "
                f"that is the main case for **{loser}**."
            )
    elif int(lose_rank - win_rank) >= 15:
        parts.append(
            f"**{winner}** is roughly **{int(lose_rank - win_rank)}** market-rank spots ahead — "
            "a meaningful overall tier gap at this stage of the draft."
        )

    needs = [str(n).strip().upper() for n in (bundle.get("needed_positions") or [])]
    if win_pos in needs and lose_pos not in needs:
        parts.append(f"Your roster still needs **{win_pos}**, which tilts the decision toward **{winner}**.")
    elif lose_pos in needs and win_pos not in needs:
        parts.append(
            f"You still need **{lose_pos}**, but **{winner}**'s overall value likely outweighs that gap."
        )

    return " ".join(parts)


def _draft_review_grade(bundle: dict[str, Any]) -> str:
    roster = bundle.get("roster") or []
    needed = bundle.get("needed_positions") or []
    cats = bundle.get("category_needs") or []
    n = len(roster)
    gaps = len(needed)
    if n >= 5 and gaps <= 1 and len(cats) <= 1:
        return "A-"
    if n >= 4 and gaps <= 2 and len(cats) <= 2:
        return "B+"
    if n >= 3 and gaps <= 3:
        return "B"
    if n >= 2:
        return "B-"
    return "C+"


def _roster_pick_extremes(bundle: dict[str, Any], roster: list[str]) -> tuple[str, str]:
    ranked: list[tuple[str, float]] = []
    for name in roster:
        clean = str(name).split(" (")[0].strip()
        row = _find_player_row_in_bundle(clean, bundle) or {}
        ranked.append((clean, _row_market_rank(row)))
    if not ranked:
        return "", ""
    ranked.sort(key=lambda item: item[1])
    return ranked[0][0], ranked[-1][0]


def _weakest_pick_explanation(bundle: dict[str, Any], name: str) -> str:
    if not name:
        return ""
    row = _find_player_row_in_bundle(name, bundle) or {}
    pos = _player_position_from_pools(bundle, name) or "?"
    market = _player_metric(row, "Market Rank", "market_rank")
    edge = _player_metric(row, "Fantasy Edge", "fantasy_edge")
    profile = _player_profile_bits(row)
    parts = [
        f"**{name}** ({pos}) is the softest pick so far",
    ]
    if market is not None:
        parts.append(f"market rank **{market}** is the lowest on your roster")
    if edge is not None:
        try:
            edge_val = float(edge)
            if edge_val < -5:
                parts.append("you reached modestly ahead of ADP for his tier")
            elif edge_val >= 0:
                parts.append("value vs ADP is still acceptable")
        except (TypeError, ValueError):
            pass
    if profile:
        parts.append(f"profile ({profile}) adds less category ceiling than your other picks")
    pos_label = _position_label_from_code(pos) if pos and pos != "?" else "this position"
    parts.append(
        f"you could have waited one more round for a similar **{pos_label}** if you prioritized raw rank over roster timing"
    )
    return ". ".join(parts) + "."


def _draft_grade_rationale(bundle: dict[str, Any], grade: str) -> str:
    roster = bundle.get("roster") or []
    needed = bundle.get("needed_positions") or []
    cats = bundle.get("category_needs") or []
    filled_lines, filled_count = _filled_roster_display_lines(bundle)
    strengths: list[str] = []
    weaknesses: list[str] = []
    if filled_count >= 3:
        strengths.append(f"**{filled_count}** position groups already covered")
    elif roster:
        strengths.append(f"**{len(roster)}** early picks on the board")
    if not needed:
        strengths.append("no major positional holes flagged yet")
    else:
        weaknesses.append(f"open slots at **{', '.join(needed[:4])}**")
    if cats:
        weaknesses.append(f"category pressure in **{', '.join(cats[:3])}**")
    elif len(needed) <= 1:
        strengths.append("category balance looks reasonable so far")
    if len(needed) >= 3:
        weaknesses.append("positional balance still needs work")
    rationale = []
    if strengths:
        rationale.append("Strengths: " + "; ".join(strengths))
    if weaknesses:
        rationale.append("Weaknesses: " + "; ".join(weaknesses))
    rationale.append(
        f"That balance profile supports a **{grade}** — "
        + (
            "solid foundation with work left at scarce positions."
            if grade.startswith("B")
            else "early roster still taking shape."
        )
    )
    return " ".join(rationale)


def _need_priority_reason(pos_code: str) -> str:
    code = str(pos_code or "").strip().upper()
    reasons = {
        "C": "catcher tiers thin quickly after the top names leave the board",
        "1B": "first-base power anchors are scarce in the middle rounds",
        "2B": "second-base depth drops sharply once the top multi-category options are gone",
        "3B": "third-base production falls off fast — premium infield slots are hard to replace",
        "SS": "shortstop is a high-scarcity infield tier in most formats",
        "OF": "outfield volume is easier to patch later, but star-level OF still moves in runs",
        "DH": "utility/DH bat helps category balance when corner infield is still open",
        "SP": "starting pitching tiers compress quickly once aces are off the board",
        "RP": "relief pitching is volatile — secure a closer tier before the run starts",
    }
    return reasons.get(code, f"**{code}** is still an open roster slot on your board")


def _finalize_draft_coach_sections(coach: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    """Align coach output with ami_answer_template six-level structure."""
    template = bundle.get("ami_answer_template") or []
    what_if = coach.get("what_if") or []
    what_if_text = "\n".join(str(x) for x in what_if[:5])
    coach.setdefault("scarcity", coach.get("scarcity") or "")
    coach.setdefault("risk_upside", coach.get("risk_upside") or "")
    coach["why_roster_fit"] = coach.get("analyst_framing") or ""
    coach["alternatives"] = coach.get("tradeoffs") or ""
    coach["what_if_text"] = what_if_text

    if template:
        label_map = {
            "direct_answer": coach.get("direct_answer") or "",
            "why_roster_fit": coach.get("why_roster_fit") or "",
            "scarcity": coach.get("scarcity") or "",
            "risk_upside": coach.get("risk_upside") or "",
            "alternatives": coach.get("alternatives") or "",
            "what_if": what_if_text,
        }
        sections: list[tuple[str, str]] = []
        for item in template:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            if name in label_map and label_map[name]:
                sections.append((name, label_map[name]))
        coach["ami_structured"] = sections
        if sections:
            coach["formatted_answer"] = "\n\n".join(text for _, text in sections)
    return coach


def _build_baseball_draft_coach_sections(
    *,
    question: str,
    bundle: dict[str, Any],
    mode: str,
    player: str,
    pick: int | None,
    rnd: int | None,
    pick_known: bool,
    round_known: bool,
    adp_val: float,
    rank_edge: float,
    verdict: str,
) -> dict[str, Any]:
    rec_names = [_draft_player_name(r) for r in bundle["recommendations"][:4] if _draft_player_name(r)]
    sleeper_names = [_draft_player_name(r) for r in bundle["sleepers"][:4] if _draft_player_name(r)]
    avail_names = [_draft_player_name(r) for r in bundle["available"][:6] if _draft_player_name(r)]
    roster = bundle["roster"]
    scoring_label = _draft_scoring_label(bundle["scoring"])
    roster_note = _draft_roster_note(bundle)
    pick_note = _format_pick_note(pick, rnd, pick_known=pick_known, round_known=round_known)
    context_notes = _draft_context_notes(bundle)
    context_suffix = f" Context: {' · '.join(context_notes)}." if context_notes else ""

    top = rec_names[0] if rec_names else (player or "the best available fit")
    alt = rec_names[1] if len(rec_names) > 1 else (avail_names[1] if len(avail_names) > 1 else (sleeper_names[0] if sleeper_names else ""))
    needs_label = _format_need_list(bundle.get("needed_positions") or [], bundle.get("category_needs") or [])
    scarcity_line = _draft_scarcity_line(bundle)
    risk_line = _draft_risk_line(bundle, player or top, mode=mode)

    if mode == "draft_market_prediction":
        subtype = _draft_market_subtype(question)
        pos_query = extract_draft_position_query(question)
        if not pos_query:
            pos_query = _infer_scarce_position_from_bundle(bundle) if subtype in ("position_run", "wait_timing") else "catcher"
        drafted_for_suffix = _drafted_names_at_position(bundle, pos_query)
        context_suffix = (
            f" Already drafted: {', '.join(drafted_for_suffix[:4])}." if drafted_for_suffix else ""
        )
        pos_label = pos_query.title() if pos_query else "position"
        remaining = _pool_rows_by_position(bundle, pos_query)
        drafted_pos = _drafted_names_at_position(bundle, pos_query)
        remaining_names = [_draft_player_name(r) for r in remaining[:5] if _draft_player_name(r)]
        next_name = remaining_names[0] if remaining_names else "no clear next pick in context"
        drafted_note = (
            f"**{', '.join(drafted_pos[:4])}** {'is' if len(drafted_pos) == 1 else 'are'} already off the board. "
            if drafted_pos
            else ""
        )

        if subtype == "make_it_back":
            target = player or (remaining_names[0] if remaining_names else "this player")
            direct = (
                f"**{target}** {'is likely to be drafted before your next pick' if remaining_names else 'may not return'} "
                f"based on Market Rank order among remaining **{pos_label}** options at {pick_note}."
            )
            framing = (
                f"Draft-flow read: {drafted_note}"
                f"Remaining **{pos_label}** pool: {', '.join(remaining_names[:4]) or '—'}. "
                f"Compare vs your next pick **{bundle.get('proj', {}).get('my_next_pick') or bundle.get('pick')}**.{context_suffix}"
            )
        elif subtype == "wait_timing":
            direct = (
                f"You can likely wait **1–2 rounds** on **{pos_label}** if **{next_name}** is the only elite name left, "
                f"but scarcity index **{bundle.get('position_scarcity') or 'rising'}** raises reach risk."
            )
            framing = (
                f"{drafted_note}"
                f"Next **{pos_label}** candidates by rank: {', '.join(remaining_names[:3]) or '—'}.{context_suffix}"
            )
        elif subtype == "position_run":
            direct = (
                f"A **{pos_label} run** is plausible — **{next_name}** is the top remaining name and "
                f"**{len(remaining_names)}** **{pos_label}** options remain in your board context."
            )
            framing = (
                f"{drafted_note}"
                f"Managers often cluster scarce positions; queue/watchlist: "
                f"{', '.join(bundle.get('draft_queue')[:3]) or '—'}.{context_suffix}"
            )
        elif subtype == "position_next" and not remaining_names:
            pool_size = len(_all_pool_rows(bundle))
            has_position_tags = any(
                _player_metric(r, "Primary Position", "position", "pos") for r in _all_pool_rows(bundle)
            )
            if pool_size == 0 or not has_position_tags:
                direct = (
                    f"{drafted_note}"
                    f"I do not have enough **{pos_label}** pool data in context to name the next pick confidently."
                )
            else:
                direct = (
                    f"{drafted_note}"
                    f"No undrafted **{pos_label}** players remain in your saved board context at {pick_note}."
                )
            framing = (
                f"Attach **available_players** with **Primary Position** from Draft Assistant before asking "
                f"who is next at **{pos_label}**.{context_suffix}"
            )
            tradeoffs = "Cannot rank alternatives without position-tagged available players in context."
            scarcity_line = ""
            risk_line = ""
            what_if = [
                "If catcher pool data is attached → rank by Market Rank among undrafted catchers.",
                "If a named catcher is already drafted → exclude them from the next-pick list.",
                "If pick/round is missing → state pick unknown rather than guessing.",
            ]
        else:
            direct = (
                f"{drafted_note}"
                f"The next **{pos_label}** most likely selected is **{next_name}** "
                f"— highest-ranked remaining **{pos_label}** on your saved board."
            )
            rank_bits = []
            for r in remaining[:3]:
                nm = _draft_player_name(r)
                mr = _player_metric(r, "Market Rank", "market_rank")
                if nm and mr is not None:
                    rank_bits.append(f"**{nm}** (Market Rank **{mr}**)")
            if rank_bits:
                drafted_line = _drafted_position_line(bundle, pos_query)
                framing = (
                    f"At {pick_note}, remaining **{pos_label}** by Market Rank: "
                    + ", ".join(rank_bits)
                    + (f" {drafted_line}" if drafted_line else "")
                    + context_suffix
                )
            else:
                drafted_line = _drafted_position_line(bundle, pos_query)
                framing = (
                    f"Ranked by Market Rank / ADP among available **{pos_label}** in context at {pick_note}."
                    + (f" {drafted_line}" if drafted_line else "")
                    + context_suffix
                )

        if remaining_names:
            if len(remaining_names) > 1:
                ranked_lines = [f"{i + 1}. **{n}**" for i, n in enumerate(remaining_names[:3])]
                tradeoffs = (
                    f"After **{next_name}**, the most likely **{pos_label}** selections are: "
                    + " · ".join(ranked_lines)
                )
            else:
                tradeoffs = (
                    f"Thin **{pos_label}** tier after **{next_name}** — alternatives may shift to other positions."
                )

            scarcity_idx = bundle.get("position_scarcity")
            if scarcity_idx is not None:
                scarcity_line = (
                    f"**{pos_label}** scarcity index **{scarcity_idx:g}**; "
                    f"**{len(remaining_names)}** undrafted **{pos_label}** remain in context."
                )
            else:
                scarcity_line = (
                    f"**{len(remaining_names)}** undrafted **{pos_label}** in your board context "
                    f"(ranked by Market Rank)."
                )
            risk_line = (
                f"If you skip **{next_name}**, the next **{pos_label}** tier may fall off before your next pick "
                f"({pick_note})."
            )
            what_if = [
                f"If **{next_name}** is drafted early → pivot to **{remaining_names[1] if len(remaining_names) > 1 else 'next tier'}**.",
                f"If you wait one round → monitor whether a **{pos_label} run** clears the top tier.",
                f"If you prioritize need elsewhere → **{pos_label}** depth drops fast after **{next_name}**.",
            ]
    elif mode == "draft_player_compare":
        context_suffix = ""
        pa, pb = extract_draft_compare_players(question)
        if not pa:
            pa = str(bundle.get("player_a") or "").strip()
        if not pb:
            pb = str(bundle.get("player_b") or "").strip()
        row_a = _find_player_row_in_bundle(pa, bundle) or {}
        row_b = _find_player_row_in_bundle(pb, bundle) or {}
        drafted = bundle.get("drafted_players") or []
        a_drafted = _name_in_player_list(pa, drafted)
        b_drafted = _name_in_player_list(pb, drafted)
        pos_a = _player_metric(row_a, "Primary Position", "position", "pos") or "?"
        pos_b = _player_metric(row_b, "Primary Position", "position", "pos") or "?"
        mkt_a = _player_metric(row_a, "Market Rank", "market_rank")
        mkt_b = _player_metric(row_b, "Market Rank", "market_rank")
        edge_a = _player_metric(row_a, "Fantasy Edge", "fantasy_edge")
        edge_b = _player_metric(row_b, "Fantasy Edge", "fantasy_edge")
        reason_a = _player_metric(row_a, "Reason", "reason")
        reason_b = _player_metric(row_b, "Reason", "reason")

        def _avail_label(name: str, drafted_flag: bool) -> str:
            if drafted_flag:
                return "**drafted** (off the board)"
            if _name_in_player_list(name, avail_names) or _find_player_row_in_bundle(name, bundle):
                return "**available** on your board"
            return "**availability unknown** in context"

        if not pa or not pb:
            direct = "I do not have both player names in context to compare — name both players in your question."
        elif not row_a and not row_b:
            direct = (
                f"I do not have enough player pool/projection data in context to compare **{pa}** and **{pb}** confidently."
            )
        elif a_drafted and not b_drafted:
            direct = f"**{pa}** is already drafted. **{pb}** ({pos_b}) is {_avail_label(pb, False)} — lean **{pb}** if you need {pos_b}."
        elif b_drafted and not a_drafted:
            direct = f"**{pb}** is already drafted. **{pa}** ({pos_a}) is {_avail_label(pa, False)} — lean **{pa}** if you need {pos_a}."
        elif a_drafted and b_drafted:
            direct = f"Both **{pa}** and **{pb}** are already drafted on your saved board."
        else:
            direct = _head_to_head_analyst_direct(
                bundle,
                pa=pa,
                pb=pb,
                pos_a=str(pos_a),
                pos_b=str(pos_b),
                mkt_a=mkt_a,
                mkt_b=mkt_b,
                pick_note=pick_note,
            )

        compare_winner = ""
        if pa and pb and not (a_drafted or b_drafted):
            try:
                rank_a = float(mkt_a) if mkt_a is not None else 9999.0
                rank_b = float(mkt_b) if mkt_b is not None else 9999.0
                compare_winner = pa if rank_a < rank_b else pb if rank_b < rank_a else ""
            except (TypeError, ValueError):
                compare_winner = ""

        filled = _roster_by_position(bundle)
        filled_bits = [
            f"**{pos}**: {', '.join(names[:3])}"
            for pos, names in sorted(filled.items())
            if names
        ]
        framing = (
            f"Head-to-head at {pick_note} for "
            + (f"your **{len(roster)}**-player roster" if roster else "your roster")
            + ". "
            + (f"Roster so far: {' · '.join(filled_bits[:4])}. " if filled_bits else "")
            + f"**{pa}** ({pos_a}) is {_avail_label(pa, a_drafted)}; **{pb}** ({pos_b}) is {_avail_label(pb, b_drafted)}."
            + (f" Open needs: **{needs_label}**." if needs_label != "balanced coverage" else "")
            + context_suffix
        )
        if reason_a or reason_b:
            framing += f" Model notes: {reason_a or '—'} | {reason_b or '—'}."
        lose_pos = pos_b if compare_winner == pa else pos_a if compare_winner == pb else ""
        lose_name = pb if compare_winner == pa else pa if compare_winner == pb else ""
        lose_query = _position_query_from_code(lose_pos) if lose_pos else ""
        lose_pool = _pool_rows_by_position(bundle, lose_query) if lose_query else []
        next_at_lose = _draft_player_name(lose_pool[1]) if len(lose_pool) > 1 else ""
        tradeoffs = (
            f"If you pass on **{compare_winner}**, you keep premium overall value. "
            f"If you take **{lose_name}** instead, you secure **{lose_pos}** but likely settle "
            + (f"for **{next_at_lose}** as the next option at that position." if next_at_lose else "for a thinner next tier.")
            if compare_winner and lose_name
            else f"**{pa}** ({pos_a}) vs **{pb}** ({pos_b}) — weigh overall tier against positional scarcity."
        )
        scarcity_line = ""
        if lose_query:
            scarcity_line = _draft_scarcity_line(
                bundle, available_count=len(lose_pool), position_query=lose_query
            )
        elif bundle.get("position_scarcity") is not None:
            scarcity_line = _draft_scarcity_line(bundle)
        risk_line = _draft_risk_line(bundle, compare_winner or pa or top, mode=mode)
        what_if = [
            f"If you need **{pos_a}** → **{pa}** becomes the positional anchor.",
            f"If you need **{pos_b}** → **{pb}** becomes the positional anchor.",
            f"If you prioritize overall value → **{compare_winner or pa}** is the default lean.",
            "If a position run starts → take the scarce position before the tier clears.",
        ]
    elif mode == "player_why":
        focus = player or top
        row = _find_player_row_in_bundle(focus, bundle) or {}
        ds = bundle.get("draft_status") if isinstance(bundle.get("draft_status"), dict) else {}
        drafted = bundle.get("drafted_players") or []
        is_drafted = bool(ds.get("is_drafted")) or _name_in_player_list(focus, drafted)
        on_roster = bool(ds.get("on_user_roster"))
        in_available = _name_in_player_list(focus, avail_names) or bool(row)
        is_top_rec = _player_name_token(focus) == _player_name_token(top)
        pos = _player_metric(row, "Primary Position", "position", "pos")
        edge = _player_metric(row, "Fantasy Edge", "fantasy_edge")
        market = _player_metric(row, "Market Rank", "market_rank")
        reason = _player_metric(row, "Reason", "reason")
        profile = _player_profile_bits(row)
        pos_query = extract_draft_position_query(question)
        pos_pool = _pool_rows_by_position(bundle, pos_query) if pos_query else []
        pos_label = pos_query.title() if pos_query else (str(pos or "").strip() or "position")
        pos_alts = _position_alt_names(bundle, position_query=pos_query, exclude_name=focus) if pos_query else []
        scarcity_note = ""
        focus_in_pos_pool = bool(
            pos_query
            and pos_pool
            and any(_player_name_token(_draft_player_name(r)) == _player_name_token(focus) for r in pos_pool)
        )
        top_at_pos = _draft_player_name(pos_pool[0]) if pos_pool else ""
        focus_leads_pos = bool(
            focus_in_pos_pool
            and top_at_pos
            and _player_name_token(top_at_pos) == _player_name_token(focus)
        )

        if is_drafted and not on_roster:
            direct = f"**{focus}** is **not available** — already drafted on your saved board."
        elif on_roster:
            direct = f"**{focus}** is already on **your roster**; you do not need to draft him again."
        elif pos_query and focus_in_pos_pool:
            drafted_line = _drafted_position_line(bundle, pos_query)
            scarcity_note = _explain_position_scarcity(
                bundle, position_query=pos_query, pool_count=len(pos_pool)
            )
            if focus_leads_pos:
                direct = _fantasy_analyst_player_why_direct(
                    bundle,
                    focus=focus,
                    pos_query=pos_query,
                    pos_label=pos_label,
                    pos_pool=pos_pool,
                    pick_note=pick_note,
                    drafted_line=drafted_line,
                    profile=profile,
                )
            else:
                top_peer = _fantasy_peer_names(pos_pool, focus, limit=1)
                direct = (
                    f"**{focus}** is a viable **{pos_label}** at {pick_note}, "
                    f"but **{top_at_pos}** leads the remaining tier on your board."
                )
                if top_peer:
                    direct += f" **{focus}** still profiles ahead of **{top_peer[0]}** on category fit."
                if profile:
                    direct += f" Profile: {profile}."
        elif is_top_rec or (rec_names and _player_name_token(focus) == _player_name_token(rec_names[0])):
            direct = (
                f"**{focus}** is a strong pick for you right now because he matches your board recommendation "
                f"and fits **{needs_label}** at {pick_note}."
            )
            if profile:
                direct += f" Profile: {profile}."
        elif focus and top and _player_name_token(focus) != _player_name_token(top) and not pos_query:
            direct = (
                f"**{focus}** is a good player, but **{top}** is the better overall fit on your current board "
                f"because **{needs_label}** and recommendation priority favor **{top}**."
            )
            if profile:
                direct += f" **{focus}** still offers: {profile}."
        else:
            direct = (
                f"**{focus}** can work at {pick_note} if he addresses **{needs_label}**, "
                "but verify he is still available on your saved board."
            )
            if profile:
                direct += f" Profile: {profile}."

        avail_note = "available in your tracked pool" if in_available else "not in your top cached available slice — check full board"
        drafted_line = _drafted_position_line(bundle, pos_query) if pos_query else ""
        framing_parts = [
            f"**{focus}** ({pos or pos_label}) on your board: {avail_note}; "
            f"draft status: {'drafted' if is_drafted else 'not drafted'}.",
        ]
        if drafted_line:
            framing_parts.append(drafted_line)
        if pos_query and pos_pool:
            remaining_pos = [_draft_player_name(r) for r in pos_pool[:5] if _draft_player_name(r)]
            framing_parts.append(
                f"Remaining **{pos_label}** pool: {', '.join(remaining_pos) or '—'}."
            )
        elif needs_label != "balanced coverage":
            framing_parts.append(f"Broader roster context: **{needs_label}** in **{scoring_label}**.")
        framing = " ".join(framing_parts) + context_suffix
        if reason:
            framing += f" Model note: {reason}."
        if pos_query and pos_pool and scarcity_note and scarcity_note not in direct:
            framing += f" {scarcity_note}"

        if pos_query and pos_alts:
            tradeoffs = (
                f"If you pass on **{focus}**, the next **{pos_label}** options are "
                f"**{', '.join(pos_alts[:3])}** — a clear step down in tier."
            )
        elif alt or (top and not is_top_rec and not pos_query):
            tradeoffs = (
                f"Compared with **{alt or top}**: **{focus}** vs **{top}** trades recommendation priority "
                f"against your stated interest in **{focus}**."
            )
        else:
            tradeoffs = f"Alternatives on board: {', '.join(avail_names[:3]) or 'see available_players'}."
        what_if = [
            f"If you prioritize power → weigh **{focus}** HR/OBP vs **{pos_alts[0] if pos_alts else (alt or top)}**.",
            f"If you prioritize speed → compare SB upside vs queue **{', '.join(bundle.get('draft_queue')[:2]) or '—'}**.",
            (
                f"If you prioritize safety → **{focus}** floor vs **{pos_alts[0] if pos_alts else (alt or top)}**."
                if pos_query
                else f"If you prioritize safety → favor **{top}** unless **{focus}** has clearer floor."
            ),
            f"If you prioritize upside → **{focus}** vs higher-ceiling alt **{sleeper_names[0] if sleeper_names else alt or '—'}**.",
        ]
        scarcity_line = _draft_scarcity_line(
            bundle, available_count=len(pos_pool) if pos_pool else None, position_query=pos_query or ""
        )
        risk_line = _draft_risk_line(bundle, focus, mode=mode)
    elif mode == "position_best_available":
        pos_query = extract_draft_position_query(question) or _infer_scarce_position_from_bundle(bundle)
        pos_label = pos_query.title() if pos_query else "position"
        pos_pool = _pool_rows_by_position(bundle, pos_query)
        drafted_pos = _drafted_names_at_position(bundle, pos_query)
        ranked = _rank_value_players(pos_pool, limit=5)
        top_at_pos = _draft_player_name(pos_pool[0]) if pos_pool else ""
        second_at_pos = _draft_player_name(pos_pool[1]) if len(pos_pool) > 1 else ""
        third_at_pos = _draft_player_name(pos_pool[2]) if len(pos_pool) > 2 else ""

        if top_at_pos:
            direct = f"**{top_at_pos}** is the best available **{pos_label}** at {pick_note}."
            if ranked:
                direct += " Ranking: " + "; ".join(ranked[:4]) + "."
        else:
            direct = (
                f"No remaining **{pos_label}** options are tracked in your available pool at {pick_note}."
            )

        drafted_line = _drafted_position_line(bundle, pos_query)
        framing = (
            (drafted_line + " " if drafted_line else "")
            + f"**{len(pos_pool)}** remaining **{pos_label}** in your tracked pool. "
            f"Scoring: **{scoring_label}**.{context_suffix}"
        )
        if second_at_pos:
            tradeoffs = (
                f"**{top_at_pos}** leads on market rank; **{second_at_pos}**"
                + (f" and **{third_at_pos}**" if third_at_pos else "")
                + f" are the next **{pos_label}** tiers if you want more upside or category fit."
            )
        else:
            tradeoffs = f"**{top_at_pos}** is the clear remaining **{pos_label}** if still available."
        what_if = [
            f"If you wait one round → **{second_at_pos or top_at_pos or 'next tier'}** may be the top **{pos_label}** left.",
            f"If you prioritize power → compare HR/OBP among {', '.join([n for n in (top_at_pos, second_at_pos, third_at_pos) if n]) or 'remaining options'}.",
            f"If you prioritize safety → favor **{top_at_pos}** (best market rank among remaining **{pos_label}**).",
            f"If a run starts → scarcity index **{bundle['position_scarcity']:g}**" if bundle.get("position_scarcity") is not None else f"If a run starts → take **{top_at_pos}** before the **{pos_label}** pool thins.",
        ]
        scarcity_line = _draft_scarcity_line(
            bundle, available_count=len(pos_pool), position_query=pos_query
        )
        risk_line = _draft_risk_line(bundle, top_at_pos or player, mode=mode)
    elif mode == "hitter_pitcher":
        direct = (
            f"At {pick_note}, weigh **hitter** vs **pitcher** by **{needs_label}** and "
            f"whether your league rewards pitching scarcity now — lean **{top}** if hitters close bigger category gaps."
        )
        framing = (
            f"Roster construction: {roster_note}; category_needs **{needs_label}**; "
            f"**{len(avail_names)}** hitters/pitchers tracked in available pool.{context_suffix}"
        )
        tradeoffs = (
            f"**Hitter path ({top})** improves counting cats; **pitcher path** helps ratios/WHIP/K if SP/RP needs are open."
        )
        what_if = [
            "If you prioritize ratios → pitcher now even if a hitter ranks higher.",
            "If you prioritize counting stats → hitter unless elite SP falls to you.",
            "If a position run is coming → take scarce position before waiting.",
        ]
        scarcity_line = _draft_scarcity_line(bundle)
        risk_line = _draft_risk_line(bundle, player or top, mode=mode)
    elif mode == "weakest_category":
        cats = bundle.get("category_needs") or []
        weakest = cats[0] if cats else "balanced"
        direct = (
            f"Your weakest tracked category gap is **{weakest}** — prioritize available players who move "
            f"**{weakest}** most at {pick_note}."
        )
        framing = (
            f"Category diagnosis from saved board: needs **{needs_label}**; "
            f"recommendations favor **{top}** for overall fit.{context_suffix}"
        )
        tradeoffs = (
            f"Closing **{weakest}** may mean passing on higher ADP names like **{alt or top}** with better raw rank."
        )
        what_if = [
            f"If you fix **{weakest}** this round → next pick can target **{alt or 'BPA'}**.",
            "If you punt the weak category → you need a later-round specialist.",
            "If league is shallow at the position → scarcity overrides category punt.",
        ]
        scarcity_line = _draft_scarcity_line(bundle)
        risk_line = _draft_risk_line(bundle, player or top, mode=mode)
    elif mode == "hitter_fit":
        hitters = _hitter_pool_rows(bundle)
        h_names = [_draft_player_name(r) for r in hitters[:4] if _draft_player_name(r)]
        h_a = h_names[0] if h_names else top
        h_b = h_names[1] if len(h_names) > 1 else alt
        row_a = hitters[0] if hitters else {}
        row_b = hitters[1] if len(hitters) > 1 else {}
        edge_a = _player_metric(row_a, "Fantasy Edge", "fantasy_edge")
        edge_b = _player_metric(row_b, "Fantasy Edge", "fantasy_edge")
        pos_a = _player_metric(row_a, "Primary Position", "position", "pos") or "?"
        pos_b = _player_metric(row_b, "Primary Position", "position", "pos") or "?"
        needs = bundle.get("needed_positions") or []
        score_a = score_b = 0.0
        if pos_a in needs or str(pos_a).upper() in [str(n).upper() for n in needs]:
            score_a += 2
        if pos_b in needs or str(pos_b).upper() in [str(n).upper() for n in needs]:
            score_b += 2
        try:
            if edge_a is not None and edge_b is not None:
                if float(edge_a) > float(edge_b):
                    score_a += 1
                elif float(edge_b) > float(edge_a):
                    score_b += 1
        except (TypeError, ValueError):
            pass
        if score_a >= score_b and h_a:
            winner, loser = h_a, h_b
        else:
            winner, loser = h_b or h_a, h_a
        direct = (
            f"**Lean {winner}** — the **better hitter fit** for your roster over **{loser}** at {pick_note} "
            f"because he closes **{needs_label}** ({pos_a} vs {pos_b}; Fantasy Edge {edge_a} vs {edge_b})."
            if h_b
            else f"**Lean {h_a}** — the best available **hitter fit** for **{needs_label}** on your roster at {pick_note}."
        )
        framing = (
            f"Hitter comparison vs {roster_note}: **{h_a}** ({pos_a}) vs **{h_b or '—'}** ({pos_b}). "
            f"Ranked by roster need + Fantasy Edge from your available hitter pool.{context_suffix}"
        )
        tradeoffs = (
            f"**{h_a}** ({pos_a}, Edge {edge_a}) vs **{h_b}** ({pos_b}, Edge {edge_b}) — "
            f"choose **{winner}** for roster fit or **{loser}** for raw rank."
            if h_b
            else f"Only one strong hitter fit in context — **{h_a}** addresses **{needs_label}**."
        )
        what_if = [
            f"If you need **{pos_a}** → lean **{h_a}**.",
            f"If you need **{pos_b}** → lean **{h_b or h_a}**.",
            "If a position run starts → take the scarce hitter before the tier drops.",
        ]
        scarcity_line = _draft_scarcity_line(bundle)
        risk_line = _draft_risk_line(bundle, winner, mode=mode)
    elif mode == "team_fit":
        direct = (
            f"**{top}** fits your team best at {pick_note} because he closes **{needs_label}** "
            f"on your saved board recommendations."
        )
        framing = f"Team-fit optimization vs raw rank at {pick_note}.{context_suffix}"
        tradeoffs = f"**{alt or 'next best'}** may rank higher overall but adds less to your roster construction."
        what_if = [
            "If you prioritize power → re-rank available_players by HR/SLG.",
            "If you prioritize speed → favor SB leaders in queue/watchlist.",
            "If you prioritize safety → take higher-floor recommendation over upside.",
        ]
        scarcity_line = _draft_scarcity_line(bundle)
        risk_line = _draft_risk_line(bundle, player or top, mode=mode)
    elif mode == "safety_upside":
        safe = top
        upside = sleeper_names[0] if sleeper_names else (alt or top)
        direct = (
            f"**Safest pick: {safe}** (recommendation/floor). "
            f"**Highest upside: {upside}** (variance/ceiling) at {pick_note}."
        )
        framing = f"Risk spectrum on your board at {pick_note} — floor vs ceiling tradeoff.{context_suffix}"
        tradeoffs = f"**{safe}** stabilizes **{needs_label}**; **{upside}** widens outcome swings."
        what_if = [
            f"If you need reliability → **{safe}**.",
            f"If you need league-winning ceiling → **{upside}**.",
            "If pick is late → upside has lower opportunity cost.",
        ]
        scarcity_line = _draft_scarcity_line(bundle)
        risk_line = _draft_risk_line(bundle, upside, mode="sleeper")
    elif mode == "roster_weakness":
        pos = bundle.get("needed_positions") or []
        cats = bundle.get("category_needs") or []
        pos_text = ", ".join(pos[:6]) if pos else "positional depth"
        cat_text = ", ".join(cats[:6]) if cats else "counting categories"
        gap_pos = pos[0] if pos else "depth"
        gap_cat = cats[0] if cats else "production"
        direct = (
            f"Your biggest **roster weakness** is **{gap_pos}** depth with a **{gap_cat}** category gap "
            f"on {roster_note} at {pick_note}. **Target {top}** next to close the gap."
        )
        framing = (
            f"**Weakness diagnosis:** positional gap at **{pos_text}**; category pressure on **{cat_text}**. "
            f"Your saved board flags **{needs_label}** as the priority fix.{context_suffix}"
        )
        tradeoffs = (
            f"Closing the **{gap_cat}** weakness may mean targeting **{top}** over higher-ADP names "
            f"with less category impact; pivot **{alt or 'next tier'}** if you want raw rank."
            if alt
            else f"Target **{top}** to address the **{gap_pos}** weakness before the tier drops."
        )
        what_if = [
            f"If you ignore the **{gap_cat}** gap → you need a late-round specialist.",
            f"If a **{gap_pos} run** starts → take **{top}** before the tier clears.",
            f"If you prioritize BPA → **{alt or top}** still helps **{cat_text}** most among available names.",
        ]
        scarcity_line = _draft_scarcity_line(bundle)
        risk_line = _draft_risk_line(bundle, player or top, mode=mode)
    elif mode == "draft_timing_decision":
        focus = str(bundle.get("question_player") or "").strip()
        if not focus:
            focus = _extract_player_from_question_text(question) or player or top
        focus = _sanitize_extracted_player_name(focus) or focus
        row = _find_player_row_in_bundle(focus, bundle) or {}
        pos_query = extract_draft_position_query(question)
        if not pos_query:
            pos_code = str(_player_metric(row, "Primary Position", "position", "pos") or "")
            pos_query = _position_query_from_code(pos_code)
        pos_query = _normalize_position_query_for_pool(pos_query)
        pos_code = str(_player_metric(row, "Primary Position", "position", "pos") or "")
        if pos_query in ("catcher", "catchers", "c"):
            pos_label = "Catcher"
        elif pos_code:
            pos_label = _position_label_from_code(pos_code)
        elif pos_query:
            pos_label = _position_label_from_code(pos_query.upper()) if len(pos_query) <= 3 else pos_query.title()
        else:
            pos_label = "position"
        pos_pool = _pool_rows_by_position(bundle, pos_query) if pos_query else []
        top_at_pos = _draft_player_name(pos_pool[0]) if pos_pool else ""
        focus_leads = bool(
            top_at_pos and _player_name_token(top_at_pos) == _player_name_token(focus)
        )
        my_next = bundle.get("my_next_pick")
        picks_until_next = (
            int(my_next) - int(pick)
            if pick_known and pick is not None and my_next is not None and int(my_next) > int(pick)
            else 12
        )
        pool_count = len(pos_pool)
        fallbacks = [_draft_player_name(r) for r in pos_pool[1:3] if _draft_player_name(r)]
        fallback_row = pos_pool[1] if len(pos_pool) > 1 else {}
        focus_market = _row_market_rank(row) if row else 9999.0
        fallback_market = _row_market_rank(fallback_row) if fallback_row else None
        scarce = pool_count <= 4 or (bundle.get("position_scarcity") or 0) >= 2.0
        drafted_line = _drafted_position_line(bundle, pos_query) if pos_query else ""
        focus_survival, fallback_survival, cost_read = _timing_survival_readout(
            focus_market,
            int(pick) if pick_known and pick is not None else 0,
            picks_until_next,
            fallback_market=fallback_market,
        )

        draft_now = focus_leads and (scarce or picks_until_next <= 6 or "draft now" in cost_read.lower())
        if draft_now:
            direct = (
                f"**Draft {focus} now** at {pick_note} — he leads the remaining **{pos_label}** tier. "
                f"Survival read: {focus_survival}."
            )
        else:
            direct = (
                f"**You can wait one round** on **{focus}** at {pick_note}. "
                f"Survival read: {focus_survival}."
            )
        direct += f" {cost_read.capitalize()}."
        if drafted_line:
            direct = drafted_line + " " + direct
        if fallbacks:
            direct += f" If **{focus}** is gone, **{', '.join(fallbacks)}** is the likely pivot ({fallback_survival})."

        scarcity_note = (
            _explain_position_scarcity(bundle, position_query=pos_query, pool_count=pool_count)
            if pos_query
            else _draft_scarcity_line(bundle, available_count=pool_count)
        )
        framing = (
            f"Timing read for **{focus}** ({pos_label}) at {pick_note}. "
            + (
                f"**{pool_count}** **{pos_label}** options remain in the tracked pool; "
                if pool_count
                else f"Limited **{pos_label}** rows in the current pool — check board sync; "
            )
            + f"**{picks_until_next}** picks until your next turn. "
            + scarcity_note
            + context_suffix
        )
        tradeoffs = (
            f"**Draft now** → lock the top **{pos_label}** before the tier drops. "
            f"**Wait** → pursue value elsewhere; {fallback_survival}."
        )
        what_if = [
            f"If a **{pos_label} run** starts → take **{focus}** immediately.",
            f"If **{focus}** is gone → pivot to **{fallbacks[0] if fallbacks else 'next tier'}**.",
            f"If you wait and he returns → you preserved pick value at **{pos_label}**.",
            f"If you need **{pos_label}** for roster balance → favor drafting now.",
        ]
        scarcity_line = scarcity_note
        risk_line = (
            f"Waiting risks losing **{focus}** ({focus_survival})."
            if draft_now
            else f"Waiting is viable if **{focus}** survives ({focus_survival})."
        )
    elif mode == "draft_review":
        roster_list = bundle.get("roster") or []
        filled = _roster_by_position(bundle)
        needed = bundle.get("needed_positions") or []
        cats = bundle.get("category_needs") or []
        grade = _draft_review_grade(bundle)
        best_pick, weakest_pick = _roster_pick_extremes(bundle, roster_list)
        filled_lines, filled_group_count = _filled_roster_display_lines(bundle)

        review_team = str(bundle.get("draft_review_team") or "").strip()
        team_note = f" for **{review_team}**" if review_team else ""

        direct = f"**Draft grade: {grade}**{team_note} through {pick_note}."
        direct += f" {_draft_grade_rationale(bundle, grade)}"
        if best_pick:
            direct += f" Best pick so far: **{best_pick}**."
        if weakest_pick and weakest_pick != best_pick:
            direct += f" {_weakest_pick_explanation(bundle, weakest_pick)}"
        if filled_lines:
            direct += " Positions covered: " + "; ".join(filled_lines[:6]) + "."
        if needed:
            direct += f" Biggest remaining gap: **{needed[0]}**."

        strengths: list[str] = []
        if filled_group_count >= 3:
            strengths.append(f"**{filled_group_count}** position groups covered")
        if best_pick:
            strengths.append(f"**{best_pick}** as an anchor")
        weaknesses: list[str] = []
        if needed:
            weaknesses.append(f"still need **{', '.join(needed[:4])}**")
        if cats:
            weaknesses.append(f"category pressure in **{', '.join(cats[:4])}**")

        framing = (
            f"Roster review{team_note} at {pick_note} on {roster_note} in **{scoring_label}** scoring."
            + (f" Positional balance: **{filled_group_count}** groups filled." if filled_group_count else "")
            + (f" Strengths: {'; '.join(strengths)}." if strengths else "")
            + (f" Weaknesses: {'; '.join(weaknesses)}." if weaknesses else "")
            + context_suffix
        )
        tradeoffs = (
            f"Close the **{needed[0]}** gap next, or chase overall value if a top player falls."
            if needed
            else "Stay flexible — balance category coverage with best player available."
        )
        what_if = [
            f"If you chase value → **{top}** over a need-filling pick.",
            f"If you chase balance → **{needed[0] if needed else top}** before the tier drops.",
            f"If you prioritize safety → favor higher-floor picks from recommendations.",
            f"If you prioritize upside → mix in **{sleeper_names[0] if sleeper_names else alt or 'a sleeper'}**.",
        ]
        scarcity_line = _draft_scarcity_line(bundle)
        risk_line = (
            "Risk profile: early roster is still forming — prioritize stable starters at scarce positions "
            "before dart throws."
            if len(roster_list) <= 4
            else "Risk profile: mix of floor and upside based on your current roster construction."
        )
    elif mode == "roster_needs":
        filled = _roster_by_position(bundle)
        needed = bundle.get("needed_positions") or []
        cats = bundle.get("category_needs") or []
        filled_lines, filled_group_count = _filled_roster_display_lines(bundle)

        direct_parts = ["**Positions already filled:**"]
        if filled_lines:
            direct_parts.extend(f"- {line}" for line in filled_lines[:8])
        else:
            direct_parts.append(f"- {roster_note}")
        if needed:
            direct_parts.append("")
            direct_parts.append("**Still needed (priority order):**")
            for i, pos_code in enumerate(needed[:6], 1):
                direct_parts.append(f"{i}. **{pos_code}** — {_need_priority_reason(pos_code)}")
            direct_parts.append("")
            direct_parts.append(
                f"Your biggest current roster gap is **{needed[0]}** — "
                f"{_need_priority_reason(needed[0])}."
            )
        elif cats:
            direct_parts.append("")
            direct_parts.append(f"Category priorities: **{', '.join(cats[:5])}**.")
        else:
            direct_parts.append("")
            direct_parts.append("No major positional holes flagged — build toward category balance.")
        direct = "\n".join(direct_parts)

        framing = (
            f"Roster construction at {pick_note}: "
            + f"**{filled_group_count}** position groups filled"
            + (f"; category needs **{', '.join(cats[:4])}**" if cats else "")
            + ". Focus on closing open slots in priority order before chasing overall value."
            + context_suffix
        )
        tradeoffs = (
            f"Priority path → target **{needed[0]}** before the tier thins."
            if needed
            else "Build toward balanced positional coverage with each pick."
        )
        what_if = [
            f"If a **{needed[0]} run** starts → take the top name at that position." if needed else "If a position run starts → secure scarce positions early.",
            f"If you prioritize power → weight HR/OBP among available: {', '.join(avail_names[:3]) or 'see board'}.",
            f"If you prioritize speed → favor SB profiles (queue/watchlist: {', '.join(bundle.get('draft_queue')[:2] + bundle.get('watchlist')[:2]) or '—'}).",
            f"If you prioritize safety → take **{top}** over upside dart throws.",
        ]
        scarcity_line = _draft_scarcity_line(bundle)
        risk_line = _draft_risk_line(bundle, needed[0] if needed else (player or top), mode=mode)
    elif mode == "best_values":
        value_rows = bundle.get("best_available") or bundle.get("available") or bundle.get("recommendations") or []
        ranked = _rank_value_players(value_rows, limit=5)
        direct = (
            f"Best values left at {pick_note}: "
            + ("; ".join(ranked[:4]) if ranked else "attach available_players / best_available in context.")
        )
        framing = (
            f"Ranked by Fantasy Edge / model-vs-market gap from your saved available pool "
            f"in **{scoring_label}** scoring.{context_suffix}"
        )
        tradeoffs = (
            f"**{ranked[0].split(' — ')[0] if ranked else top}** leads value; "
            f"**{alt or 'next value'}** is the pivot if you need **{needs_label}** instead."
        )
        what_if = [
            "If you prioritize power → bump HR-heavy names in the value list.",
            "If you prioritize speed → favor SB leaders still in available_players.",
            "If you prioritize pitching → defer hitters until SP/RP scarcity spikes.",
            "If you prioritize upside → weight younger profiles with positive Fantasy Edge.",
            "If you prioritize safety → favor higher-floor Market Rank values over edge bets.",
        ]
    elif mode == "next_pick" and rec_names:
        undrafted_roster_names = [
            n for n in (bundle.get("drafted_players") or [])
            if _player_name_token(n) not in {_player_name_token(r) for r in roster}
        ]
        avoid_note = ""
        if undrafted_roster_names:
            avoid_note = f" (off the board: {', '.join(str(x).split(' (')[0] for x in undrafted_roster_names[:3])})"
        direct = f"Given {roster_note} at {pick_note}, lean **{top}** for the next selection{avoid_note}."
        if alt:
            direct = (
                f"Given {roster_note} at {pick_note}, lean **{top}** over **{alt}** "
                f"for the next selection — both are available; do not re-draft roster players{avoid_note}."
            )
        framing = (
            f"This fits **{needs_label}** in **{scoring_label}** — not just raw rank. "
            f"Queue **{', '.join(bundle.get('draft_queue')[:3]) or '—'}** aligns with **{top}**.{context_suffix}"
        )
        tradeoffs = (
            f"**{top}** is the top board recommendation; **{alt or 'next tier'}** if you need a specific category gap."
            if alt
            else f"**{top}** balances projected value with roster fit at this pick slot."
        )
        what_if = [
            f"If you prioritize power → compare power-heavy options vs **{alt or top}**.",
            f"If you prioritize speed → favor SB profiles (watchlist: {', '.join(bundle.get('watchlist')[:2]) or '—'}).",
            f"If you prioritize safety → favor **{top}** (higher-floor recommendation).",
            f"If you prioritize upside → consider **{sleeper_names[0] if sleeper_names else alt or top}** from sleepers/tracked.",
        ]
    elif mode == "sleeper_risk":
        target = sleeper_names[0] if sleeper_names else (player or "this sleeper")
        row = next((r for r in bundle.get("sleepers") or [] if _draft_player_name(r) == target), None)
        edge = _player_metric(row, "Fantasy Edge", "fantasy_edge") if row else None
        market = _player_metric(row, "Market Rank", "market_rank") if row else None
        model = _player_metric(row, "Model Rank", "model_rank") if row else None
        reason = _player_metric(row, "Reason", "reason") if row else ""
        pool_bits = _rank_value_players(bundle.get("sleepers") or [], limit=3)
        pool_line = "; ".join(pool_bits) if pool_bits else f"**{target}** from your sleeper board"
        direct = (
            f"**{target}** is worth the risk as a sleeper when the upside (Fantasy Edge **{edge}**, "
            f"Model **{model}** vs Market **{market}**) outweighs the bust probability at this cost."
            if edge is not None
            else f"**{target}** is worth the risk only if draft cost stays low — see Fantasy Edge vs market on your sleeper board."
        )
        framing = (
            f"Sleeper pool in context: {pool_line}. "
            f"**{target}** fits roster needs **{needs_label}**; reward is ceiling, risk is playing-time/variance."
            + (f" Model note: {reason}." if reason else "")
            + context_suffix
        )
        tradeoffs = (
            f"**Upside:** **{target}** (Edge **{edge}**) can outperform ADP. "
            f"**Risk:** safer pivot **{top or 'next tier'}** from recommendations if you need floor."
        )
        what_if = [
            f"If **{target}** hits → league-winning surplus value at Market Rank **{market}**.",
            f"If **{target}** busts → opportunity cost vs **{top or 'safer pick'}**.",
            f"If similar sleepers remain ({', '.join(sleeper_names[:2]) or target}) → compare Edge before committing.",
        ]
        scarcity_line = _draft_scarcity_line(bundle, available_count=len(sleeper_names))
        risk_line = _draft_risk_line(bundle, target, mode="sleeper")
    elif mode == "sleeper":
        target = sleeper_names[0] if sleeper_names else (player or "this sleeper")
        exclusions = bundle.get("drafted_exclusions") or bundle.get("drafted_players") or []
        excl_note = f" ({len(exclusions)} players already drafted — **{target}** not among them)" if exclusions else ""
        direct = (
            f"**Take {target}** as a probability-weighted upside pick when draft cost is low enough "
            f"that hitting the ceiling pays for several misses{excl_note}."
        )
        edge = _player_metric(
            next((r for r in bundle.get("sleepers") or [] if _draft_player_name(r) == target), {}),
            "Fantasy Edge",
            "fantasy_edge",
        )
        reason = str(
            next(
                (
                    _player_metric(r, "Reason", "reason")
                    for r in bundle.get("sleepers") or []
                    if _draft_player_name(r) == target
                ),
                "",
            )
        ).strip()
        framing = (
            f"Sleeper **{target}** fits roster needs **{needs_label}**"
            + (f"; Fantasy Edge **{edge}**" if edge is not None else "")
            + (f" — {reason}" if reason else " — model rank beats market on your sleeper board")
            + f".{context_suffix}"
        )
        tradeoffs = (
            f"**{target}** balances upside vs roster need; compare to **{top}** if you want a safer floor pick."
            if top and _player_name_token(top) != _player_name_token(target)
            else f"**{target}** is the top Fantasy Edge name on your sleeper board for this spot."
        )
        what_if = [
            "If you need floor → pass and take the safer recommendation.",
            f"If you can absorb bust risk → **{target}** is a reasonable EV+ dart throw.",
            f"If similar players remain available next round → compare tracked: {', '.join(bundle.get('tracked_players')[:3]) or '—'}.",
        ]
    elif mode == "risk":
        direct = (
            f"At {pick_note}, taking **{player or top}** is worth the risk when upside moves "
            "your roster from average to competitive in a scarce category."
        )
        framing = (
            f"Risky picks are variance decisions against **{needs_label}** on {roster_note}.{context_suffix}"
        )
        tradeoffs = (
            f"**{player or top}** raises ceiling but widens downside; safer pivot **{alt or top}** stabilizes the roster."
        )
        what_if = [
            "If your roster already has power → risk on speed/upside profiles is easier to absorb.",
            "If early round → lower risk tolerance; if late round → higher risk tolerance.",
            f"If ADP is {adp_val:g} vs your pick {pick} → cost of being wrong is {'lower' if rank_edge >= 0 else 'higher'}.",
        ]
    elif mode == "category":
        direct = (
            f"Given {roster_note}, prioritize the player who closes your weakest category "
            f"in **{scoring_label}** — often **{top}** over raw rank."
        )
        framing = f"Category-balance optimization for **{needs_label}** at {pick_note}.{context_suffix}"
        tradeoffs = (
            f"**{top}** may rank lower overall but improve category balance; "
            f"**{alt or 'higher-ranked options'}** add raw value with less category impact."
            if alt
            else f"**{top}** is the better category-fit choice at {pick_note}."
        )
        what_if = [
            "If you prioritize power → favor HR/SB combo or pure power from available_players.",
            "If you prioritize speed → favor SB leaders (queue: " + (", ".join(bundle.get("draft_queue")[:3]) or "—") + ").",
            "If you prioritize pitching → target pitching scarcity before next hitter run.",
            "If you prioritize safety → favor higher-floor recommendations over upside.",
            "If you prioritize upside → weight sleepers/tracked with positive Fantasy Edge.",
        ]
    else:
        direct = f"**{verdict}** for **{player or top}** at {pick_note} (ADP **{adp_val:g}**)."
        framing = (
            "Draft value edge — compare market rank/ADP to your current pick slot "
            f"given **{needs_label}**.{context_suffix}"
        )
        tradeoffs = (
            f"Positive rank edge (~**{rank_edge:+.0f}** picks) means value; negative edge means reach. "
            f"Alternatives on board: **{alt or 'next tier'}**."
        )
        what_if = [
            "If ADP drops 3 picks → verdict can flip to value.",
            "If you need category fit more than ADP value → weight recommendations over rank edge.",
            f"If you wait one round → similar players may be available near pick **{int(adp_val)}**.",
        ]

    key_variables = [
        "Projected playing time",
        "Power vs speed category impact",
        "Positional scarcity",
        "Team need vs replacement value",
        f"Draft cost at pick {pick}" if pick else "Draft cost at current slot",
    ]
    if roster:
        key_variables.append(f"Roster construction ({len(roster)} players)")
    if rec_names:
        key_variables.append(f"Board recommendations ({', '.join(rec_names[:3])})")
    if bundle.get("draft_queue"):
        key_variables.append(f"Queue ({', '.join(bundle['draft_queue'][:3])})")

    applied_math = (
        "A draft pick is an optimization problem: maximize expected value while controlling "
        "category imbalance and downside risk at this pick slot."
    )
    _draft_mode_math_idea: dict[str, str] = {
        "draft_timing_decision": "Draft timing — survival odds, tier drop risk, and cost of waiting one round.",
        "draft_review": "Draft review — strengths, weaknesses, positional balance, then overall grade.",
        "roster_needs": "Roster construction — filled slots, open positions, and priority order.",
        "player_why": "Player fit — why this name beats peers at this position on your board.",
        "draft_player_compare": "Head-to-head draft compare — value, position need, and roster fit.",
        "position_best_available": "Best available at position — board rank and scarcity at this pick.",
    }
    if mode in _draft_mode_math_idea:
        applied_math = _draft_mode_math_idea[mode]

    coach = {
        "direct_answer": direct,
        "analyst_framing": framing,
        "scarcity": scarcity_line,
        "risk_upside": risk_line,
        "key_variables": key_variables,
        "tradeoffs": tradeoffs,
        "applied_math": applied_math,
        "what_if": what_if,
    }
    return _finalize_draft_coach_sections(coach, bundle)


def solve_baseball_draft(
    ctx: dict[str, Any],
    question: str,
    *,
    draft_round: int | None = None,
    current_pick: int | None = None,
    adp: float | None = None,
    projected_rank: int | None = None,
    replacement_value: float = 50.0,
    risk_tolerance: str = "moderate",
    num_teams: int = 12,
) -> SolverResult:
    """Draft value edge — rank_edge = ADP − current pick; uses live draft_snapshot when present."""
    bundle = _draft_context_bundle(ctx)
    player = _resolve_focus_player(question, ctx, bundle)
    if player:
        bundle["player"] = player
    proj_raw = ctx.get("draft_projection")
    parsed = _parse_draft_projection(proj_raw)
    mode = _draft_question_mode(question)

    if current_pick is not None:
        bundle["pick"] = int(current_pick)
    if draft_round is not None:
        bundle["round"] = int(draft_round)

    pick, rnd, pick_known, round_known = _resolve_draft_pick_round(bundle, ctx, parsed, num_teams=num_teams)

    focus_row = _find_player_row_in_bundle(player, bundle) if player else None
    if focus_row is None and bundle["recommendations"]:
        focus_row = bundle["recommendations"][0]
    elif focus_row is None and bundle["sleepers"]:
        focus_row = bundle["sleepers"][0]
    elif focus_row is None and bundle["best_available"]:
        focus_row = bundle["best_available"][0]

    adp_val = adp if adp is not None else _player_adp_from_row(focus_row)
    if adp_val is None:
        adp_val = parsed.get("adp")
    if adp_val is None and projected_rank is not None:
        adp_val = float(projected_rank)
    if adp_val is None and focus_row:
        adp_val = _player_adp_from_row(focus_row)
    if adp_val is None:
        adp_val = parsed.get("projected_rank") or (float(pick) if pick_known and pick is not None else None)
    if adp_val is None:
        adp_val = float(pick) if pick_known and pick is not None else 0.0

    rank = projected_rank if projected_rank is not None else parsed.get("projected_rank") or int(round(float(adp_val))) if adp_val else 0
    pick_for_edge = int(pick) if pick_known and pick is not None else 0
    adp_val = float(adp_val)
    rank_edge = adp_val - pick_for_edge if pick_known else 0.0
    value_edge = float(replacement_value) + rank_edge * 2.5

    tol = {"conservative": 1.0, "moderate": 0.0, "aggressive": -1.5}.get(str(risk_tolerance).lower(), 0.0)
    if rank_edge >= 3 + tol:
        verdict = "Worth it"
        label = "Value — player typically goes later than this pick"
    elif rank_edge >= -2 + tol:
        verdict = "Fair price"
        label = "Near fair — ADP close to your pick slot"
    elif rank_edge >= -6 + tol:
        verdict = "Wait"
        label = "Slight reach — consider waiting one round"
    else:
        verdict = "Avoid"
        label = "Overdraft — ADP much earlier than this pick"

    coach = _build_baseball_draft_coach_sections(
        question=question,
        bundle=bundle,
        mode=mode,
        player=player,
        pick=pick,
        rnd=rnd,
        pick_known=pick_known,
        round_known=round_known,
        adp_val=adp_val,
        rank_edge=rank_edge,
        verdict=verdict,
    )

    pick_round_line = _format_pick_note(pick, rnd, pick_known=pick_known, round_known=round_known)

    short_answer = coach.get("direct_answer") or coach.get("formatted_answer") or ""
    why = coach.get("why_roster_fit") or coach["analyst_framing"]
    if mode == "value_edge":
        why = label
        if rank_edge > 0:
            why += f" You get ~**{rank_edge:.0f}** picks of value vs ADP."
        elif rank_edge < 0:
            why += f" You're reaching ~**{abs(rank_edge):.0f}** picks ahead of ADP."
        if coach.get("scarcity"):
            why = f"{coach['analyst_framing']}\n\n{coach['scarcity']}"

    opp = coach.get("alternatives") or coach["tradeoffs"]
    if rank_edge < -2 and mode == "value_edge" and pick_known:
        opp = (
            f"{coach['tradeoffs']} Waiting one round could land similar value near pick "
            f"**{int(adp_val)}** instead of **{pick_for_edge}**."
        )

    math_idea = coach["applied_math"]
    variables = (
        "rank_edge = ADP − current_pick\n"
        "value_edge = replacement_value + rank_edge × scale\n"
        "roster_fit = category gaps + positional scarcity + replacement value\n"
        "positive rank_edge → value · negative → reach/overdraft"
    )
    calc = f"Draft slot: {pick_round_line}\n"
    if pick_known:
        calc += (
            f"ADP / projected rank: **{adp_val:g}**\n"
            f"rank_edge = {adp_val:g} − {pick_for_edge} = **{rank_edge:+.0f}**\n"
            f"value_edge ≈ {replacement_value:g} + {rank_edge:+.0f}×2.5 = **{value_edge:.0f}**"
        )
    else:
        calc += "Pick not in context — rank_edge not computed."
    if bundle["recommendations"]:
        rec_line = ", ".join(_draft_player_name(r) for r in bundle["recommendations"][:4])
        calc += f"\nBoard recommendations: **{rec_line}**"
    if bundle["roster"]:
        calc += f"\nRoster: {', '.join(bundle['roster'][:6])}"
    if bundle.get("draft_queue"):
        calc += f"\nQueue: {', '.join(bundle['draft_queue'][:4])}"
    if bundle.get("position_scarcity") is not None:
        calc += f"\nScarcity index: **{bundle['position_scarcity']:g}**"
    if bundle.get("needed_positions"):
        calc += f"\nPosition needs: {', '.join(bundle['needed_positions'])}"
    if bundle.get("category_needs"):
        calc += f"\nCategory needs: {', '.join(bundle['category_needs'])}"

    missing: list[str] = []
    if not bundle["snap"] and not bundle["sleepers_snap"] and not player:
        missing.append("player or draft_snapshot")
    if mode == "value_edge" and adp is None and not parsed.get("adp") and not focus_row:
        missing.append("draft_projection or ADP")
    if mode == "next_pick" and not bundle["recommendations"]:
        missing.append("recommended_players")
    if mode == "roster_needs" and not bundle.get("needed_positions") and not bundle.get("category_needs"):
        missing.append("needed_positions or category_needs")
    if mode == "draft_review" and not bundle.get("roster"):
        missing.append("user_roster or roster")
    if mode == "best_values" and not bundle.get("best_available") and not bundle.get("available"):
        missing.append("best_available or available_players")
    if mode == "player_why" and not player:
        missing.append("question_player or player name in question")
    if mode == "draft_market_prediction":
        pos_q = extract_draft_position_query(question) or "catcher"
        pool = _pool_rows_by_position(bundle, pos_q)
        if not pool:
            missing.append("available_players at requested position")
        if not pick_known:
            missing.append("current_pick")
    if mode == "draft_player_compare":
        pa, pb = extract_draft_compare_players(question)
        if not pa or not pb:
            pa = str(bundle.get("player_a") or "").strip()
            pb = str(bundle.get("player_b") or "").strip()
        if not pa or not pb:
            missing.append("player_a and player_b from question")
        elif not _find_player_row_in_bundle(pa, bundle) and not _find_player_row_in_bundle(pb, bundle):
            missing.append("board rows for compared players")

    data_used_lines = [
        f"Player focus: **{player}**" if player else "",
        f"Draft slot: {pick_round_line}",
        f"League: {ctx.get('draft_format') or ctx.get('league_format') or _draft_scoring_label(bundle['scoring'])}",
    ]
    if bundle["roster"]:
        data_used_lines.append(f"Roster: {', '.join(bundle['roster'][:6])}")
    if bundle["recommendations"]:
        data_used_lines.append(
            "Recommendations: " + ", ".join(_draft_player_name(r) for r in bundle["recommendations"][:4])
        )
    if bundle.get("best_available"):
        data_used_lines.append(
            "Best available: " + ", ".join(_draft_player_name(r) for r in bundle["best_available"][:4])
        )
    if bundle["sleepers"]:
        data_used_lines.append(
            "Sleepers: " + ", ".join(_draft_player_name(r) for r in bundle["sleepers"][:3])
        )
    if bundle.get("draft_queue"):
        data_used_lines.append("Queue: " + ", ".join(bundle["draft_queue"][:4]))
    if bundle.get("watchlist"):
        data_used_lines.append("Watchlist: " + ", ".join(bundle["watchlist"][:4]))
    if bundle.get("tracked_players"):
        data_used_lines.append("Tracked: " + ", ".join(bundle["tracked_players"][:4]))
    if bundle.get("drafted_players"):
        data_used_lines.append(
            "Drafted: " + ", ".join(bundle["drafted_players"][:5])
            + ("…" if len(bundle["drafted_players"]) > 5 else "")
        )

    live_metrics = {
        "Verdict": verdict if mode == "value_edge" else mode.replace("_", " ").title(),
        "Rank edge": f"{rank_edge:+.0f}" if pick_known else "n/a",
        "ADP vs pick": f"{adp_val:g} vs {pick_for_edge}" if pick_known else "pick unknown",
    }
    if bundle["recommendations"]:
        live_metrics["Top rec"] = _draft_player_name(bundle["recommendations"][0])
    if bundle.get("position_scarcity") is not None:
        live_metrics["Scarcity"] = f"{bundle['position_scarcity']:g}"

    sens_rows = []
    for delta in (-3, 0, 3):
        adj = rank_edge + delta
        out = "Worth it" if adj >= 3 else "Fair" if adj >= -2 else "Wait" if adj >= -6 else "Avoid"
        scenario_pick = f"{pick_for_edge + delta}" if pick_known else "pick unknown"
        sens_rows.append({"Parameter": "Pick slot", "Scenario": scenario_pick, "Outcome": out})
    for line in coach["what_if"][:5]:
        sens_rows.append(
            {
                "Parameter": "What-if",
                "Scenario": line.split("→")[0].strip(),
                "Outcome": line.split("→")[-1].strip() if "→" in line else line,
            }
        )

    partial = bool(missing) and mode in (
        "value_edge",
        "best_values",
        "roster_needs",
        "draft_review",
        "sleeper",
        "draft_market_prediction",
        "draft_player_compare",
    )
    conf = 88 if bundle["snap"] and bundle["recommendations"] else 85 if bundle["sleepers_snap"] else 80 if not missing else 55
    if mode == "draft_market_prediction" and missing:
        conf = 42
    if mode == "draft_player_compare" and missing:
        conf = 45

    sensitivity_plain = coach.get("what_if_text") or "\n".join(coach["what_if"][:5])
    if coach.get("scarcity"):
        sensitivity_plain = f"{coach['scarcity']}\n{sensitivity_plain}"
    if coach.get("risk_upside"):
        sensitivity_plain = f"{coach['risk_upside']}\n{sensitivity_plain}"

    return _coach_result(
        question=question,
        problem_type="Draft decision",
        math_idea=math_idea,
        variables=variables,
        data_used=_cap_data_used(data_used_lines),
        calculation=calc,
        result=short_answer,
        interpretation=opp,
        assumptions=[
            f"ADP reflects {num_teams}-team league norms unless you override.",
            f"Risk tolerance: **{risk_tolerance}** shifts reach/fade thresholds.",
            "Uses live draft_snapshot (roster, recommendations, sleepers) when transferred from Baseball.",
            "Does not auto-change your draft board — decision support only.",
        ],
        sensitivity_notes="If ADP moves 3 picks or category needs shift, the best pick can change — use sliders below.",
        missing_fields=missing,
        partial=partial,
        problem_type_id=BASEBALL_DRAFT,
        computed={
            "rank_edge": rank_edge,
            "value_edge": value_edge,
            "adp": adp_val,
            "pick": pick,
            "projected_rank": rank,
            "draft_mode": mode,
            "coach_sections": coach,
            **{
                k: v
                for k, v in {
                    **(ctx.get("_draft_team_diagnostics") or {}),
                    **(ctx.get("send_pipeline_diagnostics") or {}),
                }.items()
                if k
                in (
                    "requested_team",
                    "resolved_team",
                    "roster_owner_used",
                    "roster_player_count",
                    "roster_players_used",
                )
            },
        },
        default_controls={
            **({"draft_round": rnd} if rnd is not None else {}),
            **({"current_pick": pick} if pick_known and pick is not None else {}),
            "adp": adp_val,
            "projected_rank": rank,
            "replacement_value": replacement_value,
            "risk_tolerance": risk_tolerance,
            "num_teams": num_teams,
        },
        conclusion=short_answer,
        confidence_pct=conf,
        reasons=[coach.get("alternatives") or coach["tradeoffs"], coach.get("scarcity") or "", *coach["key_variables"][:2]],
        short_answer=short_answer,
        why=why,
        sensitivity_plain=sensitivity_plain,
        live_metrics=live_metrics,
        sensitivity_rows=sens_rows,
    )


def solve_nba_matchup_edge(
    ctx: dict[str, Any],
    question: str,
    *,
    injury_adjustment_pp: float = 5.0,
    prob_threshold_pp: float = 8.0,
    stat_gap_threshold: float = 0.15,
    stat_gap_weight: float = 0.4,
) -> SolverResult:
    """Matchup edge score — probability + scouting gaps − injury penalty."""
    team = str(ctx.get("team") or "").strip()
    opp = str(ctx.get("opponent") or "").strip()
    wp = _parse_pct(ctx.get("series_probability") or ctx.get("win_probability"))
    adv = ctx.get("matchup_advantages")
    adv_list = [str(a).strip() for a in adv if str(a).strip()] if isinstance(adv, list) else []
    inj = str(ctx.get("injury_summary") or "").strip()

    prob_edge = ((wp - 50.0) / 100.0) if wp is not None else 0.0
    stat_edge = min(0.35, len(adv_list) * 0.07)
    for text in adv_list[:3]:
        low = text.lower()
        if any(w in low for w in ("strong", "clear", "major", "size", "mismatch")):
            stat_edge += 0.04

    injury_penalty = 0.0
    if inj:
        injury_penalty = injury_adjustment_pp / 100.0
        if any(w in inj.lower() for w in ("out", "doubtful", "unlikely")):
            injury_penalty += 0.03

    edge_score = prob_edge * 0.55 + stat_edge * stat_gap_weight - injury_penalty
    edge_pp = edge_score * 100.0
    threshold = prob_threshold_pp

    if edge_pp >= threshold:
        verdict = "Meaningful edge"
    elif edge_pp >= threshold * 0.45:
        verdict = "Slight edge"
    else:
        verdict = "No clear edge"

    driver_parts: list[str] = []
    if wp is not None:
        driver_parts.append(f"model probability **{wp:.0f}%**")
    if adv_list:
        driver_parts.append(f"**{len(adv_list)}** scouting advantage(s)")
    if inj:
        driver_parts.append(f"injury: {inj[:80]}")
    main_driver = driver_parts[0] if driver_parts else "limited matchup data attached"

    short_answer = f"**{verdict}** for **{team or 'Team'}** vs **{opp or 'opponent'}** (edge score **{edge_pp:+.1f}** pp)."
    why = f"Main driver: {main_driver}. Edge score combines probability lean, schematic gaps, and injury downgrade."

    math_idea = (
        "This is a **matchup edge score** — not just the quoted probability. "
        "We blend probability edge vs 50%, scouting advantage strength, and injury penalty."
    )
    variables = (
        "prob_edge = (p − 50%) / 100\n"
        "stat_edge = f(matchup_advantages count/strength)\n"
        "edge_score = 0.55×prob_edge + weight×stat_edge − injury_penalty"
    )
    calc_lines = [
        f"Probability: **{wp:.0f}%** → prob_edge **{prob_edge:+.3f}**" if wp is not None else "Probability: not attached",
        f"Scouting edges: **{len(adv_list)}** → stat_edge **{stat_edge:.3f}**",
        f"Injury penalty: **{injury_penalty:.3f}** ({injury_adjustment_pp:.0f} pp base)" if inj else "Injury penalty: **0**",
        f"edge_score = **{edge_score:+.3f}** → **{edge_pp:+.1f} pp** vs threshold **{threshold:.0f} pp**",
    ]

    missing: list[str] = []
    if not team:
        missing.append("team")
    if wp is None and not adv_list:
        missing.append("win/series probability or matchup_advantages")

    live_metrics = {
        "Verdict": verdict,
        "Edge (pp)": f"{edge_pp:+.1f}",
        "Probability": f"{wp:.0f}%" if wp is not None else "—",
    }

    return _coach_result(
        question=question,
        problem_type="Matchup edge",
        math_idea=math_idea,
        variables=variables,
        data_used=_cap_data_used([
            f"**{team}** vs **{opp}**",
            f"Probability: **{wp:.0f}%**" if wp is not None else "",
            f"Advantages: {adv_list[0][:100]}" if adv_list else "",
            f"Injuries: {inj[:100]}" if inj else "",
        ]),
        calculation="\n".join(calc_lines),
        result=short_answer,
        interpretation=f"Uncertainty: injury news or hot shooting can swing edge ±{prob_threshold_pp:.0f} pp.",
        assumptions=[
            "Probability and scouting edges refer to the same series/game horizon.",
            "Injury adjustment is illustrative — update slider for your severity read.",
        ],
        sensitivity_notes=f"Increasing injury penalty by **{injury_adjustment_pp:.0f} pp** lowers edge score proportionally.",
        missing_fields=missing,
        partial=bool(missing),
        problem_type_id=NBA_MATCHUP_EDGE,
        computed={
            "edge_score": edge_score,
            "edge_pp": edge_pp,
            "prob_edge": prob_edge,
            "stat_edge": stat_edge,
            "injury_penalty": injury_penalty,
            "probability": wp,
        },
        default_controls={
            "injury_adjustment_pp": injury_adjustment_pp,
            "prob_threshold_pp": prob_threshold_pp,
            "stat_gap_threshold": stat_gap_threshold,
            "stat_gap_weight": stat_gap_weight,
        },
        conclusion=short_answer,
        confidence_pct=76 if wp is not None or adv_list else 48,
        reasons=[why],
        short_answer=short_answer,
        why=why,
        sensitivity_plain=(
            f"If injury penalty rises from **{injury_adjustment_pp:.0f}** to **{injury_adjustment_pp + 5:.0f} pp**, "
            f"edge score drops ~5 pp — may flip between slight and no clear edge."
        ),
        live_metrics=live_metrics,
    )


def _generic_solver(route: ProblemRoute, question: str, ctx: dict[str, Any], params: dict[str, Any] | None = None) -> SolverResult:
    """Interactive partial solver — closest model + assumption controls."""
    p = dict(params or {})
    purpose = route.math_purpose or PURPOSE_COMPARE
    model_name = route.model_name or "Interactive partial model"
    rationale = route.model_rationale or "We picked the closest mathematical model for your question shape."
    variables = route.model_variables or "Adjust assumptions below to explore the answer."
    restatement = route.intent_restatement or question
    relevant = route.data_relevant or []
    missing_interp = route.data_missing_interp or route.missing_fields
    pa = str(ctx.get("player_a") or ctx.get("player") or "Player A")
    pb = str(ctx.get("player_b") or "Player B")
    stat = "stat"

    default_controls: dict[str, Any] = {}
    live_metrics: dict[str, str] = {}
    calc_lines: list[str] = []
    short_answer = ""
    why = ""
    math_idea = ""
    partial = True

    if purpose == PURPOSE_FORECAST:
        math_idea = "Future accumulation — project totals as rate × seasons remaining (with optional decline)."
        rate_a = float(p.get("rate_a", p.get("generic_rate_a", 90.0)))
        rate_b = float(p.get("rate_b", p.get("generic_rate_b", 100.0)))
        seasons_a = float(p.get("seasons_a", p.get("generic_seasons_a", 10.0)))
        seasons_b = float(p.get("seasons_b", p.get("generic_seasons_b", 8.0)))
        decline_a = float(p.get("decline_a", p.get("generic_decline_a", 0.02)))
        decline_b = float(p.get("decline_b", p.get("generic_decline_b", 0.03)))
        default_controls = {
            "generic_rate_a": rate_a,
            "generic_rate_b": rate_b,
            "generic_seasons_a": seasons_a,
            "generic_seasons_b": seasons_b,
            "generic_decline_a": decline_a,
            "generic_decline_b": decline_b,
        }
        total_a = sum(rate_a * ((1 - decline_a) ** i) for i in range(int(seasons_a)))
        total_b = sum(rate_b * ((1 - decline_b) ** i) for i in range(int(seasons_b)))
        winner = pa if total_a >= total_b else pb
        margin = abs(total_a - total_b)
        short_answer = f"**{winner}** projects ~**{max(total_a, total_b):.0f}** future {stat} vs ~**{min(total_a, total_b):.0f}** (margin ~{margin:.0f})."
        why = (
            f"At these rates and horizons, **{winner}** accumulates more over time"
            + (f" despite lower current pace" if winner == pa and rate_a < rate_b else "")
            + "."
        )
        calc_lines = [
            f"{pa}: Σ rate × (1−decline)^t for t=0..{int(seasons_a) - 1} ≈ **{total_a:.0f}**",
            f"{pb}: Σ rate × (1−decline)^t for t=0..{int(seasons_b) - 1} ≈ **{total_b:.0f}**",
        ]
        live_metrics = {
            f"{pa} projected": f"{total_a:.0f}",
            f"{pb} projected": f"{total_b:.0f}",
            "Margin": f"{margin:.0f}",
        }
        partial = bool(missing_interp)

    elif purpose == PURPOSE_COMPARE:
        math_idea = "Weighted comparison — normalize two scores and compare share of total."
        score_a = float(p.get("score_a", p.get("generic_score_a", 55.0)))
        score_b = float(p.get("score_b", p.get("generic_score_b", 45.0)))
        default_controls = {"generic_score_a": score_a, "generic_score_b": score_b}
        total = score_a + score_b or 1.0
        share_a = score_a / total
        leader = pa if score_a >= score_b else pb
        short_answer = f"**{leader}** leads with **{max(score_a, score_b):.0f}** vs **{min(score_a, score_b):.0f}** ({share_a:.0%} share for {pa})."
        why = f"Comparison uses attached or assumed scores — **{leader}** is ahead at these values."
        calc_lines = [f"Share({pa}) = {score_a} / ({score_a}+{score_b}) = **{share_a:.0%}**"]
        live_metrics = {f"{pa} score": f"{score_a:.0f}", f"{pb} score": f"{score_b:.0f}", "Leader": leader}
        partial = bool(missing_interp)

    elif purpose == PURPOSE_ESTIMATE_RATE:
        math_idea = "Rate-needed model — gap ÷ periods remaining = required pace."
        gap = float(p.get("gap", p.get("generic_gap", 100.0)))
        periods = float(p.get("periods", p.get("generic_periods", 20.0)))
        expected = float(p.get("expected_rate", p.get("generic_expected_rate", 4.5)))
        default_controls = {
            "generic_gap": gap,
            "generic_periods": periods,
            "generic_expected_rate": expected,
        }
        required = gap / periods if periods else gap
        feasible = expected >= required
        short_answer = (
            f"Need **{required:.2f}**/period; expected **{expected:.2f}** → "
            + ("**on pace**" if feasible else "**behind pace**")
            + "."
        )
        why = "Required rate is the gap spread evenly across remaining periods."
        calc_lines = [f"required = {gap:.0f} ÷ {periods:.0f} = **{required:.2f}**/period"]
        live_metrics = {"Required rate": f"{required:.2f}", "Expected rate": f"{expected:.2f}", "Verdict": "On pace" if feasible else "Behind"}
        partial = bool(missing_interp)

    elif purpose == PURPOSE_TEST_SIGNIFICANCE:
        math_idea = "Trend significance — slope magnitude and R² vs thresholds."
        slope = float(p.get("slope", p.get("generic_slope", 0.8)))
        r2 = float(p.get("r2", p.get("generic_r2", 0.42)))
        min_slope = float(p.get("min_slope", 0.5))
        min_r2 = float(p.get("min_r2", 0.35))
        default_controls = {"generic_slope": slope, "generic_r2": r2, "min_slope": min_slope, "min_r2": min_r2}
        meaningful = abs(slope) >= min_slope and r2 >= min_r2
        short_answer = "**Meaningful trend**" if meaningful else "**Likely noise** — adjust slope/R² to test."
        why = f"|slope|={abs(slope):.2f} (need ≥{min_slope}), R²={r2:.2f} (need ≥{min_r2})."
        calc_lines = [f"Signal check: |{slope:.2f}| ≥ {min_slope} and {r2:.2f} ≥ {min_r2} → **{meaningful}**"]
        live_metrics = {"|Slope|": f"{abs(slope):.2f}", "R²": f"{r2:.2f}", "Verdict": "Meaningful" if meaningful else "Noise"}
        partial = bool(missing_interp)

    elif purpose in (PURPOSE_EVALUATE_RISK, PURPOSE_EXPLAIN_WHY, PURPOSE_ATTRIBUTE):
        math_idea = "Risk / attribution — return vs volatility or weight × drawdown contribution."
        ret = float(p.get("return_pct", p.get("generic_return", 8.0)))
        vol = float(p.get("volatility", p.get("generic_volatility", 14.0)))
        weight = float(p.get("weight_pct", p.get("generic_weight", 40.0)))
        default_controls = {
            "generic_return": ret,
            "generic_volatility": vol,
            "generic_weight": weight,
        }
        sharpe = ret / vol if vol else 0.0
        contrib = weight * 0.18
        if purpose == PURPOSE_ATTRIBUTE or purpose == PURPOSE_EXPLAIN_WHY:
            short_answer = f"**{weight:.0f}%** weight ≈ **{contrib:.1f}pp** drawdown contribution at −18% market."
            why = "Attribution ≈ weight × market decline × correlation — large weights dominate drawdown."
            calc_lines = [f"contribution ≈ {weight:.0f}% × 18% ≈ **{contrib:.1f}pp**"]
            live_metrics = {"Weight": f"{weight:.0f}%", "Est. contribution": f"{contrib:.1f}pp"}
        else:
            short_answer = f"Sharpe ≈ **{sharpe:.2f}** ({ret:.1f}% return ÷ {vol:.1f}% vol)."
            why = "Return must compensate for volatility at your tolerance."
            calc_lines = [f"Sharpe ≈ {ret:.1f} ÷ {vol:.1f} = **{sharpe:.2f}**"]
            live_metrics = {"Return": f"{ret:.1f}%", "Volatility": f"{vol:.1f}%", "Sharpe": f"{sharpe:.2f}"}
        partial = bool(missing_interp)

    elif purpose == PURPOSE_DECIDE:
        math_idea = "Threshold decision — act when drift or gap exceeds your cutoff."
        drift = float(p.get("drift", p.get("generic_drift", 6.0)))
        threshold = float(p.get("threshold", p.get("generic_threshold", 5.0)))
        default_controls = {"generic_drift": drift, "generic_threshold": threshold}
        act = abs(drift) >= threshold
        short_answer = "**Rebalance / act**" if act else "**Hold** — below threshold."
        why = f"|drift|={abs(drift):.1f}% vs threshold {threshold:.1f}%."
        calc_lines = [f"|{drift:.1f}| {'≥' if act else '<'} {threshold:.1f} → **{'act' if act else 'hold'}**"]
        live_metrics = {"Drift": f"{drift:.1f}%", "Threshold": f"{threshold:.1f}%", "Decision": "Act" if act else "Hold"}
        partial = bool(missing_interp)

    elif purpose == PURPOSE_ESTIMATE_PROBABILITY:
        math_idea = "Probability reasonableness — compare quoted p to an implied edge band."
        prob = float(p.get("probability", p.get("generic_probability", 62.0)))
        prior = float(p.get("prior", p.get("generic_prior", 52.0)))
        default_controls = {"generic_probability": prob, "generic_prior": prior}
        gap = prob - prior
        label = "Optimistic" if gap > 10 else "Conservative" if gap < -10 else "Reasonable"
        short_answer = f"**{prob:.0f}%** vs prior **{prior:.0f}%** → **{label}**."
        why = "Large gaps vs a simple prior warrant checking injuries, matchups, and sample size."
        calc_lines = [f"gap = {prob:.0f} − {prior:.0f} = **{gap:+.0f}pp**"]
        live_metrics = {"Quoted": f"{prob:.0f}%", "Prior": f"{prior:.0f}%", "Label": label}
        partial = bool(missing_interp)

    elif purpose == PURPOSE_MEASURE_SENSITIVITY:
        math_idea = "Scenario sensitivity — stressed return/vol under macro shock."
        base_ret = float(p.get("base_return", p.get("generic_base_return", 8.0)))
        shock = float(p.get("return_shock", p.get("generic_return_shock", -3.0)))
        base_vol = float(p.get("base_vol", p.get("generic_base_vol", 12.0)))
        vol_shock = float(p.get("vol_shock", p.get("generic_vol_shock", 4.0)))
        default_controls = {
            "generic_base_return": base_ret,
            "generic_return_shock": shock,
            "generic_base_vol": base_vol,
            "generic_vol_shock": vol_shock,
        }
        stressed_ret = base_ret + shock
        stressed_vol = base_vol + vol_shock
        short_answer = f"Stressed return **{stressed_ret:.1f}%**, vol **{stressed_vol:.1f}%**."
        why = "Macro shocks move both return and volatility — test whether the plan still fits."
        calc_lines = [
            f"return: {base_ret:.1f} + ({shock:.1f}) = **{stressed_ret:.1f}%**",
            f"vol: {base_vol:.1f} + {vol_shock:.1f} = **{stressed_vol:.1f}%**",
        ]
        live_metrics = {"Stressed return": f"{stressed_ret:.1f}%", "Stressed vol": f"{stressed_vol:.1f}%"}
        partial = bool(missing_interp)

    else:
        math_idea = route.model_variables or "Define measurable quantity, baseline, and decision threshold."
        baseline = float(p.get("baseline", p.get("generic_baseline", 50.0)))
        threshold = float(p.get("threshold", p.get("generic_threshold", 60.0)))
        default_controls = {"generic_baseline": baseline, "generic_threshold": threshold}
        short_answer = f"Baseline **{baseline:.0f}** vs threshold **{threshold:.0f}** → **{'above' if baseline >= threshold else 'below'}** cutoff."
        why = "Generic threshold model — enter your own numbers to explore."
        calc_lines = [f"{baseline:.0f} {'≥' if baseline >= threshold else '<'} {threshold:.0f}"]
        live_metrics = {"Baseline": f"{baseline:.0f}", "Threshold": f"{threshold:.0f}"}

    data_used = [f"Source: **{route.source_app}**"]
    if relevant:
        data_used.append("Available: " + ", ".join(relevant[:4]))
    if missing_interp:
        data_used.append("Missing: " + ", ".join(str(m) for m in missing_interp[:4]))

    data_improve = [
        f"Enter **{m}** in the controls below or re-send from the source app."
        for m in missing_interp[:3]
    ]
    partial_conf = _route_confidence_pct(route, partial, len(route.missing_fields))

    return _coach_result(
        question=question,
        problem_type=route.problem_type or model_name,
        math_idea=math_idea,
        variables=variables,
        data_used=data_used,
        calculation="\n\n".join(calc_lines) if calc_lines else rationale,
        result=short_answer,
        interpretation=(
            f"We don't have every field for a full answer, but this is a **{model_name}** problem. "
            f"{restatement} Adjust assumptions below."
        ),
        assumptions=[
            "Assumption values are editable — change them to see how the verdict shifts.",
            "Partial solvability: " + (route.solvability or "approximate"),
        ],
        sensitivity_notes="Changing rates, horizons, or thresholds updates the live result above.",
        missing_fields=list(route.missing_fields),
        partial=partial,
        problem_type_id=route.problem_type_id,
        default_controls=default_controls,
        conclusion=short_answer,
        confidence_pct=partial_conf,
        reasons=[why] if why else [],
        model_note=rationale,
        data_would_improve=data_improve,
        short_answer=short_answer,
        why=why,
        sensitivity_plain="Drag the assumption sliders — the short answer and live metrics update immediately.",
        live_metrics=live_metrics,
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
    if pid == BASEBALL_VALUATION:
        return solve_baseball_valuation(
            ctx,
            question,
            over_threshold=float(p.get("over_threshold", 0.72)),
            under_threshold=float(p.get("under_threshold", 0.38)),
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

    if pid == BASEBALL_FUTURE_ACCUMULATION:
        return solve_baseball_future_accumulation(
            ctx,
            question,
            seasons_a=p.get("seasons_a"),
            seasons_b=p.get("seasons_b"),
            decline_a=float(p.get("decline_a", 0.02)),
            decline_b=float(p.get("decline_b", 0.03)),
            horizon_seasons=int(p.get("horizon_seasons", 10)),
            rate_a_override=p.get("rate_a"),
            rate_b_override=p.get("rate_b"),
        )
    if pid == INVESTMENT_DRAWDOWN_ATTRIBUTION:
        return solve_investment_drawdown_attribution(
            ctx,
            question,
            focus_ticker=str(p.get("focus_ticker", "")),
            market_decline=float(p.get("market_decline", -20.0)),
            equity_correlation=float(p.get("equity_correlation", 0.85)),
        )
    if pid == NBA_INVERSE_STAT_CHASE:
        return solve_nba_inverse_stat_chase(
            ctx,
            question,
            expected_rate=p.get("expected_rate"),
            target_value=p.get("target_value"),
        )
    if pid == INVESTMENT_CONCENTRATION:
        return solve_investment_concentration(
            ctx,
            question,
            max_single_pct=float(p.get("max_single_pct", 25.0)),
            max_top3_pct=float(p.get("max_top3_pct", 60.0)),
        )
    if pid == BASEBALL_PROJECTION:
        return solve_baseball_projection_realism(
            ctx,
            question,
            max_above_recent_pct=float(p.get("max_above_recent_pct", 25.0)),
            max_above_career_pct=float(p.get("max_above_career_pct", 35.0)),
        )

    if pid == BASEBALL_DRAFT:
        return solve_baseball_draft(
            ctx,
            question,
            draft_round=p.get("draft_round"),
            current_pick=p.get("current_pick"),
            adp=p.get("adp"),
            projected_rank=p.get("projected_rank"),
            replacement_value=float(p.get("replacement_value", 50.0)),
            risk_tolerance=str(p.get("risk_tolerance", "moderate")),
            num_teams=int(p.get("num_teams", 12)),
        )

    if pid == NBA_MATCHUP_EDGE:
        return solve_nba_matchup_edge(
            ctx,
            question,
            injury_adjustment_pp=float(p.get("injury_adjustment_pp", 5.0)),
            prob_threshold_pp=float(p.get("prob_threshold_pp", 8.0)),
            stat_gap_threshold=float(p.get("stat_gap_threshold", 0.15)),
            stat_gap_weight=float(p.get("stat_gap_weight", 0.4)),
        )

    if pid in (NBA_WIN_PROBABILITY, NBA_LEGACY_COMPARISON):
        if pid == NBA_WIN_PROBABILITY:
            return solve_nba_win_probability(ctx, question)
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

    if pid == BASEBALL_HISTORICAL:
        return solve_baseball_historical(ctx, question)

    if pid == BASEBALL_PLAYER_COMPARE:
        return solve_baseball_player_compare(
            ctx,
            question,
            weight_rate=float(p.get("weight_rate", 1.0)),
            weight_power=float(p.get("weight_power", 1.0)),
            weight_career=float(p.get("weight_career", 0.5)),
            weight_peak=float(p.get("weight_peak", 0.5)),
        )

    if pid == INVESTMENT_MACRO:
        return solve_investment_macro_stress(
            ctx,
            question,
            return_shock=float(p.get("return_shock", -3.0)),
            vol_shock=float(p.get("vol_shock", 4.0)),
            recession_prob=float(p.get("recession_prob", 30.0)),
        )

    if pid in (
        BASEBALL_GENERIC,
        NBA_GENERIC,
        INVESTMENT_GENERIC,
        GENERIC_FALLBACK,
        GENERIC_INTERACTIVE,
    ):
        return _generic_solver(route, question, ctx, p)

    return _generic_solver(route, question, ctx, p)


def _solver_dispatch_error_result(
    route: ProblemRoute,
    question: str,
    ctx: dict[str, Any],
    exc: Exception,
) -> SolverResult:
    """Honest partial answer when a specific solver raises — never crash the UI path."""
    solver_id = route.problem_type_id
    missing = list(route.missing_fields)
    err_note = f"{type(exc).__name__}: {exc}"
    short = (
        f"I could not finish a full **{route.problem_type}** answer from the context attached. "
        "Return to the source app, load the relevant page, and re-send the question."
    )
    improve = [f"**{m}**" for m in missing[:4]] or [
        "Re-send with draft board / filters loaded on the source page.",
    ]
    return _coach_result(
        question=question,
        problem_type=route.problem_type,
        math_idea="Solver could not run — insufficient or incompatible context.",
        variables="context keys · required fields · solver inputs",
        data_used=[f"Source: **{route.source_app or 'suite'}**", f"Solver: **{solver_id}**"],
        calculation="Solver dispatch aborted before completion.",
        result="Insufficient context for a firm answer",
        interpretation=short,
        assumptions=["Context reflects the user's view at send time."],
        sensitivity_notes="Re-send after the source page has fully loaded.",
        missing_fields=missing,
        partial=True,
        problem_type_id=solver_id,
        computed={"solver_error": err_note, "solver_id": solver_id, "fallback": True},
        conclusion=short,
        confidence_pct=30,
        confidence_label="Low",
        reasons=[f"**{solver_id}** failed: {err_note}"],
        data_would_improve=improve,
        short_answer=short,
        why=improve[0] if improve else "",
    )


def solve_suite_question(
    question: str,
    *,
    source_app: str = "",
    context: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    purpose_override: str = "",
) -> tuple[ProblemRoute, SolverResult]:
    ctx = dict(context or {})
    route = route_suite_question(
        question,
        source_app=source_app,
        context=ctx,
        purpose_override=purpose_override,
    )
    try:
        result = dispatch_solver(route, question, ctx, params)
    except Exception as exc:
        result = _solver_dispatch_error_result(route, question, ctx, exc)
    if result is None:
        raise ValueError("dispatch_solver returned None")
    return route, _finalize_result(route, result)
