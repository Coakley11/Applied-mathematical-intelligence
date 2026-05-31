"""Quantitative analyst UI — brief analysis, interactive tools, math, labs."""

import streamlit as st

from components.nav import navigate_to
from content.analyst_briefs import ANALYST_BRIEFS


def render_analyst_brief(pattern: dict, problem: str, pattern_id: str) -> dict:
    """Steps 2–3: problem type and analyst framing."""
    brief = ANALYST_BRIEFS.get(pattern_id, ANALYST_BRIEFS["default"])
    type_label = brief["type_label"]
    categories = ", ".join(pattern.get("categories", ["quantitative"]))

    st.markdown(f"#### Problem type: **{type_label}**")
    st.caption(f"Categories: {categories}")

    with st.container(border=True):
        st.markdown(f"**Your question:** *{problem}*")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**What is being asked?**")
        st.markdown(brief["what_is_asked"])
        st.markdown("**What variables matter?**")
        st.markdown(brief["variables"])
    with c2:
        st.markdown("**What math is useful?**")
        st.markdown(brief["math_useful"])
        st.markdown("**How an analyst approaches this**")
        for i, step in enumerate(brief["analyst_steps"], 1):
            st.markdown(f"{i}. {step}")

    st.caption(f"*Limitations:* {brief['limitations']}")
    return brief


def _render_ev_analysis(key_prefix: str) -> None:
    """Interactive EV for sports/betting questions."""
    st.markdown("**Quick EV check** — adjust inputs and see if the bet is +EV.")
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
        st.success(f"**+EV** at your estimates — but verify probability and track results over many bets.")
    else:
        st.warning(f"**−EV** at your estimates — the market price may be fair or better than your edge.")


def _render_growth_analysis(key_prefix: str) -> None:
    """Simple treatment vs. growth comparison."""
    st.markdown("**Growth vs. treatment** — compare rates over time.")
    growth = st.slider("Untreated growth rate (% per month)", 1, 30, 10, key=f"{key_prefix}_g")
    kill = st.slider("Treatment kill rate (% per month)", 0, 30, 8, key=f"{key_prefix}_k")
    months = st.slider("Months", 1, 24, 6, key=f"{key_prefix}_m")

    net = (growth - kill) / 100.0
    if net > 0:
        st.warning(f"Net growth **+{net*100:.0f}%/month** — tumor still growing; treatment may be insufficient.")
    elif net < 0:
        st.success(f"Net shrinkage **{net*100:.0f}%/month** — model favors treatment effect (still need control arm).")
    else:
        st.info("Net rate ≈ 0 — stable volume; watch measurement error and patient variation.")


def _render_ml_analysis(key_prefix: str) -> None:
    """Train/val/test split intuition."""
    st.markdown("**Train / validation / test** — why analysts split data.")
    train_acc = st.slider("Training accuracy (%)", 50, 100, 92, key=f"{key_prefix}_tr")
    val_acc = st.slider("Validation accuracy (%)", 50, 100, 78, key=f"{key_prefix}_va")
    gap = train_acc - val_acc

    st.metric("Train − validation gap", f"{gap} pts")
    if gap > 15:
        st.warning("Large gap → likely **overfitting**. Simplify model, regularize, or get more data.")
    elif val_acc < 60:
        st.warning("Low validation score → model may be **underfitting** or features are weak.")
    else:
        st.success("Gap is moderate — continue tuning on validation only; report test set once at the end.")


def _render_unit_econ(key_prefix: str) -> None:
    """Simple unit economics."""
    st.markdown("**Unit economics** — profit per customer.")
    price = st.number_input("Price per unit ($)", 1.0, 10000.0, 50.0, key=f"{key_prefix}_price")
    cost = st.number_input("Variable cost per unit ($)", 0.0, 10000.0, 30.0, key=f"{key_prefix}_cost")
    conv = st.slider("Conversion rate (%)", 0.1, 50.0, 2.0, key=f"{key_prefix}_conv") / 100
    spend = st.number_input("Marketing spend ($)", 0.0, 1_000_000.0, 1000.0, key=f"{key_prefix}_spend")

    margin = price - cost
    customers = spend * conv if spend > 0 else 0
    profit = customers * margin - spend
    st.metric("Margin per unit", f"${margin:.2f}")
    st.metric("Estimated profit", f"${profit:+.2f}")


