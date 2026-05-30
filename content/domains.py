"""Applied domain pages — professional applied mathematics content."""

from __future__ import annotations


def _domain(
    title: str,
    tagline: str,
    primary_lenses: list[str],
    why_matters: str,
    concepts: list[str],
    professional_applications: list[str],
    breakthroughs: list[dict],
    ai_connection: str,
    excel_projects: list[str],
    python_projects: list[str],
    portfolio_ideas: list[str],
    simulation_id: str,
    interpretation: str,
    simulation_caption: str = "",
    portfolio_tip: str = "",
) -> dict:
    return {
        "title": title,
        "tagline": tagline,
        "primary_lenses": primary_lenses,
        "why_matters": why_matters,
        "concepts": concepts,
        "professional_applications": professional_applications,
        "breakthroughs": breakthroughs,
        "ai_connection": ai_connection,
        "excel_projects": excel_projects,
        "python_projects": python_projects,
        "portfolio_ideas": portfolio_ideas,
        "simulation_id": simulation_id,
        "interpretation": interpretation,
        "simulation_caption": simulation_caption or (
            f"Interactive model illustrating core dynamics in {title}."
        ),
        "portfolio_tip": portfolio_tip,
    }


DOMAINS: dict[str, dict] = {}

# --- Accumulation / calculus-heavy ---

DOMAINS["Drug Development & Pharmacokinetics"] = _domain(
    title="Drug Development & Pharmacokinetics",
    tagline="Mathematics of **how molecules enter, distribute, metabolize, and clear** — the foundation of dosing, trials, and therapeutic windows.",
    primary_lenses=["Calculus / Accumulation", "Statistics / Pattern Detection"],
    why_matters="""
    A drug that works in a petri dish fails in patients if concentration never reaches the target tissue,
    or stays toxic too long. Pharmaceutical R&D depends on **dynamic models** of concentration over time,
    not static averages. Calculus links infusion rates to exposure; statistics designs trials that detect
    real efficacy against biological noise.
    """,
    concepts=[
        "Ordinary differential equations for absorption and elimination",
        "Half-life and area-under-the-curve (AUC) exposure metrics",
        "Compartment models (one- and two-compartment PK)",
        "Dose-response curves and therapeutic index",
        "Survival analysis and time-to-event endpoints in trials",
        "Bayesian adaptive trial designs",
    ],
    professional_applications=[
        "Phase I dose-escalation using PK/PD models",
        "PBPK simulation before first-in-human trials",
        "Population PK across age, weight, and organ function",
        "Regulatory submissions linking exposure to efficacy and safety",
        "Formulation design for sustained release",
    ],
    breakthroughs=[
        {"title": "One-compartment PK models", "era": "Mid 20th century", "description": "Formalized drug clearance and half-life, enabling rational dosing schedules."},
        {"title": "PBPK modeling", "era": "1990s–present", "description": "Physiology-based models predict tissue concentrations without exhaustive human trials."},
        {"title": "Adaptive platform trials", "era": "2010s–present", "description": "Bayesian statistics accelerates learning across multiple treatments simultaneously."},
    ],
    ai_connection="""
    AI predicts molecular properties (ADMET), generates candidate structures, and fits PK models to sparse data.
    Deep learning on clinical time-series forecasts toxicity; generative models propose new compounds optimized
    for target exposure profiles.
    """,
    excel_projects=[
        "Build a half-life calculator: dose, k_elim, and predicted C(t) at hourly steps.",
        "Simulate repeated dosing and steady-state accumulation.",
    ],
    python_projects=[
        "Solve a one-compartment ODE with scipy.integrate and plot concentration vs time.",
        "Monte Carlo over clearance values to show inter-patient variability bands.",
    ],
    portfolio_ideas=[
        "PK dashboard for a fictional oncology drug with therapeutic window shading.",
        "Compare oral vs IV dosing achieving the same AUC.",
        "Adaptive trial simulation with early stopping rules.",
    ],
    simulation_id="pharmacokinetics",
    interpretation="""
    The curve shows **accumulation and clearance** as competing processes. Professionals ask whether
    peak concentration exceeds toxicity, whether trough stays above minimum effective level, and how
    missed doses perturb steady state — all integral questions over time.
    """,
)

DOMAINS["Medicine & Biological Modeling"] = _domain(
    title="Medicine & Biological Modeling",
    tagline="**Competing growth and treatment rates** in tumors, infections, and organ systems — where calculus meets clinical uncertainty.",
    primary_lenses=["Calculus / Accumulation", "Probability / Uncertainty", "Statistics / Pattern Detection"],
    why_matters="Biology is dynamic. Treatment success often means making a **negative net growth rate** — not a single measurement. Mathematical oncology, epidemiology, and physiology share this structure.",
    concepts=["Exponential and logistic growth", "Net rate = growth − treatment − clearance", "Survival curves and hazard functions", "Clinical trial power and effect sizes", "Patient heterogeneity as random effects"],
    professional_applications=["Tumor growth kinetics in trial planning", "ICU pharmacology and ventilator dynamics", "Epidemic forecasting for hospital surge", "Diagnostic test evaluation with Bayes"],
    breakthroughs=[
        {"title": "Logistic growth models", "era": "1838–1920s", "description": "Verhulst and later ecologists modeled saturating growth — later adapted to tumors."},
        {"title": "Kaplan–Meier survival", "era": "1958", "description": "Nonparametric survival analysis became standard for cancer trials."},
    ],
    ai_connection="Medical AI segments tumors on imaging, predicts progression from EHR time-series, and personalizes dosing using PK models learned from populations.",
    excel_projects=["Model tumor size over 24 months with and without treatment columns."],
    python_projects=["Simulate patient-level random effects on growth rate; compare treatment arms."],
    portfolio_ideas=["Treatment crossover simulation with uncertainty bands.", "Survival curve replication from published trial summary stats."],
    simulation_id="tumor_growth",
    interpretation="When treatment effect exceeds natural growth, the system predicts decline — the mathematical heart of many therapy strategies (not a clinical device).",
)

