"""Mathematical decision analysis for imported problems — adapts by bet format."""

from __future__ import annotations

from typing import Any


def price_to_implied_probability(price_cents: float) -> float:
    """Convert contract price in cents to implied probability (0–1)."""
    if price_cents <= 0:
        return 0.0
    if price_cents >= 100:
        return 1.0
    return price_cents / 100.0


def multiplier_to_implied_probability(multiplier: float) -> float:
    if multiplier <= 0:
        return 0.0
    return 1.0 / multiplier


def _effective_multiplier(fields: dict[str, Any]) -> float:
    try:
        raw = fields.get("multiplier") if fields.get("multiplier") is not None else fields.get("decimal_odds")
        if raw is None:
            return 0.0
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def _market_implied_probability(fields: dict[str, Any], *, fallback_multiplier: float = 0.0) -> float:
    """Prefer displayed market/team %; fall back to multiplier-implied odds."""
    raw = fields.get("implied_probability")
    if raw is not None:
        p = float(raw)
        return p / 100.0 if p > 1 else p
    if fallback_multiplier > 1:
        return multiplier_to_implied_probability(fallback_multiplier)
    return 0.0


def enrich_bet_fields(fields: dict[str, Any]) -> dict[str, Any]:
    """Fill derived bet fields based on detected bet_format."""
    out = dict(fields)
    bet_format = str(out.get("bet_format") or "prediction_market")

    if bet_format == "prediction_market" or (out.get("price") is not None and not out.get("multiplier")):
        price = out.get("price")
        if price is not None:
            try:
                cents = float(price)
                if cents > 1:
                    cost = cents / 100.0
                else:
                    cost = cents
                    cents = cents * 100
                out["cost"] = round(cost, 4)
                out["payout"] = round(1.0, 4)
                out["implied_probability"] = round(price_to_implied_probability(cents), 4)
                out["price"] = cents
                out["bet_format"] = "prediction_market"
            except (TypeError, ValueError):
                pass

    elif bet_format in ("decimal_multiplier", "moneyline_matchup", "spread_total", "percentage_implied"):
        mult = _effective_multiplier(out)
        if mult > 1:
            out["multiplier"] = mult
            out["decimal_odds"] = mult
            if bet_format == "percentage_implied":
                out["bet_format"] = "moneyline_matchup"
            # Keep team/display implied % when present; do not overwrite with 1/multiplier.
            if out.get("implied_probability") is None:
                out["implied_probability"] = round(multiplier_to_implied_probability(mult), 4)
        elif out.get("team_options") and out.get("contract_side"):
            for opt in out.get("team_options") or []:
                if str(opt.get("name", "")).lower() == str(out["contract_side"]).lower():
                    out["implied_probability"] = round(float(opt.get("implied_probability", 0)), 4)
                    if bet_format not in ("decimal_multiplier", "moneyline_matchup", "spread_total"):
                        out["bet_format"] = "percentage_implied"
                    break

    elif bet_format == "percentage_implied":
        if out.get("implied_probability") is None and out.get("team_options") and out.get("contract_side"):
            for opt in out.get("team_options") or []:
                if str(opt.get("name", "")).lower() == str(out["contract_side"]).lower():
                    out["implied_probability"] = round(float(opt.get("implied_probability", 0)), 4)
                    break
        if out.get("implied_probability") is not None:
            p = float(out["implied_probability"])
            if p > 1:
                p /= 100.0
            out["implied_probability"] = round(p, 4)

    return out


def _normalize_user_probability(fields: dict[str, Any], implied: float) -> float:
    p_user = fields.get("user_probability")
    if p_user is None:
        return implied
    p_user = float(p_user)
    if p_user > 1:
        p_user /= 100.0
    return p_user


