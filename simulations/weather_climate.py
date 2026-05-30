"""Weather and climate — forecast cones and scenario ensembles."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from simulations.plots import plot_line


def weather_uncertainty_cone():
    st.markdown("**Forecast uncertainty cone** — ensemble spread grows with lead time.")
    lead_days = st.slider("Forecast horizon (days)", 3, 14, 10, key="wc_days")
    temp0 = st.slider("Day-0 temperature (°F)", 20, 90, 72, key="wc_t0")
    daily_unc = st.slider("Daily uncertainty growth (°F)", 0.3, 2.5, 1.1, key="wc_grow")
    members = st.slider("Ensemble members", 10, 80, 40, key="wc_mem")

    fig, ax = plt.subplots()
    days = np.arange(lead_days + 1)
    all_paths = []
    for _ in range(members):
        shocks = np.cumsum(np.random.normal(0, daily_unc, lead_days))
        path = np.concatenate([[temp0], temp0 + shocks])
        all_paths.append(path)
        ax.plot(days, path, color="steelblue", alpha=0.12)

    all_paths = np.array(all_paths)
    median = np.median(all_paths, axis=0)
    p10 = np.percentile(all_paths, 10, axis=0)
    p90 = np.percentile(all_paths, 90, axis=0)
    ax.fill_between(days, p10, p90, color="#0ea5e9", alpha=0.25, label="10–90% cone")
    ax.plot(days, median, color="#0f172a", linewidth=2, label="Median forecast")
    ax.set_xlabel("Lead time (days)")
    ax.set_ylabel("Temperature (°F)")
    ax.set_title("Ensemble Temperature Forecast Cone")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)


def climate_scenario_ensemble():
    st.markdown("**Climate scenario ensemble** — forcing pathways and feedback uncertainty.")
    scenarios = {
        "Low mitigation": (1.2, 0.04),
        "Current policies": (2.0, 0.05),
        "High emissions": (3.2, 0.06),
    }
    years = st.slider("Projection years", 30, 120, 80, key="cl_y")
    runs = st.slider("Ensemble runs per scenario", 20, 150, 60, key="cl_r")

    fig, ax = plt.subplots()
    for name, (forcing, sens) in scenarios.items():
        bundle = []
        for _ in range(runs):
            temp = [0.0]
            f = forcing * np.random.uniform(0.85, 1.15)
            s = sens * np.random.uniform(0.8, 1.2)
            for _ in range(years):
                temp.append(temp[-1] + (f - s * temp[-1]) * 0.04)
            bundle.append(temp)
            ax.plot(temp, alpha=0.08)
        med = np.median(bundle, axis=0)
        ax.plot(med, linewidth=2, label=name)

    ax.set_xlabel("Year")
    ax.set_ylabel("Global temperature anomaly (index)")
    ax.set_title("Climate Scenario Ensemble")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)
