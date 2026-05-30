"""Interactive lab simulation runners."""

from simulations.labs.ai_training import run_ai_training_lab
from simulations.labs.finance import run_finance_lab
from simulations.labs.forecasting import run_forecasting_lab
from simulations.labs.optimization import run_optimization_lab
from simulations.labs.poker import run_poker_lab
from simulations.labs.sports_betting import run_sports_betting_lab

LAB_RUNNERS = {
    "lab_poker": run_poker_lab,
    "lab_sports_betting": run_sports_betting_lab,
    "lab_finance": run_finance_lab,
    "lab_forecasting": run_forecasting_lab,
    "lab_optimization": run_optimization_lab,
    "lab_ai_training": run_ai_training_lab,
}

LAB_RUNNER_COUNT = len(LAB_RUNNERS)