DOMAINS["Epidemiology"] = _domain(
    title="Epidemiology",
    tagline="**Population-scale dynamics** of infection — how contact rates, immunity, and intervention change the shape of epidemics.",
    primary_lenses=["Calculus / Accumulation", "Simulation / Alternate Futures", "Statistics / Pattern Detection"],
    why_matters="Policy decisions (lockdowns, vaccination targets, hospital staffing) require forecasting **how fast cases accumulate** and when peaks occur. Epidemiology is applied calculus and simulation on networks of humans.",
    concepts=["SIR / SEIR compartment models", "Reproduction number R₀ and effective R_t", "Exponential early-phase growth", "Herd immunity thresholds", "Surveillance statistics and outbreak detection"],
    professional_applications=["CDC and WHO scenario planning", "Vaccine trial design and effectiveness monitoring", "Hospital capacity forecasting", "Modeling variant emergence and waning immunity"],
    breakthroughs=[
        {"title": "Kermack–McKendrick SIR", "era": "1927", "description": "Foundational compartment model linking infection rates to epidemic curves."},
        {"title": "R₀ formalization", "era": "20th century", "description": "Quantified how many secondary cases one infection generates on average."},
    ],
    ai_connection="ML nowcasts outbreaks from search trends, mobility data, and wastewater; graph neural networks model contact structure; AI assists genomic surveillance of variants.",
    excel_projects=["Discrete-time SIR spreadsheet with contact rate slider."],
    python_projects=["Agent-based or ODE SIR with Monte Carlo over R₀; plot peak timing distributions."],
    portfolio_ideas=["Vaccination threshold analysis for a fictional pathogen.", "Compare intervention timing on cumulative deaths distributions."],
    simulation_id="epidemic_sir",
    interpretation="Small changes in contact rate shift peak timing and total infections dramatically — why early data and uncertainty bands drive policy.",
)

DOMAINS["Genetics"] = _domain(
    title="Genetics",
    tagline="**Randomness, inheritance, and population change** — the mathematics of variation, selection, and modern genomic inference.",
    primary_lenses=["Probability / Uncertainty", "Statistics / Pattern Detection", "Simulation / Alternate Futures"],
    why_matters="Genetic variation underlies disease risk, evolution, agriculture, and forensic identity. Genetics uses probability for inheritance patterns and statistics for genome-wide association at millions of loci.",
    concepts=["Hardy–Weinberg equilibrium", "Genetic drift and selection", "Linkage and association statistics", "Sequencing error and variant calling uncertainty", "Heritability and polygenic scores"],
    professional_applications=["GWAS for disease loci", "Breeding program optimization", "Forensic DNA match probabilities", "CRISPR off-target risk assessment", "Population genetics in conservation"],
    breakthroughs=[
        {"title": "Mendelian inheritance", "era": "1865", "description": "Discrete trait transmission — later merged with population genetics."},
        {"title": "Human Genome Project", "era": "2003", "description": "Enabled base-pair resolution statistics across cohorts."},
    ],
    ai_connection="Deep learning predicts protein structure (AlphaFold), variant pathogenicity, and gene expression from sequence; generative models design synthetic DNA libraries.",
    excel_projects=["Simulate allele frequency over generations with selection coefficient."],
    python_projects=["Wright–Fisher genetic drift Monte Carlo across many populations."],
    portfolio_ideas=["GWAS-style toy dataset: multiple testing correction demo.", "Polygenic risk score construction from simulated SNPs."],
    simulation_id="genetic_drift",
    interpretation="Drift shows how randomness alone changes allele frequencies — essential intuition before attributing every shift to selection.",
)

DOMAINS["Climate Modeling"] = _domain(
    title="Climate Modeling",
    tagline="**Energy balance, accumulation of heat, and ensemble futures** — Earth's climate as a coupled dynamical system.",
    primary_lenses=["Calculus / Accumulation", "Simulation / Alternate Futures", "Statistics / Pattern Detection"],
    why_matters="Climate policy spans decades. Decisions rely on models integrating radiation, oceans, ice, and emissions — not weather next week. Calculus describes fluxes; simulation explores parameter uncertainty.",
    concepts=["Energy balance equations", "Radiative forcing", "Coupled ODE/PDE climate models", "Ensemble forecasts and uncertainty bands", "Carbon cycle accumulation"],
    professional_applications=["IPCC scenario analysis", "Insurance catastrophe models for climate peril", "Renewable siting and grid planning", "Agricultural adaptation planning"],
    breakthroughs=[
        {"title": "Arrhenius greenhouse estimate", "era": "1896", "description": "Early quantitative link between CO₂ and global temperature."},
        {"title": "General circulation models", "era": "1960s–present", "description": "3D numerical simulations of atmosphere and ocean."},
    ],
    ai_connection="ML emulates expensive climate submodels, downscales global runs to cities, and detects extreme events; physics-informed nets embed conservation laws.",
    excel_projects=["Simple energy balance box model with emissions scenario slider."],
    python_projects=["Integrate forcing vs feedback parameters; plot temperature anomaly paths."],
    portfolio_ideas=["Compare RCP scenarios on cumulative warming distributions.", "Sea-level rise sensitivity to ice-sheet parameter uncertainty."],
    simulation_id="climate_balance",
    interpretation="Feedback loops turn small forcing changes into large long-run temperature shifts — the core reason accumulation thinking matters.",
)

# --- Probability / uncertainty ---

DOMAINS["Quantitative Finance"] = _domain(
    title="Quantitative Finance",
    tagline="**Random walks, volatility, and optimization** — markets as stochastic systems, not fixed returns.",
    primary_lenses=["Probability / Uncertainty", "Simulation / Alternate Futures", "Optimization / Improvement"],
    why_matters="A 7% expected return does not mean +7% every year. Quant finance prices uncertainty, constructs hedges, and optimizes portfolios under constraints — the professional antidote to spreadsheet certainty.",
    concepts=["Geometric Brownian motion", "Volatility, correlation, and covariance matrices", "VaR and tail risk", "Black–Scholes and risk-neutral pricing", "Mean-variance and factor optimization"],
    professional_applications=["Derivative desk pricing and hedging", "Risk desk stress testing", "Algorithmic execution minimizing market impact", "Credit portfolio modeling"],
    breakthroughs=[
        {"title": "Brownian motion in finance", "era": "1900 / 1973", "description": "Bachelier and later Black–Scholes linked random walks to option prices."},
        {"title": "Markowitz portfolio theory", "era": "1952", "description": "Formalized risk-return tradeoff via covariance."},
    ],
    ai_connection="ML forecasts returns and volatility, detects regime change, and powers reinforcement learning for execution; LLMs parse filings for sentiment signals.",
    excel_projects=["Simulate 1,000 annual return paths; chart percentiles of terminal wealth."],
    python_projects=["Monte Carlo with fat tails; compare normal vs t-distributed shocks."],
    portfolio_ideas=["Two-asset efficient frontier with constraint on sector weight.", "Options hedging P&L simulation under volatility spikes."],
    simulation_id="monte_carlo_portfolio",
    interpretation="The distribution of outcomes — not the mean — drives solvency, leverage limits, and client risk conversations.",
)

