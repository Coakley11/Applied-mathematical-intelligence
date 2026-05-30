"""Simulation registry — maps domain simulation_id to runner functions."""

import streamlit as st

from simulations import legacy
from simulations.ai_learning import ai_ml_suite
from simulations.astronomy_sci import exoplanet_transit, orbital_mechanics
from simulations.crypto_demo import crypto_rsa_demo
from simulations.finance_risk import finance_quant_suite
from simulations.poker_math import poker_quant_suite
from simulations.sports_proj import sports_shrinkage
from simulations.weather_climate import climate_scenario_ensemble, weather_uncertainty_cone

SIMULATION_RUNNERS = {
    # Domain-specific suites
    "finance_quant_suite": finance_quant_suite,
    "poker_quant_suite": poker_quant_suite,
    "ai_ml_suite": ai_ml_suite,
    "exoplanet_transit": exoplanet_transit,
    "orbital_mechanics": orbital_mechanics,
    "crypto_rsa_demo": crypto_rsa_demo,
    "sports_shrinkage": sports_shrinkage,
    "weather_uncertainty_cone": weather_uncertainty_cone,
    "climate_scenario_ensemble": climate_scenario_ensemble,
    # Specialized tools
    "pharmacokinetics": legacy.pharmacokinetics,
    "tumor_growth": legacy.tumor_growth,
    "epidemic_sir": legacy.epidemic_sir,
    "election_forecast": legacy.election_forecast,
    "actuarial_losses": legacy.actuarial_losses,
    "genetic_drift": legacy.genetic_drift,
    "supply_chain": legacy.supply_chain,
    "casino_edge": legacy.casino_edge,
    "recommendation": legacy.recommendation,
    "signal_wave": legacy.signal_wave,
    "regression_noise": legacy.regression_noise,
    "projectile": legacy.projectile,
    "monte_carlo_pi": legacy.monte_carlo_pi,
    "kalman_tracking": legacy.kalman_tracking,
}

SIMULATION_COUNT = len(SIMULATION_RUNNERS)


def run_simulation(simulation_id: str | None) -> None:
    if not simulation_id:
        st.info("Simulation for this domain is in development.")
        return
    runner = SIMULATION_RUNNERS.get(simulation_id)
    if runner:
        runner()
    else:
        st.warning(f"Unknown simulation: {simulation_id}")
