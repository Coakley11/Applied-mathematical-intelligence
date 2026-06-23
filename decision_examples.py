"""Quick-start examples for the Real Problem Importer."""

from __future__ import annotations

from typing import Any

EXAMPLE_PREDICTION_MARKET: dict[str, Any] = {
    "id": "prediction_market",
    "title": "Sample prediction market",
    "description": "Kalshi-style yes/no contract with stake and probability estimate.",
    "decision_type": "prediction_market_bet",
    "source_type": "text",
    "text": """Will the Knicks make the 2026 NBA playoffs?
Yes: 42¢
No: 58¢

Side: Yes
Stake: $100
My estimate: 55%
Bankroll: $1,000""",
}

EXAMPLE_POKER_HAND: dict[str, Any] = {
    "id": "poker_hand",
    "title": "Sample poker hand",
    "description": "Texas Hold'em call decision with pot odds and equity estimate.",
    "decision_type": "poker_hand_decision",
    "source_type": "text",
    "text": """Texas Hold'em.

Hero has Ah Kh.
Board: Qh Jh 2c.
Pot: $100.
Villain bets $50.
Amount to call: $50.
Estimated equity: 40%.""",
}

EXAMPLE_JOB_OFFER: dict[str, Any] = {
    "id": "job_offer",
    "title": "Sample job offer",
    "description": "Compare salary, bonus, commute, and hybrid work between two jobs.",
    "decision_type": "job_offer_decision",
    "source_type": "text",
    "text": """Job offer decision

Current job:
- Salary: $95,000
- Commute: 15 minutes one way
- Remote: 0 days per week

New job offer:
- Salary: $115,000
- Signing bonus: $10,000
- Commute: 50 minutes one way
- Hybrid: 2 days remote per week""",
}

EXAMPLE_INVESTMENT: dict[str, Any] = {
    "id": "investment",
    "title": "Sample investment decision",
    "description": "Buy/hold/sell framing (structured investment analysis coming soon).",
    "decision_type": "investment",
    "source_type": "text",
    "coming_soon": True,
    "text": """Investment decision

Ticker: VTI
Current position: $25,000
Considering adding: $5,000
Time horizon: 10 years
Goal: long-term growth with moderate risk tolerance""",
}

IMPORTER_EXAMPLES: list[dict[str, Any]] = [
    EXAMPLE_PREDICTION_MARKET,
    EXAMPLE_POKER_HAND,
    EXAMPLE_JOB_OFFER,
    EXAMPLE_INVESTMENT,
]


def get_example(example_id: str) -> dict[str, Any] | None:
    for ex in IMPORTER_EXAMPLES:
        if ex["id"] == example_id:
            return ex
    return None