DOMAINS["Hedge Funds & Alternative Risk"] = _domain(
    title="Hedge Funds & Alternative Risk",
    tagline="**Nonlinear payoffs, tail risk, and dynamic hedging** — where Gaussian intuition fails and simulation dominates.",
    primary_lenses=["Probability / Uncertainty", "Optimization / Improvement", "Simulation / Alternate Futures"],
    why_matters="Hedge strategies exploit mispricing, volatility, and correlation breakdowns. Success requires modeling **joint extreme events**, not average returns alone.",
    concepts=["Skew and kurtosis", "Dynamic hedging and Greeks", "Pairs trading and cointegration", "Leverage and drawdown pathology", "Regime-switching models"],
    professional_applications=["Long-short equity market-neutral books", "Volatility arbitrage and dispersion trades", "CTA trend following with risk parity overlays", "Fund-of-funds due diligence"],
    breakthroughs=[
        {"title": "CAPM and factor models", "era": "1960s–1990s", "description": "Decomposed returns into systematic and idiosyncratic components."},
        {"title": "Risk parity", "era": "2000s", "description": "Allocated risk budgets rather than capital weights alone."},
    ],
    ai_connection="Alternative data + ML for alpha signals; deep learning on order flow; RL for trade timing; NLP on macro news for regime detection.",
    excel_projects=["Drawdown distribution from simulated monthly hedge returns."],
    python_projects=["Simulate correlation spike in crisis; measure portfolio tail loss."],
    portfolio_ideas=["Pairs trade backtest with transaction costs and stop rules.", "Volatility strategy P&L under 2008-style correlation breakdown."],
    simulation_id="monte_carlo_portfolio",
    interpretation="Paths reveal drawdown depth and duration — metrics LPs scrutinize more than average annual return.",
)

DOMAINS["Actuarial Science"] = _domain(
    title="Actuarial Science",
    tagline="**Frequency × severity = solvency** — the mathematics insurance companies use to survive rare catastrophes.",
    primary_lenses=["Probability / Uncertainty", "Simulation / Alternate Futures", "Statistics / Pattern Detection"],
    why_matters="Insurance sells promises decades into the future. Actuaries model claim randomness, reserve capital, and price policies so the firm survives the worst plausible years.",
    concepts=["Compound distributions (frequency × severity)", "Ruin theory", "Credibility and experience rating", "Life tables and mortality", "Catastrophe modeling"],
    professional_applications=["Property casualty pricing", "Pension liability valuation", "Health stop-loss insurance", "Catastrophe bond structuring"],
    breakthroughs=[
        {"title": "Law of large numbers in insurance", "era": "19th century", "description": "Pooling risk makes aggregate claims predictable even when individual claims are not."},
        {"title": "Catastrophe models", "era": "1990s", "description": "Hurricane and earthquake simulation for capital requirements."},
    ],
    ai_connection="ML improves telematics pricing, fraud detection, and image-based claims; generative models synthesize rare catastrophe scenarios for stress tests.",
    excel_projects=["Simulate Poisson claim counts × lognormal severities annually."],
    python_projects=["10,000-year aggregate loss distribution; compute 99.5th percentile capital."],
    portfolio_ideas=["Ratemaking workbook with loss ratio and expense load.", "Compare reinsurance layers on tail loss reduction."],
    simulation_id="actuarial_losses",
    interpretation="Regulators care about the **right tail** of annual loss — simulation makes that tail visible.",
)

DOMAINS["Gambling, Poker & Decision Mathematics"] = _domain(
    title="Gambling, Poker & Decision Mathematics",
    tagline="**Expected value under hidden information** — disciplined risk when outcomes are random and opponents deceive.",
    primary_lenses=["Probability / Uncertainty", "Optimization / Improvement"],
    why_matters="Poker and professional betting are applied probability: pot odds, implied probability, bankroll survival, and exploitative adjustments. Casinos encode the same math as **house edge** over millions of trials.",
    concepts=["Expected value and variance of bets", "Pot odds and fold equity", "Bayesian updating on opponent ranges", "Kelly criterion for bet sizing", "House edge and RTP"],
    professional_applications=["Professional poker tournament strategy", "Sports book line setting and sharp detection", "Casino game design and table limits", "Risk of ruin analysis for bankrolls"],
    breakthroughs=[
        {"title": "Kelly criterion", "era": "1956", "description": "Optimal bet sizing to maximize long-run growth rate."},
        {"title": "Game theory in poker", "era": "2000s", "description": "Nash equilibrium concepts applied to balanced strategies (GTO)."},
    ],
    ai_connection="Pluribus and Libratus solved imperfect-information games with RL; sportsbooks use ML for live odds; fraud AI detects collusion patterns.",
    excel_projects=["EV calculator: win% × pot − lose% × call amount."],
    python_projects=["Simulate 10,000 poker sessions with Kelly vs fixed fraction betting."],
    portfolio_ideas=["Bankroll survival curves under varying edge and variance.", "Compare call/fold decisions across pot odds thresholds."],
    simulation_id="poker_ev",
    interpretation="Positive EV does not guarantee short-run winning — variance and bankroll math explain why professionals think in thousands of hands.",
)

DOMAINS["Casino Mathematics"] = _domain(
    title="Casino Mathematics",
    tagline="**House edge as industrialized probability** — how entertainment businesses guarantee long-run profit.",
    primary_lenses=["Probability / Uncertainty", "Statistics / Pattern Detection"],
    why_matters="Every game is engineered so law of large numbers favors the house. Surveillance statistics detect advantage players; table limits manage variance.",
    concepts=["Expected value per wager", "Gambler's ruin", "Central limit theorem on aggregate house win", "Card counting detection via running counts", "RNG fairness testing"],
    professional_applications=["Game design and payout tables", "Slot machine PAR sheets", "Comp program optimization", "Anti-fraud analytics"],
    breakthroughs=[
        {"title": "Monte Carlo roulette analysis", "era": "Historical", "description": "Inspired early simulation methods for complex probabilities."},
    ],
    ai_connection="Computer vision monitors tables; ML flags anomalous win rates; generative AI personalizes comps while optimizing casino margin.",
    excel_projects=["Build roulette EV: P(win)×payout − P(lose)×stake across 1M simulated spins."],
    python_projects=["Simulate blackjack with basic strategy vs counting spread."],
    portfolio_ideas=["Design a new game and prove house edge > 2% over 1M trials.", "Surveillance dashboard: player win-rate z-scores."],
    simulation_id="casino_edge",
    interpretation="Short-run player wins are noise; house profit emerges from volume × edge — pure applied probability at scale.",
)

# --- Statistics / forecasting ---

