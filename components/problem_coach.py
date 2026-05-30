"""Problem coach UI — scoring, experts, challenges, adaptive flow helpers."""

import streamlit as st

from content.consultant import (
    ALTERNATIVE_MODELS,
    BRANCHING_FOLLOWUPS,
    MODEL_BUILDER_FIELDS,
    MODEL_FAILURE_MODES,
    MODEL_TEMPLATES,
    REAL_PROBLEM_REFRAMES,
    REAL_WORLD_EXAMPLES,
    SIMILAR_PROBLEMS,
    assess_confidence,
    critique_model,
    get_critical_pushbacks,
)
from content.problem_coach import (
    CHALLENGE_QUESTIONS,
    EXPERT_PERSPECTIVES,
    PROBLEM_LIBRARY,
    SCORE_DIMENSIONS,
)
from content.problem_solving import ADAPTIVE_QUESTIONS


def render_conversational_adaptive(pattern_id: str, key_prefix: str) -> dict[str, str | list]:
    """Branching discussion — first question drives follow-ups."""
    questions = ADAPTIVE_QUESTIONS.get(pattern_id, ADAPTIVE_QUESTIONS["default"])
    responses: dict[str, str | list] = {}
    branch_answers: dict[str, str] = {}

    st.markdown("##### Let's talk it through")
    st.caption("The coach adapts follow-up questions based on what matters most to you.")

    first = questions[0]
    st.markdown(f"**Coach:** {first['question']}")
    optimizing = st.radio(
        first["options"],
        key=f"{key_prefix}_adaptive_{first['id']}",
        label_visibility="collapsed",
    )
    responses[first["id"]] = optimizing

    branch_key = pattern_id if pattern_id in BRANCHING_FOLLOWUPS else "default"
    followups = BRANCHING_FOLLOWUPS.get(branch_key, {}).get(optimizing, [])
    if followups:
        with st.chat_message("assistant"):
            st.markdown(f"**Coach:** You said **{optimizing}** matters most. A few more questions:")
        for fq in followups:
            st.markdown(f"**{fq['question']}**")
            branch_answers[fq["question"]] = st.radio(
                fq["options"],
                key=f"{key_prefix}_branch_{fq['question'][:40]}",
                label_visibility="collapsed",
            )
    responses["branch_answers"] = branch_answers

    for q in questions[1:]:
        st.markdown(f"**{q['question']}**")
        if q.get("multi"):
            responses[q["id"]] = st.multiselect(
                "Select all that apply",
                q["options"],
                key=f"{key_prefix}_adaptive_{q['id']}",
                label_visibility="collapsed",
            )
        else:
            responses[q["id"]] = st.radio(
                q["options"],
                key=f"{key_prefix}_adaptive_{q['id']}",
                label_visibility="collapsed",
            )

    return responses


def render_real_problem_section(problem: str, pattern_id: str) -> None:
    """Help user distinguish stated vs. underlying vs. measurable problem."""
    reframe = REAL_PROBLEM_REFRAMES.get(pattern_id, REAL_PROBLEM_REFRAMES["default"])

    st.markdown("##### What is the real problem?")
    st.caption("Many people solve the wrong problem. Let's separate layers.")

    with st.container(border=True):
        st.markdown(f"**Stated problem:** *{problem}*")
        st.markdown(f"**Underlying problem:** {reframe['underlying']}")
        st.markdown(f"**Measurable problem:** {reframe['measurable']}")
        st.markdown(f"**Optimization target:** {reframe['optimization_target']}")

    for wrong, right in reframe.get("wrong_problem_examples", []):
        with st.expander(f"Common trap: \"{wrong}\""):
            st.warning(right)

    st.text_area(
        "In your own words — what is the real problem you're trying to solve?",
        key=f"ps_real_{pattern_id}",
        placeholder="Not what you said first — what you'd actually measure and optimize…",
        height=72,
    )


def render_critical_pushback(adaptive: dict, pattern_id: str) -> None:
    """Coach challenges assumptions — does not always agree."""
    st.markdown("##### Coach pushback")
    st.caption("A consultant tests your thinking, not just your confidence.")

    for msg in get_critical_pushbacks(adaptive, pattern_id):
        with st.chat_message("assistant"):
            st.markdown(msg)


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


def render_similar_problems(pattern_id: str) -> None:
    """Show related fields and shared concepts — mathematical ideas transfer."""
    info = SIMILAR_PROBLEMS.get(pattern_id, SIMILAR_PROBLEMS["default"])

    st.markdown("##### Similar problems")
    st.caption("The same mathematical ideas appear in many domains.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Related fields**")
        for field in info["related_fields"]:
            st.markdown(f"- {field}")
    with c2:
        st.markdown("**Shared concepts**")
        for concept in info["shared_concepts"]:
            st.markdown(f"- {concept}")

    st.info(f"**Transfer insight:** {info['transfer_insight']}")