def analyze_prediction_market_bet(fields: dict[str, Any]) -> dict[str, Any]:
    """Binary prediction market — price in cents, payout $1 per contract."""
    mult = _effective_multiplier(fields)
    bet_format = str(fields.get("bet_format") or "prediction_market")

    # Explicit decimal multiplier always wins for payout math (even with team % displayed).
    if mult > 1.0:
        return analyze_decimal_odds_bet(fields)

    if bet_format in ("decimal_multiplier", "moneyline_matchup", "spread_total"):
        return analyze_decimal_odds_bet(fields)
    if bet_format == "percentage_implied" and not fields.get("price"):
        return analyze_percentage_implied_bet(fields)

    price_cents = float(fields.get("price") or 0)
    cost = float(fields.get("cost") or price_cents / 100.0)
    payout = float(fields.get("payout") or 1.0)
    profit_if_win = max(payout - cost, 0.0)
    loss_if_lose = cost
    implied = float(fields.get("implied_probability") or price_to_implied_probability(price_cents))
    break_even = cost / payout if payout > 0 else 1.0

    stake = float(fields.get("stake") or 100.0)
    contracts = stake / cost if cost > 0 else 0.0
    p_user = _normalize_user_probability(fields, implied)

    ev_per_unit = p_user * profit_if_win - (1 - p_user) * loss_if_lose
    ev_total = ev_per_unit * contracts if contracts else ev_per_unit * (stake / max(cost, 0.01))
    expected_roi = ev_per_unit / cost if cost > 0 else 0.0
    edge = p_user - implied

    return _finalize_analysis(
        fields=fields,
        bet_format="prediction_market",
        implied=implied,
        break_even=break_even,
        profit_if_win=profit_if_win,
        loss_if_lose=loss_if_lose,
        ev_per_unit=ev_per_unit,
        ev_total=ev_total,
        expected_roi=expected_roi,
        edge=edge,
        p_user=p_user,
        stake=stake,
        unit_label="contract",
        units=contracts,
    )


def analyze_decimal_odds_bet(fields: dict[str, Any]) -> dict[str, Any]:
    """Decimal/multiplier odds — profit = stake * (multiplier - 1)."""
    mult = _effective_multiplier(fields)
    if mult <= 1:
        return _unsupported_format(fields, "Multiplier must be greater than 1.0")

    stake = float(fields.get("stake") or 100.0)
    profit_if_win = stake * (mult - 1)
    loss_if_lose = stake
    implied = _market_implied_probability(fields, fallback_multiplier=mult)
    break_even = 1.0 / mult
    p_user = _normalize_user_probability(fields, implied)

    ev_total = p_user * profit_if_win - (1 - p_user) * loss_if_lose
    ev_per_unit = ev_total / stake if stake > 0 else 0.0
    expected_roi = ev_total / stake if stake > 0 else 0.0
    edge = p_user - implied

    return _finalize_analysis(
        fields=fields,
        bet_format=str(fields.get("bet_format") or "decimal_multiplier"),
        implied=implied,
        break_even=break_even,
        profit_if_win=profit_if_win,
        loss_if_lose=loss_if_lose,
        ev_per_unit=ev_per_unit,
        ev_total=ev_total,
        expected_roi=expected_roi,
        edge=edge,
        p_user=p_user,
        stake=stake,
        unit_label="bet",
        units=1.0,
        multiplier=mult,
    )


def analyze_percentage_implied_bet(fields: dict[str, Any]) -> dict[str, Any]:
    """Percentage-implied probability — needs multiplier or user-confirmed payout."""
    implied = fields.get("implied_probability")
    if implied is None:
        return _unsupported_format(fields, "Select a side with a displayed percentage or enter a multiplier.")
    implied = float(implied)
    if implied > 1:
        implied /= 100.0

    mult = fields.get("multiplier") or fields.get("decimal_odds")
    if mult and _effective_multiplier(fields) > 1:
        return analyze_decimal_odds_bet({**fields, "implied_probability": implied})

    stake = float(fields.get("stake") or 100.0)
    profit_if_win = stake * (1 - implied) / implied if implied > 0 else 0.0
    loss_if_lose = stake
    break_even = implied
    p_user = _normalize_user_probability(fields, implied)

    ev_total = p_user * profit_if_win - (1 - p_user) * loss_if_lose
    ev_per_unit = ev_total / stake if stake > 0 else 0.0
    expected_roi = ev_total / stake if stake > 0 else 0.0
    edge = p_user - implied

    result = _finalize_analysis(
        fields=fields,
        bet_format="percentage_implied",
        implied=implied,
        break_even=break_even,
        profit_if_win=profit_if_win,
        loss_if_lose=loss_if_lose,
        ev_per_unit=ev_per_unit,
        ev_total=ev_total,
        expected_roi=expected_roi,
        edge=edge,
        p_user=p_user,
        stake=stake,
        unit_label="bet",
        units=1.0,
    )
    result["assumptions_checked"].append(
        "Payout derived from displayed percentage (fair-odds assumption) — confirm actual multiplier if shown"
    )
    return result


def compute_kelly_fraction(p_win: float, net_odds: float) -> float:
    """Full-Kelly fraction of bankroll to risk (net odds = profit / amount at risk)."""
    if net_odds <= 0:
        return 0.0
    return max(0.0, (p_win * net_odds - (1.0 - p_win)) / net_odds)