DOMAINS["Sports Analytics"] = _domain(
    title="Sports Analytics",
    tagline="**Separating talent from noise** — how teams make better draft, trade, and tactical decisions.",
    primary_lenses=["Statistics / Pattern Detection", "Probability / Uncertainty", "Optimization / Improvement"],
    why_matters="A 40-home-run season is not a 40-HR true talent level. Billion-dollar franchises invest in models that regress extremes, project aging, and quantify win probability.",
    concepts=["Regression to the mean", "Bayesian talent estimation", "Win probability models", "Lineup optimization", "Aging curves"],
    professional_applications=["Player projection systems (PECOTA, ZiPS-style thinking)", "In-game decision models (fourth down, bullpen)", "Scouting combine metric integration", "Salary cap roster optimization"],
    breakthroughs=[
        {"title": "Sabermetrics", "era": "1970s–2000s", "description": "Objective performance metrics replaced intuition for valuation."},
        {"title": "Moneyball drafting", "era": "2002", "description": "Market inefficiencies exploited via statistical undervaluation."},
    ],
    ai_connection="Computer vision tracks player pose and ball trajectory; deep learning forecasts injury risk; RL studies in-game strategy.",
    excel_projects=["Weighted blend: 70% career avg + 30% current season for projection."],
    python_projects=["Simulate season stats; show shrinkage estimators beating raw averages."],
    portfolio_ideas=["Build aging curve for a position with confidence bands.", "Win probability model from score differential and time remaining."],
    simulation_id="sports_aging",
    interpretation="Observed points scatter around a smoother true-talent curve — the reason teams shrink hot streaks before paying for them.",
)

DOMAINS["Fantasy Sports"] = _domain(
    title="Fantasy Sports",
    tagline="**Optimization under uncertainty** — draft capital, projections, and weekly lineup as a quantitative game.",
    primary_lenses=["Statistics / Pattern Detection", "Optimization / Improvement", "Probability / Uncertainty"],
    why_matters="Fantasy is a miniature quant desk: forecast points, estimate variance, optimize lineups under salary caps, and trade off boom/bust vs floor.",
    concepts=["Projections with uncertainty intervals", "Value over replacement player (VORP)", "Knapsack / integer lineup optimization", "Monte Carlo season simulations", "Correlation in stacked players"],
    professional_applications=["Daily fantasy ownership optimization", "Season-long draft strategy", "Injury news Bayesian updates", "Trade value calculators"],
    breakthroughs=[
        {"title": "Replacement level theory", "era": "2000s", "description": "Standardized player value relative to waiver-wire baseline."},
    ],
    ai_connection="ML projections ingest tracking data; optimizers solve lineup ILPs in seconds; LLMs parse injury reports for automated updates.",
    excel_projects=["Salary-cap lineup with POSITION constraints and projected points."],
    python_projects=["PuLP/opt lineup optimizer with simulated weekly variance."],
    portfolio_ideas=["Draft simulator with ADP noise and value-based drafting rules.", "Compare conservative vs upside-chasing lineup optimizers."],
    simulation_id="sports_aging",
    interpretation="The same signal-vs-noise lesson applies: chase projections that adjust for sample size and role changes, not one hot week.",
)

DOMAINS["Election Forecasting"] = _domain(
    title="Election Forecasting",
    tagline="**Aggregating noisy polls into probability maps** — statistics, uncertainty, and humility in public prediction.",
    primary_lenses=["Statistics / Pattern Detection", "Probability / Uncertainty", "Simulation / Alternate Futures"],
    why_matters="Elections are not deterministic from one poll. Forecasters model state-level errors, correlation, and late swings — then report **probabilities**, not certainties.",
    concepts=["Poll aggregation and house effects", "Binomial / electoral college simulation", "Forecast calibration and Brier scores", "Time-series of voter sentiment", "Uncertainty intervals on swing states"],
    professional_applications=["Newsroom decision desks", "Campaign resource allocation", "Academic political science", "Betting market arbitrage analysis"],
    breakthroughs=[
        {"title": "FiveThirtyEight-style aggregation", "era": "2008–present", "description": "Popularized probabilistic forecasts with transparent uncertainty."},
    ],
    ai_connection="NLP on social media for sentiment; graph models of demographic turnout; deep learning on fundraising and early vote patterns.",
    excel_projects=["Simulate 1000 electoral college outcomes from state win probabilities."],
    python_projects=["Poll-plus fundamentals model with correlated state shocks."],
    portfolio_ideas=["Backtest calibration: predicted 70% events should win ~70%.", "Sensitivity of overall odds to one swing state poll."],
    simulation_id="election_forecast",
    interpretation="A 65% chance to win is not a prediction of 65% vote share — it is a statement about **many plausible worlds** given polling error.",
)

DOMAINS["Statistics & Prediction Systems"] = _domain(
    title="Statistics & Prediction Systems",
    tagline="**Inference engines for modern institutions** — from clinical trials to recommendation ranking.",
    primary_lenses=["Statistics / Pattern Detection", "AI / Learning Systems"],
    why_matters="Every prediction product needs honest uncertainty, out-of-sample validation, and skepticism of spurious correlation.",
    concepts=["Regression and regularization", "Classification metrics", "Cross-validation", "Causal inference basics", "Bayesian updating"],
    professional_applications=["A/B testing platforms", "Demand forecasting", "Churn prediction", "Public health surveillance"],
    breakthroughs=[
        {"title": "Least squares regression", "era": "1805", "description": "Gauss and Legendre formalized fitting lines to noisy observations."},
        {"title": "Bootstrap", "era": "1979", "description": "Resampling methods for confidence intervals without formulas."},
    ],
    ai_connection="Classical statistics is the backbone of ML evaluation — leakage detection, calibration, fairness metrics, and experiment design.",
    excel_projects=["Advertising spend vs sales with trendline and R²."],
    python_projects=["Train/test split regression; report RMSE and residual plots."],
    portfolio_ideas=["End-to-end churn model with business impact translation.", "Causal A/B analysis with confidence intervals."],
    simulation_id="regression_noise",
    interpretation="Estimated slope wanders when noise dominates — motivating larger samples and regularization.",
)

# --- Optimization ---

