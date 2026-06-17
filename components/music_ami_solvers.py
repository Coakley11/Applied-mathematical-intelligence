"""Music Coach AMI solvers — practice plans, sections, chords, tempo/key."""

from __future__ import annotations

from typing import Any

from components.applied_math_problem_router import (
    MUSIC_BACKING_TRACK,
    MUSIC_CHORD_TRANSITION,
    MUSIC_PRACTICE_PLAN,
    MUSIC_SECTION_FOCUS,
    MUSIC_SKILL_TECHNIQUE,
    MUSIC_TEMPO_KEY,
    ProblemRoute,
)
from components.music_ami_intent import detect_music_send_intent, minutes_from_question


def _music_coach_result(**kwargs: Any):
    from components.applied_math_solvers import SolverResult, _coach_result, _confidence_label

    if "confidence_label" not in kwargs and kwargs.get("confidence_pct") is not None:
        kwargs["confidence_label"] = _confidence_label(int(kwargs["confidence_pct"]))
    return _coach_result(**kwargs)


def _ctx_value(ctx: dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        val = ctx.get(key)
        if val is not None and str(val).strip() != "":
            return val
    snap = ctx.get("practice_snapshot")
    if isinstance(snap, dict):
        for key in keys:
            val = snap.get(key)
            if val is not None and str(val).strip() != "":
                return val
    active = ctx.get("active_song")
    if isinstance(active, dict):
        for key in keys:
            val = active.get(key)
            if val is not None and str(val).strip() != "":
                return val
    song = ctx.get("song")
    if isinstance(song, str) and song.strip() and "song" in keys:
        return song.strip()
    return default


def _session_minutes(ctx: dict[str, Any], question: str) -> int:
    parsed = minutes_from_question(question)
    if parsed is not None:
        return parsed
    raw = _ctx_value(ctx, "practice_minutes", "session_minutes", "minutes", default=30)
    try:
        minutes = int(float(raw))
    except (TypeError, ValueError):
        minutes = 30
    return max(15, min(90, minutes))


def _allocate_minutes(total: int, weights: dict[str, float]) -> dict[str, int]:
    if not weights:
        return {}
    norm = sum(max(0.0, float(v)) for v in weights.values()) or 1.0
    raw = {k: total * max(0.0, float(v)) / norm for k, v in weights.items()}
    rounded = {k: int(v) for k, v in raw.items()}
    remainder = total - sum(rounded.values())
    order = sorted(raw.keys(), key=lambda k: raw[k] - rounded[k], reverse=True)
    idx = 0
    while remainder > 0 and order:
        rounded[order[idx % len(order)]] += 1
        remainder -= 1
        idx += 1
    return rounded


def _practice_plan_result(question: str, ctx: dict[str, Any], *, chord_focus: bool):
    minutes = _session_minutes(ctx, question)
    section = str(_ctx_value(ctx, "practice_focus_section", "section_focus_named", "practice_section", default="")).strip()
    instrument = str(_ctx_value(ctx, "instrument", default="your instrument")).strip()
    song = str(_ctx_value(ctx, "question_song", "song", "song_title", default="")).strip()
    if "—" in song:
        song = song.split("—")[0].strip()
    if chord_focus:
        weights = {
            "chord changes": 0.40,
            "rhythm / groove": 0.25,
            "melody or difficult section": 0.20,
            "full run-through": 0.15,
        }
        focus_line = "Prioritize clean chord changes before speed."
    else:
        weights = {
            "technique / drills": 0.35,
            "rhythm / groove": 0.25,
            "melody or difficult section": 0.25,
            "full run-through": 0.15,
        }
        focus_line = "Balance technique, time feel, and musical run-throughs."
    blocks = _allocate_minutes(minutes, weights)
    lines = [f"**{minutes}-minute practice plan**"]
    for label, block_min in blocks.items():
        lines.append(f"- **{block_min} min** {label}")
    if section:
        lines.append(f"- Primary section focus: **{section}**")
    if song:
        lines.append(f"- Song anchor: **{song}**")
    lines.append(f"- On **{instrument}**, {focus_line}")
    short = "\n".join(lines)
    pct = 84
    return _music_coach_result(
        question=question,
        problem_type="Music practice plan",
        math_idea="Time-boxed practice blocks weighted toward your stated focus and session length.",
        variables=f"session_minutes={minutes}",
        data_used=[
            f"Instrument: **{instrument}**" if instrument else "",
            f"Section: **{section}**" if section else "",
            f"Song: **{song}**" if song else "",
        ],
        calculation="Allocate session minutes across technique, groove, repertoire, and run-through.",
        result=short,
        interpretation=short,
        assumptions=[
            "Session length is taken from your question when you name minutes; otherwise defaults to 30.",
            "Adjust blocks ±2 minutes if warmup or cooldown needs more time.",
        ],
        sensitivity_notes="Slow tempos on hard transitions usually beat rushing the full song.",
        problem_type_id=MUSIC_PRACTICE_PLAN,
        computed={"session_minutes": minutes, **blocks},
        conclusion=f"{minutes}-minute practice plan ready",
        confidence_pct=pct,
        short_answer=short,
        why=focus_line,
        model_note="Music Coach practice planner",
    )


def _chord_transition_result(question: str, ctx: dict[str, Any]) -> Any:
    minutes = max(10, min(25, _session_minutes(ctx, question) // 2 or 15))
    bpm = _ctx_value(ctx, "bpm", "practice_bpm", default="")
    instrument = str(_ctx_value(ctx, "instrument", default="your instrument")).strip()
    lines = [
        f"Spend about **{minutes} minutes** on chord-change drills, then plug them into the song.",
        "- Loop chord pairs slowly (metronome 60–70% of target tempo).",
        "- Keep common-finger anchors; lift only fingers that must move.",
        f"- Run 4-bar loops, then 8-bar loops, then add rhythm on **{instrument}**.",
    ]
    if bpm:
        lines.append(f"- Tempo ladder: 70% → 85% → 100% of **{bpm} BPM**.")
    short = "\n".join(lines)
    pct = 82
    return _music_coach_result(
        question=question,
        problem_type="Chord transition coaching",
        math_idea="Isolated transition reps before tempo and groove integration.",
        variables=f"drill_minutes={minutes}",
        data_used=[],
        calculation="Drill pairs → loops → tempo ladder → song context.",
        result=short,
        interpretation=short,
        assumptions=["One chord pair at a time beats rushing the full progression."],
        sensitivity_notes="",
        problem_type_id=MUSIC_CHORD_TRANSITION,
        computed={"drill_minutes": minutes},
        conclusion="Chord transition drill plan",
        confidence_pct=pct,
        short_answer=short,
        model_note="Music Coach chord transitions",
    )


def _section_focus_result(question: str, ctx: dict[str, Any]) -> Any:
    section = str(_ctx_value(ctx, "practice_focus_section", "section_focus_named", default="this section")).strip()
    minutes = _session_minutes(ctx, question)
    drill = max(8, minutes // 3)
    short = (
        f"For **{section}**: loop **{drill} min** slow reps, **{drill} min** rhythm-focused reps, "
        f"then **{max(5, minutes - 2 * drill)} min** connecting into the full song."
    )
    pct = 80
    return _music_coach_result(
        question=question,
        problem_type="Section focus coaching",
        math_idea="Section loops with escalating tempo and song context.",
        variables=f"section={section}",
        data_used=[f"Section: **{section}**"],
        calculation="Slow loop → rhythm loop → connect to full song.",
        result=short,
        interpretation=short,
        assumptions=[],
        sensitivity_notes="",
        problem_type_id=MUSIC_SECTION_FOCUS,
        computed={"section": section, "loop_minutes": drill},
        conclusion=f"Section plan for {section}",
        confidence_pct=pct,
        short_answer=short,
        model_note="Music Coach section focus",
    )


def _tempo_key_result(question: str, ctx: dict[str, Any]) -> Any:
    bpm = str(_ctx_value(ctx, "bpm", "practice_bpm", default="")).strip()
    display_key = str(_ctx_value(ctx, "display_key", "key", default="")).strip()
    level = str(_ctx_value(ctx, "level", default="Intermediate")).strip()
    tempo_line = (
        f"Try **{int(float(bpm) * 0.75)} BPM** as a learning tempo (about 75% of {bpm})."
        if bpm
        else "Start 15–25% below performance tempo until transitions stay clean."
    )
    key_line = f"Written key **{display_key}** is fine for practice." if display_key else "Match the chart key you are reading."
    short = f"{tempo_line}\n{key_line}\nFor **{level}** players, add +5 BPM only after two clean passes."
    pct = 78
    return _music_coach_result(
        question=question,
        problem_type="Tempo & key coaching",
        math_idea="Tempo ladder with key context from the active chart.",
        variables="suggested_bpm_pct=75",
        data_used=[],
        calculation="Learning tempo → clean reps → gradual BPM increases.",
        result=short,
        interpretation=short,
        assumptions=[],
        sensitivity_notes="",
        problem_type_id=MUSIC_TEMPO_KEY,
        computed={"suggested_bpm_pct": 75},
        conclusion="Tempo & key guidance",
        confidence_pct=pct,
        short_answer=short,
        model_note="Music Coach tempo & key",
    )


def _skill_technique_result(question: str, ctx: dict[str, Any]) -> Any:
    level = str(_ctx_value(ctx, "level", default="your level")).strip()
    instrument = str(_ctx_value(ctx, "instrument", default="your instrument")).strip()
    short = (
        f"At **{level}** on **{instrument}**, build technique before full-tempo performance: "
        "slow reps with a metronome, short bursts at target tempo, then rest. "
        "If the song feels too hard, reduce tempo 20% and isolate the hardest bar."
    )
    pct = 76
    return _music_coach_result(
        question=question,
        problem_type="Technique & readiness coaching",
        math_idea="Readiness check with technique-first progression.",
        variables="",
        data_used=[],
        calculation="Technique → tempo bursts → song integration.",
        result=short,
        interpretation=short,
        assumptions=[],
        sensitivity_notes="",
        problem_type_id=MUSIC_SKILL_TECHNIQUE,
        computed={},
        conclusion="Technique roadmap",
        confidence_pct=pct,
        short_answer=short,
        model_note="Music Coach technique roadmap",
    )


def _backing_track_result(question: str, ctx: dict[str, Any]) -> Any:
    groove = str(_ctx_value(ctx, "groove", "practice_groove_style", "backing_groove_style", default="the groove")).strip()
    section = str(_ctx_value(ctx, "practice_focus_section", default="the chorus")).strip()
    short = (
        f"Loop **{section}** with **{groove}** at a comfortable tempo. "
        "Practice chord changes first without the backing, then add the track for time feel."
    )
    pct = 77
    return _music_coach_result(
        question=question,
        problem_type="Backing track coaching",
        math_idea="Backing-track practice order: technique → groove integration.",
        variables="",
        data_used=[],
        calculation="Dry practice → backing track integration.",
        result=short,
        interpretation=short,
        assumptions=[],
        sensitivity_notes="",
        problem_type_id=MUSIC_BACKING_TRACK,
        computed={},
        conclusion="Backing track practice strategy",
        confidence_pct=pct,
        short_answer=short,
        model_note="Music Coach backing track",
    )


def solve_music_question(
    route: ProblemRoute,
    question: str,
    ctx: dict[str, Any],
) -> Any:
    """Dispatch music coach solver by routed problem_type_id."""
    pid = route.problem_type_id
    intent = detect_music_send_intent(
        question,
        str(ctx.get("coach_page") or ctx.get("source_page") or ""),
        ctx,
    )
    low = question.lower()
    chord_focus = intent in {"practice_plan", "chord_transition"} or any(
        p in low for p in ("chord change", "chord changes", "chord transition", "transitions")
    )

    if pid == MUSIC_PRACTICE_PLAN:
        return _practice_plan_result(question, ctx, chord_focus=chord_focus)
    if pid == MUSIC_CHORD_TRANSITION:
        return _chord_transition_result(question, ctx)
    if pid == MUSIC_SECTION_FOCUS:
        return _section_focus_result(question, ctx)
    if pid == MUSIC_TEMPO_KEY:
        return _tempo_key_result(question, ctx)
    if pid == MUSIC_SKILL_TECHNIQUE:
        return _skill_technique_result(question, ctx)
    if pid == MUSIC_BACKING_TRACK:
        return _backing_track_result(question, ctx)
    return _practice_plan_result(question, ctx, chord_focus=chord_focus)
