"""Quantitative analyst UI — 7-step area flow."""

import streamlit as st

from components.nav import navigate_to
from content.analyst_briefs import ANALYST_BRIEFS, get_analyst_brief


def render_quantitative_flow(
    problem: str,
    pattern: dict,
    pattern_id: str,
    area: dict,
    key_prefix: str,
) -> None:
    """Full area flow: framing → variables → abstract → math → solve → deeper."""
    brief = get_analyst_brief(pattern_id)

    with st.container(border=True):
        st.markdown(f"**Your question:** *{problem}*")
        st.caption(f"Area: {area['icon']} {area['name']}")

    # 2 — Mathematical form
    st.markdown("#### 1. What is being asked?")
    st.markdown(brief.get("mathematical_form", brief["what_is_asked"]))
    st.caption(brief["what_is_asked"])

    # 3 — Variables
    st.markdown("#### 2. Variables that matter")
    for v in brief.get("variables_list", []):
        st.markdown(f"- {v}")
    st.caption(brief["variables"])

    # 4 — Abstract thinking
    st.markdown("#### 3. How to think about it abstractly")
    abs_t = brief.get("abstract_thinking", {})
    if abs_t:
        st.markdown(f"**Kind of problem:** {abs_t.get('problem_kind', '')}")
        st.markdown(f"**Structure:** {abs_t.get('structure', '')}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Comparing:** {abs_t.get('comparing', '')}")
            st.markdown(f"**What matters:** {abs_t.get('matters', '')}")
        with c2:
            st.markdown(f"**Assumptions:** {abs_t.get('assumptions', '')}")

    # 5 — Math that applies
    st.markdown("#### 4. Math that applies (in context)")
    st.markdown(f"**Tools:** {brief['math_useful']}")
    math_behind = brief.get("math_behind", {})
    for topic, explanation in math_behind.items():
        with st.container(border=True):
            st.markdown(f"**{topic}** — {explanation}")

    # 6 — Help solve
    st.markdown("#### 5. Work the problem")
    st.caption("Adjust numbers — see how an analyst reasons.")
    render_interactive_analysis(pattern_id, key_prefix)

    sol = brief.get("solution", {})
    if sol:
        st.markdown("**Interpretation**")
        st.markdown(sol.get("interpretation", ""))
        st.markdown("**Recommendation**")
        st.info(sol.get("recommendation", ""))
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Data that would sharpen this:** {sol.get('data_needed', '')}")
        with c2:
            st.markdown(f"**Uncertainty remaining:** {sol.get('uncertainty', '')}")

    st.caption(f"*Caveat:* {brief['limitations']}")

    # 7 — Go deeper
    render_go_deeper(brief, pattern, area)

    render_try_yourself(pattern, area)


def render_go_deeper(brief: dict, pattern: dict, area: dict) -> None:
    """Optional depth — simulation, analyst lens, practice."""
    deeper = brief.get("go_deeper", {})
    with st.expander("#### Go deeper (optional)", expanded=False):
        if deeper.get("simulation"):
            st.markdown(f"**Simulation:** {deeper['simulation']}")
        if deeper.get("analyst"):
            st.markdown(f"**Analyst lens:** {deeper['analyst']}")
        if deeper.get("practice"):
            st.markdown(f"**Practice:** {deeper['practice']}")
        st.markdown("**Analyst approach (step-by-step)**")
        for i, step in enumerate(brief.get("analyst_steps", []), 1):
            st.markdown(f"{i}. {step}")
        if area.get("lab_hint"):
            st.caption(area["lab_hint"])


def _render_ev_analysis(key_prefix: str) -> None:
    p_pct = st.slider("Your estimated win probability (%)", 5, 95, 45, key=f"{key_prefix}_p")
    odds_choice = st.selectbox(
        "Market odds (American)",
        ["+200", "+150", "+100", "-110", "-150"],
        index=1,
        key=f"{key_prefix}_odds",
    )
    stake = st.number_input("Stake ($)", min_value=1.0, value=100.0, key=f"{key_prefix}_stake")

    p = p_pct / 100.0
    if odds_choice.startswith("+"):
        n = int(odds_choice[1:])
        profit_if_win = stake * n / 100
        implied = 100 / (n + 100)
    else:
        n = int(odds_choice[1:])
        profit_if_win = stake * 100 / n
        implied = n / (n + 100)

    ev = p * profit_if_win - (1 - p) * stake
    edge = p - implied
    c1, c2, c3 = st.columns(3)
    c1.metric("Implied probability", f"{implied:.1%}")
    c2.metric("Your edge", f"{edge:+.1%}")
    c3.metric("Expected value", f"${ev:+.2f}")
    if ev > 0:
        st.success("At these inputs, the bet is **+EV** long-term — verify your probability estimate.")
    else:
        st.warning("At these inputs, the bet is **−EV** — the price may already reflect fair odds.")