def render_real_world_examples(pattern_id: str) -> None:
    """Concise real-world applications of similar modeling."""
    examples = REAL_WORLD_EXAMPLES.get(pattern_id, REAL_WORLD_EXAMPLES["default"])

    st.markdown("##### Where this has been used in real life")
    st.caption("Practical applications — not theory.")

    for ex in examples:
        with st.container(border=True):
            st.markdown(f"**{ex['name']}**")
            st.caption(ex["use"])


def render_alternative_models(pattern_id: str) -> None:
    """Show different ways to model the same problem."""
    alternatives = ALTERNATIVE_MODELS.get(pattern_id, ALTERNATIVE_MODELS["default"])
    template_types = MODEL_TEMPLATES.get(pattern_id, MODEL_TEMPLATES["default"]).get("model_types", [])

    st.markdown("##### Is there another way to think about this?")
    st.caption("Most problems can be modeled in several valid ways — each with tradeoffs.")

    for alt in alternatives:
        with st.expander(f"**{alt['name']}**", expanded=False):
            st.markdown(f"**When to use:** {alt['when']}")
            st.markdown(f"**Tradeoff:** {alt['tradeoff']}")

    if template_types:
        st.markdown("**Domain model types you could combine:**")
        for mt in template_types:
            st.caption(f"- **{mt['name']}:** {mt['plain']}")


def render_model_critique(
    model: dict[str, str],
    breakdown: dict[int, str],
    adaptive: dict,
    pattern_id: str,
) -> None:
    """Evaluate the user's model with strengths, weaknesses, blind spots, improvements."""
    result = critique_model(model, breakdown, adaptive, pattern_id)

    st.markdown("##### Model critique")
    st.caption("The consultant evaluates your model — and explains why.")

    dim_labels = [
        ("Objective clarity", model.get("objective", "") or breakdown.get(1, "")),
        ("Variable quality", model.get("variables", "") or breakdown.get(2, "")),
        ("Constraints", model.get("constraints", "") or breakdown.get(3, "")),
        ("Data quality", model.get("data_inputs", "") or breakdown.get(5, "")),
        ("Uncertainty", model.get("uncertainty", "") or breakdown.get(4, "")),
        ("Model complexity", model.get("simplified_model", "") or breakdown.get(6, "")),
    ]
    cols = st.columns(3)
    for i, (label, text) in enumerate(dim_labels):
        with cols[i % 3]:
            n = len(text.strip())
            pct = min(100, int(n / 40 * 100)) if n else 0
            st.progress(pct / 100, text=f"{label}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Strengths**")
        for item in result["strengths"]:
            st.markdown(f"- **{item['text']}** — {item['why']}")
        st.markdown("**Blind spots**")
        for item in result["blind_spots"]:
            st.warning(f"**{item['text']}** — {item['why']}")
    with c2:
        st.markdown("**Weaknesses**")
        for item in result["weaknesses"]:
            st.markdown(f"- **{item['text']}** — {item['why']}")
        st.markdown("**Suggested improvements**")
        for item in result["improvements"]:
            st.success(f"**{item['text']}** — {item['why']}")


def render_what_could_break(pattern_id: str, model: dict[str, str]) -> None:
    """Identify failure modes — teach robustness and critical thinking."""
    failure = MODEL_FAILURE_MODES.get(pattern_id, MODEL_FAILURE_MODES["default"])

    st.markdown("##### What could break this model?")
    st.caption("Robust thinking means knowing how your model fails.")

    for cat in failure["categories"]:
        with st.expander(f"**{cat['type']}**", expanded=cat["type"] in ("Bad assumptions", "Missing information")):
            for ex in cat["examples"]:
                st.markdown(f"- {ex}")

    user_risk = st.text_area(
        "What is the single biggest risk to *your* model?",
        key=f"ps_break_{pattern_id}",
        placeholder="Name one assumption that, if wrong, would invalidate your approach…",
        height=68,
    )
    if user_risk.strip():
        with st.chat_message("assistant"):
            st.markdown(
                f"**Consultant:** You flagged: *{user_risk.strip()}* — good. "
                "How would you detect this failing before it costs you? What's your early warning signal?"
            )


def render_confidence_uncertainty(
    model: dict[str, str],
    breakdown: dict[int, str],
    adaptive: dict,
    pattern_id: str,
) -> None:
    """Discuss how confident we should be — uncertainty is part of good thinking."""
    assessment = assess_confidence(model, breakdown, adaptive, pattern_id)

    st.markdown("##### How confident should we be?")
    st.caption("Good mathematical thinking includes honest uncertainty.")

    color = "#059669" if assessment["score"] >= 65 else "#d97706" if assessment["score"] >= 40 else "#dc2626"
    st.markdown(
        f"<div style='text-align:center;padding:0.75rem;border-radius:8px;"
        f"background:#f8fafc;border:1px solid {color};'>"
        f"<div style='font-size:1.5rem;font-weight:600;color:{color};'>{assessment['label']}</div>"
        f"<div style='color:#64748b;font-size:0.85rem;'>Confidence index: {assessment['score']}/90</div></div>",
        unsafe_allow_html=True,
    )

    for f in assessment["factors"]:
        icon = "✓" if f["impact"] == "positive" else "⚠"
        st.markdown(f"{icon} **{f['factor']}** — {f['detail']}")

    st.info(assessment["guidance"])


