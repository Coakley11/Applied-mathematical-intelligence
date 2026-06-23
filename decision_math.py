"""Mathematical decision analysis for imported problems."""

from __future__ import annotations

from typing import Any


def price_to_implied_probability(price_cents: float) -> float:
    """Convert contract price in cents to implied probability (0–1)."""
    if price_cents <= 0:
        return 0.0
    if price_cents >= 100:
        return 1.0
    return price_cents / 100.0


def enrich_bet_fields(fields: dict[str, Any]) -> dict[str, Any]:
    """Fill derived bet fields: cost, payout, implied_probability."""
    out = dict(fields)
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
        except (TypeError, ValueError):
            pass
    return out


def analyze_prediction_market_bet(fields: dict[str, Any]) -> dict[str, Any]:
    """
    Compute EV, break-even, ROI, sensitivity, and narrative summary.

    Not gambling advice — mathematical decision analysis only.
    """
    price_cents = float(fields.get("price") or 0)
    cost = float(fields.get("cost") or price_cents / 100.0)
    payout = float(fields.get("payout") or 1.0)
    profit_if_win = max(payout - cost, 0.0)
    loss_if_lose = cost
    implied = float(fields.get("implied_probability") or price_to_implied_probability(price_cents))
    break_even = cost / payout if payout > 0 else 1.0

    stake = float(fields.get("stake") or 100.0)
    contracts = stake / cost if cost > 0 else 0.0
    p_user = fields.get("user_probability")
    if p_user is None:
        p_user = implied
    p_user = float(p_user)
    if p_user > 1:
        p_user /= 100.0

    ev_per_contract = p_user * profit_if_win - (1 - p_user) * loss_if_lose
    ev_total = ev_per_contract * contracts if contracts else ev_per_contract * (stake / max(cost, 0.01))
    expected_roi = ev_per_contract / cost if cost > 0 else 0.0
    edge = p_user - implied

    # Kelly (conservative cap at 25% of bankroll fraction)
    if profit_if_win > 0:
        kelly_raw = (p_user * profit_if_win - (1 - p_user) * loss_if_lose) / profit_if_win
        kelly_fraction = max(0.0, min(kelly_raw, 0.25))
    else:
        kelly_fraction = 0.0

    risk_tol = str(fields.get("risk_tolerance") or "moderate").lower()
    sizing_cap = {"conservative": 0.05, "moderate": 0.10, "aggressive": 0.25}.get(risk_tol, 0.10)
    suggested_fraction = min(kelly_fraction, sizing_cap)
    suggested_stake = round(suggested_fraction * stake * 10, 2) if stake else 0.0

    sensitivity = []
    for pct in range(5, 96, 5):
        p = pct / 100.0
        ev_p = p * profit_if_win - (1 - p) * loss_if_lose
        sensitivity.append({
            "user_probability": pct,
            "ev_per_contract": round(ev_p, 4),
            "ev_total": round(ev_p * contracts, 2) if contracts else round(ev_p * stake / max(cost, 0.01), 2),
            "favorable": ev_p > 0,
        })

    if ev_per_contract > 0.02:
        verdict = "mathematically_favorable"
        verdict_label = "Favorable (+EV at your estimate)"
    elif ev_per_contract > 0:
        verdict = "marginal"
        verdict_label = "Marginal (+EV but thin edge)"
    else:
        verdict = "unfavorable"
        verdict_label = "Unfavorable (−EV at your estimate)"

    explanation = _build_explanation(
        fields=fields,
        implied=implied,
        break_even=break_even,
        p_user=p_user,
        ev_per_contract=ev_per_contract,
        edge=edge,
        verdict=verdict,
    )

    return {
        "implied_probability": round(implied, 4),
        "break_even_probability": round(break_even, 4),
        "profit_if_win": round(profit_if_win, 4),
        "loss_if_lose": round(loss_if_lose, 4),
        "ev_per_contract": round(ev_per_contract, 4),
        "ev_total": round(ev_total, 2),
        "expected_roi": round(expected_roi, 4),
        "edge": round(edge, 4),
        "contracts": round(contracts, 2),
        "kelly_fraction": round(kelly_fraction, 4),
        "suggested_stake_fraction": round(suggested_fraction, 4),
        "suggested_stake": suggested_stake,
        "downside_risk": round(loss_if_lose * contracts, 2) if contracts else round(stake, 2),
        "upside": round(profit_if_win * contracts, 2) if contracts else round(profit_if_win * stake / max(cost, 0.01), 2),
        "sensitivity": sensitivity,
        "verdict": verdict,
        "verdict_label": verdict_label,
        "explanation": explanation,
        "assumptions_checked": _assumptions_checklist(fields),
        "information_to_verify": _info_to_verify(fields),
        "disclaimer": (
            "Mathematical decision analysis only — not gambling or investment advice. "
            "Outcomes are uncertain; verify market rules and your probability estimate."
        ),
    }


def _build_explanation(
    *,
    fields: dict[str, Any],
    implied: float,
    break_even: float,
    p_user: float,
    ev_per_contract: float,
    edge: float,
    verdict: str,
) -> dict[str, Any]:
    title = str(fields.get("title") or "this market")
    side = str(fields.get("contract_side") or "Yes")

    is_good = verdict in ("mathematically_favorable", "marginal")
    good_bet = (
        f"At your **{p_user:.1%}** estimate vs **{implied:.1%}** market-implied, "
        f"the math shows **{'positive' if ev_per_contract > 0 else 'negative'}** expected value "
        f"(**${ev_per_contract:+.3f}** per contract)."
    )

    worth_it_prob = (
        f"You need roughly **{break_even:.1%}** true probability to break even. "
        f"The market implies **{implied:.1%}** — your edge is **{edge:+.1%}**."
    )

    assumptions = (
        "Key assumptions: your probability estimate is well-calibrated; "
        "settlement rules match your reading of the market; "
        "price and fees are as shown."
    )

    risks = (
        "Risks: overconfidence in your probability; rule ambiguity at settlement; "
        "capital locked until expiration; adverse selection (market may know more)."
    )

    return {
        "summary": f"**{side}** on *{title}* — {good_bet}",
        "is_good_bet": is_good,
        "worth_it_probability": worth_it_prob,
        "assumptions": assumptions,
        "risks": risks,
    }


def _assumptions_checklist(fields: dict[str, Any]) -> list[str]:
    items = [
        "Your probability estimate reflects all available information",
        "Contract settles as you interpret the market rules",
        "No material fees beyond the quoted price",
    ]
    if fields.get("rules_summary"):
        items.append(f"Rules summary considered: {fields['rules_summary'][:80]}…")
    if fields.get("expiration"):
        items.append(f"Time horizon: expires {fields['expiration']}")
    return items


def _info_to_verify(fields: dict[str, Any]) -> list[str]:
    return [
        "Official market rules and settlement criteria",
        "Recent news affecting the outcome",
        "Liquidity and whether you can exit early",
        "Whether your probability is based on data or intuition",
        "Correlation with other bets in your portfolio",
    ]


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
