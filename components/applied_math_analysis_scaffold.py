"""Analysis scaffold when Applied Intelligence opens from a suite Applied Math question."""

from __future__ import annotations

import re
from typing import Any

_UNIVERSAL_STEPS = [
    "Define the decision or claim in one sentence.",
    "Identify the variables (what you can measure or estimate).",
    "State the assumptions (what must be true for the analysis to apply).",
    "Choose a mathematical method (comparison, trend test, probability model, optimization, etc.).",
    "Explain what result would support one answer vs another.",
    "Give a plain-English interpretation — what would you do differently based on the outcome?",
]


def _question_topics(question: str) -> set[str]:
    low = question.lower()
    topics: set[str] = set()
    if any(w in low for w in ("draft", "round", "pick", "wait")):
        topics.add("draft")
    if any(w in low for w in ("trend", "slope", "declin", "improv", "significant", "meaningful")):
        topics.add("trend")
    if any(w in low for w in ("compare", "better", "vs", "versus", "value")):
        topics.add("compare")
    if any(w in low for w in ("probability", "percent", "odds", "chance", "likely")):
        topics.add("probability")
    if any(w in low for w in ("injur", "sensitivity", "assume")):
        topics.add("sensitivity")
    if any(w in low for w in ("risk", "volatil", "concentration", "diversif")):
        topics.add("risk")
    if any(w in low for w in ("rebalance", "allocat", "hold")):
        topics.add("rebalance")
    if any(w in low for w in ("return", "expect", "health", "score")):
        topics.add("return")
    if any(w in low for w in ("recession", "macro", "rate", "inflation")):
        topics.add("macro")
    return topics


def _baseball_hints(question: str, ctx: dict[str, Any]) -> list[str]:
    topics = _question_topics(question)
    hints: list[str] = []
    players = ctx.get("players") or []
    if isinstance(players, str):
        players = [players]
    player = ctx.get("player") or (players[0] if players else "")
    metrics = ctx.get("metrics") or []
    if isinstance(metrics, str):
        metrics = [metrics]

    if "compare" in topics or ctx.get("workflow") == "Player comparison":
        hints.append(
            "Compare players on the same stat window and playing-time baseline — "
            "rate stats (OBP, OPS) need enough plate appearances to be stable."
        )
    if "trend" in topics or "trend" in str(ctx.get("workflow") or "").lower():
        stat = metrics[0] if metrics else "the selected stat"
        hints.append(
            f"Ask whether {stat} change is larger than normal year-to-year noise — "
            "check sample size (seasons played) and whether a short hot streak drives the slope."
        )
    if "draft" in topics or "draft" in str(ctx.get("page") or "").lower():
        hints.append(
            "Frame draft value as opportunity cost: who you pass in this round vs who might be available next round."
        )
    if player and not hints:
        hints.append(f"Anchor the analysis on {player}'s role, playing time, and league scoring context.")
    if not hints:
        hints.append(
            "Separate counting stats (HR, RBI) from rate stats (BA, OBP) — they answer different fantasy questions."
        )
    return hints[:3]


def _nba_hints(question: str, ctx: dict[str, Any]) -> list[str]:
    topics = _question_topics(question)
    hints: list[str] = []
    team = str(ctx.get("team") or "").strip()
    if "probability" in topics:
        hints.append(
            "Decompose win or series probability: team strength, home court, rest, injuries, and sample size behind the model."
        )
    if "sensitivity" in topics or "injur" in question.lower():
        hints.append(
            "List which players or minutes shifts would move the probability most — "
            "one absence rarely changes odds linearly."
        )
    if team:
        hints.append(f"State what {team}'s recent performance metric the probability claim is based on.")
    if not hints:
        hints.append(
            "Check whether the quoted probability is model-based or market-based — they measure different things."
        )
    return hints[:3]


def _investment_hints(question: str, ctx: dict[str, Any]) -> list[str]:
    topics = _question_topics(question)
    hints: list[str] = []
    if "health" in question.lower() or ctx.get("health_score") is not None:
        hints.append(
            "Identify which health-score components drag down the result: concentration, volatility, macro mismatch, or goal alignment."
        )
    if "risk" in topics:
        hints.append(
            "Separate total volatility from concentration risk — a portfolio can be volatile but diversified, or quiet but concentrated."
        )
    if "rebalance" in topics:
        hints.append(
            "Compare current weights to target weights and estimate transaction cost vs drift risk before recommending trades."
        )
    if "macro" in topics or ctx.get("macro_summary"):
        hints.append(
            "Link macro assumptions (rates, recession odds, inflation) to expected return and correlation — not just headline scores."
        )
    if "return" in topics:
        hints.append(
            "State the return horizon explicitly (your selected date range) — short windows overstate luck; long windows hide regime shifts."
        )
    if not hints:
        hints.append(
            "Express the tradeoff in units: expected return vs volatility vs goal fit, not a single headline number."
        )
    return hints[:3]


def domain_hints(source_app: str, question: str, context: dict[str, Any] | None) -> list[str]:
    ctx = dict(context or {})
    app = str(source_app or "").strip().lower()
    if app == "baseball":
        return _baseball_hints(question, ctx)
    if app == "nba":
        return _nba_hints(question, ctx)
    if app == "investment":
        return _investment_hints(question, ctx)
    return [
        "Name the quantity you want to estimate and the unit it is measured in.",
        "List what evidence would change your mind after the first calculation.",
    ]


def render_applied_math_analysis_scaffold(
    st: Any,
    *,
    question: str,
    source_app: str = "",
    source_page: str = "",
    context: dict[str, Any] | None = None,
) -> None:
    """Show reasoning scaffold for a preloaded suite question."""
    import streamlit as st_module

    st = st or st_module
    ctx = dict(context or {})
    app_label = str(ctx.get("source_app") or source_app or "Suite app").strip()
    page_label = str(ctx.get("page") or source_page or "").strip()

    st.markdown("---")
    st.markdown("### How to analyze this")
    st.markdown(
        "Work through the steps below — you do not need a perfect answer on the first pass. "
        "The goal is a clear quantitative reason for your decision."
    )

    hints = domain_hints(source_app or app_label, question, ctx)
    if hints:
        st.markdown("**Focus for this question**")
        for hint in hints:
            st.markdown(f"- {hint}")

    st.markdown("**Steps**")
    for idx, step in enumerate(_UNIVERSAL_STEPS, start=1):
        st.markdown(f"{idx}. {step}")

    workflow = str(ctx.get("workflow") or "").strip()
    if workflow:
        st.caption(f"Workflow: {workflow}")

    st.markdown("---")
    st.markdown("#### Work the problem")
    st.caption("Use the guided flow below to structure variables, assumptions, and interpretation.")
