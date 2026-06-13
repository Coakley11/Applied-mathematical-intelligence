"""Draft-market prediction question detection (position runs, next off board)."""

from __future__ import annotations

import re

_DRAFT_MARKET_PATTERNS: tuple[str, ...] = (
    r"who is likely to be the next",
    r"who(?:'s| is) likely to be (?:the )?next",
    r"which .+ will be drafted next",
    r"which .+ (?:is|are) likely to (?:be )?(?:drafted|picked|taken)",
    r"next .+ (?:picked|drafted|selected|taken) in this draft",
    r"how long can i wait on",
    r"will .+ make it back to me",
    r"make it back to me",
    r"which position .+ likely to run",
    r"position .+ likely to run",
    r"(?:is|are) a? ?.+ run (?:about to|coming|starting)",
    r"catcher run",
    r"before my next pick",
    r"most likely to be drafted before",
    r"likely to be drafted before my",
)

_POSITION_ALIASES: dict[str, tuple[str, ...]] = {
    "catcher": ("catcher", "catchers", " c", " c "),
    "c": ("catcher", "catchers", " c", " c "),
    "first base": ("first base", "1b", "first baseman"),
    "1b": ("first base", "1b", "first baseman"),
    "second base": ("second base", "2b", "second baseman"),
    "2b": ("second base", "2b", "second baseman"),
    "third base": ("third base", "3b", "third baseman"),
    "3b": ("third base", "3b", "third baseman"),
    "shortstop": ("shortstop", "shortstops", "ss"),
    "ss": ("shortstop", "shortstops", "ss"),
    "outfield": ("outfield", "outfielder", "of"),
    "of": ("outfield", "outfielder", "of"),
    "starting pitcher": ("starting pitcher", "sp", "starter"),
    "sp": ("starting pitcher", "sp", "starter"),
    "relief pitcher": ("relief pitcher", "closer", "rp"),
    "rp": ("relief pitcher", "closer", "rp"),
}


def is_draft_market_prediction_question(question: str) -> bool:
    """True when question is about draft board flow, not player career projection."""
    low = str(question or "").strip().lower()
    if not low:
        return False
    if any(re.search(pat, low) for pat in _DRAFT_MARKET_PATTERNS):
        return True
    if "likely" in low and any(
        w in low for w in ("draft", "picked", "catcher", "position", "run", "round", "pick")
    ):
        return True
    if "next" in low and any(w in low for w in ("catcher", "picked", "drafted", "position")):
        return True
    return False


def extract_draft_position_query(question: str) -> str:
    """Return position token from question (e.g. catcher, C, SP) or empty."""
    low = str(question or "").strip().lower()
    m = re.search(
        r"(?:next|which|a)\s+([a-z][a-z\s-]{1,20}?)(?:\s+(?:picked|drafted|selected|taken|run))",
        low,
    )
    if m:
        token = m.group(1).strip()
        if token and not any(w in token for w in ("likely", "is ", " to ")):
            return token
    if re.search(r"which position", low):
        return ""
    for token in (
        "catcher",
        "catchers",
        "shortstop",
        "shortstops",
        "outfield",
        "outfielder",
        "first base",
        "second base",
        "third base",
        "starting pitcher",
        "relief pitcher",
        "closer",
    ):
        if token in low:
            return token
    if re.search(r"\bc\b", low) and "catcher" in low or re.search(r"\bcatchers?\b", low):
        return "catcher"
    return ""


def position_matches_row(position_label: str, row_position: str) -> bool:
    """Whether a player row matches a position query from the question."""
    query = str(position_label or "").strip().lower()
    row = str(row_position or "").strip().lower()
    if not query or not row:
        return False
    aliases = _POSITION_ALIASES.get(query, (query,))
    if query not in aliases:
        aliases = (*aliases, query)
    for alias in aliases:
        alias = alias.strip()
        if not alias:
            continue
        if alias == row or alias in row or row in alias:
            return True
        if len(alias) <= 3 and re.search(rf"\b{re.escape(alias)}\b", row):
            return True
    return False
