"""Finance & Investing Lab — portfolio simulation."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


def run_finance_lab() -> None:
    st.markdown("#### Build your portfolio")

    col1, col2 = st.columns(2)
    with col1:
        capital = st.number_input("Starting capital ($)", value=100_000, step=10_000, key="fn_cap")
        years = st.slider("Investment horizon (years)", 1, 40, 15, key="fn_yrs")
        n_paths = st.slider("Simulated paths", 500, 5000, 1500, key="fn_paths")
    with col2:
        w_stocks = st.slider("Stocks allocation (%)", 0, 100, 70, key="fn_ws") / 100
        w_bonds = st.slider("Bonds allocation (%)", 0, 100, 30, key="fn_wb") / 100
        total_w = w_stocks + w_bonds
        if abs(total_w - 1.0) > 0.01:
            st.caption(f"Allocations sum to {total_w:.0%} — normalized automatically.")
            w_stocks /= total_w
            w_bonds /= total_w

    mu_s = st.slider("Stocks expected return (annual %)", 2, 15, 9, key="fn_ms") / 100
    mu_b = st.slider("Bonds expected return (annual %)", 0, 8, 4, key="fn_mb") / 100
    sig_s = st.slider("Stocks volatility (annual %)", 5, 40, 18, key="fn_ss") / 100
    sig_b = st.slider("Bonds volatility (annual %)", 2, 20, 6, key="fn_sb") / 100

    port_mu = w_stocks * mu_s + w_bonds * mu_b
    port_sig = np.sqrt(w_stocks ** 2 * sig_s ** 2 + w_bonds ** 2 * sig_b ** 2)

    st.markdown("---")
    st.markdown("#### Monte Carlo results")

    rng = np.random.default_rng(7)
    finals = np.zeros(n_paths)
    max_drawdowns = np.zeros(n_paths)

    for i in range(n_paths):
        v = capital
        peak = v
        worst_dd = 0.0
        for _ in range(years):
            r = rng.normal(port_mu, port_sig)
            v *= 1 + r
            peak = max(peak, v)
            worst_dd = min(worst_dd, (v - peak) / peak)
        finals[i] = v
        max_drawdowns[i] = worst_dd

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))

    axes[0].hist(finals, bins=45, color="#0ea5e9", alpha=0.85, edgecolor="white")
    axes[0].axvline(capital, color="#ef4444", linestyle="--", linewidth=1.5, label="Start")
    axes[0].axvline(np.median(finals), color="#059669", linestyle="--", linewidth=1.5, label="Median")
    axes[0].set_xlabel("Terminal wealth ($)")
    axes[0].set_title("Wealth distribution after horizon")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    sample = min(80, n_paths)
    t_axis = np.arange(years + 1)
    for _ in range(sample):
        path = [capital]
        v = capital
        for _ in range(years):
            v *= 1 + rng.normal(port_mu, port_sig)
            path.append(v)
        axes[1].plot(t_axis, path, alpha=0.15, color="#6366f1", linewidth=0.8)
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Portfolio value ($)")
    axes[1].set_title(f"Sample paths ({sample} of {n_paths})")
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    p_loss = np.mean(finals < capital)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Expected return", f"{port_mu:.1%}")
    c2.metric("Portfolio volatility", f"{port_sig:.1%}")
    c3.metric("Median outcome", f"${np.median(finals):,.0f}")
    c4.metric("P(ending below start)", f"{p_loss:.1%}")
    c5.metric("Worst 5% outcome", f"${np.percentile(finals, 5):,.0f}")

    if port_mu > 0.06 and port_sig > 0.15:
        st.info(
            "Higher expected return comes with wider outcomes. "
            "Calculus-like **compounding** grows wealth exponentially in expectation, "
            "but **volatility** creates real probability of interim and terminal loss."
        )
    elif p_loss > 0.25:
        st.warning(
            f"There is a {p_loss:.0%} chance of losing money over {years} years. "
            "Longer horizons and lower volatility reduce this risk."
        )
    else:
        st.success(
            "This allocation shows favorable long-run expected growth with manageable downside risk "
            "at the 5th percentile."
        )

    st.caption(
        "Geometric Brownian Motion approximation — educational only, not investment advice."
    )
