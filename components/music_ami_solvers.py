"""Music Coach AMI solvers — practice plans, sections, chords, tempo/key."""

from __future__ import annotations

from typing import Any

from components.applied_math_problem_router import (
    MUSIC_BACKING_TRACK,
    MUSIC_CHORD_TRANSITION,
    MUSIC_PRACTICE_LOG_ANALYSIS,
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


def _as_str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _summary_top(summary: dict[str, Any], *keys: str) -> str:
    for key in keys:
        items = _as_str_list(summary.get(key))
        if items:
            return items[0]
        raw = summary.get(key)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return ""


def _summary_list(summary: dict[str, Any], *keys: str, limit: int = 5) -> list[str]:
    for key in keys:
        items = _as_str_list(summary.get(key))
        if items:
            return items[:limit]
    return []


def _session_instruments(sessions: list[dict[str, Any]]) -> list[str]:
    from collections import Counter

    counts = Counter(
        str(row.get("instrument") or "").strip()
        for row in sessions
        if isinstance(row, dict) and str(row.get("instrument") or "").strip()
    )
    return [name for name, _ in counts.most_common(4)]


def _session_notes(sessions: list[dict[str, Any]], *, limit: int = 4) -> list[str]:
    notes: list[str] = []
    for row in sessions:
        if not isinstance(row, dict):
            continue
        for key in ("what_was_hard", "what_went_well", "next_step", "notes"):
            text = str(row.get(key) or "").strip()
            if text and text not in notes:
                notes.append(text)
            if len(notes) >= limit:
                return notes
    return notes


def _practice_log_confidence(count: int) -> tuple[int, str]:
    if count <= 0:
        return 52, "Confidence is low because no logged sessions were included in this handoff."
    if count <= 2:
        return 68, f"Confidence is moderate because only **{count}** session(s) are logged so far."
    if count <= 4:
        return 78, f"Confidence is fair — **{count}** recent sessions give a useful but still limited sample."
    return 88, f"Confidence is solid based on **{count}** logged sessions in view."


def _practice_log_priorities(
    *,
    top_focus: str,
    repeated: list[str],
    suggested: str,
    sessions: list[dict[str, Any]],
    top_song: str,
) -> list[str]:
    priorities: list[str] = []
    seen: set[str] = set()

    def _add(line: str) -> None:
        key = line.lower().strip()
        if not line or key in seen:
            return
        seen.add(key)
        priorities.append(line)

    for challenge in repeated[:2]:
        label = challenge[0].upper() + challenge[1:] if challenge else challenge
        _add(f"Reduce friction on **{label}** — loop the trouble spot slowly before tempo.")
    if top_focus:
        focus_low = top_focus.lower()
        if "tone" in focus_low or "sound" in focus_low:
            _add("Keep **tone and control** as the main quality bar, not speed.")
        elif "chord" in focus_low or "transition" in focus_low:
            _add(f"Isolate **chord transitions** on **{top_song or 'your chart'}** in short loops.")
        elif "rhythm" in focus_low or "timing" in focus_low or "groove" in focus_low:
            _add("Practice with a metronome or backing track until the groove stays steady.")
        elif "scale" in focus_low:
            _add("Connect scale work to one musical section so it transfers to the song.")
        else:
            _add(f"Keep **{top_focus}** as the primary focus for the next block.")
    if suggested and suggested.lower() not in {p.lower() for p in priorities}:
        _add(f"Your logs suggest next emphasis: **{suggested}**.")
    for row in sessions[:3]:
        if not isinstance(row, dict):
            continue
        hard = str(row.get("what_was_hard") or "").strip()
        song = str(row.get("active_song") or row.get("song") or "").strip()
        if hard:
            _add(
                f"On **{song or 'recent material'}**, keep working **{hard}** until it feels predictable."
            )
        if len(priorities) >= 4:
            break
    if top_song and len(priorities) < 4:
        _add(f"Anchor the next session to **{top_song}** — one section at a time, then a run-through.")
    if not priorities:
        priorities.append("Log one more focused session so your coach can spot clearer patterns.")
    return priorities[:4]


def _practice_log_session_plan(
    *,
    plan_mins: int,
    top_song: str,
    top_focus: str,
    repeated: list[str],
    instrument: str,
    last_session: dict[str, Any],
) -> list[str]:
    focus_low = (top_focus or "").lower()
    challenge = repeated[0] if repeated else ""
    section = str(last_session.get("section_practiced") or last_session.get("section_name") or "").strip()
    bpm = last_session.get("bpm")
    weights = {
        "warmup_tone": 5.0,
        "slow_section": 8.0,
        "rhythm_bpm": 7.0,
        "run_through": 7.0,
        "notes_next": 3.0,
    }
    if "tone" in focus_low or "sound" in focus_low:
        weights["warmup_tone"] = 8.0
        weights["slow_section"] = 7.0
    elif "chord" in focus_low or "transition" in focus_low or challenge:
        weights["slow_section"] = 12.0
        weights["rhythm_bpm"] = 5.0
    elif "rhythm" in focus_low or "timing" in focus_low or "groove" in focus_low:
        weights["rhythm_bpm"] = 12.0
        weights["slow_section"] = 6.0
    elif bpm:
        weights["rhythm_bpm"] = 10.0
    blocks = _allocate_minutes(plan_mins, weights)
    inst = instrument or "your instrument"
    warmup_focus = top_focus or "long tones and easy articulation"
    section_target = section if section and section.lower() not in {"unspecified", "whole song", ""} else (
        challenge or top_focus or "the hardest section"
    )
    song_ref = top_song or str(last_session.get("active_song") or last_session.get("song") or "your song").strip()
    bpm_note = f" at **{bpm} BPM**" if bpm else ""
    lines = [f"**Next {plan_mins}-minute session plan**"]
    lines.append(
        f"- **{blocks.get('warmup_tone', 5)} min** warmup / tone on **{inst}** — {warmup_focus}."
    )
    lines.append(
        f"- **{blocks.get('slow_section', 8)} min** slow section work on **{section_target}**"
        + (f" in **{song_ref}**" if song_ref else "")
        + "."
    )
    lines.append(
        f"- **{blocks.get('rhythm_bpm', 7)} min** rhythm / tempo work"
        + (f" on **{top_focus}**" if top_focus else "")
        + bpm_note
        + "."
    )
    lines.append(
        f"- **{blocks.get('run_through', 7)} min** song run-through"
        + (f" of **{song_ref}**" if song_ref else "")
        + " at a comfortable tempo."
    )
    lines.append(
        f"- **{blocks.get('notes_next', 3)} min** notes + next step — write one thing that improved and one to fix."
    )
    return lines


def _practice_log_analysis_result(question: str, ctx: dict[str, Any]) -> Any:
    progress = ctx.get("progress_report") if isinstance(ctx.get("progress_report"), dict) else {}
    if progress:
        try:
            from practice_progress_report_render import format_progress_report_markdown

            markdown = format_progress_report_markdown(progress)
        except Exception:
            markdown = str(progress.get("executive_summary") or "").strip()
        if markdown:
            run_id = str(ctx.get("analysis_run_id") or "").strip()
            return _music_coach_result(
                question=question,
                problem_type="Music Practice Log Analysis",
                math_idea="Cross-source practice synthesis from saved logs, analyses, and tone takes.",
                variables=f"analysis_run_id={run_id}" if run_id else "",
                data_used=["Full progress report from Music Practice Coach handoff."],
                calculation="Render pre-built progress_report sections from practice history synthesis.",
                result=markdown,
                interpretation=markdown,
                assumptions=["Progress report was generated in Music Practice Coach before handoff."],
                sensitivity_notes="",
                problem_type_id=MUSIC_PRACTICE_LOG_ANALYSIS,
                computed={"analysis_run_id": run_id, "progress_report_sections": len(progress)},
                conclusion="Practice history analysis",
                confidence_pct=88,
                short_answer=markdown,
                why=str(progress.get("executive_summary") or markdown.split("\n", 1)[0]),
                model_note="Music practice history progress report",
            )

    summary = ctx.get("practice_log_summary") if isinstance(ctx.get("practice_log_summary"), dict) else {}
    payload = ctx.get("practice_log_ami_payload") if isinstance(ctx.get("practice_log_ami_payload"), dict) else {}
    if not summary and isinstance(payload.get("practice_log_summary"), dict):
        summary = dict(payload.get("practice_log_summary") or {})
    sessions = (
        ctx.get("recent_practice_history")
        or ctx.get("recent_sessions")
        or payload.get("recent_sessions")
        or []
    )
    if not isinstance(sessions, list):
        sessions = []
    sessions = [row for row in sessions if isinstance(row, dict)]

    last_raw = summary.get("last_session_summary")
    last_session = dict(last_raw) if isinstance(last_raw, dict) else (sessions[0] if sessions else {})

    count = int(summary.get("session_count") or len(sessions) or 0)
    total_mins = int(summary.get("total_minutes") or 0)
    top_songs = _summary_list(summary, "most_practiced_songs", "top_song", limit=3)
    if not top_songs:
        top_songs = _as_str_list(summary.get("top_song"))
    top_song = top_songs[0] if top_songs else ""
    top_focuses = _summary_list(summary, "most_common_focus_areas", "top_focus", "suggested_next_focus", limit=3)
    top_focus = top_focuses[0] if top_focuses else _summary_top(summary, "top_focus", "suggested_next_focus")
    repeated = _summary_list(summary, "repeated_challenges", "repeated_challenge", limit=4)
    if not repeated:
        repeated = _as_str_list(summary.get("repeated_challenge"))
    suggested = _summary_top(summary, "suggested_next_focus", "top_focus")
    instruments = _session_instruments(sessions)
    if not instruments and isinstance(last_session, dict):
        inst = str(last_session.get("instrument") or "").strip()
        if inst:
            instruments = [inst]
    session_notes = _session_notes(sessions)
    conf_pct, conf_note = _practice_log_confidence(count)
    plan_mins = 30

    # Opening short answer — coach tone, data-backed.
    if count and top_song:
        focus_phrase = f" with emphasis on **{top_focus}**" if top_focus else ""
        challenge_phrase = ""
        if repeated:
            challenge_phrase = f"; **{repeated[0]}** shows up as a repeated challenge"
        opening = (
            f"Your recent practice history points toward **{top_song}**{focus_phrase}{challenge_phrase}. "
            f"Across **{count}** logged session(s) ({total_mins} min), the logs support a focused next session "
            f"on slow quality work, written-key transitions, and one full run-through."
        )
    elif count:
        opening = (
            f"Your **{count}** logged session(s) ({total_mins} min total) give a starting picture of your practice habits. "
            "Use the priorities and timed plan below for the next session."
        )
    else:
        opening = (
            "No logged sessions were included in this handoff — log a few sessions in Music Practice Coach "
            "so this analysis can summarize patterns and build a concrete plan."
        )

    lines: list[str] = [opening, "", "**Practice patterns**"]
    if count:
        lines.append(f"- **{count}** session(s) in view · **{total_mins}** total minutes logged")
    else:
        lines.append("- No sessions in the current window.")
    if top_songs:
        lines.append(f"- Most practiced song(s): **{', '.join(top_songs)}**")
    if instruments:
        lines.append(f"- Instrument(s): **{', '.join(instruments)}**")
    if top_focuses:
        lines.append(f"- Top focus area(s): **{', '.join(top_focuses)}**")
    if repeated:
        lines.append(f"- Repeated challenge(s): **{'; '.join(repeated[:3])}**")
    if session_notes:
        lines.append("- Recent notes from your log:")
        for note in session_notes[:3]:
            excerpt = note if len(note) <= 160 else note[:157] + "…"
            lines.append(f"  - {excerpt}")

    priorities = _practice_log_priorities(
        top_focus=top_focus,
        repeated=repeated,
        suggested=suggested,
        sessions=sessions,
        top_song=top_song,
    )
    lines.extend(["", "**What to focus on next**"])
    for item in priorities:
        lines.append(f"- {item}")

    lines.extend(
        _practice_log_session_plan(
            plan_mins=plan_mins,
            top_song=top_song,
            top_focus=top_focus,
            repeated=repeated,
            instrument=instruments[0] if instruments else "",
            last_session=last_session,
        )
    )

    if sessions:
        lines.extend(["", "**Recent sessions**"])
        for row in sessions[:6]:
            song = str(row.get("active_song") or row.get("song") or "Untitled")
            mins = row.get("duration_minutes") or row.get("minutes") or 0
            inst = str(row.get("instrument") or "").strip()
            focus = str(row.get("focus_area") or row.get("focus") or "").strip()
            hard = str(row.get("what_was_hard") or "").strip()
            bits = [f"**{song}** ({mins} min)"]
            if inst:
                bits.append(inst)
            if focus:
                bits.append(focus)
            suffix = f" — hard: {hard}" if hard else ""
            lines.append(f"- {' · '.join(bits)}{suffix}")

    lines.extend(["", f"**Confidence / caveat**", f"- {conf_note}"])

    short = "\n".join(lines)
    intent = (
        "You're asking for an analysis of your recent practice history, including patterns, "
        "repeated challenges, and a concrete next-session plan."
    )
    data_used = [
        f"Sessions analyzed: **{count}**",
        f"Total minutes: **{total_mins}**" if total_mins else "",
        f"Top song: **{top_song}**" if top_song else "",
        f"Top focus: **{top_focus}**" if top_focus else "",
        f"Instrument(s): **{', '.join(instruments)}**" if instruments else "",
    ]
    result = _music_coach_result(
        question=question,
        problem_type="Music Practice Log Analysis",
        math_idea="Pattern synthesis over logged sessions — frequency, focus areas, and friction points.",
        variables=f"session_count={count}; total_minutes={total_mins}",
        data_used=[line for line in data_used if line],
        calculation="Aggregate practice_log_summary + recent_practice_history rows into coach priorities and a timed plan.",
        result=short,
        interpretation=short,
        assumptions=["Practice log entries in the handoff reflect your recent logged sessions."],
        sensitivity_notes="Add more logged sessions for stronger pattern detection.",
        problem_type_id=MUSIC_PRACTICE_LOG_ANALYSIS,
        computed={
            "session_count": count,
            "total_minutes": total_mins,
            "plan_minutes": plan_mins,
            "top_song": top_song,
            "top_focus": top_focus,
        },
        conclusion="Practice history analysis",
        confidence_pct=conf_pct,
        short_answer=short,
        why=opening,
        model_note="Structured practice log handoff",
    )
    result.intent_restatement = intent
    result.model_name = "Music Practice Log Analysis"
    return result


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

    if pid == MUSIC_PRACTICE_LOG_ANALYSIS:
        return _practice_log_analysis_result(question, ctx)
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