DOMAINS["Machine Learning"] = _domain(
    title="Machine Learning",
    tagline="**Automated pattern extraction** — systems that improve predictions by optimizing parameters on data.",
    primary_lenses=["AI / Learning Systems", "Optimization / Improvement", "Statistics / Pattern Detection"],
    why_matters="ML powers ranking, vision, speech, and forecasting pipelines inside every major tech company. It is statistics + optimization + compute.",
    concepts=["Loss functions and empirical risk", "Gradient descent and variants", "Bias-variance tradeoff", "Feature engineering and embeddings", "Cross-validation"],
    professional_applications=["Production ranking models", "Fraud detection", "Predictive maintenance", "Personalization"],
    breakthroughs=[
        {"title": "Backpropagation popularization", "era": "1986", "description": "Enabled training deep networks efficiently."},
        {"title": "ImageNet deep learning revolution", "era": "2012", "description": "CNNs surpassed hand-crafted vision pipelines."},
    ],
    ai_connection="This domain is the engineering practice of AI — training, deployment, monitoring, and retraining loops.",
    excel_projects=["Track epoch vs training/validation error in a table."],
    python_projects=["Implement logistic regression from scratch with gradient descent."],
    portfolio_ideas=["End-to-end sklearn pipeline with leakage audit document.", "Compare L1 vs L2 regularization on high-dimensional data."],
    simulation_id="gradient_descent",
    interpretation="Loss descent is the visual spine of training — high-dimensional in reality, same principle.",
)

DOMAINS["Artificial Intelligence"] = _domain(
    title="Artificial Intelligence",
    tagline="**Large-scale adaptive systems** — language, vision, planning, and reasoning built on mathematical learning.",
    primary_lenses=["AI / Learning Systems", "Probability / Uncertainty", "Optimization / Improvement"],
    why_matters="AI is transforming law, medicine, coding, and science. Understanding its mathematical roots separates informed deployment from hype.",
    concepts=["Transformers and attention", "Reinforcement learning from human feedback", "Token probability distributions", "Multimodal fusion", "Alignment and reward modeling"],
    professional_applications=["Copilots for software and analysis", "Autonomous perception stacks", "Scientific discovery assistants", "Customer support automation"],
    breakthroughs=[
        {"title": "Transformer architecture", "era": "2017", "description": "Attention mechanisms enabled scalable language modeling."},
        {"title": "GPT-scale pretraining", "era": "2018–present", "description": "Emergent capabilities from scale + data + compute."},
    ],
    ai_connection="Frontier AI stacks LLMs with retrieval, tools, and fine-tuning — all optimization and probability under the hood.",
    excel_projects=["Token-level perplexity toy: compare model A vs B error rates."],
    python_projects=["Fine-tune a small classifier; document train/val gap."],
    portfolio_ideas=["RAG system with evaluation harness and citation accuracy metrics.", "Safety eval notebook for prompt injection cases."],
    simulation_id="gradient_descent",
    interpretation="Even billion-parameter models minimize a loss surface — the industrial form of gradient descent.",
)

DOMAINS["Supply Chain Optimization"] = _domain(
    title="Supply Chain Optimization",
    tagline="**Flows, inventories, and routes** — mathematics that keeps global commerce from collapsing under disruption.",
    primary_lenses=["Optimization / Improvement", "Simulation / Alternate Futures", "Statistics / Pattern Detection"],
    why_matters="Pandemics, port strikes, and weather expose fragile supply networks. Firms optimize inventory, routing, and sourcing under uncertainty.",
    concepts=["Linear and integer programming", "Network flow models", "Newsvendor model", "Stochastic lead times", "Multi-echelon inventory"],
    professional_applications=["Amazon-style fulfillment routing", "Airline spare parts positioning", "Automotive just-in-time tuning", "Humanitarian logistics"],
    breakthroughs=[
        {"title": "Simplex algorithm", "era": "1947", "description": "Made large-scale linear optimization practical."},
        {"title": "Supply chain digital twins", "era": "2020s", "description": "Simulation + live data for disruption response."},
    ],
    ai_connection="ML forecasts demand; reinforcement learning controls warehouses; digital twins simulate port closures.",
    excel_projects=["EOQ model with holding vs ordering cost tradeoff."],
    python_projects=["Solve small TSP with OR-Tools; visualize route cost."],
    portfolio_ideas=["Disruption simulation: lead time +50% impact on stockouts.", "Multi-warehouse allocation linear program."],
    simulation_id="supply_chain",
    interpretation="Small lead-time volatility propagates to stockout risk nonlinearly — why simulation complements formulas.",
)

DOMAINS["Engineering & Optimization"] = _domain(
    title="Engineering & Optimization",
    tagline="**Design under physics and constraints** — bridges, rockets, chips, and machines as optimization problems.",
    primary_lenses=["Optimization / Improvement", "Calculus / Accumulation", "Simulation / Alternate Futures"],
    why_matters="Engineering failures are expensive. Models integrate calculus (motion, heat, stress) with optimization (lightest safe design) and simulation (million virtual tests).",
    concepts=["Equations of motion", "Finite element analysis", "Constrained optimization", "Control theory", "Reliability engineering"],
    professional_applications=["Aerospace trajectory design", "Structural safety factors", "Robotics path planning", "Energy grid dispatch"],
    breakthroughs=[
        {"title": "Finite element method", "era": "1950s", "description": "Numerical stress analysis for complex geometries."},
    ],
    ai_connection="Generative design AI explores shape space; physics-informed nets accelerate CFD; RL trains control policies in sim.",
    excel_projects=["Angle vs range table for projectile motion."],
    python_projects=["Optimize launch angle for maximum range with scipy.optimize."],
    portfolio_ideas=["Truss weight minimization subject to stress constraints (toy FEA).", "Cooling system heat ODE with control strategy."],
    simulation_id="projectile",
    interpretation="Trajectory is calculus made visible — optimization picks parameters that extremize mission objectives.",
)

DOMAINS["Robotics"] = _domain(
    title="Robotics",
    tagline="**Sense, plan, act** — geometry, control, and optimization in physical space.",
    primary_lenses=["Optimization / Improvement", "Calculus / Accumulation", "AI / Learning Systems"],
    why_matters="Robots manipulate surgery tools, warehouse pallets, and Mars soil. Errors are physical. Math links kinematics, dynamics, and perception uncertainty.",
    concepts=["Forward/inverse kinematics", "PID control", "SLAM and sensor fusion", "Motion planning (RRT, CHOMP)", "Grasp stability"],
    professional_applications=["Warehouse AMRs", "Surgical assistants", "Manufacturing arms", "Exploration rovers"],
    breakthroughs=[
        {"title": "Denavit–Hartenberg parameters", "era": "1955", "description": "Standardized robot arm geometry modeling."},
    ],
    ai_connection="Deep learning for grasping and segmentation; sim-to-real RL; diffusion policies for dexterous manipulation.",
    excel_projects=["2-link arm endpoint position from joint angles (trig)."],
    python_projects=["Planar arm animation; inverse kinematics numeric solve."],
    portfolio_ideas=["Obstacle avoidance path cost comparison.", "Sim-to-real gap analysis document for a pick-and-place task."],
    simulation_id="projectile",
    interpretation="Motion planning extends projectile thinking to constrained configuration spaces.",
)

