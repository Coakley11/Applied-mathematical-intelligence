"""Interactive mini-calculators for Math Idea Explorer."""

import math

import streamlit as st


def render_idea_play(interactive: str, key_prefix: str, defaults: dict | None = None) -> None:
    defaults = defaults or {}
    handlers = {
        "ev_bet": _play_ev,
        "derivative": _play_derivative,
        "integral": _play_integral,
        "quadratic": _play_quadratic,
        "confidence_interval": _play_ci,
        "exponential": _play_exponential,
        "optimization": _play_optimization,
        "ml_split": _play_ml,
    }
    fn = handlers.get(interactive, _play_generic)
    fn(key_prefix, defaults)


def _play_ev(key_prefix: str, defaults: dict) -> None:
    st.caption("Adjust probabilities and payoffs — see expected value change.")
    p = st.slider("P(success) %", 1, 99, int(defaults.get("p", 40)), key=f"{key_prefix}_iep")
    win = st.number_input("Profit if success ($)", 1.0, 10000.0, float(defaults.get("win", 200)), key=f"{key_prefix}_iew")
    lose = st.number_input("Loss if fail ($)", 1.0, 10000.0, float(defaults.get("lose", 200)), key=f"{key_prefix}_iel")
    ev = (p / 100) * win - (1 - p / 100) * lose
    st.metric("Expected value", f"${ev:+.2f}")


def _play_derivative(key_prefix: str, defaults: dict) -> None:
    st.caption("Linear approximation: f(x) ≈ f(a) + f′(a)(x−a)")
    a = st.number_input("At x = a", value=float(defaults.get("a", 2.0)), key=f"{key_prefix}_ida")
    fa = st.number_input("f(a)", value=float(defaults.get("fa", 5.0)), key=f"{key_prefix}_idfa")
    slope = st.number_input("Slope f′(a)", value=float(defaults.get("slope", 3.0)), key=f"{key_prefix}_ids")
    dx = st.slider("Small change Δx", -2.0, 2.0, 0.1, key=f"{key_prefix}_iddx")
    approx = fa + slope * dx
    st.metric(f"f({a + dx:.1f}) ≈", f"{approx:.2f}")


def _play_integral(key_prefix: str, defaults: dict) -> None:
    st.caption("Rectangle sum — area under a constant rate")
    rate = st.slider("Rate (units per hour)", 1, 100, int(defaults.get("rate", 60)), key=f"{key_prefix}_iir")
    hours = st.slider("Hours", 1, 24, int(defaults.get("hours", 2)), key=f"{key_prefix}_iih")
    st.metric("Total accumulated", f"{rate * hours} units")


def _play_quadratic(key_prefix: str, defaults: dict) -> None:
    st.caption("Solve (x+h)² = k style — two solutions when k > 0")
    h = st.number_input("h in (x+h)²", value=float(defaults.get("h", 3)), key=f"{key_prefix}_iqh")
    k = st.number_input("k (right-hand side)", value=float(defaults.get("k", 7)), key=f"{key_prefix}_iqk")
    if k < 0:
        st.warning("No real solutions when k < 0.")
    else:
        root = k ** 0.5
        st.write(f"x = −{h} + {root:.3f}  or  x = −{h} − {root:.3f}")


def _play_ci(key_prefix: str, defaults: dict) -> None:
    mean = st.number_input("Sample mean", value=float(defaults.get("mean", 50)), key=f"{key_prefix}_icm")
    sd = st.number_input("Std dev", min_value=0.01, value=float(defaults.get("sd", 10)), key=f"{key_prefix}_ics")
    n = st.number_input("Sample size n", min_value=2, value=int(defaults.get("n", 30)), key=f"{key_prefix}_icn")
    se = sd / (n ** 0.5)
    margin = 1.96 * se
    st.metric("Approx. 95% CI", f"{mean - margin:.2f} to {mean + margin:.2f}")


def _play_exponential(key_prefix: str, defaults: dict) -> None:
    v0 = st.number_input("Starting value", value=float(defaults.get("v0", 100)), key=f"{key_prefix}_iev0")
    rate = st.slider("Growth rate % per period", -50, 50, int(defaults.get("rate", 10)), key=f"{key_prefix}_ier")
    t = st.slider("Periods", 1, 24, int(defaults.get("t", 6)), key=f"{key_prefix}_iet")
    v = v0 * ((1 + rate / 100) ** t)
    st.metric(f"Value after {t} periods", f"{v:.1f}")


def _play_optimization(key_prefix: str, defaults: dict) -> None:
    benefit = st.number_input("Benefit per unit", value=float(defaults.get("benefit", 10)), key=f"{key_prefix}_iob")
    cost = st.number_input("Cost per unit", value=float(defaults.get("cost", 4)), key=f"{key_prefix}_ioc")
    cap = st.number_input("Capacity limit", value=float(defaults.get("cap", 100)), key=f"{key_prefix}_iocap")
    profit = benefit * cap - cost * cap
    st.metric("Profit at capacity", f"${profit:.0f}")
    if benefit <= cost:
        st.warning("Benefit ≤ cost — expanding loses money.")


def _play_ml(key_prefix: str, defaults: dict) -> None:
    tr = st.slider("Train %", 50, 100, int(defaults.get("tr", 95)), key=f"{key_prefix}_itr")
    va = st.slider("Val %", 50, 100, int(defaults.get("va", 80)), key=f"{key_prefix}_iva")
    st.metric("Gap", f"{tr - va} pts")


def _play_generic(key_prefix: str, defaults: dict) -> None:
    st.caption("Enter two numbers — see their ratio (simple quantitative check).")
    a = st.number_input("Value A", value=1.0, key=f"{key_prefix}_iga")
    b = st.number_input("Value B", value=2.0, key=f"{key_prefix}_igb")
    if b != 0:
        st.metric("A / B", f"{a / b:.3f}")
