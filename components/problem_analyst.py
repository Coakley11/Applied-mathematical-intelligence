"""Quantitative analyst UI — worked examples and 7-step flow."""

import streamlit as st

from components.nav import navigate_to
from content.analyst_briefs import get_analyst_brief
from content.worked_examples import get_worked_example


def _merge_worked_with_brief(worked: dict | None, pattern_id: str) -> dict:
    """Combine worked example with area brief fallbacks."""
    brief = get_analyst_brief(pattern_id)
    if not worked:
        return {
            "asked": brief.get("mathematical_form", brief["what_is_asked"]),
            "problem_kind": brief.get("abstract_thinking", {}).get("problem_kind", ""),
            "variables": brief.get("variables_list", []),
            "assumptions": [brief.get("abstract_thinking", {}).get("assumptions", "")],
            "math_helps": brief["math_useful"],
            "worked_simple": brief.get("solution", {}).get("recommendation", brief["limitations"]),
            "interactive": brief.get("interactive", "ev_bet"),
            "interactive_defaults": {},
            "deeper_math": brief.get("math_behind", {}),
            "interpretation": brief.get("solution", {}).get("interpretation", ""),
            "recommendation": brief.get("solution", {}).get("recommendation", ""),
            "limitations": brief["limitations"],
            "analyst_steps": brief.get("analyst_steps", []),
        }
    assumptions = worked.get("assumptions", [])
    if isinstance(assumptions, str):
        assumptions = [assumptions]
    return {
        "asked": worked["asked"],
        "problem_kind": worked["problem_kind"],
        "variables": worked["variables"],
        "assumptions": assumptions,
        "math_helps": worked["math_helps"],
        "worked_simple": worked["worked_simple"],
        "interactive": worked.get("interactive", brief.get("interactive", "ev_bet")),
        "interactive_defaults": worked.get("interactive_defaults", {}),
        "deeper_math": worked.get("deeper_math", brief.get("math_behind", {})),
        "interpretation": worked.get("interpretation", ""),
        "recommendation": worked.get("recommendation", ""),
        "limitations": brief.get("limitations", ""),
        "analyst_steps": brief.get("analyst_steps", []),
    }


def render_quantitative_flow(
    problem: str,
    pattern: dict,
    pattern_id: str,
    area: dict,
    key_prefix: str,
) -> None:
    """Seven-step analyst flow for a specific question."""
    worked = get_worked_example(problem, area["id"])
    flow = _merge_worked_with_brief(worked, pattern_id)

    with st.container(border=True):
        st.markdown(f"**Your question:** *{problem}*")
        st.caption(f"{area['icon']} {area['name']}")

    st.markdown("#### 1. What is being asked?")
    st.markdown(flow["asked"])

    st.markdown("#### 2. What kind of mathematical problem is this?")
    st.markdown(flow["problem_kind"])

    st.markdown("#### 3. What variables matter?")
    for v in flow["variables"]:
        st.markdown(f"- {v}")

    st.markdown("#### 4. What assumptions are we making?")
    for a in flow["assumptions"]:
        if a:
            st.markdown(f"- {a}")

    st.markdown("#### 5. What math helps?")
    st.markdown(flow["math_helps"])

    st.markdown("#### 6. Work through a simple version")
    st.markdown(flow["worked_simple"])
    render_interactive_analysis(
        flow["interactive"],
        key_prefix,
        flow.get("interactive_defaults", {}),
    )
    if flow.get("interpretation"):
        st.markdown(f"**Interpretation:** {flow['interpretation']}")
    if flow.get("recommendation"):
        st.info(f"**Analyst take:** {flow['recommendation']}")
    if flow.get("limitations"):
        st.caption(f"*Caveat:* {flow['limitations']}")

    render_deeper_math(flow, area)

    render_try_yourself(pattern, area)


def render_deeper_math(flow: dict, area: dict) -> None:
    with st.expander("#### 7. Deeper math (optional)", expanded=False):
        for topic, explanation in flow.get("deeper_math", {}).items():
            st.markdown(f"**{topic}** — {explanation}")
        if flow.get("analyst_steps"):
            st.markdown("**Full analyst checklist**")
            for i, step in enumerate(flow["analyst_steps"], 1):
                st.caption(f"{i}. {step}")
        if area.get("lab_hint"):
            st.caption(area["lab_hint"])


def _render_ev_analysis(key_prefix: str, defaults: dict) -> None:
    p_pct = st.slider(
        "Your estimated win probability (%)",
        5, 95,
        int(defaults.get("p", 45)),
        key=f"{key_prefix}_p",
    )
    odds_options = ["+200", "+150", "+100", "-110", "-150", "+400", "+240"]
    default_odds = defaults.get("odds", "+150")
    odds_idx = odds_options.index(default_odds) if default_odds in odds_options else 1
    odds_choice = st.selectbox("Market odds (American)", odds_options, index=odds_idx, key=f"{key_prefix}_odds")
    stake = st.number_input("Stake ($)", min_value=1.0, value=float(defaults.get("stake", 100)), key=f"{key_prefix}_stake")

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
        st.success("**+EV** at these inputs.")
    else:
        st.warning("**−EV** at these inputs.")