def render_consultant_personalities(pattern: dict, problem: str, model: dict[str, str]) -> None:
    """View the problem through different consultant personalities."""
    st.markdown("##### Consultant personalities")
    st.caption("Each expert emphasizes different concerns — pick one to hear their take.")

    roles = [e["role"] for e in EXPERT_PERSPECTIVES]
    chosen = st.selectbox("Whose perspective?", roles, key="ps_personality")

    expert = next(e for e in EXPERT_PERSPECTIVES if e["role"] == chosen)
    objective = model.get("objective", "")[:80] or problem[:80]

    with st.chat_message("assistant"):
        st.markdown(
            f"{expert['icon']} **As a {expert['role']}**, my primary concern is "
            f"**{expert.get('primary_concern', expert['lens'])}**.\n\n"
            f"{expert.get('personality', expert['lens'])}\n\n"
            f"On your problem — *{objective}* — I'd ask:"
        )
        for q in expert["questions"]:
            st.markdown(f"- {q}")

    with st.expander("Compare all six personalities", expanded=False):
        render_expert_comparison(pattern, problem)


def render_expert_comparison(pattern: dict, problem: str) -> None:
    """Compare how different experts would approach the same problem."""
    st.markdown("##### How would different experts approach this?")
    snippet = problem[:80] + ("…" if len(problem) > 80 else "")
    st.caption(f"Same problem — six lenses. *{snippet}*")

    roles = [e["role"] for e in EXPERT_PERSPECTIVES]
    selected = st.multiselect(
        "Compare perspectives (pick 2–3 for side-by-side view)",
        roles,
        default=roles[:3],
        key="ps_expert_compare",
    )
    compare = [e for e in EXPERT_PERSPECTIVES if e["role"] in selected] or EXPERT_PERSPECTIVES[:3]

    cols = st.columns(len(compare))
    for col, expert in zip(cols, compare):
        with col:
            with st.container(border=True):
                st.markdown(f"{expert['icon']} **{expert['role']}**")
                st.caption(expert["lens"])
                st.caption(f"*Emphasis:* {expert.get('primary_concern', '')}")
                st.markdown(f"*Approach:* {expert.get('approach', expert['lens'])}")
                for q in expert["questions"][:2]:
                    st.markdown(f"- {q}")
                tools = pattern.get("tools", [])
                if tools:
                    st.caption(f"Tools: {', '.join(tools[:2])}")

    with st.expander("All six expert perspectives", expanded=False):
        render_expert_perspectives(pattern, problem)


def render_expert_perspectives(pattern: dict, problem: str) -> None:
    """Show how different experts would approach this problem."""
    st.markdown("##### How would different experts think?")
    snippet = problem[:80] + ("…" if len(problem) > 80 else "")
    st.caption(f"Same problem — six different lenses. Problem: *{snippet}*")

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


def render_model_builder(pattern_id: str, key_prefix: str) -> dict[str, str]:
    """Build a mathematical model — objective through improvements."""
    template = MODEL_TEMPLATES.get(pattern_id, MODEL_TEMPLATES["default"])
    defaults = template.get("defaults", {})

    st.markdown("##### Build a mathematical model")
    st.caption("Structure your thinking before any formulas — a consultant builds models in plain language first.")

    if template.get("model_types"):
        st.markdown("**Example model types for your domain:**")
        for mt in template["model_types"]:
            with st.container(border=True):
                st.markdown(f"**{mt['name']}** — {mt['purpose']}")
                st.caption(mt["plain"])

    model: dict[str, str] = {}
    for field_id, label, hint in MODEL_BUILDER_FIELDS:
        with st.expander(label, expanded=field_id in ("objective", "variables", "simplified_model")):
            st.caption(hint)
            model[field_id] = st.text_area(
                f"Your {label.lower()}",
                value=defaults.get(field_id, ""),
                key=f"{key_prefix}_model_{field_id}",
                height=68,
                label_visibility="collapsed",
            )
    return model


def render_decision_support(
    problem: str,
    breakdown: dict[int, str],
    model: dict[str, str],
    pattern: dict,
) -> None:
    """Decision support — what to do next based on structured reasoning."""
    st.markdown("##### Decision support")
    st.caption("Problem → Discussion → Modeling → Decision — what would you do next?")

    objective = model.get("objective") or breakdown.get(1, "")
    simplified = model.get("simplified_model") or breakdown.get(6, "")
    decision = breakdown.get(8, "")

    with st.container(border=True):
        st.markdown("**Summary**")
        if objective.strip():
            st.markdown(f"- **Objective:** {objective.strip()}")
        if simplified.strip():
            st.markdown(f"- **Model:** {simplified.strip()}")
        if decision.strip():
            st.markdown(f"- **Decision:** {decision.strip()}")
        else:
            st.markdown("- **Decision:** Define what action you'll take once you've validated your model.")

    st.info(
        f"**Next step:** Test one assumption with data or a small experiment before opening "
        f"**{pattern.get('suggested_lab', 'a lab')}**. A model you haven't tested is still a guess."
    )


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