def _render_queue_analysis(key_prefix: str) -> None:
    """Simple capacity vs. demand."""
    demand = st.slider("Demand (vehicles/hour)", 100, 5000, 1200, key=f"{key_prefix}_d")
    capacity = st.slider("Capacity (vehicles/hour)", 100, 5000, 1000, key=f"{key_prefix}_c")
    if demand > capacity:
        st.warning(f"Demand exceeds capacity by **{demand - capacity}**/hr — expect queues and delay.")
    else:
        st.success(f"Spare capacity **{capacity - demand}**/hr — system not saturated (under typical conditions).")


def _render_forecast_analysis(key_prefix: str) -> None:
    """Lead time vs. uncertainty."""
    lead = st.slider("Forecast lead time (days)", 1, 14, 3, key=f"{key_prefix}_lead")
    spread = min(45, 5 + lead * 3)
    st.metric("Typical uncertainty band (illustrative)", f"±{spread}%")
    st.caption("Uncertainty usually grows with lead time — prefer probabilistic forecasts.")


def _render_tradeoff_analysis(key_prefix: str) -> None:
    """Performance vs. cost tradeoff."""
    perf = st.slider("Performance index", 1, 100, 70, key=f"{key_prefix}_perf")
    cost = st.slider("Cost index", 1, 100, 50, key=f"{key_prefix}_cost")
    ratio = perf / max(cost, 1)
    st.metric("Performance / cost", f"{ratio:.2f}")
    st.caption("Analysts maximize this ratio subject to safety and feasibility constraints.")


def render_interactive_analysis(pattern_id: str, key_prefix: str) -> None:
    """Step 4: hands-on analysis — pattern-specific mini tools."""
    brief = ANALYST_BRIEFS.get(pattern_id, ANALYST_BRIEFS["default"])
    kind = brief.get("interactive", "ev_bet")

    st.markdown("#### Interactive analysis")
    st.caption("Adjust inputs — see how a quantitative analyst reasons numerically.")

    if kind == "ev_bet":
        _render_ev_analysis(key_prefix)
    elif kind == "growth":
        _render_growth_analysis(key_prefix)
    elif kind == "ml_split":
        _render_ml_analysis(key_prefix)
    elif kind == "unit_econ":
        _render_unit_econ(key_prefix)
    elif kind == "queue":
        _render_queue_analysis(key_prefix)
    elif kind == "forecast":
        _render_forecast_analysis(key_prefix)
    elif kind == "tradeoff":
        _render_tradeoff_analysis(key_prefix)
    else:
        _render_ev_analysis(key_prefix)


def render_show_math(pattern_id: str) -> None:
    """Step 5: math behind this problem."""
    brief = ANALYST_BRIEFS.get(pattern_id, ANALYST_BRIEFS["default"])
    math_behind = brief.get("math_behind", {})

    with st.expander("#### Show the math behind this", expanded=False):
        st.caption("Learn the tools in context — not as a formula sheet.")
        for topic, explanation in math_behind.items():
            with st.container(border=True):
                st.markdown(f"**{topic}**")
                st.markdown(explanation)


def render_try_yourself(pattern: dict) -> None:
    """Step 6: jump to connected lab."""
    lab = pattern.get("suggested_lab", "Solve a Problem")
    st.markdown("#### Try it yourself")
    st.caption("Run a simulation or tool connected to this type of problem.")

    if lab == "Advanced reference":
        st.info("Open **Advanced reference** in the sidebar for background on this topic.")
        return

    st.markdown(f"**Recommended:** {lab}")
    if st.button(f"Open {lab} →", type="primary", key=f"ps_go_{pattern.get('id', 'default')}"):
        navigate_to(lab)
