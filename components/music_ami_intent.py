"""Music Coach AMI intent classification for Command Center routing."""

from __future__ import annotations

import re

_PRACTICE_INTENT_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "practice_plan",
        (
            "what should i practice",
            "what should i do",
            "practice next",
            "practice plan",
            "what to practice",
            "this week",
            "how much time",
            "how long should",
            "minutes should",
            "minutes to practice",
            "time should i spend",
            "time on",
            "focus on today",
            "what should i focus",
            "practice this song",
            "practice the song",
            "have to practice",
        ),
    ),
    (
        "chord_transition",
        ("chord change", "chord changes", "chord transition", "transition between", "improve these chords"),
    ),
    ("section_focus", ("chorus", "verse", "bridge", "pre-chorus", "section", "drill", "loop this")),
    ("tempo_key", ("tempo", "bpm", "too fast", "too slow", "what key", "transpose", "play this in")),
    (
        "skill_technique",
        ("technique", "what technique", "learn before", "what should i learn", "skill should"),
    ),
    ("difficulty", ("too difficult", "too hard", "too easy", "my level", "difficult for", "within my level")),
    ("backing_track", ("backing track", "groove", "play along")),
    ("lyrics_cues", ("lyrics", "lyric", "when do i come in", "memorize", "cue")),
)

_SOLVER_INTENTS = frozenset(
    {
        "practice_plan",
        "chord_transition",
        "section_focus",
        "tempo_key",
        "backing_track",
        "skill_technique",
        "difficulty",
    }
)


def minutes_from_question(question: str) -> int | None:
    """Parse session length from free text, e.g. '15 minutes'."""
    m = re.search(r"\b(\d{1,3})\s*minutes?\b", str(question or ""), flags=re.I)
    if not m:
        return None
    try:
        return max(5, min(120, int(m.group(1))))
    except (TypeError, ValueError):
        return None


def detect_music_send_intent(question: str, coach_page: str = "", ctx: dict | None = None) -> str:
    """Classify Music Coach AMI send intent from question text and context."""
    q = str(question or "").strip()
    low = q.lower()
    if not low:
        return "music_general"

    bag = dict(ctx or {})
    hint = str(bag.get("routing_hint") or bag.get("intent") or bag.get("problem_type_hint") or "").strip().lower()
    if hint in _SOLVER_INTENTS:
        return hint

    page = str(
        coach_page or bag.get("coach_page") or bag.get("source_page") or ""
    ).strip().lower()

    if page in {"backing", "karaoke"}:
        if any(p in low for p in ("tempo", "bpm", "too fast", "too slow")):
            return "tempo_key"
        if any(p in low for p in ("loop", "section", "verse", "chorus")):
            return "section_focus"
        if "lyric" in low or "memorize" in low or "cue" in low:
            return "lyrics_cues"
        return "backing_track"
    if page == "custom":
        if "voicing" in low or "progression" in low or "ii" in low or "chord" in low:
            return "chord_transition"
        return "practice_plan"

    if minutes_from_question(q) is not None and any(
        p in low for p in ("practice", "song", "session", "today", "do")
    ):
        return "practice_plan"
    if "what should i do" in low and any(p in low for p in ("practice", "song", "minutes", "session")):
        return "practice_plan"

    for intent, phrases in _PRACTICE_INTENT_RULES:
        if any(p in low for p in phrases):
            return intent

    if any(p in low for p in ("practice", "rehearse", "run-through", "run through")):
        return "practice_plan"

    return "music_general"


def music_intent_to_problem_type_id(intent: str, question: str = "") -> str:
    """Map music intent to stable AMI model / problem_type ids."""
    mapping = {
        "practice_plan": "music_practice_plan",
        "chord_transition": "music_chord_transition",
        "section_focus": "music_section_focus",
        "tempo_key": "music_tempo_key",
        "backing_track": "music_backing_track",
        "skill_technique": "music_skill_technique",
        "difficulty": "music_skill_technique",
    }
    pid = mapping.get(str(intent or "").strip().lower())
    if pid:
        return pid
    low = str(question or "").lower()
    if any(p in low for p in ("practice", "song", "chorus", "verse", "chord", "tempo", "groove")):
        return "music_practice_plan"
    return "music_practice_plan"
