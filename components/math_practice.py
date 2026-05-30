"""Interactive 'Try the math yourself' widgets."""

import streamlit as st


def render_math_practice(practice_id: str) -> None:
    """Render a hands-on math widget by practice type."""
    renderers = {
        "ev_bet": _practice_ev_bet,
        "ev_pot_odds": _practice_ev_pot_odds,
        "shrinkage": _practice_shrinkage,
        "forecast_slope": _practice_forecast_slope,
        "sir_rates": _practice_sir_rates,
        "tumor_growth": _practice_tumor_growth,
        "accumulation": _practice_accumulation,
        "gradient_step": _practice_gradient_step,
        "probability_compare": _practice_probability_compare,
    }
    fn = renderers.get(practice_id)
    if fn:
        fn()
    else:
        st.caption("Practice widget coming soon.")


def _practice_ev_bet() -> None:
    st.markdown("**Is this bet worth it?** Enter your numbers and calculate expected value.")
    c1, c2, c3 = st.columns(3)
    with c1:
        win_pct = st.number_input("Your win probability (%)", 10, 90, 55, key="pr_ev_wp")
    with c2:
        odds = st.number_input("Decimal odds", 1.1, 5.0, 1.90, step=0.05, key="pr_ev_odds")
    with c3:
        stake = st.number_input("Stake ($)", 10, 500, 100, key="pr_ev_stake")

    win_p = win_pct / 100
    profit = stake * (odds - 1)
    ev = win_p * profit - (1 - win_p) * stake
    implied = 1 / odds

    st.markdown("**Your calculation:**")
    st.latex(r"EV = P(win) \times profit - P(lose) \times stake")
    st.markdown(
        f"EV = {win_p:.2f} × ${profit:.2f} − {1-win_p:.2f} × ${stake:.2f} = **${ev:+.2f}**"
    )
    st.caption(f"Market implied probability: {implied:.1%} · Your estimate: {win_p:.1%} · Edge: {win_p - implied:+.1%}")
    if ev > 0:
        st.success("Positive EV — mathematically favorable over many similar bets.")
    else:
        st.warning("Negative EV — unfavorable long-term.")


def _practice_ev_pot_odds() -> None:
    st.markdown("**Pot odds vs your equity** — the core poker math check.")
    c1, c2, c3 = st.columns(3)
    with c1:
        pot = st.number_input("Pot before call ($)", 20, 500, 150, key="pr_po_pot")
    with c2:
        call = st.number_input("Call cost ($)", 5, 200, 60, key="pr_po_call")
    with c3:
        equity = st.number_input("Your win probability (%)", 5, 95, 38, key="pr_po_eq")

    pot_odds = call / (pot + call)
    eq = equity / 100
    ev = eq * (pot + call) - (1 - eq) * call

    st.markdown(f"**Pot odds (break-even equity):** {pot_odds:.1%}")
    st.markdown(f"**Your equity:** {eq:.1%}")
    st.markdown(f"**EV of calling:** ${ev:+.2f}")
    if eq > pot_odds:
        st.success("Your equity exceeds pot odds — calling is justified.")
    else:
        st.warning("Equity below pot odds — fold unless implied odds help.")


def _practice_shrinkage() -> None:
    st.markdown("**Regression to the mean** — adjust a small-sample win rate.")
    c1, c2 = st.columns(2)
    with c1:
        wins = st.number_input("Wins", 0, 50, 8, key="pr_sh_w")
        games = st.number_input("Games played", 1, 100, 10, key="pr_sh_g")
    with c2:
        league_avg = st.slider("League average win rate (%)", 30, 70, 50, key="pr_sh_avg")
        prior = st.slider("Prior strength (games)", 5, 40, 15, key="pr_sh_prior")

    raw = wins / games
    adjusted = (wins + prior * league_avg / 100) / (games + prior)

    st.markdown(f"**Raw win rate:** {raw:.1%} ({wins}/{games})")
    st.markdown(f"**Adjusted estimate:** {adjusted:.1%}")
    st.caption(f"Pulled {abs(raw - adjusted):.1%} toward the league average because the sample is small.")


def _practice_forecast_slope() -> None:
    st.markdown("**Fit a trend by hand** — enter two points and see the slope.")
    c1, c2 = st.columns(2)
    with c1:
        t1, y1 = st.number_input("Time 1", 0, 100, 0, key="pr_fs_t1"), st.number_input("Value 1", 0, 200, 50, key="pr_fs_y1")
    with c2:
        t2, y2 = st.number_input("Time 2", 1, 100, 10, key="pr_fs_t2"), st.number_input("Value 2", 0, 200, 80, key="pr_fs_y2")

    if t2 != t1:
        slope = (y2 - y1) / (t2 - t1)
        intercept = y1 - slope * t1
        st.markdown(f"**Slope:** {slope:.2f} per period")
        st.markdown(f"**Trend line:** value ≈ {intercept:.1f} + {slope:.2f} × time")
        st.latex(r"slope = \frac{y_2 - y_1}{t_2 - t_1}")
        forecast_5 = intercept + slope * (t2 + 5)
        st.caption(f"Forecast 5 periods ahead: ≈ {forecast_5:.1f}")
    else:
        st.warning("Pick two different time points.")


