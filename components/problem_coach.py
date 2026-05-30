"""Problem coach UI — scoring, experts, challenges, adaptive flow helpers."""

import streamlit as st

from content.problem_coach import (
    CHALLENGE_QUESTIONS,
    EXPERT_PERSPECTIVES,
    PROBLEM_LIBRARY,
    SCORE_DIMENSIONS,
)
from content.problem_solving import ADAPTIVE_QUESTIONS


def render_adaptive_questions(pattern_id: str, key_prefix: str) -> dict[str, str | list]:
    """Render pattern-specific follow-up questions; return user responses."""
    questions = ADAPTIVE_QUESTIONS.get(pattern_id, ADAPTIVE_QUESTIONS["default"])
    responses: dict[str, str | list] = {}

    st.markdown("##### Let's narrow this down")
    st.caption("These questions adapt to your problem — answer honestly, there are no wrong choices.")

    for q in questions:
        st.markdown(f"**{q['question']}**")
        if q.get("multi"):
            selected = st.multiselect(
                "Select all that apply",
                q["options"],
                key=f"{key_prefix}_adaptive_{q['id']}",
                label_visibility="collapsed",
            )
            responses[q["id"]] = selected
        else:
            selected = st.radio(
                q["options"],
                key=f"{key_prefix}_adaptive_{q['id']}",
                label_visibility="collapsed",
            )
            responses[q["id"]] = selected

    return responses


def render_challenge_questions(key_prefix: str) -> dict[str, str]:
    """Challenge the user — probing questions they must think through."""
    st.markdown("##### Challenge yourself")
    st.caption("A good coach asks hard questions. Take a moment with each one.")

    answers: dict[str, str] = {}
    for cq in CHALLENGE_QUESTIONS:
        with st.container(border=True):
            st.markdown(f"**{cq['question']}**")
            st.caption(cq["coach"])
            answers[cq["id"]] = st.text_area(
                "Your answer",
                key=f"{key_prefix}_challenge_{cq['id']}",
                height=68,
                label_visibility="collapsed",
            )
    return answers


def render_expert_perspectives(pattern: dict, problem: str) -> None:
    """Show how different experts would approach this problem."""
    st.markdown("##### How would different experts think?")
    snippet = problem[:80] + ("…" if len(problem) > 80 else "")
    st.caption(f"Same problem — five different lenses. Problem: *{snippet}*")

    cols = st.columns(2)
    for i, expert in enumerate(EXPERT_PERSPECTIVES):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"{expert['icon']} **{expert['role']}**")
                st.caption(expert["lens"])
                for q in expert["questions"]:
                    st.markdown(f"- {q}")
                tools = pattern.get("tools", [])
                if tools:
                    st.caption(f"Would likely use: {', '.join(tools[:2])}")


def compute_thinking_score(
    breakdown_answers: dict[int, str],
    adaptive_responses: dict,
    challenge_answers: dict[str, str],
) -> tuple[int, dict[str, int], list[str], list[str]]:
    """Score mathematical thinking clarity 0–100 with per-dimension breakdown."""

    def _text_score(text: str, thresholds: tuple[int, int]) -> int:
        n = len(text.strip())
        if n >= thresholds[1]:
            return 100
        if n >= thresholds[0]:
            return 65
        if n > 0:
            return 35
        return 0

    dim_scores: dict[str, int] = {
        "objective_clarity": _text_score(breakdown_answers.get(1, ""), (15, 40)),
        "variables": _text_score(breakdown_answers.get(2, ""), (20, 50)),
        "constraints": _text_score(breakdown_answers.get(3, ""), (10, 30)),
        "uncertainty": _text_score(breakdown_answers.get(4, ""), (10, 30)),
        "data": _text_score(breakdown_answers.get(5, ""), (10, 30)),
        "model": _text_score(breakdown_answers.get(6, ""), (25, 60)),
    }

    adaptive_filled = sum(1 for v in adaptive_responses.values() if v)
    adaptive_bonus = min(15, adaptive_filled * 5)

    challenge_filled = sum(1 for v in challenge_answers.values() if v.strip())
    challenge_bonus = min(15, challenge_filled * 3)

    base = sum(dim_scores.values()) / len(dim_scores)
    total = min(100, int(base * 0.85 + adaptive_bonus + challenge_bonus))

    strengths: list[str] = []
    weaknesses: list[str] = []

    labels = {key: label for key, label, _ in SCORE_DIMENSIONS}
    for key, score in dim_scores.items():
        label = labels.get(key, key)
        if score >= 65:
            strengths.append(label)
        elif score < 35:
            weaknesses.append(label)

    if challenge_filled >= 3:
        strengths.append("Reflective thinking (challenge questions)")
    elif challenge_filled <= 1:
        weaknesses.append("Self-challenge — push back on your own assumptions")

    if adaptive_filled >= 2:
        strengths.append("Problem framing (adaptive questions)")
    else:
        weaknesses.append("Problem framing — clarify what you're optimizing")

    if not strengths:
        strengths.append("You started — keep refining each dimension")
    if not weaknesses:
        weaknesses.append("Consider stress-testing assumptions further")

    return total, dim_scores, strengths[:4], weaknesses[:4]


