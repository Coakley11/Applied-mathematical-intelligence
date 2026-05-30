"""Backward-compatible entry point for simulations."""

from simulations.registry import SIMULATION_COUNT, run_simulation

__all__ = ["run_simulation", "SIMULATION_COUNT"]
