"""Quantitative analyst UI — worked examples and applied-math lab flow."""

import math

import streamlit as st

from components.nav import navigate_to
from content.analyst_briefs import get_analyst_brief
from content.worked_examples import get_worked_example


def _abstract_from_brief(brief: dict) -> dict:
    at = brief.get("abstract_thinking", {})
    return {
        "kind": at.get("problem_kind", ""),
        "comparing": at.get("comparing", ""),
        "unknown": at.get("unknown", ""),
        "needs_estimate": at.get("needs_estimate", at.get("matters", "")),
        "structure": at.get("structure", ""),
    }


def _merge_worked_with_brief(worked: dict | None, pattern_id: str) -> dict:
    """Combine worked example with area brief fallbacks."""
    brief = get_analyst_brief(pattern_id)
    if not worked:
        at = brief.get("abstract_thinking", {})
        return {
            "asked": brief.get("mathematical_form", brief["what_is_asked"]),
            "math_translation": brief.get("mathematical_form", ""),
            "problem_kind": at.get("problem_kind", ""),
            "variables": brief.get("variables_list", []),
            "abstract_structure": _abstract_from_brief(brief),
            "assumptions": [at.get("assumptions", "")],
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
    abs_struct = worked.get("abstract_structure")
    if not abs_struct:
        abs_struct = _abstract_from_brief(brief)
    return {
        "asked": worked["asked"],
        "math_translation": worked.get("math_translation", worked.get("problem_kind", "")),
        "problem_kind": worked["problem_kind"],
        "variables": worked["variables"],
        "abstract_structure": abs_struct,
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
    """Applied-math lab flow: interpret → structure → compute → interpret → deepen."""
    worked = get_worked_example(problem, area["id"])
    flow = _merge_worked_with_brief(worked, pattern_id)

    with st.container(border=True):
        st.markdown(f"**Your question:** *{problem}*")
        st.caption(f"{area['icon']} {area['name']}")

    st.markdown("#### 1. What is being asked?")
    st.markdown(flow["asked"])

    st.markdown("#### 2. Translate into math")
    st.markdown(flow.get("math_translation") or flow["problem_kind"])

    st.markdown("#### 3. What variables matter?")
    for v in flow["variables"]:
        st.markdown(f"- {v}")

    st.markdown("#### 4. Abstract structure")
    st.caption("What kind of problem is this — before formulas.")
    abs_s = flow.get("abstract_structure", {})
    if abs_s.get("kind"):
        st.markdown(f"**Kind of problem:** {abs_s['kind']}")
    if abs_s.get("structure"):
        st.markdown(f"**Structure:** {abs_s['structure']}")
    if abs_s.get("comparing"):
        st.markdown(f"**What we're comparing:** {abs_s['comparing']}")
    if abs_s.get("unknown"):
        st.markdown(f"**What is unknown:** {abs_s['unknown']}")
    if abs_s.get("needs_estimate"):
        st.markdown(f"**What needs estimating:** {abs_s['needs_estimate']}")

    st.markdown("#### 5. Assumptions")
    for a in flow["assumptions"]:
        if a:
            st.markdown(f"- {a}")

    st.markdown("#### 6. Useful math (connected to this question)")
    st.markdown(flow["math_helps"])

    st.markdown("#### 7. Work through a simple version")
    st.markdown(flow["worked_simple"])

    st.markdown("#### 8. Compute — change assumptions and see results")
    live_note = render_interactive_analysis(
        flow["interactive"],
        key_prefix,
        flow.get("interactive_defaults", {}),
    )
    if live_note:
        try:
            from applied_intelligence_activity import log_problem_solved

            act_sig = (problem, area.get("id", ""), flow.get("interactive", ""))
            if st.session_state.get("_cc_ai_problem_sig") != act_sig:
                st.session_state["_cc_ai_problem_sig"] = act_sig
                log_problem_solved(
                    topic=problem,
                    area=area.get("name", ""),
                    interactive=flow.get("interactive", ""),
                )
        except Exception:
            pass

    st.markdown("#### 9. What does this mean?")
    if live_note:
        st.markdown(live_note)
    if flow.get("interpretation"):
        st.markdown(flow["interpretation"])
    if flow.get("recommendation"):
        st.info(f"**Lab take:** {flow['recommendation']}")
    if flow.get("limitations"):
        st.caption(f"*Caveat:* {flow['limitations']}")

    render_deeper_math(flow, area)
    render_try_yourself(pattern, area)


def render_deeper_math(flow: dict, area: dict) -> None:
    with st.expander("Go deeper — formulas, checklist, related lab", expanded=False):
        for topic, explanation in flow.get("deeper_math", {}).items():
            st.markdown(f"**{topic}** — {explanation}")
        if flow.get("analyst_steps"):
            st.markdown("**Analyst checklist**")
            for i, step in enumerate(flow["analyst_steps"], 1):
                st.caption(f"{i}. {step}")
        if area.get("lab_hint"):
            st.caption(area["lab_hint"])


def _render_ev_analysis(key_prefix: str, defaults: dict) -> str:
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
    break_even = stake / (stake + profit_if_win)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Implied probability", f"{implied:.1%}")
    c2.metric("Break-even P", f"{break_even:.1%}")
    c3.metric("Your edge", f"{edge:+.1%}")
    c4.metric("Expected value", f"${ev:+.2f}")

    if ev > 0 and edge > 0.02:
        st.success("**Favorable** at these inputs — +EV with edge over the market price.")
    elif ev > 0:
        st.info("**Slightly +EV** — thin edge; small errors in your probability estimate can erase it.")
    else:
        st.warning("**Unfavorable** at these inputs — −EV unless your true probability is higher than you entered.")

    return (
        f"At **{p_pct:.0f}%** vs **{implied:.0%}** implied, EV is **${ev:+.2f}** per bet. "
        f"If your true chance is too optimistic, the edge disappears — sensitivity matters."
    )


def _render_ev_prop_analysis(key_prefix: str, defaults: dict) -> str:
    st.caption("Prop / futures style: stake, profit if the event hits, your P(success).")
    stake = st.number_input("Amount risked ($)", min_value=1.0, value=float(defaults.get("stake", 200)), key=f"{key_prefix}_pst")
    profit = st.number_input("Profit if you win ($)", min_value=1.0, value=float(defaults.get("profit", 180)), key=f"{key_prefix}_ppr")
    p_pct = st.slider("Your P(event happens) %", 5, 95, int(defaults.get("p", 35)), key=f"{key_prefix}_ppp")
    p = p_pct / 100.0
    break_even = stake / (stake + profit)
    ev = p * profit - (1 - p) * stake
    c1, c2, c3 = st.columns(3)
    c1.metric("Break-even probability", f"{break_even:.1%}")
    c2.metric("Your estimate", f"{p:.1%}")
    c3.metric("Expected value", f"${ev:+.2f}")
    if p > break_even + 0.03:
        st.success("**Favorable** — your estimate clears break-even with room for error.")
    elif p > break_even:
        st.info("**Marginal +EV** — small estimation errors flip the sign.")
    else:
        st.warning("**Unfavorable** — market price likely fair or better than your estimate.")
    return (
        f"Risking **${stake:.0f}** to win **${profit:.0f}** needs about **{break_even:.0%}** to break even. "
        f"At **{p_pct}%**, EV is **${ev:+.2f}** — the hard part is whether **{p_pct}%** is defensible."
    )


def _render_sports_edge_analysis(key_prefix: str, defaults: dict) -> str:
    model_p = st.slider("Your projected win probability (%)", 30, 80, int(defaults.get("model", 58)), key=f"{key_prefix}_spm")
    market_p = st.slider("Market implied probability (%)", 30, 80, int(defaults.get("market", 52)), key=f"{key_prefix}_spk")
    injury = st.slider("Injury / news adjustment (percentage points)", -15, 15, int(defaults.get("injury", 0)), key=f"{key_prefix}_spi")
    adj = model_p + injury
    edge = adj - market_p
    c1, c2, c3 = st.columns(3)
    c1.metric("Adjusted probability", f"{adj}%")
    c2.metric("Market", f"{market_p}%")
    c3.metric("Edge", f"{edge:+} pts")
    if edge >= 5:
        st.success("Apparent edge — still validate calibration on out-of-sample games.")
    elif edge > 0:
        st.info("Thin edge — vig and model error may consume it.")
    else:
        st.warning("No edge at these inputs — your model agrees with or trails the market.")
    return (
        f"After adjustments, **{adj}%** vs market **{market_p}%** is **{edge:+} points**. "
        "Wide uncertainty on injuries and small samples can erase apparent edge."
    )


def _render_growth_analysis(key_prefix: str, defaults: dict) -> str:
    v0 = st.number_input("Starting volume (index)", min_value=1.0, value=float(defaults.get("v0", 100)), key=f"{key_prefix}_gv0")
    growth = st.slider("Untreated growth (%/month)", 1, 30, int(defaults.get("g", 10)), key=f"{key_prefix}_g")
    kill = st.slider("Treatment effect (%/month)", 0, 30, int(defaults.get("k", 8)), key=f"{key_prefix}_k")
    months = st.slider("Months forward", 1, 24, int(defaults.get("months", 6)), key=f"{key_prefix}_gm")
    net = (growth - kill) / 100.0
    projected = v0 * ((1 + net) ** months)
    st.metric(f"Projected volume after {months} mo.", f"{projected:.1f}")
    if net > 0:
        st.warning(f"Net **+{growth - kill}%/month** — volume still increasing in this model.")
    elif net < 0:
        st.success(f"Net **{growth - kill}%/month** — decline direction (confirm with data).")
    else:
        st.info("Net ≈ 0 — stable within this simplified model.")
    return (
        f"With net **{(growth - kill):+}%/month** over **{months}** months, "
        f"volume moves from **{v0:.0f}** to about **{projected:.0f}**. "
        "Real tumors need controls and measurement error — this is a teaching sketch."
    )


def _render_ml_analysis(key_prefix: str, defaults: dict) -> str:
    train_acc = st.slider("Training accuracy (%)", 50, 100, int(defaults.get("tr", 92)), key=f"{key_prefix}_tr")
    val_acc = st.slider("Validation accuracy (%)", 50, 100, int(defaults.get("va", 78)), key=f"{key_prefix}_va")
    lr = st.select_slider(
        "Learning rate (order of magnitude)",
        options=["1e-2", "1e-3", "1e-4", "1e-5"],
        value=defaults.get("lr", "1e-3"),
        key=f"{key_prefix}_lr",
    )
    gap = train_acc - val_acc
    st.metric("Train − validation gap", f"{gap} pts")
    if gap > 15:
        st.warning("Likely **overfitting** — simplify, regularize, or get more data.")
    elif val_acc < 60:
        st.warning("Likely **underfitting** or weak features.")
    else:
        st.success("Moderate gap — reasonable starting point.")
    if lr == "1e-2" and gap > 12:
        st.caption("High learning rate + large gap: try lower η, early stopping, or L2/dropout.")
    return (
        f"A **{gap}-point** train–val gap suggests {'overfitting' if gap > 15 else 'watch generalization'}. "
        f"Learning rate **{lr}** affects stability — tune on validation, not training accuracy alone."
    )


def _render_motion_analysis(key_prefix: str, defaults: dict) -> str:
    velocity = st.slider("Speed (m/s)", 100, 12000, int(defaults.get("v", 7670)), step=50, key=f"{key_prefix}_v")
    radius_km = st.slider("Orbital radius (km)", 6371, 50000, int(defaults.get("r", 6771)), key=f"{key_prefix}_r")
    mu = 3.986e14
    circular_v = (mu / (radius_km * 1000)) ** 0.5
    st.metric("Circular orbital speed", f"{circular_v:.0f} m/s")
    diff_pct = abs(velocity - circular_v) / circular_v * 100
    if diff_pct < 5:
        st.success("Near circular-orbit speed for this radius.")
    elif velocity < circular_v:
        st.info(f"Below circular speed by ~{diff_pct:.0f}% — sub-orbital or elliptical.")
    else:
        st.warning(f"Above circular speed by ~{diff_pct:.0f}% — higher orbit or escape energy.")
    return (
        f"At **{radius_km} km** radius, circular speed is about **{circular_v:.0f} m/s**. "
        "Wrong speed ⇒ wrong orbit class — match mission target state."
    )


def _render_projectile_analysis(key_prefix: str, defaults: dict) -> str:
    v0 = st.number_input("Launch speed (m/s)", min_value=1.0, value=float(defaults.get("v0", 50)), key=f"{key_prefix}_pv0")
    angle = st.slider("Launch angle (degrees)", 5, 85, int(defaults.get("angle", 45)), key=f"{key_prefix}_pang")
    g = st.number_input("Gravity (m/s²)", min_value=1.0, value=float(defaults.get("g", 9.81)), key=f"{key_prefix}_pg")
    rad = math.radians(angle)
    vy = v0 * math.sin(rad)
    vx = v0 * math.cos(rad)
    t_flight = 2 * vy / g if g > 0 else 0
    max_height = (vy ** 2) / (2 * g) if g > 0 else 0
    range_m = vx * t_flight
    c1, c2, c3 = st.columns(3)
    c1.metric("Max height", f"{max_height:.1f} m")
    c2.metric("Range", f"{range_m:.1f} m")
    c3.metric("Time of flight", f"{t_flight:.2f} s")
    if abs(angle - 45) < 3:
        st.caption("Near **45°** — maximum range on flat ground (no drag).")
    return (
        f"At **{angle}°** and **{v0:.0f} m/s**, peak height ≈ **{max_height:.0f} m**, range ≈ **{range_m:.0f} m** (no drag). "
        "Orbits need horizontal speed, not just loft."
    )


def _render_forecast_analysis(key_prefix: str, defaults: dict) -> str:
    baseline = st.number_input("Baseline forecast", value=float(defaults.get("baseline", 100)), key=f"{key_prefix}_fb")
    trend = st.slider("Trend per period (%)", -30, 30, int(defaults.get("trend", 0)), key=f"{key_prefix}_ft")
    noise = st.slider("Typical noise (±%)", 1, 40, int(defaults.get("noise", 12)), key=f"{key_prefix}_fn")
    conf = st.slider("Confidence level (%)", 80, 99, int(defaults.get("conf", 95)), key=f"{key_prefix}_fc")
    lead = st.slider("Forecast lead time (periods)", 1, 14, int(defaults.get("lead", 3)), key=f"{key_prefix}_fl")
    center = baseline * (1 + trend / 100) ** lead
    width = center * (noise / 100) * (1 + (100 - conf) / 40 + lead * 0.15)
    low, high = center - width, center + width
    st.metric("Point forecast", f"{center:.1f}")
    st.metric(f"~{conf}% illustrative range", f"{low:.1f} – {high:.1f}")
    st.caption("Ranges widen with lead time and noise — point forecasts hide uncertainty.")
    return (
        f"After **{lead}** periods, center forecast **{center:.1f}** with a rough **{conf}%** band "
        f"**{low:.1f}–{high:.1f}**. Trust calibrated probabilities over single icons."
    )


def _render_structure_analysis(key_prefix: str, defaults: dict) -> str:
    st.caption("Map the question to a tool family — modeling before formulas.")
    goal = st.radio(
        "Primary goal",
        ["Predict an outcome", "Compare options", "Optimize a choice", "Explain a mechanism"],
        key=f"{key_prefix}_goal",
    )
    tool_map = {
        "Predict an outcome": "Probability + statistics + simulation",
        "Compare options": "Expected value or hypothesis testing",
        "Optimize a choice": "Optimization with constraints",
        "Explain a mechanism": "Calculus / differential equations",
    }
    st.info(f"**Start with:** {tool_map[goal]}")
    return (
        f"For **{goal.lower()}**, begin with **{tool_map[goal]}**. "
        "List variables, constraints, and what you must estimate before calculating."
    )


def render_interactive_analysis(interactive: str, key_prefix: str, defaults: dict) -> str:
    st.caption("Adjust inputs — results update immediately.")
    handlers = {
        "ev_bet": _render_ev_analysis,
        "ev_prop": _render_ev_prop_analysis,
        "sports_edge": _render_sports_edge_analysis,
        "growth": _render_growth_analysis,
        "ml_split": _render_ml_analysis,
        "motion": _render_motion_analysis,
        "projectile": _render_projectile_analysis,
        "forecast": _render_forecast_analysis,
        "forecast_range": _render_forecast_analysis,
        "structure": _render_structure_analysis,
    }
    fn = handlers.get(interactive, _render_ev_analysis)
    return fn(key_prefix, defaults) or ""


def render_try_yourself(pattern: dict, area: dict) -> None:
    lab = area.get("suggested_lab") or pattern.get("suggested_lab", "Solve a Problem")
    st.markdown("---")
    st.markdown("#### Related lab")
    if area.get("lab_hint"):
        st.info(area["lab_hint"])
    if lab == "Advanced reference":
        return
    if st.button(f"Open **{lab}** →", type="primary", key=f"ps_go_{area['id']}"):
        navigate_to(lab)


def render_abstract_section() -> None:
    from content.quant_areas import MODELING_REAL_SYSTEMS

    st.markdown(f"#### {MODELING_REAL_SYSTEMS['title']}")
    st.markdown(MODELING_REAL_SYSTEMS["purpose"])
    for title, desc in MODELING_REAL_SYSTEMS["steps"]:
        st.caption(f"**{title}** — {desc}")
    st.markdown("**Connects across areas**")
    for src, dst in MODELING_REAL_SYSTEMS["translations"]:
        st.markdown(f"- *{src}* {dst}")