def render_thinking_score(
    total: int,
    dim_scores: dict[str, int],
    strengths: list[str],
    weaknesses: list[str],
) -> None:
    """Display Mathematical Thinking Score with breakdown."""
    st.markdown("##### Your Mathematical Thinking Score")

    color = "#059669" if total >= 70 else "#d97706" if total >= 45 else "#dc2626"
    st.markdown(
        f"<div style='text-align:center;padding:1rem;border-radius:12px;"
        f"background:#f8fafc;border:2px solid {color};'>"
        f"<div style='font-size:2.5rem;font-weight:700;color:{color};'>{total}/100</div>"
        f"<div style='color:#64748b;font-size:0.9rem;'>Mathematical Thinking Score</div></div>",
        unsafe_allow_html=True,
    )

    labels = {key: label for key, label, _ in SCORE_DIMENSIONS}
    cols = st.columns(3)
    for i, (key, _, _) in enumerate(SCORE_DIMENSIONS):
        with cols[i % 3]:
            score = dim_scores.get(key, 0)
            st.progress(score / 100, text=f"{labels[key]}: {score}%")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Strengths**")
        for s in strengths:
            st.markdown(f"- {s}")
    with c2:
        st.markdown("**Areas to sharpen**")
        for w in weaknesses:
            st.markdown(f"- {w}")


def render_problem_pipeline(problem: str, thinking: str, model: str, math_link: str) -> None:
    """Problem → Thinking → Model → Math (never formulas first)."""
    st.markdown("##### Your reasoning pipeline")
    st.caption("Problem → Thinking → Model → Math — always in this order.")

    steps = [
        ("Problem", problem, "What you're trying to figure out"),
        ("Thinking", thinking, "How a quantitative thinker frames it"),
        ("Model", model, "A simple structure in plain language"),
        ("Math", math_link, "Why the mathematics matters here — not which formula to memorize"),
    ]
    for title, content, sub in steps:
        with st.container(border=True):
            st.markdown(f"**{title}** — *{sub}*")
            st.markdown(content)


def render_problem_library(on_select) -> None:
    """Real-world example problems demonstrating mathematical thinking."""
    st.markdown("##### Problem library")
    st.caption("See how mathematical thinking works on classic problems — then try your own.")

    categories = sorted({p["category"] for p in PROBLEM_LIBRARY})
    cat = st.selectbox("Category", ["All"] + categories, key="ps_library_cat")

    items = PROBLEM_LIBRARY if cat == "All" else [p for p in PROBLEM_LIBRARY if p["category"] == cat]

    for item in items:
        with st.expander(f"{item['icon']} {item['title']} ({item['category']})", expanded=False):
            st.markdown(f"*{item['problem']}*")
            render_problem_pipeline(
                item["problem"],
                item["thinking"],
                item["model"],
                item["math_link"],
            )
            st.success(f"**Try in app:** {item['lab']}")
            if st.button(f"Use this problem →", key=f"lib_{item['category']}_{item['title']}"):
                on_select(item["problem"])