def _stake_pct_risk_rating(stake_pct: float) -> str:
    if stake_pct < 0.02:
        return "low"
    if stake_pct < 0.05:
        return "moderate"
    if stake_pct < 0.10:
        return "high"
    return "very_high"


def _risk_rating_label(rating: str) -> str:
    return {
        "low": "Low",
        "moderate": "Moderate",
        "high": "High",
        "very_high": "Very high",
    }.get(rating, rating.replace("_", " ").title())


def compute_stake_sizing(
    *,
    fields: dict[str, Any],
    p_user: float,
    edge: float,
    ev_total: float,
    profit_if_win: float,
    loss_if_lose: float,
    stake: float,
) -> dict[str, Any]:
    """Bankroll-aware Kelly sizing, risk rating, and stake-vs-edge guidance."""
    risk_tol = str(fields.get("risk_tolerance") or "moderate").lower()
    net_odds = profit_if_win / loss_if_lose if loss_if_lose > 0 else 0.0
    kelly_fraction = compute_kelly_fraction(p_user, net_odds)
    half_fraction = kelly_fraction * 0.5
    quarter_fraction = kelly_fraction * 0.25

    bankroll_raw = fields.get("bankroll")
    has_bankroll = bankroll_raw is not None and float(bankroll_raw) > 0
    bankroll = float(bankroll_raw) if has_bankroll else 0.0

    conservative_cap = 0.04
    moderate_cap = 0.10
    aggressive_cap = 0.25

    recommended = {
        "conservative": round(min(quarter_fraction * bankroll, conservative_cap * bankroll), 2) if has_bankroll else None,
        "moderate": round(min(half_fraction * bankroll, moderate_cap * bankroll), 2) if has_bankroll else None,
        "aggressive": round(min(kelly_fraction * bankroll, aggressive_cap * bankroll), 2) if has_bankroll else None,
    }
    recommended_pct = {
        "conservative": (round(min(quarter_fraction, conservative_cap), 4), round(conservative_cap, 4)),
        "moderate": (round(min(half_fraction, moderate_cap), 4), round(moderate_cap, 4)),
        "aggressive": (round(min(kelly_fraction, aggressive_cap), 4), round(aggressive_cap, 4)),
    }

    result: dict[str, Any] = {
        "has_bankroll": has_bankroll,
        "bankroll": round(bankroll, 2) if has_bankroll else None,
        "net_odds": round(net_odds, 4),
        "kelly_fraction": round(kelly_fraction, 4),
        "half_kelly_fraction": round(half_fraction, 4),
        "quarter_kelly_fraction": round(quarter_fraction, 4),
        "kelly_stake": round(kelly_fraction * bankroll, 2) if has_bankroll else None,
        "half_kelly_stake": round(half_fraction * bankroll, 2) if has_bankroll else None,
        "quarter_kelly_stake": round(quarter_fraction * bankroll, 2) if has_bankroll else None,
        "stake_pct_of_bankroll": None,
        "risk_rating": None,
        "risk_rating_label": None,
        "stake_assessment": None,
        "stake_assessment_label": None,
        "stake_warning": False,
        "stake_warning_message": "",
        "recommended_stakes": recommended,
        "recommended_stake_pct": recommended_pct,
        "risk_tolerance": risk_tol,
        "sizing_explanation": "",
    }

    if not has_bankroll:
        result["sizing_explanation"] = (
            f"Estimated edge **{edge:+.1%}**. Full Kelly suggests risking **{kelly_fraction:.1%}** of bankroll "
            f"(half **{half_fraction:.1%}**, quarter **{quarter_fraction:.1%}**). "
            "Enter your **bankroll** to convert these into dollar stakes and compare your proposed bet."
        )
        return result

    stake_pct = stake / bankroll if bankroll > 0 else 0.0
    result["stake_pct_of_bankroll"] = round(stake_pct, 4)
    risk_rating = _stake_pct_risk_rating(stake_pct)
    result["risk_rating"] = risk_rating
    result["risk_rating_label"] = _risk_rating_label(risk_rating)

    tol_stake = recommended.get(risk_tol) or recommended["moderate"]
    tol_lo, tol_hi = recommended_pct.get(risk_tol) or recommended_pct["moderate"]

    if ev_total <= 0 or kelly_fraction <= 0:
        assessment = "no_positive_edge"
        assessment_label = "No positive edge — do not size up"
        warning = stake_pct > 0.02
        warning_msg = (
            f"Your proposed stake is **{stake_pct:.1%}** of bankroll, but this bet is not +EV at your estimate. "
            "Consider passing or revisiting your probability."
        ) if warning else ""
    elif stake_pct > max(kelly_fraction * 1.25, aggressive_cap * 0.8) or stake > (recommended["aggressive"] or 0) * 1.25:
        assessment = "too_large"
        assessment_label = "Too large for estimated edge"
        warning = True
        warning_msg = (
            f"Your stake is **{stake_pct:.1%}** of bankroll, which is aggressive relative to the estimated edge. "
            f"Full Kelly suggests **${result['kelly_stake']:.2f}** ({kelly_fraction:.1%}); "
            f"half Kelly **${result['half_kelly_stake']:.2f}**; quarter Kelly **${result['quarter_kelly_stake']:.2f}**. "
            f"A more conservative stake for your tolerance is closer to **{tol_lo:.0%}–{tol_hi:.0%}** of bankroll "
            f"(about **${recommended['conservative']:.2f}–${recommended['moderate']:.2f}**)."
        )
    elif stake_pct < quarter_fraction * 0.5 and ev_total > 0:
        assessment = "too_small"
        assessment_label = "Conservative vs Kelly — room to size up"
        warning = False
        warning_msg = ""
    else:
        assessment = "reasonable"
        assessment_label = "Reasonable for estimated edge"
        warning = stake_pct > (tol_hi if risk_tol != "aggressive" else aggressive_cap)
        warning_msg = (
            f"Stake is **{stake_pct:.1%}** of bankroll — on the high side for **{risk_tol}** tolerance "
            f"(target roughly **{tol_lo:.0%}–{tol_hi:.0%}**)."
        ) if warning else ""

    result["stake_assessment"] = assessment
    result["stake_assessment_label"] = assessment_label
    result["stake_warning"] = warning
    result["stake_warning_message"] = warning_msg

    result["sizing_explanation"] = _build_sizing_explanation(
        stake=stake,
        stake_pct=stake_pct,
        bankroll=bankroll,
        edge=edge,
        kelly_fraction=kelly_fraction,
        half_fraction=half_fraction,
        quarter_fraction=quarter_fraction,
        kelly_stake=result["kelly_stake"],
        half_kelly_stake=result["half_kelly_stake"],
        quarter_kelly_stake=result["quarter_kelly_stake"],
        recommended=recommended,
        recommended_pct=recommended_pct,
        risk_rating=risk_rating,
        assessment=assessment,
        risk_tol=risk_tol,
        tol_stake=tol_stake,
        tol_lo=tol_lo,
        tol_hi=tol_hi,
    )
    return result


