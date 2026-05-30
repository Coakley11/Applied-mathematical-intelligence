"""Forecasting Lab — trend fitting and uncertainty."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


def run_forecasting_lab() -> None:
    st.markdown("#### Generate or configure data")

    col1, col2 = st.columns(2)
    with col1:
        data_mode = st.radio("Data source", ["Generate", "Manual trend"], horizontal=True, key="fc_mode")
        n_points = st.slider("Historical points", 20, 300, 80, key="fc_n")
        true_slope = st.slider("True trend (slope)", -2.0, 5.0, 2.5, step=0.1, key="fc_slope")
        intercept = st.slider("Starting level", 0, 200, 50, key="fc_int")
    with col2:
        noise = st.slider("Noise level (σ)", 0.0, 40.0, 12.0, key="fc_noise")
        forecast_steps = st.slider("Forecast steps ahead", 5, 60, 20, key="fc_fwd")
        seed = st.slider("Random seed", 0, 99, 42, key="fc_seed")

    rng = np.random.default_rng(seed)
    t_hist = np.arange(n_points)
    y_hist = intercept + true_slope * t_hist + rng.normal(0, noise, n_points)

    coeffs = np.polyfit(t_hist, y_hist, 1)
    est_slope, est_intercept = coeffs[0], coeffs[1]
    y_fit = est_slope * t_hist + est_intercept
    ss_res = np.sum((y_hist - y_fit) ** 2)
    ss_tot = np.sum((y_hist - np.mean(y_hist)) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    t_future = np.arange(n_points, n_points + forecast_steps)
    y_forecast = est_slope * t_future + est_intercept
    forecast_se = noise * np.sqrt(1 + 1 / n_points + (t_future - np.mean(t_hist)) ** 2 / np.sum((t_hist - np.mean(t_hist)) ** 2))
    upper = y_forecast + 1.96 * forecast_se
    lower = y_forecast - 1.96 * forecast_se

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.scatter(t_hist, y_hist, alpha=0.5, s=25, color="#64748b", label="Observed")
    ax.plot(t_hist, y_fit, color="#0ea5e9", linewidth=2, label="Fitted trend")
    ax.plot(t_future, y_forecast, color="#059669", linewidth=2, linestyle="--", label="Forecast")
    ax.fill_between(t_future, lower, upper, alpha=0.2, color="#059669", label="95% interval")
    ax.axvline(n_points - 0.5, color="#94a3b8", linestyle=":", linewidth=1)
    ax.set_xlabel("Time period")
    ax.set_ylabel("Value")
    ax.set_title("Trend fit and forecast with uncertainty band")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estimated slope", f"{est_slope:.3f}")
    m2.metric("True slope", f"{true_slope:.3f}")
    m3.metric("R² (signal captured)", f"{r_squared:.2f}")
    m4.metric(f"Forecast at t+{forecast_steps}", f"{y_forecast[-1]:.1f}")

    if r_squared > 0.7:
        st.success(
            f"Strong signal — R² = {r_squared:.2f}. The trend explains most variation; "
            "forecasts are relatively reliable near the data."
        )
    elif r_squared > 0.4:
        st.info(
            f"Moderate signal — R² = {r_squared:.2f}. Some pattern is visible but noise is significant. "
            "Widen uncertainty bands before making decisions."
        )
    else:
        st.warning(
            f"Weak signal — R² = {r_squared:.2f}. High noise dominates; "
            "forecasts far ahead are unreliable. Collect more data or reduce noise."
        )

    st.markdown("##### What the math is doing")
    st.latex(r"\hat{y} = \beta_0 + \beta_1 t \quad\quad R^2 = 1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}")
    st.caption(
        "Uncertainty bands widen as you forecast further — extrapolation is inherently riskier. "
        "This is how election models, sales forecasts, and epidemiology projections communicate confidence."
    )
