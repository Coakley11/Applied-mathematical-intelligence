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


_DRAFT_MARKET_FLOW_PHRASES: tuple[str, ...] = (
    "likely to be",
    "will be drafted",
    "picked in this draft",
    "run coming",
    "make it back",
    "before my next pick",
    "drafted before",
)


def is_draft_market_flow_question(question: str) -> bool:
    """True when the question is about draft-board timing/flow, not best-available ranking."""
    low = str(question or "").strip().lower()
    return any(phrase in low for phrase in _DRAFT_MARKET_FLOW_PHRASES)


def is_position_best_available_question(question: str) -> bool:
    """True when the user asks who is the best remaining player at a position."""
    low = str(question or "").strip().lower()
    if not low or is_player_explanation_question(question):
        return False
    if is_draft_market_flow_question(question):
        return False
    pos = extract_draft_position_query(question)
    if not pos:
        return False
    if any(
        phrase in low
        for phrase in (
            "best available",
            "next best",
            "top available",
            "top remaining",
            "best catcher",
            "best shortstop",
            "best outfielder",
            "best player available",
            "who is the best",
            "who's the best",
            "which catcher",
            "which shortstop",
        )
    ):
        return True
    if "best" in low and any(w in low for w in ("available", "left", "remaining", "draft")):
        return True
    return False


def draft_question_restatement(question: str) -> str:
    """Human-readable restatement for draft questions (avoids Player A vs Player B)."""
    low = str(question or "").strip().lower()
    pos = extract_draft_position_query(question)
    pos_label = pos.title() if pos else ""
    if is_player_explanation_question(question):
        q = str(question or "").strip()
        m = re.search(r"why is (.+?) (?:the best|worth|a good)", q, flags=re.I)
        player = m.group(1).strip().strip("?").strip() if m else "this player"
        if pos_label:
            return (
                f"You're asking **why {player}** is the best remaining **{pos_label}** "
                "to draft right now."
            )
        return f"You're asking **why {player}** is the best draft choice for you right now."
    if is_position_best_available_question(question):
        return (
            f"You're asking which available **{pos_label}** is the best draft choice right now."
            if pos_label
            else "You're asking which available player is the best draft choice right now."
        )
    if is_draft_head_to_head_question(question):
        a, b = extract_draft_compare_players(question)
        if a and b:
            return f"You're asking whether to draft **{a}** or **{b}** at this pick."
    if is_draft_review_question(question):
        return "You're asking for a draft review — how your picks and roster look so far."
    if is_roster_needs_question(question):
        return "You're asking which positions and roster gaps to target with your next picks."
    if is_draft_market_prediction_question(question) and pos_label:
        return f"You're asking about **{pos_label}** draft-board flow at your current pick."
    if "who should i draft" in low or "draft next" in low:
        return "You're asking who to draft with your next pick on your saved board."
    return ""


def is_player_explanation_question(question: str) -> bool:
    """True when the user asks why a named player is the right draft pick."""
    low = str(question or "").strip().lower()
    if "why is" not in low:
        return False
    if re.search(r"why is .+? (?:the best|worth|a good|the right|the top)", low):
        return True
    if any(
        phrase in low
        for phrase in (
            "good pick",
            "worth drafting",
            "right pick",
            "strong pick",
            "worth it",
            "best catcher",
            "best player",
            "best pick",
        )
    ):
        return True
    return False


def is_draft_market_prediction_question(question: str) -> bool:
    """True when question is about draft board flow, not player career projection."""
    low = str(question or "").strip().lower()
    if not low:
        return False
    if is_player_explanation_question(question):
        return False
    if is_position_best_available_question(question):
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


_DRAFT_COMPARE_PATTERNS: tuple[str, ...] = (
    r"(?:which player (?:would be )?better to draft[,?]?\s*)(.+?)\s+(?:or|vs\.?|versus)\s+(.+?)(?:\?|\s*$)",
    r"(?:should i draft|who should i draft[,?]?\s*)(.+?)\s+(?:or|vs\.?|versus)\s+(.+?)(?:\?|\s*$)",
    r"(?:compare|between)\s+(.+?)\s+(?:and|or|vs\.?|versus)\s+(.+?)(?:\?|\s*$)",
    r"^(.+?)\s+(?:vs\.?|versus)\s+(.+?)(?:\?|\s*$)",
)


