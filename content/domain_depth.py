"""Depth layer: unique simulations, case studies, and data hooks per domain."""

from content.case_studies import CASE_STUDIES

# domain title → enrichment
DOMAIN_DEPTH: dict[str, dict] = {
    "Quantitative Finance": {
        "simulation_id": "finance_quant_suite",
        "simulation_caption": "Tail-risk Monte Carlo, Markowitz efficient frontier, and drawdown path analytics.",
        "case_study_ids": ["finance_black_scholes", "finance_2008_crisis"],
        "data_source": "finance",
    },
    "Hedge Funds & Alternative Risk": {
        "simulation_id": "finance_quant_suite",
        "simulation_caption": "Drawdown and tail-risk lens for alternative book dynamics.",
        "case_study_ids": ["finance_2008_crisis", "finance_black_scholes"],
        "data_source": "finance",
    },
    "Gambling, Poker & Decision Mathematics": {
        "simulation_id": "poker_quant_suite",
        "simulation_caption": "Expected value, pot-odds thresholding, and Kelly growth sizing.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Epidemiology": {
        "simulation_id": "epidemic_sir",
        "simulation_caption": "SIR compartment model — peak infections and intervention timing.",
        "case_study_ids": ["epidemiology_covid_policy"],
        "data_source": "public_health",
    },
    "Artificial Intelligence": {
        "simulation_id": "ai_ml_suite",
        "simulation_caption": "Loss landscape gradient descent and toy neural-network training dynamics.",
        "case_study_ids": ["ai_llm_training", "ai_calibration"],
        "data_source": None,
    },
    "Machine Learning": {
        "simulation_id": "ai_ml_suite",
        "simulation_caption": "Optimization trajectory and train/loss monitoring for ML systems.",
        "case_study_ids": ["ai_llm_training", "ai_calibration"],
        "data_source": None,
    },
    "Astronomy & Astrophysics": {
        "simulation_id": "exoplanet_transit",
        "simulation_caption": "Transit photometry — infer planetary signal from stellar light curves.",
        "case_study_ids": ["astronomy_exoplanet"],
        "data_source": "astronomy",
    },
    "Space Exploration": {
        "simulation_id": "orbital_mechanics",
        "simulation_caption": "Keplerian orbit mechanics for mission design and trajectory planning.",
        "case_study_ids": ["astronomy_exoplanet"],
        "data_source": "astronomy",
    },
    "Cryptography": {
        "simulation_id": "crypto_rsa_demo",
        "simulation_caption": "Modular arithmetic laboratory and toy RSA encryption cycle.",
        "case_study_ids": ["crypto_tls"],
        "data_source": None,
    },
    "Sports Analytics": {
        "simulation_id": "sports_shrinkage",
        "simulation_caption": "Empirical Bayes shrinkage — project talent from noisy season samples.",
        "case_study_ids": ["sports_moneyball", "sports_win_probability"],
        "data_source": "sports",
    },
    "Fantasy Sports": {
        "simulation_id": "sports_shrinkage",
        "simulation_caption": "Shrinkage projections for lineup and draft valuation under uncertainty.",
        "case_study_ids": ["sports_moneyball"],
        "data_source": "sports",
    },
    "Weather Forecasting": {
        "simulation_id": "weather_uncertainty_cone",
        "simulation_caption": "Ensemble forecast cone — uncertainty growth with lead time.",
        "case_study_ids": ["weather_hurricane_cone"],
        "data_source": "weather",
    },
    "Climate Modeling": {
        "simulation_id": "climate_scenario_ensemble",
        "simulation_caption": "Multi-scenario climate ensemble with forcing and feedback uncertainty.",
        "case_study_ids": ["climate_paris"],
        "data_source": "weather",
    },
    "Medicine & Biological Modeling": {
        "simulation_id": "tumor_growth",
        "simulation_caption": "Competing proliferation vs treatment rates in tumor dynamics.",
        "case_study_ids": ["medicine_clinical_trial", "medicine_tumor_competing_rates"],
        "data_source": "public_health",
    },
    "Drug Development & Pharmacokinetics": {
        "simulation_id": "pharmacokinetics",
        "simulation_caption": "One-compartment PK — exposure (AUC) drives dosing decisions.",
        "case_study_ids": ["medicine_clinical_trial"],
        "data_source": "public_health",
    },
    "Election Forecasting": {
        "simulation_id": "election_forecast",
        "simulation_caption": "Electoral college Monte Carlo from state-level win probabilities.",
        "case_study_ids": [],
        "data_source": "elections",
    },
    "Actuarial Science": {
        "simulation_id": "actuarial_losses",
        "simulation_caption": "Frequency–severity compound model for annual loss capital.",
        "case_study_ids": ["finance_2008_crisis"],
        "data_source": "finance",
    },
    "Engineering & Optimization": {
        "simulation_id": "projectile",
        "simulation_caption": "Projectile trajectory — calculus of motion for design and launch optimization.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Robotics": {
        "simulation_id": "projectile",
        "simulation_caption": "Planar motion model — foundation for trajectory and path planning in configuration space.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Autonomous Vehicles": {
        "simulation_id": "kalman_tracking",
        "simulation_caption": "Kalman sensor fusion — predict/update cycle for position tracking under noise.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Simulation & Monte Carlo Methods": {
        "simulation_id": "monte_carlo_pi",
        "simulation_caption": "Monte Carlo integration — estimate π by random sampling.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Military Simulations & Wargaming": {
        "simulation_id": "monte_carlo_pi",
        "simulation_caption": "Monte Carlo scenario engine — same sampling logic scales to attrition and logistics stress tests.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Statistics & Prediction Systems": {
        "simulation_id": "regression_noise",
        "simulation_caption": "Noisy regression — estimate hidden linear structure from observational data.",
        "case_study_ids": ["sports_moneyball"],
        "data_source": None,
    },
    "Genetics": {
        "simulation_id": "genetic_drift",
        "simulation_caption": "Wright–Fisher drift — allele frequency paths under demographic randomness.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Supply Chain Optimization": {
        "simulation_id": "supply_chain",
        "simulation_caption": "Stochastic lead times and inventory balance — stockout risk under demand volatility.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Internet Recommendation Systems": {
        "simulation_id": "recommendation",
        "simulation_caption": "Latent structure in user–item ratings — collaborative filtering geometry.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Social Network Analysis": {
        "simulation_id": "epidemic_sir",
        "simulation_caption": "Contagion on a network — SIR dynamics as a model of diffusion and influence.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Search Engines": {
        "simulation_id": "recommendation",
        "simulation_caption": "Low-rank preference structure — analogous to latent ranking and relevance signals.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Cybersecurity": {
        "simulation_id": "actuarial_losses",
        "simulation_caption": "Compound cyber-loss model — incident frequency × severity for capital planning.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Casino Mathematics": {
        "simulation_id": "casino_edge",
        "simulation_caption": "House-edge accumulation over thousands of wagers — law of large numbers in practice.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Computer Graphics": {
        "simulation_id": "signal_wave",
        "simulation_caption": "Time-domain signal and FFT spectrum — basis of shading, audio, and image processing pipelines.",
        "case_study_ids": [],
        "data_source": None,
    },
    "Audio Processing & Music": {
        "simulation_id": "signal_wave",
        "simulation_caption": "Fourier decomposition of composite tones — core DSP for compression and synthesis.",
        "case_study_ids": [],
        "data_source": None,
    },
}


def apply_domain_depth(domains: dict[str, dict]) -> None:
    for domain in domains.values():
        domain.setdefault("case_studies", [])
    for name, domain in domains.items():
        depth = DOMAIN_DEPTH.get(name)
        if not depth:
            continue
        domain.update({k: v for k, v in depth.items() if k != "case_study_ids"})
        ids = depth.get("case_study_ids", [])
        if ids:
            domain["case_studies"] = [CASE_STUDIES[i] for i in ids if i in CASE_STUDIES]