def _build_sizing_explanation(
    *,
    stake: float,
    stake_pct: float,
    bankroll: float,
    edge: float,
    kelly_fraction: float,
    half_fraction: float,
    quarter_fraction: float,
    kelly_stake: float | None,
    half_kelly_stake: float | None,
    quarter_kelly_stake: float | None,
    recommended: dict[str, float | None],
    recommended_pct: dict[str, tuple[float, float]],
    risk_rating: str,
    assessment: str,
    risk_tol: str,
    tol_stake: float | None,
    tol_lo: float,
    tol_hi: float,
) -> str:
    parts = [
        f"Your stake is **{stake_pct:.1%}** of a **${bankroll:,.2f}** bankroll "
        f"({ _risk_rating_label(risk_rating).lower() } risk by size alone). "
        f"Estimated edge vs market: **{edge:+.1%}**.",
        (
            f"Full Kelly suggests **${kelly_stake:,.2f}** ({kelly_fraction:.1%} of bankroll); "
            f"half Kelly **${half_kelly_stake:,.2f}**; quarter Kelly **${quarter_kelly_stake:,.2f}**."
        ),
        (
            f"Suggested stakes — conservative **${recommended['conservative']:,.2f}**, "
            f"moderate **${recommended['moderate']:,.2f}**, aggressive **${recommended['aggressive']:,.2f}**."
        ),
    ]
    if assessment == "too_large":
        parts.append(
            f"At **{stake_pct:.1%}** of bankroll you are betting more than Kelly and your **{risk_tol}** "
            f"comfort zone ({tol_lo:.0%}–{tol_hi:.0%}). A tighter stake would be closer to "
            f"**${recommended['conservative']:,.2f}–${recommended['moderate']:,.2f}**."
        )
    elif assessment == "too_small":
        parts.append(
            f"Your **${stake:,.2f}** stake is well below quarter Kelly "
            f"(**${quarter_kelly_stake:,.2f}**) — fine if you prefer minimal variance; "
            f"you could consider up to **${tol_stake:,.2f}** for **{risk_tol}** tolerance."
        )
    elif assessment == "reasonable":
        parts.append(
            f"Your **${stake:,.2f}** stake is in a reasonable range for the estimated edge "
            f"and **{risk_tol}** tolerance (about **{tol_lo:.0%}–{tol_hi:.0%}** of bankroll)."
        )
    else:
        parts.append("Without a positive edge, bankroll sizing should stay minimal or zero.")
    return " ".join(parts)