def _render_growth_analysis(key_prefix: str, defaults: dict) -> None:
    growth = st.slider("Untreated growth (%/month)", 1, 30, int(defaults.get("g", 10)), key=f"{key_prefix}_g")
    kill = st.slider("Treatment effect (%/month)", 0, 30, int(defaults.get("k", 8)), key=f"{key_prefix}_k")
    net = growth - kill
    if net > 0:
        st.warning(f"Net **+{net}%/month** — volume still increasing.")
    elif net < 0:
        st.success(f"Net **{net}%/month** — shrinkage direction (confirm with data).")
    else:
        st.info("Net ≈ 0 — stable within model.")


def _render_ml_analysis(key_prefix: str, defaults: dict) -> None:
    train_acc = st.slider("Training accuracy (%)", 50, 100, int(defaults.get("tr", 92)), key=f"{key_prefix}_tr")
    val_acc = st.slider("Validation accuracy (%)", 50, 100, int(defaults.get("va", 78)), key=f"{key_prefix}_va")
    gap = train_acc - val_acc
    st.metric("Train − validation gap", f"{gap} pts")
    if gap > 15:
        st.warning("Likely **overfitting**.")
    elif val_acc < 60:
        st.warning("Likely **underfitting** or weak features.")
    else:
        st.success("Moderate gap — reasonable starting point.")


def _render_motion_analysis(key_prefix: str, defaults: dict) -> None:
    velocity = st.slider("Speed (m/s)", 100, 12000, int(defaults.get("v", 7670)), step=50, key=f"{key_prefix}_v")
    radius_km = st.slider("Radius (km)", 6371, 50000, int(defaults.get("r", 6771)), key=f"{key_prefix}_r")
    mu = 3.986e14
    circular_v = (mu / (radius_km * 1000)) ** 0.5
    st.metric("Circular orbital speed", f"{circular_v:.0f} m/s")
    diff_pct = abs(velocity - circular_v) / circular_v * 100
    if diff_pct < 5:
        st.success("Near circular-orbit speed for this radius.")
    elif velocity < circular_v:
        st.info(f"Below circular speed by ~{diff_pct:.0f}%.")
    else:
        st.warning(f"Above circular speed by ~{diff_pct:.0f}%.")


def _render_forecast_analysis(key_prefix: str, defaults: dict) -> None:
    lead = st.slider("Forecast lead time (days)", 1, 14, int(defaults.get("lead", 3)), key=f"{key_prefix}_lead")
    spread = min(45, 5 + lead * 3)
    st.metric("Illustrative uncertainty band", f"±{spread}%")


def _render_structure_analysis(key_prefix: str, defaults: dict) -> None:
    st.caption("Pick the closest goal — maps to a mathematical tool family.")
    goal = st.radio(
        "Primary goal",
        ["Predict an outcome", "Compare options", "Optimize a choice", "Explain a mechanism"],
        key=f"{key_prefix}_goal",
    )
    tool_map = {
        "Predict an outcome": "Probability + statistics",
        "Compare options": "Expected value or hypothesis testing",
        "Optimize a choice": "Optimization with constraints",
        "Explain a mechanism": "Calculus / differential equations",
    }
    st.info(f"**Start with:** {tool_map[goal]}")


def render_interactive_analysis(interactive: str, key_prefix: str, defaults: dict) -> None:
    st.caption("Adjust numbers — see the analysis update.")
    handlers = {
        "ev_bet": _render_ev_analysis,
        "growth": _render_growth_analysis,
        "ml_split": _render_ml_analysis,
        "motion": _render_motion_analysis,
        "forecast": _render_forecast_analysis,
        "structure": _render_structure_analysis,
    }
    handlers.get(interactive, _render_ev_analysis)(key_prefix, defaults)


def render_try_yourself(pattern: dict, area: dict) -> None:
    lab = area.get("suggested_lab") or pattern.get("suggested_lab", "Solve a Problem")
    st.markdown("---")
    st.markdown("#### Try it in a lab")
    if area.get("lab_hint"):
        st.info(area["lab_hint"])
    if lab == "Advanced reference":
        return
    if st.button(f"Open **{lab}** →", type="primary", key=f"ps_go_{area['id']}"):
        navigate_to(lab)


def render_abstract_section() -> None:
    from content.quant_areas import ABSTRACT_PROBLEM_SOLVING

    st.markdown(f"#### {ABSTRACT_PROBLEM_SOLVING['title']}")
    st.markdown(ABSTRACT_PROBLEM_SOLVING["purpose"])
    for title, desc in ABSTRACT_PROBLEM_SOLVING["steps"]:
        st.caption(f"**{title}** — {desc}")
    st.markdown("**Translations**")
    for src, dst in ABSTRACT_PROBLEM_SOLVING["translations"]:
        st.markdown(f"- *{src}* {dst}")
