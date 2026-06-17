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
    if is_draft_timing_question(question):
        player = ""
        m = re.search(r"(?:draft|select|take|grab)\s+(.+?)\s+(?:now|as a)", str(question or ""), flags=re.I)
        if m:
            player = m.group(1).strip()
        elif re.search(r"will (.+?) make it back", str(question or ""), flags=re.I):
            m2 = re.search(r"will (.+?) make it back", str(question or ""), flags=re.I)
            player = m2.group(1).strip() if m2 else ""
        if player:
            return f"You're asking whether to draft **{player}** now or wait for a later round."
        return "You're asking whether to draft this player now or wait for a later round."
    if is_draft_market_prediction_question(question) and pos_label:
        return f"You're asking about **{pos_label}** draft-board flow at your current pick."
    if "who should i draft" in low or "draft next" in low:
        return "You're asking who to draft with your next pick on your saved board."
    return ""


def is_player_explanation_question(question: str) -> bool:
    """True when the user asks why a named player is the right draft pick or team fit."""
    low = str(question or "").strip().lower()
    if re.search(r"would .+ help (?:my team|my roster|the team)", low):
        return True
    if re.search(r"would .+ be (?:a )?good (?:fit|add)", low):
        return True
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


_DRAFT_TIMING_PHRASES: tuple[str, ...] = (
    "now or wait",
    "now vs wait",
    "draft now or",
    "draft now or later",
    "now or later",
    "now or a later round",
    "this round or later",
    "wait for a later round",
    "wait another round",
    "wait one more round",
    "wait a round",
    "can i wait",
    "should i wait",
    "grab him now",
    "grab her now",
    "take him now",
    "take her now",
    "before my next pick",
    "make it back to me",
    "make it back",
    "grab him before",
    "grab her before",
    " as a catcher now",
)


def is_draft_timing_question(question: str) -> bool:
    """True when user asks whether to draft a player now vs waiting."""
    low = str(question or "").strip().lower()
    if not low:
        return False
    if is_player_explanation_question(question):
        return False
    if any(phrase in low for phrase in _DRAFT_TIMING_PHRASES):
        return True
    if re.search(
        r"(?:draft|select|take|grab)\s+.+?\s+(?:now or (?:a )?later(?: round)?|this round or later|now or wait)",
        low,
    ):
        return True
    if re.search(r"should i (?:draft|select|take|grab)", low) and any(
        w in low for w in ("now", "wait", "later", "later round", "next round", "a later round")
    ):
        return True
    if re.search(r"(?:draft|select|take|grab) .+ now or (?:wait|later)", low):
        return True
    if re.search(r"will .+ make it back", low):
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
    if is_draft_timing_question(question):
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
        r"\bat\s+(c\b|catcher|catchers|1b|2b|3b|ss|of|sp|rp|closer|shortstop|outfield|first base|second base|third base|starting pitcher|relief pitcher)",
        low,
    )
    if m:
        token = m.group(1).strip()
        if token == "c":
            return "catcher"
        return token
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


def _is_timing_compare_operand(text: str) -> bool:
    low = str(text or "").strip().lower()
    if low in {"later", "now", "wait", "a later round", "later round", "this round", "next round"}:
        return True
    return any(
        phrase in low
        for phrase in (
            "later round",
            "next round",
            "this round",
            "a later",
            "or later",
            "or wait",
        )
    )


def extract_draft_compare_players(question: str) -> tuple[str, str]:
    """Pull two player names from a draft head-to-head question."""
    q = str(question or "").strip()
    if not q:
        return "", ""
    if is_draft_timing_question(q):
        return "", ""
    for pat in _DRAFT_COMPARE_PATTERNS:
        m = re.search(pat, q, flags=re.I)
        if not m:
            continue
        a = q[m.start(1) : m.end(1)].strip().strip("?,").strip()
        b = q[m.start(2) : m.end(2)].strip().strip("?,").strip()
        skip = {"this player", "this pick", "he", "him", "a hitter", "a pitcher", "later", "now", "wait"}
        if _is_timing_compare_operand(a) or _is_timing_compare_operand(b):
            continue
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
            "later",
            "round",
            "catcher",
            "now",
        }
    )
    if any(p.lower() in invalid for p in parts):
        return False
    if any(p.lower() in ("later", "round", "catcher", "now") for p in parts[-2:]):
        return False
    if parts[0].lower() in ("who", "which", "what", "should", "better"):
        return False
    return True


def is_draft_head_to_head_question(question: str) -> bool:
    """True when question compares two named players in a draft decision."""
    low = str(question or "").strip().lower()
    if is_draft_timing_question(question):
        return False
    if any(p in low for p in _DRAFT_TIMING_PHRASES):
        return False
    if re.search(r"now or (?:a )?later(?: round)?", low):
        return False
    if re.search(r"this round or later", low):
        return False
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


def extract_draft_team_query(
    question: str,
    *,
    my_team: str = "",
    team_names: list[str] | None = None,
) -> str:
    """Resolve which fantasy team the user wants reviewed (empty = default/my team)."""
    q = str(question or "").strip()
    low = q.lower()
    names = [str(n).strip() for n in (team_names or []) if str(n).strip()]
    if not low:
        return my_team

    if re.search(r"\bmy (?:team|roster|picks|draft)\b", low) and not re.search(r"\bteam\s+\d", low):
        return my_team

    m = re.search(r"\bteam\s+(\d+|[a-z])\b", low)
    if m:
        token = m.group(1)
        label = f"team {token}".lower()
        for name in names:
            if name.lower() == label or name.lower().endswith(f" {token.lower()}"):
                return name
        if token.isdigit():
            return f"Team {token}"
        return f"Team {token.upper()}"

    m = re.search(
        r"(?:rate|review|grade|how (?:would|do) you rate)\s+(.+?)(?:'s|’s)\s+(?:picks|draft|roster|team)",
        q,
        flags=re.I,
    )
    if m:
        owner = m.group(1).strip()
        for name in names:
            if owner.lower() in name.lower():
                return name
        return owner

    for name in names:
        if name.lower() in low and any(w in low for w in ("picks", "draft", "roster", "team")):
            return name

    return ""


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
    # Weakness/gap phrasing — e.g. "biggest statistical and position weakness in this draft"
    "roster weakness",
    "position weakness",
    "positional weakness",
    "statistical weakness",
    "category weakness",
    "stat weakness",
    "weakest category",
    "weakest position",
    "weakest spot",
    "category gap",
    "stat gap",
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
    # "biggest statistical and position weakness", "biggest category weakness", etc.
    if re.search(r"biggest\b.{0,30}\bweakness", low):
        return True
    if re.search(r"\b(statistical|category|positional?|stat|roster)\b.{0,20}\bweakness", low):
        return True
    return False