def _render_growth_analysis(key_prefix: str) -> None:
    growth = st.slider("Untreated growth rate (% per month)", 1, 30, 10, key=f"{key_prefix}_g")
    kill = st.slider("Treatment kill rate (% per month)", 0, 30, 8, key=f"{key_prefix}_k")
    net = (growth - kill) / 100.0
    if net > 0:
        st.warning(f"Net growth **+{net*100:.0f}%/month** — still growing; need stronger effect or control comparison.")
    elif net < 0:
        st.success(f"Net shrinkage **{net*100:.0f}%/month** — favorable direction (confirm with control data).")
    else:
        st.info("Net rate ≈ 0 — stable; check measurement noise.")


def _render_ml_analysis(key_prefix: str) -> None:
    train_acc = st.slider("Training accuracy (%)", 50, 100, 92, key=f"{key_prefix}_tr")
    val_acc = st.slider("Validation accuracy (%)", 50, 100, 78, key=f"{key_prefix}_va")
    gap = train_acc - val_acc
    st.metric("Train − validation gap", f"{gap} pts")
    if gap > 15:
        st.warning("Likely **overfitting** — simplify, regularize, or add data.")
    elif val_acc < 60:
        st.warning("Likely **underfitting** or weak features.")
    else:
        st.success("Reasonable gap — keep tuning on validation only.")


def _render_motion_analysis(key_prefix: str) -> None:
    velocity = st.slider("Velocity (m/s)", 100, 12000, 7800, step=100, key=f"{key_prefix}_v")
    radius_km = st.slider("Orbital radius (km)", 6371, 50000, 6771, key=f"{key_prefix}_r")
    g = 3.986e14 / (radius_km * 1000) ** 2
    circular_v = (g * radius_km * 1000) ** 0.5
    st.metric("Circular orbital speed (approx.)", f"{circular_v:.0f} m/s")
    if abs(velocity - circular_v) / circular_v < 0.05:
        st.success("Velocity is near circular-orbit speed for this radius.")
    elif velocity < circular_v:
        st.info("Below circular speed — sub-orbital or transfer orbit unless thrust continues.")
    else:
        st.warning("Above circular speed — escape or higher orbit unless constrained.")


def _render_forecast_analysis(key_prefix: str) -> None:
    lead = st.slider("Forecast lead time (days)", 1, 14, 3, key=f"{key_prefix}_lead")
    spread = min(45, 5 + lead * 3)
    st.metric("Illustrative uncertainty band", f"±{spread}%")
    st.caption("Uncertainty typically grows with lead time — use probabilistic forecasts.")


def _render_structure_analysis(key_prefix: str) -> None:
    goal = st.radio(
        "Primary goal",
        ["Predict an outcome", "Compare options", "Optimize a choice", "Explain a mechanism"],
        key=f"{key_prefix}_goal",
    )
    tool_map = {
        "Predict an outcome": "Probability + statistics (distributions, confidence)",
        "Compare options": "Expected value or hypothesis testing",
        "Optimize a choice": "Optimization subject to constraints",
        "Explain a mechanism": "Calculus or differential equations (rates of change)",
    }
    st.info(f"**Likely tools:** {tool_map[goal]}")


def render_interactive_analysis(pattern_id: str, key_prefix: str) -> None:
    brief = get_analyst_brief(pattern_id)
    kind = brief.get("interactive", "ev_bet")
    handlers = {
        "ev_bet": _render_ev_analysis,
        "growth": _render_growth_analysis,
        "ml_split": _render_ml_analysis,
        "motion": _render_motion_analysis,
        "forecast": _render_forecast_analysis,
        "structure": _render_structure_analysis,
        "tradeoff": lambda k: _render_motion_analysis(k),
        "queue": _render_forecast_analysis,
        "unit_econ": _render_ev_analysis,
    }
    handlers.get(kind, _render_ev_analysis)(key_prefix)


def render_try_yourself(pattern: dict, area: dict) -> None:
    lab = area.get("suggested_lab") or pattern.get("suggested_lab", "Solve a Problem")
    st.markdown("#### 6. Try it yourself")
    if area.get("lab_hint"):
        st.info(area["lab_hint"])
    if lab == "Advanced reference":
        st.caption("Use sidebar → **Advanced reference** for Space & Motion or Weather labs.")
        return
    if st.button(f"Open **{lab}** →", type="primary", key=f"ps_go_{area['id']}"):
        navigate_to(lab)


def render_abstract_section() -> None:
    """Standalone abstract mathematical problem solving."""
    from content.quant_areas import ABSTRACT_PROBLEM_SOLVING

    st.markdown(f"#### {ABSTRACT_PROBLEM_SOLVING['title']}")
    st.markdown(ABSTRACT_PROBLEM_SOLVING["purpose"])
    for title, desc in ABSTRACT_PROBLEM_SOLVING["steps"]:
        with st.container(border=True):
            st.markdown(f"**{title}** — {desc}")
    st.markdown("**How questions translate**")
    for src, dst in ABSTRACT_PROBLEM_SOLVING["translations"]:
        st.markdown(f"- *{src}* {dst}")
