"""Route raw imported input to a decision type."""

from __future__ import annotations

import re
from typing import Any

from decision_registry import ENABLED_DECISION_TYPES, get_decision_label

_KALSHI_MARKERS = re.compile(
    r"\b(kalshi|calci|prediction\s+market|event\s+contract|yes\s+contract|no\s+contract)\b",
    re.I,
)
_PRICE_CENTS = re.compile(r"(?:yes|no)?\s*(\d{1,2})\s*(?:¢|cents?)\b", re.I)
_PRICE_DOLLAR = re.compile(r"\$\s*0?\.(\d{2})\b")
_YES_NO_LINE = re.compile(r"\b(yes|no)\b[:\s]+(\d{1,2})(?:\s*¢|\s*cents?|\s*%|\s*\$)?", re.I)
_INVESTMENT_MARKERS = re.compile(
    r"\b(stock|etf|ticker|shares?|buy\s+stock|sell\s+stock|portfolio)\b",
    re.I,
)
_JOB_MARKERS = re.compile(r"\b(job\s+offer|salary\s+offer|compensation\s+package|remote\s+work)\b", re.I)
_LOAN_MARKERS = re.compile(r"\b(car\s+loan|auto\s+loan|financing|apr|monthly\s+payment)\b", re.I)
_POKER_MARKERS = re.compile(
    r"\b("
    r"texas\s+hold'?em|hold'?em|poker|"
    r"preflop|flop|turn|river|"
    r"hero|villain|opponent|"
    r"pot\s+odds|all[- ]?in|"
    r"equity|fold|call|raise|check|"
    r"board|stack|button|bb|sb"
    r")\b",
    re.I,
)
_POKER_CARDS = re.compile(r"\b[AKQJT2-9][shdc♠♥♦♣]\b", re.I)


def _score_prediction_market(text: str) -> float:
    score = 0.0
    if _KALSHI_MARKERS.search(text):
        score += 0.45
    if _PRICE_CENTS.search(text) or _PRICE_DOLLAR.search(text):
        score += 0.25
    if _YES_NO_LINE.search(text):
        score += 0.2
    if re.search(r"\b(will|chance|probability|odds|bet|wager|market)\b", text, re.I):
        score += 0.1
    if re.search(r"\b(yes|no)\b", text, re.I) and re.search(r"\d{1,2}", text):
        score += 0.1
    return min(score, 1.0)


def _score_investment(text: str) -> float:
    return 0.6 if _INVESTMENT_MARKERS.search(text) else 0.0


def _score_job(text: str) -> float:
    return 0.6 if _JOB_MARKERS.search(text) else 0.0


def _score_loan(text: str) -> float:
    return 0.6 if _LOAN_MARKERS.search(text) else 0.0


def _score_poker_hand(text: str) -> float:
    score = 0.0
    markers = len(_POKER_MARKERS.findall(text))
    if markers:
        score += min(0.25 + markers * 0.08, 0.55)
    if re.search(r"\bhero\b", text, re.I) and _POKER_CARDS.search(text):
        score += 0.2
    if re.search(r"\bboard\b", text, re.I) and _POKER_CARDS.search(text):
        score += 0.15
    if re.search(r"\bpot\b", text, re.I) and re.search(r"\$\s*\d+", text):
        score += 0.15
    if re.search(r"\b(equity|pot\s+odds)\b", text, re.I):
        score += 0.1
    if _KALSHI_MARKERS.search(text) or _YES_NO_LINE.search(text):
        score -= 0.15
    return max(0.0, min(score, 1.0))


_SCORERS: dict[str, Any] = {
    "prediction_market_bet": _score_prediction_market,
    "poker_hand_decision": _score_poker_hand,
    "investment": _score_investment,
    "job_offer": _score_job,
    "loan_financing": _score_loan,
}


def route_imported_problem(
    raw_input: str,
    *,
    source_type: str = "text",
    hint: str = "",
) -> dict[str, Any]:
    """
    Classify imported content into a decision type.

    Returns dict with decision_type, confidence, label, and routing_notes.
    """
    text = str(raw_input or "").strip()
    hint = str(hint or "").strip().lower()

    if hint and hint in ENABLED_DECISION_TYPES:
        return {
            "decision_type": hint,
            "confidence": 1.0,
            "label": get_decision_label(hint),
            "routing_notes": ["User-selected decision type"],
        }

    if not text:
        return {
            "decision_type": "prediction_market_bet",
            "confidence": 0.0,
            "label": get_decision_label("prediction_market_bet"),
            "routing_notes": ["Empty input — defaulting to prediction market (Phase 0)"],
        }

    scores: dict[str, float] = {}
    for dtype, scorer in _SCORERS.items():
        scores[dtype] = float(scorer(text))

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    if best_score < 0.35:
        best_type = "prediction_market_bet"
        best_score = max(best_score, 0.35)
        notes = ["Low confidence — defaulting to prediction market"]
    else:
        notes = [f"Best match: {get_decision_label(best_type)} (score {best_score:.2f})"]

    poker_score = scores.get("poker_hand_decision", 0.0)
    market_score = scores.get("prediction_market_bet", 0.0)
    if poker_score >= 0.45 and poker_score >= market_score + 0.1:
        best_type = "poker_hand_decision"
        best_score = poker_score
        notes = [f"Poker hand signals detected (score {poker_score:.2f})"]

    if source_type == "csv":
        if scores.get("prediction_market_bet", 0) >= 0.2:
            best_type = "prediction_market_bet"
            notes.append("CSV format suggests structured bet data")

    return {
        "decision_type": best_type,
        "confidence": round(best_score, 3),
        "label": get_decision_label(best_type),
        "routing_notes": notes,
        "all_scores": scores,
    }
