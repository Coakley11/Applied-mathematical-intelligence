"""Quantitative finance simulations — tail risk, frontier, drawdown."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from simulations.plots import plot_line


def finance_quant_suite():
    tab1, tab2, tab3 = st.tabs(["Tail risk", "Efficient frontier", "Drawdown"])

    with tab1:
        _tail_risk()
    with tab2:
        _efficient_frontier()
    with tab3:
        _drawdown_model()


def _tail_risk():
    st.markdown("**Monte Carlo tail-risk engine** — distribution of terminal wealth and crash scenarios.")
    mu = st.slider("Expected annual return", -0.05, 0.15, 0.07, key="tail_mu")
    sigma = st.slider("Annual volatility", 0.05, 0.45, 0.18, key="tail_sig")
    years = st.slider("Horizon (years)", 1, 30, 10, key="tail_y")
    paths = st.slider("Simulated paths", 500, 5000, 2000, key="tail_n")
    capital = st.number_input("Initial capital ($)", value=100_000, key="tail_cap")

    finals = []
    max_dd = []
    for _ in range(paths):
        v = capital
        peak = v
        worst_dd = 0.0
        for _ in range(years):
            v *= 1 + np.random.normal(mu, sigma)
            peak = max(peak, v)
            worst_dd = min(worst_dd, (v - peak) / peak)
        finals.append(v)
        max_dd.append(worst_dd)

    finals = np.array(finals)
    fig, ax = plt.subplots()
    ax.hist(finals, bins=50, color="steelblue", alpha=0.85)
    ax.axvline(capital, color="crimson", linestyle="--", label="Starting capital")
    ax.axvline(np.percentile(finals, 5), color="orange", linestyle="--", label="5th percentile")
    ax.set_title("Terminal Wealth Distribution")
    ax.set_xlabel("Wealth ($)")
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("VaR 5% (terminal)", f"${np.percentile(finals, 5):,.0f}")
    c2.metric("CVaR 5%", f"${np.mean(finals[finals <= np.percentile(finals, 5)]):,.0f}")
    c3.metric("P(ruin >30% DD)", f"{np.mean(np.array(max_dd) < -0.30):.1%}")
    c4.metric("Median wealth", f"${np.median(finals):,.0f}")


def _efficient_frontier():
    st.markdown("**Mean–variance efficient frontier** — risk-return tradeoff for two risky assets + risk-free rate.")
    rf = st.slider("Risk-free rate (annual)", 0.0, 0.08, 0.03, key="ef_rf")
    mu_a = st.slider("Asset A expected return", 0.02, 0.20, 0.10, key="ef_mua")
    mu_b = st.slider("Asset B expected return", 0.02, 0.20, 0.12, key="ef_mub")
    sig_a = st.slider("Asset A volatility", 0.05, 0.40, 0.18, key="ef_sa")
    sig_b = st.slider("Asset B volatility", 0.05, 0.40, 0.22, key="ef_sb")
    rho = st.slider("Correlation A–B", -0.9, 0.9, 0.35, key="ef_rho")

    weights = np.linspace(0, 1, 80)
    port_mu = []
    port_sig = []
    for w in weights:
        m = w * mu_a + (1 - w) * mu_b
        v = (
            w ** 2 * sig_a ** 2
            + (1 - w) ** 2 * sig_b ** 2
            + 2 * w * (1 - w) * rho * sig_a * sig_b
        )
        port_mu.append(m)
        port_sig.append(np.sqrt(v))

    fig, ax = plt.subplots()
    ax.plot(np.array(port_sig) * 100, np.array(port_mu) * 100, linewidth=2, color="#0ea5e9")
    ax.scatter([sig_a * 100, sig_b * 100], [mu_a * 100, mu_b * 100], s=80, c=["#6366f1", "#059669"])
    ax.set_xlabel("Portfolio volatility (%)")
    ax.set_ylabel("Expected return (%)")
    ax.set_title("Efficient Frontier (two-asset mix)")
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Markowitz (1952): diversification shifts the feasible risk-return set.")


def _drawdown_model():
    st.markdown("**Drawdown path analytics** — peak-to-trough loss dynamics under correlated shocks.")
    months = st.slider("Months simulated", 24, 240, 120, key="dd_m")
    crash_prob = st.slider("Crisis month probability", 0.0, 0.15, 0.04, key="dd_cp")
    daily_vol = st.slider("Monthly vol (normal times)", 0.01, 0.12, 0.04, key="dd_v")

    rng = np.random.default_rng(42)
    returns = rng.normal(0.006, daily_vol, months)
    crisis = rng.random(months) < crash_prob
    returns[crisis] = rng.normal(-0.12, 0.06, crisis.sum())

    wealth = 100 * np.cumprod(1 + returns)
    peak = np.maximum.accumulate(wealth)
    drawdown = (wealth - peak) / peak

    fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    ax[0].plot(wealth, color="#0f172a")
    ax[0].plot(peak, linestyle="--", color="#94a3b8", label="Running peak")
    ax[0].set_ylabel("Index")
    ax[0].set_title("Wealth vs Running Peak")
    ax[0].legend()
    ax[0].grid(True)
    ax[1].fill_between(range(months), drawdown * 100, 0, color="#ef4444", alpha=0.5)
    ax[1].set_ylabel("Drawdown %")
    ax[1].set_xlabel("Month")
    ax[1].grid(True)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.metric("Maximum drawdown", f"{drawdown.min():.1%}")
    st.metric("Months underwater", int(np.sum(drawdown < -0.01)))
