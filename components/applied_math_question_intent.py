"""Classify user question intent before selecting a mathematical model."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Six question-intent categories — model is chosen AFTER intent, not before.
INTENT_WHY = "why"
INTENT_WHAT_IF = "what_if"
INTENT_SHOULD_I = "should_i"
INTENT_WHO_IS_BETTER = "who_is_better"
INTENT_WILL_HAPPEN = "will_this_happen"
INTENT_IS_MEANINGFUL = "is_this_meaningful"
INTENT_UNKNOWN = "unknown"

INTENT_LABELS: dict[str, str] = {
    INTENT_WHY: "Why (cause / attribution)",
    INTENT_WHAT_IF: "What if (scenario / sensitivity)",
    INTENT_SHOULD_I: "Should I (decision / threshold)",
    INTENT_WHO_IS_BETTER: "Who is better (present comparison)",
    INTENT_WILL_HAPPEN: "Will this happen (forecast / accumulation)",
    INTENT_IS_MEANINGFUL: "Is this meaningful (signal vs noise)",
}


@dataclass(frozen=True)
class QuestionIntent:
    intent_id: str
    label: str
    confidence: float
    restatement: str
    horizon: str = ""  # e.g. "10 seasons", "next decade"
    focus_stat: str = ""  # e.g. "runs", "rebounds"
    attribution_target: str = ""  # e.g. "VTI"


def _extract_horizon(question: str) -> str:
    low = question.lower()
    m = re.search(r"(?:next|over the next)\s+(\d+)\s+(season|year|game)", low)
    if m:
        return f"{m.group(1)} {m.group(2)}s"
    if "next decade" in low or "10 season" in low or "10 year" in low:
        return "10 seasons"
    return ""


def _extract_focus_stat(question: str) -> str:
    low = question.lower()
    for stat in (
        "runs scored",
        "runs",
        "home runs",
        "hr",
        "rebounds",
        "points",
        "war",
        "ops",
        "drawdown",
    ):
        if stat in low:
            return stat.replace(" scored", "").strip()
    return ""


def _extract_attribution_target(question: str) -> str:
    m = re.search(
        r"\b([A-Z]{2,5})\b",
        question,
    )
    if m and m.group(1) not in ("WHY", "VTI", "ETF", "IRA"):
        return m.group(1)
    for ticker in ("VTI", "VOO", "SPY", "BND", "QQQ", "AAPL", "MSFT", "NVDA"):
        if ticker.lower() in question.lower() or ticker in question:
            return ticker
    return ""


def _is_future_forecast_question(question: str) -> bool:
    low = question.lower()
    future_phrases = (
        "over the next",
        "next season",
        "next year",
        "next decade",
        "continue to be better",
        "will continue",
        "accumulate",
        "surpass",
        "pass ",
        "years based on",
        "seasons based on",
    )
    if any(p in low for p in future_phrases):
        return True
    return bool(re.search(r"next\s+\d+\s+(season|year)", low))


def classify_question_intent(question: str) -> QuestionIntent:
    """Determine what the user is really asking before picking a solver."""
    q = (question or "").strip()
    low = q.lower()
    horizon = _extract_horizon(q)
    focus_stat = _extract_focus_stat(q)
    attribution = _extract_attribution_target(q)

    # Order matters — specific patterns before generic ones.

    if low.startswith("why") or "why did" in low or "why is" in low or "why does" in low:
        if "drawdown" in low or ("risk" in low and ("create" in low or "cause" in low or "expos" in low)):
            return QuestionIntent(
                INTENT_WHY,
                INTENT_LABELS[INTENT_WHY],
                0.88,
                "You are asking **why** a holding or factor contributes to portfolio drawdown risk — not what happens in a stress scenario.",
                attribution_target=attribution or "VTI",
            )
        return QuestionIntent(
            INTENT_WHY,
            INTENT_LABELS[INTENT_WHY],
            0.75,
            "You are asking **why** something happened or creates risk — cause and contribution come first.",
            attribution_target=attribution,
        )

    if (
        "what if" in low
        or "how sensitive" in low
        or "sensitive to" in low
        or ("if recession" in low or "recession risk" in low and "why" not in low)
    ):
        return QuestionIntent(
            INTENT_WHAT_IF,
            INTENT_LABELS[INTENT_WHAT_IF],
            0.85,
            "You are asking **what if** assumptions change — scenario and sensitivity analysis.",
        )

    if (
        low.startswith("should")
        or "should i" in low
        or "worth a round" in low
        or "worth it" in low
        or "rebalance" in low
        or "too early" in low
    ):
        return QuestionIntent(
            INTENT_SHOULD_I,
            INTENT_LABELS[INTENT_SHOULD_I],
            0.82,
            "You are asking **should I** take an action — decision against a threshold or expected value.",
        )

    if any(
        w in low
        for w in (
            "meaningful",
            "significant",
            "real edge",
            "edge meaningful",
            "noisy",
            "signal",
        )
    ):
        return QuestionIntent(
            INTENT_IS_MEANINGFUL,
            INTENT_LABELS[INTENT_IS_MEANINGFUL],
            0.86,
            "You are asking **is this meaningful** — signal vs noise, not a raw comparison.",
        )

    if (
        _is_future_forecast_question(q)
        or low.startswith("will ")
        or "likely to" in low
        or "how many games" in low
    ):
        stat_note = f" for **{focus_stat}**" if focus_stat else ""
        h_note = f" over **{horizon}**" if horizon else ""
        return QuestionIntent(
            INTENT_WILL_HAPPEN,
            INTENT_LABELS[INTENT_WILL_HAPPEN],
            0.84,
            f"You are asking **will this happen**{stat_note}{h_note} — forecast and accumulation, not who is better today.",
            horizon=horizon,
            focus_stat=focus_stat,
        )

    if any(
        w in low
        for w in (
            "who is better",
            "better than",
            " vs ",
            "versus",
            "compare",
            "was .* better",
        )
    ) or re.search(r"\bbetter\b.*\bthan\b", low):
        return QuestionIntent(
            INTENT_WHO_IS_BETTER,
            INTENT_LABELS[INTENT_WHO_IS_BETTER],
            0.78,
            "You are asking **who is better** on attached stats today — present comparison, not a multi-year forecast.",
            focus_stat=focus_stat,
        )

    return QuestionIntent(
        INTENT_UNKNOWN,
        "General quantitative question",
        0.4,
        "We will pick the closest mathematical model once the question shape is clearer.",
        horizon=horizon,
        focus_stat=focus_stat,
    )