def extract_draft_compare_players(question: str) -> tuple[str, str]:
    """Pull two player names from a draft head-to-head question."""
    q = str(question or "").strip()
    if not q:
        return "", ""
    for pat in _DRAFT_COMPARE_PATTERNS:
        m = re.search(pat, q, flags=re.I)
        if not m:
            continue
        a = q[m.start(1) : m.end(1)].strip().strip("?,").strip()
        b = q[m.start(2) : m.end(2)].strip().strip("?,").strip()
        skip = {"this player", "this pick", "he", "him", "a hitter", "a pitcher"}
        if len(a) >= 3 and len(b) >= 3 and a.lower() not in skip and b.lower() not in skip:
            return a, b
    return "", ""


def _looks_like_player_name(name: str) -> bool:
    parts = str(name or "").strip().split()
    if len(parts) < 2:
        return False
    invalid = frozenset(
        {
            "safest",
            "upside",
            "highest",
            "weakest",
            "better",
            "value",
            "risk",
            "floor",
            "ceiling",
            "who",
            "which",
            "what",
            "should",
        }
    )
    if any(p.lower() in invalid for p in parts):
        return False
    if parts[0].lower() in ("who", "which", "what", "should", "better"):
        return False
    return True


def is_draft_head_to_head_question(question: str) -> bool:
    """True when question compares two named players in a draft decision."""
    a, b = extract_draft_compare_players(question)
    return bool(a and b and _looks_like_player_name(a) and _looks_like_player_name(b))


_DRAFT_REVIEW_PHRASES: tuple[str, ...] = (
    "rate my picks",
    "grade my draft",
    "how would you rate my picks",
    "how is my team looking",
    "how is my draft",
    "what do you think of my roster",
    "what do you think of my draft",
    "review my draft",
    "review my picks",
    "picks so far",
    "draft so far",
    "how am i doing",
    "strengths and weaknesses",
    "strengths and weakness",
    "team strengths",
    "team weaknesses",
    "how's my roster",
    "hows my roster",
)


def is_draft_review_question(question: str) -> bool:
    """True when the user wants a holistic draft/roster review, not a single-player value read."""
    low = str(question or "").strip().lower()
    if not low:
        return False
    if is_draft_head_to_head_question(question) or is_player_explanation_question(question):
        return False
    if any(phrase in low for phrase in _DRAFT_REVIEW_PHRASES):
        return True
    if re.search(r"how (?:would you|do you) rate", low) and any(w in low for w in ("pick", "draft", "roster", "team")):
        return True
    if re.search(r"grade (?:my|the) draft", low):
        return True
    return False


_ROSTER_NEEDS_PHRASES: tuple[str, ...] = (
    "roster need",
    "what does my roster",
    "which positions left",
    "positions left",
    "positions still needed",
    "positions should i target",
    "what positions should i",
    "what roster holes",
    "roster holes",
    "what does my team still need",
    "what should i draft next based on my team",
    "remaining priorities",
    "positional priorities",
    "positional gaps",
    "roster gaps",
    "what do i still need",
    "what am i missing",
    "holes do i have",
    "positions needed",
    "still need to pick",
    "needed for me to pick",
)


def is_roster_needs_question(question: str) -> bool:
    """True when the user asks what positions or roster gaps to fill next."""
    low = str(question or "").strip().lower()
    if not low:
        return False
    if is_draft_review_question(question) or is_draft_head_to_head_question(question):
        return False
    if any(phrase in low for phrase in _ROSTER_NEEDS_PHRASES):
        return True
    if re.search(r"which positions?", low) and any(
        w in low for w in ("need", "needed", "left", "target", "pick", "fill", "missing", "hole")
    ):
        return True
    if re.search(r"what (?:position|roster)", low) and any(
        w in low for w in ("need", "still", "left", "target", "hole", "gap", "missing")
    ):
        return True
    return False