DOMAINS["Autonomous Vehicles"] = _domain(
    title="Autonomous Vehicles",
    tagline="**Perception, prediction, planning** — a stack of geometry, probability, and optimization at 70 mph.",
    primary_lenses=["AI / Learning Systems", "Probability / Uncertainty", "Optimization / Improvement"],
    why_matters="Self-driving must fuse noisy sensors, predict other agents, and plan safe paths in milliseconds — applied math with life-safety stakes.",
    concepts=["Sensor fusion (Kalman, particle filters)", "Occupancy grids", "Trajectory forecasting", "Optimal control and MPC", "Safety case verification"],
    professional_applications=["L4 highway pilots", "ADAS lane keeping", "Mining haul trucks", "Delivery bots"],
    breakthroughs=[
        {"title": "DARPA Urban Challenge", "era": "2007", "description": "Proved large-scale autonomous navigation feasibility."},
        {"title": "Deep learning perception era", "era": "2010s", "description": "CNNs replaced many hand-tuned vision pipelines."},
    ],
    ai_connection="End-to-end driving networks debated vs modular stacks; world models simulate futures for planning.",
    excel_projects=["Time-to-collision spreadsheet from speed and distance."],
    python_projects=["Kalman filter tracking two vehicles from noisy radar."],
    portfolio_ideas=["Multi-agent intersection simulation with failure mode analysis.", "Perception mAP vs planning safety case tradeoff memo."],
    simulation_id="projectile",
    interpretation="Planning is continuous optimization over predicted futures — not just detecting objects.",
)

# --- Simulation ---

DOMAINS["Simulation & Monte Carlo Methods"] = _domain(
    title="Simulation & Monte Carlo Methods",
    tagline="**When closed-form answers fail, sample the world** — the universal engine for complex risk.",
    primary_lenses=["Simulation / Alternate Futures", "Probability / Uncertainty"],
    why_matters="Integration, finance, physics, and AI uncertainty all use random sampling to approximate quantities analytically intractable.",
    concepts=["Monte Carlo integration", "Variance reduction", "Agent-based models", "Discrete-event simulation", "Sensitivity analysis"],
    professional_applications=["Derivative pricing", "Nuclear shielding", "Queueing systems", "Playoff odds"],
    breakthroughs=[
        {"title": "Metropolis–Hastings", "era": "1953", "description": "MCMC methods for Bayesian inference and statistical physics."},
    ],
    ai_connection="Diffusion models, RL rollouts, and Bayesian neural networks rely on sampling-based computation.",
    excel_projects=["Estimate π with RAND() dartboard experiment."],
    python_projects=["Price Asian option by simulation; compare to tree method."],
    portfolio_ideas=["Insurance annual loss distribution with copula dependence.", "Manufacturing throughput discrete-event sim."],
    simulation_id="monte_carlo_pi",
    interpretation="π estimation is the teaching classic — the same logic prices tail risk and tests engineering reliability.",
)

DOMAINS["Military Simulations & Wargaming"] = _domain(
    title="Military Simulations & Wargaming",
    tagline="**Explore conflicts before they happen** — logistics, attrition, and scenario stress under uncertainty.",
    primary_lenses=["Simulation / Alternate Futures", "Optimization / Improvement", "Probability / Uncertainty"],
    why_matters="Defense planning cannot experiment on live battlefields. Simulation and game theory test strategies, supply lines, and escalation paths.",
    concepts=["Lanchester attrition models", "Logistics network flow", "Game theory equilibria", "Monte Carlo battle outcomes", "Agent-based conflict models"],
    professional_applications=["Joint wargaming exercises", "Force structure planning", "Cyber exercise red teams", "Logistics under contested supply"],
    breakthroughs=[
        {"title": "Lanchester equations", "era": "1916", "description": "Mathematical attrition laws for force-on-force modeling."},
    ],
    ai_connection="AI generates scenarios, adversarial agents, and synthetic training environments; computer vision for ISR fusion.",
    excel_projects=["Attrition spreadsheet with exchange ratios."],
    python_projects=["Monte Carlo over supply delay distributions for campaign success probability."],
    portfolio_ideas=["Red vs blue logistics disruption tabletop + simulation appendix.", "Game-theoretic escalation tree analysis."],
    simulation_id="monte_carlo_pi",
    interpretation="Military planners think in distributions of outcomes — simulation makes assumptions explicit and testable.",
)

# --- Space & astronomy ---

DOMAINS["Astronomy & Astrophysics"] = _domain(
    title="Astronomy & Astrophysics",
    tagline="**Gravity, light, and scale** — modeling the universe from planetary orbits to cosmological expansion.",
    primary_lenses=["Calculus / Accumulation", "Statistics / Pattern Detection", "Simulation / Alternate Futures"],
    why_matters="We infer black holes, exoplanets, and dark energy from **tiny noisy signals** integrated over vast dynamics. Astrophysics is observation + differential equations + statistics.",
    concepts=["Keplerian orbits and N-body simulation", "Inverse-square gravity", "Stellar luminosity and distance ladders", "Bayesian parameter estimation from light curves", "Cosmological expansion models"],
    professional_applications=["Exoplanet detection (transit fitting)", "Galaxy survey analysis", "Gravitational wave matched filtering", "Mission trajectory design"],
    breakthroughs=[
        {"title": "Kepler's laws", "era": "1609–1619", "description": "Elliptical orbits unified planetary motion mathematically."},
        {"title": "Hubble expansion", "era": "1929", "description": "Linked redshift to universe expansion."},
    ],
    ai_connection="ML classifies galaxies, detects transits in TESS data, and emulates expensive radiative transfer simulations.",
    excel_projects=["Orbital period from semi-major axis (Kepler's third law scaled)."],
    python_projects=["Two-body orbit integrator; plot eccentric orbits."],
    portfolio_ideas=["Fit exoplanet transit depth/noise to estimate planet radius uncertainty.", "N-body toy system stability analysis."],
    simulation_id="orbital_mechanics",
    interpretation="Small perturbations in initial conditions change long-run paths — motivation for ensemble forecasts in space missions.",
)