def _unsupported_format(fields: dict[str, Any], message: str) -> dict[str, Any]:
    return {
        "verdict": "incomplete",
        "verdict_label": "Need more information",
        "explanation": {"summary": message},
        "disclaimer": "Complete missing fields before analysis.",
        "bet_format": fields.get("bet_format"),
    }


def _finalize_analysis(
    *,
    fields: dict[str, Any],
    bet_format: str,
    implied: float,
    break_even: float,
    profit_if_win: float,
    loss_if_lose: float,
    ev_per_unit: float,
    ev_total: float,
    expected_roi: float,
    edge: float,
    p_user: float,
    stake: float,
    unit_label: str,
    units: float,
    multiplier: float | None = None,
) -> dict[str, Any]:
    net_odds = profit_if_win / loss_if_lose if loss_if_lose > 0 else 0.0
    kelly_fraction = compute_kelly_fraction(p_user, net_odds)

    stake_sizing = compute_stake_sizing(
        fields=fields,
        p_user=p_user,
        edge=edge,
        ev_total=ev_total,
        profit_if_win=profit_if_win,
        loss_if_lose=loss_if_lose,
        stake=stake,
    )
    risk_tol = str(fields.get("risk_tolerance") or "moderate").lower()
    suggested_stake = stake_sizing["recommended_stakes"].get(risk_tol) or stake_sizing["recommended_stakes"].get("moderate")
    tol_pair = stake_sizing["recommended_stake_pct"].get(risk_tol) or stake_sizing["recommended_stake_pct"]["moderate"]
    suggested_fraction = tol_pair[1] if tol_pair else kelly_fraction

    sensitivity = []
    for pct in range(5, 96, 5):
        p = pct / 100.0
        if bet_format == "prediction_market":
            ev_p = p * profit_if_win - (1 - p) * loss_if_lose
            ev_t = ev_p * units if units else ev_p * stake / max(loss_if_lose, 0.01)
        else:
            ev_t = p * profit_if_win - (1 - p) * loss_if_lose
            ev_p = ev_t / stake if stake > 0 else ev_t
        sensitivity.append({
            "user_probability": pct,
            "ev_per_contract": round(ev_p, 4),
            "ev_total": round(ev_t, 2),
            "favorable": ev_t > 0,
        })

    if ev_per_unit > 0.02 or ev_total > 0.02:
        verdict = "mathematically_favorable"
        verdict_label = "Favorable (+EV at your estimate)"
    elif ev_per_unit > 0 or ev_total > 0:
        verdict = "marginal"
        verdict_label = "Marginal (+EV but thin edge)"
    else:
        verdict = "unfavorable"
        verdict_label = "Unfavorable (−EV at your estimate)"

    explanation = _build_explanation(
        fields=fields,
        bet_format=bet_format,
        implied=implied,
        break_even=break_even,
        p_user=p_user,
        ev_per_unit=ev_per_unit,
        ev_total=ev_total,
        edge=edge,
        verdict=verdict,
        multiplier=multiplier,
        stake_sizing=stake_sizing,
    )

    return {
        "bet_format": bet_format,
        "implied_probability": round(implied, 4),
        "break_even_probability": round(break_even, 4),
        "profit_if_win": round(profit_if_win, 4),
        "loss_if_lose": round(loss_if_lose, 4),
        "ev_per_contract": round(ev_per_unit, 4),
        "ev_total": round(ev_total, 2),
        "expected_roi": round(expected_roi, 4),
        "edge": round(edge, 4),
        "contracts": round(units, 2),
        "multiplier": multiplier,
        "kelly_fraction": round(kelly_fraction, 4),
        "suggested_stake_fraction": round(suggested_fraction, 4) if suggested_fraction is not None else None,
        "suggested_stake": suggested_stake,
        "stake_sizing": stake_sizing,
        "downside_risk": round(loss_if_lose * units, 2) if bet_format == "prediction_market" and units else round(loss_if_lose, 2),
        "upside": round(profit_if_win * units, 2) if bet_format == "prediction_market" and units else round(profit_if_win, 2),
        "sensitivity": sensitivity,
        "verdict": verdict,
        "verdict_label": verdict_label,
        "explanation": explanation,
        "assumptions_checked": _assumptions_checklist(fields, bet_format),
        "information_to_verify": _info_to_verify(fields),
        "disclaimer": (
            "Mathematical decision analysis only — not gambling or investment advice. "
            "Outcomes are uncertain; verify market rules and your probability estimate."
        ),
    }


