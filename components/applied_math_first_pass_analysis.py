"""Rule-based first-pass mathematical analysis for suite Applied Math questions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FirstPassAnalysis:
    problem_type: str
    method: str
    sections: list[tuple[str, str]] = field(default_factory=list)
    answer: str = ""
    assumptions: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    data_needed: list[str] = field(default_factory=list)


def _ctx_list(val: Any) -> list[str]:
    if isinstance(val, list):
        return [str(v).strip() for v in val if str(v).strip()]
    if val:
        return [str(val).strip()]
    return []


def _topics(question: str) -> set[str]:
    low = question.lower()
    out: set[str] = set()
    keys = {
        "trend": ("trend", "slope", "declin", "improv", "significant", "meaningful"),
        "compare": ("compare", "better", " vs ", "versus", "value"),
        "draft": ("draft", "round", "pick", "wait"),
        "probability": ("probability", "percent", "odds", "chance", "likely", "pass"),
        "rebalance": ("rebalance", "allocat", "drift", "weight"),
        "risk": ("risk", "volatil", "concentration", "diversif"),
        "macro": ("recession", "macro", "rate", "inflation"),
    }
    for name, words in keys.items():
        if any(w in low for w in words):
            out.add(name)
    return out


def _baseball_analysis(question: str, ctx: dict[str, Any]) -> FirstPassAnalysis:
    topics = _topics(question)
    player = str(ctx.get("player") or (_ctx_list(ctx.get("players")) or [""])[0]).strip()
    metrics = _ctx_list(ctx.get("metrics")) or ["selected stat"]
    stat = metrics[0]
    workflow = str(ctx.get("workflow") or "").lower()

    if "trend" in topics or "trend" in workflow:
        sections = [
            (
                "Problem type",
                "**Trend significance** — is the observed change in "
                f"{stat} larger than normal year-to-year noise for {player or 'this player'}?",
            ),
            (
                "Mathematical approach",
                "1. Fit a line to season-by-season values (slope = change per year).\n"
                "2. Compare |slope| to typical year-to-year variation (standard deviation of diffs).\n"
                "3. Check R² or rank correlation — high fit + large slope supports a real trend.\n"
                "4. Penalize small sample sizes (< 4 seasons) and playing-time changes.",
            ),
            (
                "Variables",
                f"- **Response:** {stat} per season\n"
                f"- **Time:** season index (recent window from Trends page)\n"
                f"- **Baseline:** league-average year-to-year noise for {stat}\n"
                f"- **Playing time:** games/AB — rate stats need stable opportunity",
            ),
        ]
        trend_data = ctx.get("trend_summary")
        data_needed: list[str] = []
        if isinstance(trend_data, dict) and trend_data:
            direction = trend_data.get("direction", "unknown")
            slope = trend_data.get("slope")
            r2 = trend_data.get("r2")
            parts = [f"Direction from context: **{direction}**."]
            if slope is not None:
                parts.append(f"Estimated slope: **{slope}** per season.")
            if r2 is not None:
                parts.append(f"Fit (R²): **{r2}**.")
            answer = " ".join(parts)
            if direction in ("up", "rising", "improving"):
                answer += (
                    " A rising slope can be meaningful if sample size is adequate and playing time is stable; "
                    "otherwise treat as **monitor, not act** until confirmed."
                )
            elif direction in ("down", "declining"):
                answer += (
                    " Declines often regress — compare slope magnitude to historical volatility before "
                    "downgrading a player in draft or trade decisions."
                )
            else:
                answer += " Compare slope magnitude to typical noise before treating the trend as actionable."
        else:
            answer = (
                f"Without season-by-season {stat} values attached, the first pass is **methodological**: "
                f"compute slope and R² on the Trends chart for {player or 'the player'}, then ask whether "
                f"|slope| exceeds ~1–1.5× the player's own year-to-year standard deviation. "
                "Flat or noisy series → trend is **not meaningful** for decisions."
            )
            data_needed = [
                f"Season-by-season {stat} for {player or 'selected player'}",
                "Games/AB per season (playing-time stability)",
                "Trend window length (years in chart)",
            ]
        return FirstPassAnalysis(
            problem_type="Trend significance (regression / signal vs noise)",
            method="Linear trend + comparison to year-to-year variance",
            sections=sections,
            answer=answer,
            assumptions=[
                "Recent seasons are comparable (role, league environment, health).",
                f"{stat} is measured on similar playing-time opportunity each year.",
            ],
            limitations=[
                "Small samples (2–3 seasons) produce unstable slopes.",
                "Single hot/cold streak within a season is not captured by yearly aggregates.",
            ],
            data_needed=data_needed,
        )

    if "compare" in topics or "comparison" in workflow:
        pa = str(ctx.get("player_a") or "").strip()
        pb = str(ctx.get("player_b") or "").strip()
        pair = f"**{pa}** vs **{pb}**" if pa and pb else "the selected players"
        diff_note = ""
        diffs = ctx.get("comparison_differences")
        if isinstance(diffs, list) and diffs:
            bits = []
            for d in diffs[:2]:
                if not isinstance(d, dict):
                    continue
                name = str(d.get("player") or "").strip()
                slope = d.get("Slope") or d.get("slope")
                if name and slope is not None:
                    bits.append(f"{name}: slope {slope}")
            if bits:
                diff_note = " From context: " + "; ".join(bits) + "."
        stats = _ctx_list(ctx.get("comparison_stats")) or metrics
        return FirstPassAnalysis(
            problem_type="Player value comparison",
            method="Rate-stat comparison with playing-time normalization",
            sections=[
                ("Problem type", f"Compare fantasy/value contribution: {pair} on {', '.join(stats[:3])}."),
                (
                    "Mathematical approach",
                    "Normalize counting stats by PA/AB; compare rate stats (OBP, OPS) directly. "
                    "Weight categories by league scoring format. Use replacement-level baseline, not league average.",
                ),
            ],
            answer=(
                f"First pass: express both players in **value per plate appearance** for your league categories, "
                f"then subtract. The larger gap on scarce categories (SB, HR in some leagues) drives the decision. "
                "If gaps are within one standard error of career rates, call it **too close to call**."
                f"{diff_note}"
            ),
            assumptions=["Same position eligibility matters for roster fit.", "Recent window reflects expected role."],
            limitations=["Does not include injury risk or playing-time projection without extra data."],
            data_needed=[] if (pa and pb) else ["Both player names and comparison stats"],
        )

    return FirstPassAnalysis(
        problem_type="Baseball decision analysis",
        method="Define metric, baseline, and opportunity cost",
        sections=[
            (
                "Mathematical approach",
                "Identify the single quantity the decision hinges on (rate stat, counting total, or draft slot value). "
                "Compare to a baseline (replacement level, next-best alternative, or historical average).",
            ),
        ],
        answer=(
            f"Anchor on {player}'s role and league scoring context. "
            "Quantify the claim in one number, then compare to what you'd give up (next pick, trade piece, roster spot)."
        ),
        assumptions=["League format from context applies to category weights."],
        limitations=["Without attached stat lines, this is a framework — add numbers from the Baseball page."],
    )


def _nba_analysis(question: str, ctx: dict[str, Any]) -> FirstPassAnalysis:
    topics = _topics(question)
    team = str(ctx.get("team") or "").strip()
    low = question.lower()

    if "pass" in low or "rebound" in low or "record" in low:
        players = re.findall(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+", question)
        target = players[0] if players else "the leader"
        challenger = players[1] if len(players) > 1 else str(ctx.get("player") or "the challenger")
        gap_ctx = ctx.get("stat_gap")
        gap_note = ""
        games_rem = ctx.get("games_remaining")
        rate_needed = ctx.get("rate_needed")
        if isinstance(gap_ctx, dict):
            gap_note = str(gap_ctx.get("summary") or "").strip()
            challenger = str(gap_ctx.get("player") or challenger)
            target = str(gap_ctx.get("comparison") or target)
            games_rem = gap_ctx.get("games_remaining") or games_rem
            rate_needed = gap_ctx.get("rate_needed") or rate_needed
        elif gap_ctx:
            gap_note = str(gap_ctx).strip()
        sections = [
            (
                "Problem type",
                "**Counting-record catch-up** — can one player exceed another's cumulative playoff stat "
                "before the series/season ends?",
            ),
            (
                "Mathematical approach",
                "1. **Gap** = leader total − challenger total.\n"
                "2. **Expected remaining** = games left × rebound rate (per game).\n"
                "3. **Uncertainty** — rate variance across games; injury/rest reduces effective games.\n"
                "4. Compare gap to expected remaining + 1–2 standard deviations.",
            ),
        ]
        answer = (
            f"Set **Gap** = {target} total − {challenger} total (playoff stat from context). "
            f"Estimate **E[remaining]** = (games left) × (challenger rate per game). "
            "If Gap > E[remaining] + margin for volatility, **unlikely**; if Gap is small relative to "
            "2–3 games at usual rate, **plausible but not certain**."
        )
        if games_rem is not None:
            answer += f" Games remaining in context: **{games_rem}**."
        if rate_needed is not None:
            answer += f" Rate needed per game: **{rate_needed}**."
        if gap_note:
            answer = f"{gap_note} {answer}"
        return FirstPassAnalysis(
            problem_type="Playoff counting record / catch-up probability",
            method="Gap vs expected remaining production",
            sections=sections,
            answer=answer,
            assumptions=[
                "Minutes and role stay similar to recent playoff usage.",
                "Leader may also accumulate rebounds in remaining games.",
            ],
            limitations=[
                "Does not model matchups or blowouts that reduce fourth-quarter minutes.",
                "Single-rate estimate ignores game-to-game variance without variance data.",
            ],
            data_needed=[] if gap_note else ["Current playoff rebound totals for both players", "Games remaining"],
        )

    if "probability" in topics or ctx.get("win_probability") or ctx.get("series_probability"):
        wp = ctx.get("win_probability") or ctx.get("series_probability") or "quoted probability"
        return FirstPassAnalysis(
            problem_type="Probability reasonableness",
            method="Decompose model probability vs implied base rate",
            sections=[
                (
                    "Mathematical approach",
                    f"Compare **{wp}** to: (a) pre-game Elo/strength model, (b) implied odds if market exists, "
                    "(c) sensitivity — shift margin or star-player minutes ±10% and recompute.",
                ),
            ],
            answer=(
                f"For {team or 'this team'}: if {wp} is far from a simple strength model (>15 pp), "
                "list what must be true (large home court, injury advantage, hot shooting). "
                "If those aren't in context, treat the number as **optimistic** until verified."
            ),
            assumptions=["Probability refers to the same event horizon (single game vs series)."],
            limitations=["Model probabilities are not guarantees; small samples dominate playoff games."],
        )

    return FirstPassAnalysis(
        problem_type="NBA quantitative decision",
        method="Rate × opportunity × uncertainty",
        sections=[("Approach", "Express the claim as expected value per game or per series, then stress-test key inputs.")],
        answer="Decompose into production rate, minutes, and games remaining; compare gap to expected production.",
        assumptions=[f"Team context: {team}" if team else "Team not specified in context."],
        limitations=["Attach box-score or series totals from the NBA page for numeric first pass."],
    )


def _investment_analysis(question: str, ctx: dict[str, Any]) -> FirstPassAnalysis:
    topics = _topics(question)
    holdings = _ctx_list(ctx.get("holdings"))
    health = ctx.get("health_score")
    exp_ret = ctx.get("expected_return")
    vol = ctx.get("volatility")
    pv = ctx.get("portfolio_value")

    if "rebalance" in topics or "rebalance" in question.lower():
        sections = [
            ("Problem type", "**Portfolio rebalance decision** — is drift large enough to justify trades?"),
            (
                "Mathematical approach",
                "1. Compute **weight drift**: |current − target| for each holding.\n"
                "2. Sum **risk contribution** — concentrated positions dominate portfolio variance.\n"
                "3. Compare expected benefit (return/risk alignment) to transaction costs and taxes.\n"
                "4. Use health score components if available.",
            ),
        ]
        parts = []
        if health is not None:
            parts.append(f"Portfolio health score: **{health}** — low scores often flag concentration or goal mismatch.")
        if holdings:
            parts.append(f"Holdings in context: {', '.join(holdings[:6])}.")
        if exp_ret and vol:
            parts.append(f"Expected return **{exp_ret}** vs volatility **{vol}** — check Sharpe-like tradeoff.")
        answer = (
            " ".join(parts)
            + " **First-pass rule:** rebalance when any position exceeds target by >5 pp *or* "
            "top-3 holdings exceed ~60% of risk contribution, unless costs exceed expected risk reduction."
        )
        if not parts:
            answer = (
                "Without weights attached, compare each holding's **current weight − target weight**. "
                "Rebalance when max drift > 5 percentage points or health score flags concentration."
            )
            data_needed_list = ["Current vs target weights", "Health score breakdown"]
        else:
            data_needed_list = []
        return FirstPassAnalysis(
            problem_type="Rebalance decision",
            method="Drift + risk contribution vs cost",
            sections=sections,
            answer=answer,
            assumptions=["Goal and horizon from context match your investment objective."],
            limitations=["Does not replace tax or lot-specific analysis."],
            data_needed=data_needed_list,
        )

    macro = ctx.get("macro_outlook") or ctx.get("macro_summary")
    hist_note = str(ctx.get("context_note_historical") or "").strip()
    fwd_note = str(ctx.get("context_note_forward") or "").strip()
    macro_assumption = str(macro or "Macro assumptions not attached.")
    if fwd_note:
        macro_assumption += f" ({fwd_note})"
    if hist_note and ("macro" in topics or macro):
        macro_assumption = f"{macro_assumption} Historical metrics note: {hist_note}"

    return FirstPassAnalysis(
        problem_type="Portfolio risk / return analysis",
        method="Expected return vs volatility vs goal fit",
        sections=[
            (
                "Approach",
                "Express portfolio quality as return per unit risk, adjusted for concentration and macro regime. "
                + (f"Macro outlook: {macro}" if macro else ""),
            ),
        ],
        answer=(
            f"{'Health score: ' + str(health) + '. ' if health is not None else ''}"
            f"{'Holdings: ' + ', '.join(holdings[:4]) + '. ' if holdings else ''}"
            f"{'Sharpe: ' + str(ctx.get('sharpe_ratio')) + '. ' if ctx.get('sharpe_ratio') else ''}"
            f"{'Max drawdown: ' + str(ctx.get('max_drawdown')) + '. ' if ctx.get('max_drawdown') else ''}"
            "Compare expected return to volatility for your horizon; flag if one sector dominates risk. "
            + (hist_note if hist_note else "")
        ),
        assumptions=[macro_assumption],
        limitations=["Attach weights and return/volatility from Portfolio Health for numeric recommendation."],
    )


def analyze_suite_question(
    question: str,
    *,
    source_app: str = "",
    context: dict[str, Any] | None = None,
) -> FirstPassAnalysis:
    ctx = dict(context or {})
    app = str(source_app or ctx.get("source_app") or "").strip().lower()
    if "baseball" in app:
        return _baseball_analysis(question, ctx)
    if "nba" in app:
        return _nba_analysis(question, ctx)
    if "investment" in app:
        return _investment_analysis(question, ctx)
    return FirstPassAnalysis(
        problem_type="Quantitative decision",
        method="Define variable, baseline, and decision threshold",
        sections=[("Approach", "Translate the question into a measurable quantity and compare to a baseline.")],
        answer="State the claim numerically, list assumptions, then compare outcome to a decision threshold.",
    )


def render_first_pass_analysis(st: Any, analysis: FirstPassAnalysis) -> None:
    st.markdown("### First-pass analysis")
    st.markdown(f"**Problem type:** {analysis.problem_type}")
    st.markdown(f"**Method:** {analysis.method}")
    for heading, body in analysis.sections:
        st.markdown(f"**{heading}**")
        st.markdown(body)
    if analysis.answer:
        st.info(f"**Working answer:** {analysis.answer}")
    if analysis.assumptions:
        st.markdown("**Assumptions**")
        for a in analysis.assumptions:
            st.markdown(f"- {a}")
    if analysis.limitations:
        st.markdown("**Limitations**")
        for lim in analysis.limitations:
            st.markdown(f"- {lim}")
    if analysis.data_needed:
        st.markdown("**Data needed for a numeric answer**")
        for d in analysis.data_needed:
            st.markdown(f"- {d}")