DOMAINS["Space Exploration"] = _domain(
    title="Space Exploration",
    tagline="**Trajectory, fuel, and reliability** — every mission is an optimization problem under Newton's laws.",
    primary_lenses=["Calculus / Accumulation", "Optimization / Improvement", "Simulation / Alternate Futures"],
    why_matters="Mars landings and satellite constellations fail if integration of forces, mass, and thrust is wrong. Simulation tests millions of virtual launches before one real ignition.",
    concepts=["Rocket equation (Tsiolkovsky)", "Hohmann transfers", "Re-entry heating", "Monte Carlo landing dispersion", "Reliability block diagrams"],
    professional_applications=["NASA/SpaceX trajectory offices", "Satellite constellation deployment", "Planetary entry, descent, landing", "Life support mass budgeting"],
    breakthroughs=[
        {"title": "Apollo guidance", "era": "1960s", "description": "Real-time navigation and optimization on limited hardware."},
        {"title": "Reusable boosters", "era": "2010s", "description": "Changed launch cost structure via engineering optimization."},
    ],
    ai_connection="GNC networks learn landing policies in sim; generative design for lightweight structures; autonomous rover path planning.",
    excel_projects=["Δv budget table for multi-stage rocket."],
    python_projects=["Simulate gravity turn launch profile; optimize pitch program."],
    portfolio_ideas=["Monte Carlo landing ellipse from navigation error model.", "Constellation coverage optimization memo."],
    simulation_id="orbital_mechanics",
    interpretation="Orbital mechanics connects calculus (acceleration) to mission feasibility (fuel mass).",
)

# --- Tech / media ---

DOMAINS["Internet Recommendation Systems"] = _domain(
    title="Internet Recommendation Systems",
    tagline="**Predict preference at scale** — the statistics and optimization behind feeds, shops, and streams.",
    primary_lenses=["Statistics / Pattern Detection", "AI / Learning Systems", "Optimization / Improvement"],
    why_matters="Billions of dollars flow through ranking systems that estimate what you will click, watch, or buy next — under latency and diversity constraints.",
    concepts=["Collaborative filtering", "Matrix factorization", "Learning-to-rank", "Exploration vs exploitation (bandits)", "Bias and filter bubbles"],
    professional_applications=["YouTube/Netflix ranking", "Amazon product graphs", "Spotify playlists", "News feed personalization"],
    breakthroughs=[
        {"title": "Netflix Prize", "era": "2006–2009", "description": "Accelerated matrix factorization research for collaborative filtering."},
    ],
    ai_connection="Deep ranking models, two-tower retrieval, and LLM-based recommendations are the modern stack.",
    excel_projects=["User-item rating matrix with SVD-style manual factor iteration (toy)."],
    python_projects=["Train implicit feedback recommender; evaluate precision@k."],
    portfolio_ideas=["A/B test design for new ranking function with guardrail metrics.", "Cold-start strategy comparison report."],
    simulation_id="recommendation",
    interpretation="Low-rank structure in ratings reveals latent taste dimensions — the geometric heart of collaborative filtering.",
)

DOMAINS["Social Network Analysis"] = _domain(
    title="Social Network Analysis",
    tagline="**Graphs, influence, and contagion** — mathematics of how ideas and behavior spread.",
    primary_lenses=["Statistics / Pattern Detection", "Simulation / Alternate Futures", "AI / Learning Systems"],
    why_matters="Networks shape elections, epidemics, fraud rings, and viral marketing. Graph math quantifies centrality, community structure, and diffusion.",
    concepts=["Graph Laplacians and spectral methods", "PageRank", "Community detection", "Epidemic thresholds on networks", "Homophily and bias"],
    professional_applications=["Influence maximization in marketing", "Fraud graph detection", "Organizational knowledge flow", "Public health contact tracing"],
    breakthroughs=[
        {"title": "PageRank", "era": "1998", "description": "Eigenvector centrality powered early web search ranking."},
    ],
    ai_connection="Graph neural networks predict links, classify nodes, and detect anomalies; LLMs analyze text networks.",
    excel_projects=["Adjacency matrix powers to count 3-hop paths."],
    python_projects=["Simulate SIR on Barabási–Albert graph vs lattice."],
    portfolio_ideas=["Identify bridge nodes whose removal fragments network.", "Compare centrality metrics on corporate email graph (synthetic)."],
    simulation_id="epidemic_sir",
    interpretation="Network topology changes epidemic speed — same SIR math, different graph yields different policy.",
)

DOMAINS["Search Engines"] = _domain(
    title="Search Engines",
    tagline="**Retrieve, rank, learn** — inverted indexes plus optimization and statistics at web scale.",
    primary_lenses=["Optimization / Improvement", "Statistics / Pattern Detection", "AI / Learning Systems"],
    why_matters="Search is the original big-data ML product: billions of queries, constant experimentation, adversarial SEO, and semantic retrieval via embeddings.",
    concepts=["Inverted index and BM25", "Learning to rank", "Click-through rate bias", "Embeddings and semantic search", "Index freshness and crawling optimization"],
    professional_applications=["Web search", "Enterprise knowledge search", "E-commerce product search", "Legal discovery"],
    breakthroughs=[
        {"title": "PageRank + BM25 era", "era": "1990s–2000s", "description": "Combined link structure and term relevance."},
        {"title": "Neural semantic search", "era": "2010s–present", "description": "Dense vectors capture meaning beyond keywords."},
    ],
    ai_connection="LLMs rewrite queries, summarize results, and rank with cross-encoders; RAG connects search to generation.",
    excel_projects=["TF-IDF toy on 10 documents; manual rank top 3."],
    python_projects=["Build mini inverted index + BM25; compare to embedding retrieval."],
    portfolio_ideas=["Offline eval harness: NDCG@10 across query set.", "Click-bias correction experiment design."],
    simulation_id="recommendation",
    interpretation="Ranking is optimization over relevance objectives with latency constraints — not just matching keywords.",
)

DOMAINS["Cybersecurity"] = _domain(
    title="Cybersecurity",
    tagline="**Adversarial uncertainty** — modeling attack rates, vulnerabilities, and defense tradeoffs.",
    primary_lenses=["Probability / Uncertainty", "Statistics / Pattern Detection", "Simulation / Alternate Futures"],
    why_matters="Breaches are random in timing and impact. Security teams quantify risk, simulate incident paths, and detect anomalies statistically — not deterministically.",
    concepts=["Threat modeling", "Poisson process of incidents", "Bayesian intrusion detection", "Risk = likelihood × impact", "Red team exercise simulation"],
    professional_applications=["SOC alert prioritization", "Cyber insurance pricing", "Zero-trust architecture ROI", "Phishing detection ML"],
    breakthroughs=[
        {"title": "Kerckhoffs's principle", "era": "1883", "description": "Security should not rely on secrecy of the algorithm."},
    ],
    ai_connection="Anomaly detection on logs, LLM-assisted phishing, and automated patch triage use ML; adversarial ML attacks model robustness.",
    excel_projects=["Annual loss expectancy = event rate × average cost."],
    python_projects=["Monte Carlo cyber loss with correlated ransomware events."],
    portfolio_ideas=["Detection ROC curve from synthetic attack/legit traffic.", "Purple team exercise timeline simulation."],
    simulation_id="actuarial_losses",
    interpretation="Tail losses from correlated attacks dominate expected annual cost — actuarial thinking in security.",
)