def _build_explanation(
    *,
    fields: dict[str, Any],
    bet_format: str,
    implied: float,
    break_even: float,
    p_user: float,
    ev_per_unit: float,
    ev_total: float,
    edge: float,
    verdict: str,
    multiplier: float | None,
    stake_sizing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    title = str(fields.get("title") or "this market")
    side = str(fields.get("contract_side") or fields.get("selected_option") or "your pick")
    format_note = {
        "prediction_market": "binary prediction market (¢ price → $1 payout)",
        "decimal_multiplier": f"decimal odds ({multiplier:.2f}x)" if multiplier else "decimal/multiplier odds",
        "moneyline_matchup": "matchup / moneyline market",
        "percentage_implied": "percentage-implied probability",
        "spread_total": "spread/total related market",
    }.get(bet_format, bet_format)

    is_good = verdict in ("mathematically_favorable", "marginal")
    good_bet = (
        f"At your **{p_user:.1%}** estimate vs **{implied:.1%}** market-implied ({format_note}), "
        f"expected value is **${ev_total:+.2f}** total."
    )

    worth_it_prob = (
        f"Break-even probability ≈ **{break_even:.1%}**. "
        f"Market implies **{implied:.1%}** — edge **{edge:+.1%}**."
    )

    vol = fields.get("volume")
    vol_note = f" Volume **{vol:,.0f}** is context for liquidity, not directly in EV." if vol else ""

    sizing_note = str((stake_sizing or {}).get("sizing_explanation") or "")

    return {
        "summary": f"**{side}** on *{title}* — {good_bet}{vol_note}",
        "is_good_bet": is_good,
        "worth_it_probability": worth_it_prob,
        "stake_sizing_summary": sizing_note,
        "assumptions": (
            "Key assumptions: your probability estimate is calibrated; "
            "displayed numbers are prices/probabilities as you interpreted them; "
            "settlement rules match your reading."
        ),
        "risks": (
            "Risks: OCR/parse errors; overconfidence; rule ambiguity; "
            "low liquidity; related spread/total markets may correlate."
        ),
    }


def _assumptions_checklist(fields: dict[str, Any], bet_format: str) -> list[str]:
    items = [
        "Your probability estimate reflects available information",
        f"Bet format interpreted as: {bet_format.replace('_', ' ')}",
        "Displayed numbers read correctly from screenshot or paste",
    ]
    if fields.get("rules_summary"):
        items.append(f"Rules: {fields['rules_summary'][:80]}…")
    if fields.get("expiration"):
        items.append(f"Time horizon: {fields['expiration']}")
    if fields.get("volume"):
        items.append(f"Volume/liquidity noted: {fields['volume']:,.0f}")
    if fields.get("spread_total_markets"):
        items.append(f"Spread/total: {fields['spread_total_markets']} related markets detected")
    return items


def _info_to_verify(fields: dict[str, Any]) -> list[str]:
    items = [
        "Are displayed numbers prices, implied probabilities, or payout multipliers?",
        "Which side/team are you actually considering?",
        "Official settlement rules and expiration",
        "Whether spread/total markets affect your thesis",
    ]
    if fields.get("volume"):
        items.append("Can you get filled at this price given the volume?")
    return items


def solve_decision(decision_type: str, fields: dict[str, Any]) -> dict[str, Any]:
    """Run analysis for a decision type."""
    if decision_type == "prediction_market_bet":
        enriched = enrich_bet_fields(fields)
        return analyze_prediction_market_bet(enriched)
    return {
        "verdict": "unsupported",
        "verdict_label": "Not yet implemented",
        "explanation": {"summary": f"Analysis for {decision_type} is planned for a future phase."},
        "disclaimer": "Phase 0 supports prediction market bets only.",
    }