def _practice_sir_rates() -> None:
    st.markdown("**Estimate outbreak speed** — what do β and γ mean?")
    c1, c2 = st.columns(2)
    with c1:
        beta = st.slider("Transmission rate β", 0.1, 1.0, 0.45, key="pr_sir_b")
    with c2:
        gamma = st.slider("Recovery rate γ", 0.05, 0.5, 0.12, key="pr_sir_g")

    r0 = beta / gamma if gamma > 0 else 0
    st.markdown(f"**Basic reproduction number R₀ ≈ {r0:.2f}**")
    st.caption("R₀ = β/γ — average people infected by one case. R₀ > 1 → outbreak grows.")
    if r0 > 1:
        st.warning(f"R₀ > 1 ({r0:.2f}) — epidemic likely to spread.")
    else:
        st.success(f"R₀ < 1 ({r0:.2f}) — outbreak should die out.")


def _practice_tumor_growth() -> None:
    st.markdown("**Will treatment win?** Compare growth vs treatment rates.")
    c1, c2, c3 = st.columns(3)
    with c1:
        size0 = st.number_input("Initial size", 1.0, 20.0, 5.0, key="pr_tg_s")
    with c2:
        growth = st.slider("Growth rate", 0.01, 0.25, 0.08, key="pr_tg_r")
    with c3:
        treat = st.slider("Treatment effect", 0.0, 0.25, 0.06, key="pr_tg_d")

    net = growth - treat
    size_10 = size0 * (2.71828 ** (net * 10))
    size_50 = size0 * (2.71828 ** (net * 50))

    st.markdown(f"**Net rate:** {net:+.3f} per period")
    st.markdown(f"**Size after 10 periods:** {size_10:.1f}")
    st.markdown(f"**Size after 50 periods:** {size_50:.1f}")
    st.latex(r"Size(t) = Size_0 \times e^{(growth - treatment) \times t}")
    if net > 0:
        st.error("Treatment is not strong enough — tumor grows.")
    else:
        st.success("Treatment dominates — tumor shrinks over time.")


def _practice_accumulation() -> None:
    st.markdown("**Small changes add up** — compound a rate over time.")
    c1, c2, c3 = st.columns(3)
    with c1:
        start = st.number_input("Starting value", 1.0, 1000.0, 100.0, key="pr_ac_s")
    with c2:
        rate = st.slider("Per-period change (%)", -20, 20, 5, key="pr_ac_r") / 100
    with c3:
        periods = st.number_input("Periods", 1, 100, 20, key="pr_ac_n")

    final = start * ((1 + rate) ** periods)
    st.markdown(f"**After {periods} periods:** {final:.2f}")
    st.latex(r"Final = Start \times (1 + rate)^{periods}")
    st.caption("This is discrete compounding — the same idea behind drug decay, tumor growth, and interest.")


def _practice_gradient_step() -> None:
    st.markdown("**One gradient descent step** on f(x) = x².")
    x = st.slider("Current x", -5.0, 5.0, 3.0, key="pr_gd_x")
    lr = st.slider("Learning rate α", 0.01, 1.0, 0.1, key="pr_gd_lr")

    fx = x ** 2
    grad = 2 * x
    x_new = x - lr * grad
    fx_new = x_new ** 2

    st.markdown(f"f(x) = x²  →  f({x:.2f}) = {fx:.2f}")
    st.markdown(f"Gradient df/dx = 2x = {grad:.2f}")
    st.markdown(f"New x = x − α × gradient = {x:.2f} − {lr:.2f} × {grad:.2f} = **{x_new:.2f}**")
    st.markdown(f"New f(x) = {fx_new:.2f} ({'lower ✓' if fx_new < fx else 'higher — learning rate too high!'})")
    st.latex(r"x_{new} = x - \alpha \cdot \frac{df}{dx}")


def _practice_probability_compare() -> None:
    st.markdown("**Compare two probabilities** — which outcome is more likely?")
    c1, c2 = st.columns(2)
    with c1:
        p_a = st.slider("Outcome A probability (%)", 0, 100, 30, key="pr_pc_a")
    with c2:
        p_b = st.slider("Outcome B probability (%)", 0, 100, 45, key="pr_pc_b")

    st.markdown(f"**A:** {p_a}% · **B:** {p_b}% · **Neither:** {100 - p_a - p_b}%")
    if p_a + p_b > 100:
        st.error("Probabilities exceed 100% — adjust your inputs.")
    elif p_a > p_b:
        st.info(f"A is more likely by {p_a - p_b} percentage points.")
    elif p_b > p_a:
        st.info(f"B is more likely by {p_b - p_a} percentage points.")
    else:
        st.info("Both outcomes are equally likely.")