DOMAINS["Cryptography"] = _domain(
    title="Cryptography",
    tagline="**Hard math problems guarding information** — primes, entropy, and provable difficulty.",
    primary_lenses=["Probability / Uncertainty", "Optimization / Improvement"],
    why_matters="Digital commerce and privacy depend on mathematical problems believed intractable — factoring, discrete log, lattice problems — and on randomness quality.",
    concepts=["Modular arithmetic", "RSA and elliptic curves", "Entropy and key generation", "Hash functions", "Post-quantum lattice crypto"],
    professional_applications=["TLS certificates", "Blockchain consensus", "Secure messaging", "Hardware security modules"],
    breakthroughs=[
        {"title": "RSA", "era": "1977", "description": "Public-key encryption from prime factorization hardness."},
        {"title": "Shor's algorithm threat", "era": "1994", "description": "Quantum computers threaten classical schemes — driving PQC migration."},
    ],
    ai_connection="ML aids side-channel detection and automated crypto analysis; also creates deepfake threats cryptography cannot alone solve.",
    excel_projects=["Modular exponentiation spreadsheet for toy RSA."],
    python_projects=["Implement RSA on small primes; demonstrate brute-force break."],
    portfolio_ideas=["Compare RSA vs elliptic curve key sizes for equivalent security.", "Entropy audit script on generated passwords."],
    simulation_id="casino_edge",
    interpretation="Security margins are probabilistic — odds an attacker breaks a key before rotation.",
)

DOMAINS["Computer Graphics"] = _domain(
    title="Computer Graphics",
    tagline="**Turn equations into pixels** — linear algebra, calculus, and Monte Carlo light transport.",
    primary_lenses=["Calculus / Accumulation", "Probability / Uncertainty", "Optimization / Improvement"],
    why_matters="Films, games, and VR require simulating light, motion, and materials. Ray tracing integrates paths; animation integrates motion curves.",
    concepts=["Linear transforms and homogeneous coordinates", "Ray tracing and path tracing", "Shading models", "Numerical integration for global illumination", "Mesh optimization"],
    professional_applications=["VFX houses", "Game engines (Unreal/Unity)", "GPU rasterization pipelines", "Medical visualization"],
    breakthroughs=[
        {"title": "Phong shading", "era": "1975", "description": "Practical local illumination model."},
        {"title": "Path tracing in production", "era": "2010s", "description": "Monte Carlo light transport for photorealism."},
    ],
    ai_connection="NeRF and diffusion generate views; AI denoises ray-traced frames; neural radiance fields replace explicit geometry.",
    excel_projects=["2D rotation matrix applied to polygon vertices."],
    python_projects=["Ray-sphere intersection image; accumulate random samples per pixel."],
    portfolio_ideas=["Path tracer with progressive noise reduction demo.", "Compare raster vs ray cast on same scene."],
    simulation_id="signal_wave",
    interpretation="Each pixel is an estimate (integral) of light — Monte Carlo graphics in miniature.",
)

DOMAINS["Audio Processing & Music"] = _domain(
    title="Audio Processing & Music",
    tagline="**Signals as functions** — frequencies, filters, and patterns in sound.",
    primary_lenses=["Calculus / Accumulation", "Statistics / Pattern Detection", "AI / Learning Systems"],
    why_matters="Speech assistants, streaming compression, and music recommendation all decompose sound into mathematical structure — Fourier modes, spectrograms, learned embeddings.",
    concepts=["Fourier series and FFT", "Convolution and filters", "Sampling theorem", "Spectrograms", "Source separation"],
    professional_applications=["MP3/AAC compression", "Noise cancellation headphones", "Shazam fingerprinting", "Music information retrieval"],
    breakthroughs=[
        {"title": "Fourier analysis", "era": "1822", "description": "Decomposed signals into sinusoids — foundation of modern DSP."},
        {"title": "MP3 perceptual coding", "era": "1990s", "description": "Removed inaudible components via psychoacoustics + math."},
    ],
    ai_connection="Deep learning generates music, clones voices ethically debated, and separates stems; transformers model long audio context.",
    excel_projects=["Sample sine wave at 440 Hz; plot discretized points."],
    python_projects=["FFT of chord clip; visualize frequency peaks."],
    portfolio_ideas=["Beat tracker on WAV file with autocorrelation.", "Genre classifier from MFCC features + sklearn."],
    simulation_id="signal_wave",
    interpretation="Complex sounds are sums of simple waves — calculus and linear algebra made audible.",
)

DOMAINS["Weather Forecasting"] = _domain(
    title="Weather Forecasting",
    tagline="**Chaos, ensembles, and calibrated probability** — when the atmosphere refuses determinism.",
    primary_lenses=["Calculus / Accumulation", "Probability / Uncertainty", "Simulation / Alternate Futures"],
    why_matters="A butterfly flapping is the cliché; the reality is **numerical weather prediction** integrating fluid PDEs plus ensemble spreads for hurricane tracks.",
    concepts=["Navier–Stokes on a sphere", "Data assimilation", "Ensemble forecasts", "Calibration and Brier scores", "Chaos and sensitive dependence"],
    professional_applications=["National weather services", "Aviation routing", "Energy trading (wind/solar)", "Disaster response"],
    breakthroughs=[
        {"title": "Numerical weather prediction", "era": "1950", "description": "Charney-Fjørtoft-von Neumann first computer forecast."},
        {"title": "Ensemble forecasting", "era": "1990s", "description": "Multiple perturbed runs bracket uncertainty."},
    ],
    ai_connection="ML nowcasts precipitation from radar; neural emulators speed global models; GraphCast-style models learn dynamics from data.",
    excel_projects=["Temperature forecast error vs days ahead scatter."],
    python_projects=["Bayesian update on rain given radar hit rate and base rate."],
    portfolio_ideas=["Compare single-model vs ensemble interval coverage.", "Hurricane track fan chart from synthetic ensembles."],
    simulation_id="bayesian_diagnosis",
    interpretation="Forecasting is sequential belief updating plus physics — probability is the user-facing output.",
)

DOMAIN_NAMES = sorted(DOMAINS.keys())
