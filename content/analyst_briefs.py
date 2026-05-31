"""Quantitative analyst briefs — what to ask, variables, math, and approach per problem type."""

ANALYST_BRIEFS: dict[str, dict] = {
    "betting": {
        "type_label": "Betting / poker decision",
        "what_is_asked": "Does this wager have **positive expected value** over many similar decisions?",
        "variables": "Win probability, pot size, bet/call amount, stack size, rake",
        "math_useful": "Probability, expected value, pot odds, bankroll sizing",
        "analyst_steps": [
            "Estimate your win probability (equity) for this decision.",
            "Convert pot odds to the break-even probability required to call.",
            "Compute expected value: EV = P(win)×gain − P(lose)×loss.",
            "Size the bet so variance does not threaten long-run survival.",
        ],
        "limitations": "Single-hand results are noisy — judge decision quality over hundreds of hands.",
        "math_behind": {
            "Probability": "Equity = P(win) given cards and opponent ranges.",
            "Expected value": "EV = Σ P(outcome) × payoff — positive EV means profitable long-term.",
            "Optimization": "Kelly criterion sizes bets to maximize long-run growth subject to ruin risk.",
        },
        "interactive": "ev_bet",
    },
    "sports": {
        "type_label": "Sports prediction / wagering",
        "what_is_asked": "Is your estimated win probability **higher than the market's implied probability**?",
        "variables": "Team strength, injuries, home field, sample size, odds, bet size",
        "math_useful": "Statistics, probability, expected value, regression to the mean",
        "analyst_steps": [
            "Estimate true win probability from data (ratings, injuries, context).",
            "Convert betting odds to implied probability.",
            "Calculate expected value per dollar wagered.",
            "Report uncertainty — wide intervals on small samples.",
        ],
        "limitations": "Past performance blends skill and luck; shrink extreme records toward average.",
        "math_behind": {
            "Statistics": "Shrinkage estimators pull extreme stats toward the league mean.",
            "Probability": "Implied probability from odds: for +150, implied ≈ 100/(150+100) = 40%.",
            "Expected value": "EV = p×(profit if win) − (1−p)×(stake if lose).",
        },
        "interactive": "ev_bet",
    },
    "medicine": {
        "type_label": "Treatment / disease modeling",
        "what_is_asked": "Does the treatment **change the outcome vs. a control**, and at what cost in toxicity?",
        "variables": "Tumor volume, growth rate, kill rate, dose, survival time, side-effect rate",
        "math_useful": "Calculus (rates), statistics (trials), differential equations, optimization",
        "analyst_steps": [
            "Define the outcome (survival, shrinkage, biomarker).",
            "Identify variables: growth rate vs. treatment kill rate.",
            "Require a control group — compare treatment to no treatment or standard care.",
            "State limitations: patient heterogeneity, trial size, follow-up time.",
        ],
        "limitations": "Response rate without control does not prove causation.",
        "math_behind": {
            "Calculus": "dV/dt = growth rate − treatment kill rate models tumor volume over time.",
            "Statistics": "Hazard ratios and survival curves compare treatment vs. control.",
            "Optimization": "Dose optimization trades efficacy against toxicity constraints.",
        },
        "interactive": "growth",
    },
    "ai": {
        "type_label": "Machine learning / prediction model",
        "what_is_asked": "Will this model **predict well on new data**, not just training data?",
        "variables": "Features, labels, loss, parameters, train/validation/test metrics",
        "math_useful": "Optimization (gradients), statistics, probability, regularization",
        "analyst_steps": [
            "Define the objective (loss) you are minimizing.",
            "Split data: train, validate, test — never tune on test.",
            "Track validation error while training; stop before overfitting.",
            "Report test performance once, with confidence intervals if possible.",
        ],
        "limitations": "High training accuracy often means memorization, not learning.",
        "math_behind": {
            "Optimization": "Gradient descent updates weights to minimize loss: w ← w − η∇L.",
            "Statistics": "Bias-variance tradeoff: complex models fit noise; simple models underfit.",
            "Probability": "Calibration — predicted probabilities should match observed frequencies.",
        },
        "interactive": "ml_split",
    },
    "business": {
        "type_label": "Business / strategy quant question",
        "what_is_asked": "Which lever **most moves the metric** (profit, conversion, LTV) per unit of spend?",
        "variables": "Conversion, CAC, LTV, price, cost, capacity, demand",
        "math_useful": "Statistics (A/B tests), optimization, forecasting, unit economics",
        "analyst_steps": [
            "Write the metric as a function of levers (e.g. profit = revenue − cost).",
            "Identify the binding constraint (budget, capacity, demand).",
            "Run a controlled experiment or cohort analysis before scaling.",
            "Forecast with scenarios, not a single point estimate.",
        ],
        "limitations": "Correlation in historical data is not causation.",
        "math_behind": {
            "Statistics": "A/B tests estimate causal lift with confidence intervals.",
            "Optimization": "Maximize objective subject to budget and capacity constraints.",
            "Probability": "Forecast ranges account for demand uncertainty.",
        },
        "interactive": "unit_econ",
    },
    "traffic": {
        "type_label": "Traffic / operations optimization",
        "what_is_asked": "How do we **minimize delay** (or cost) subject to capacity and safety?",
        "variables": "Flow rate, capacity, demand, signal timing, route choice",
        "math_useful": "Optimization, simulation, queueing theory, statistics",
        "analyst_steps": [
            "Model demand vs. capacity — where is the bottleneck?",
            "Simulate interventions (signals, lanes, pricing) before deploying.",
            "Check for induced demand — fixing one bottleneck may shift congestion.",
            "Measure average travel time and variance, not single trips.",
        ],
        "limitations": "Static models miss accidents and demand spikes.",
        "math_behind": {
            "Optimization": "Minimize average travel time subject to capacity constraints.",
            "Simulation": "Monte Carlo runs many demand scenarios to estimate delay distributions.",
            "Calculus": "Flow conservation links entry rate, exit rate, and queue buildup.",
        },
        "interactive": "queue",
    },
    "engineering": {
        "type_label": "Engineering / design optimization",
        "what_is_asked": "What design **maximizes performance per cost** within physical and safety limits?",
        "variables": "Efficiency, dimensions, materials, speed, cost, failure rate",
        "math_useful": "Calculus, optimization, simulation, tolerance analysis",
        "analyst_steps": [
            "List constraints (physics, safety, budget) before optimizing.",
            "Build a simple model linking inputs to performance.",
            "Prototype and measure — compare model prediction to data.",
            "Add safety margins for unknown operating conditions.",
        ],
        "limitations": "Lab conditions may not match field performance.",
        "math_behind": {
            "Calculus": "Derivatives find where performance changes fastest with a design parameter.",
            "Optimization": "Maximize output/cost subject to stress and safety constraints.",
            "Simulation": "Finite-element models stress-test designs before building.",
        },
        "interactive": "tradeoff",
    },
    "weather": {
        "type_label": "Weather / forecast quant question",
        "what_is_asked": "What is the **probability distribution** of outcomes, and how does uncertainty grow with lead time?",
        "variables": "Initial conditions, ensemble members, lead time, region",
        "math_useful": "Statistics, probability, simulation, chaos-sensitive dynamics",
        "analyst_steps": [
            "Use ensemble forecasts — many model runs, not one deterministic track.",
            "Report calibrated probabilities (e.g. 30% chance of rain means ~30% of such days rain).",
            "Widen uncertainty intervals as lead time increases.",
            "Compare models to observations to score calibration.",
        ],
        "limitations": "Small errors in initial conditions grow — long-range detail is unreliable.",
        "math_behind": {
            "Probability": "Ensemble spread approximates forecast uncertainty.",
            "Statistics": "Brier score measures calibration of probabilistic forecasts.",
            "Simulation": "Numerical weather models integrate fluid dynamics forward in time.",
        },
        "interactive": "forecast",
    },
    "default": {
        "type_label": "Quantitative decision / prediction",
        "what_is_asked": "What quantity are you **estimating, comparing, or optimizing** — and how will you know if you're right?",
        "variables": "Outcome, inputs you control, external factors, measurement error",
        "math_useful": "Statistics, probability, optimization — pick tools that match the question",
        "analyst_steps": [
            "State the question as a measurable quantity.",
            "List variables: decisions vs. observations vs. unknowns.",
            "Choose math that fits (EV for bets, regression for trends, optimization for constraints).",
            "Define one test that would falsify your answer.",
        ],
        "limitations": "Vague questions produce vague models — sharpen before calculating.",
        "math_behind": {
            "Probability": "Quantify uncertainty with distributions, not point guesses.",
            "Statistics": "Use data to estimate parameters and confidence intervals.",
            "Optimization": "Find the best feasible choice given constraints.",
        },
        "interactive": "ev_bet",
    },
    "space": {
        "type_label": "Space, motion & trajectory",
        "what_is_asked": "Where will the object be, and what path or velocity **satisfies physics and mission constraints**?",
        "variables": "Position, velocity, acceleration, mass, thrust, fuel, time, orbital parameters",
        "math_useful": "Calculus, differential equations, optimization, simulation",
        "analyst_steps": [
            "Write equations of motion (Newton's laws or energy conservation).",
            "List constraints: fuel, thrust limits, safety corridors.",
            "Integrate forward in time or optimize the control path.",
            "Validate against known solutions (e.g. circular orbit speed).",
        ],
        "limitations": "Models simplify atmosphere, perturbations, and vehicle flexibility.",
        "math_behind": {
            "Calculus": "Velocity is the derivative of position; acceleration is the derivative of velocity.",
            "Differential equations": "F = ma gives second-order ODEs for trajectory.",
            "Optimization": "Minimize fuel subject to reaching target position/velocity.",
        },
        "interactive": "motion",
    },
    "abstract": {
        "type_label": "Abstract structure (before formulas)",
        "what_is_asked": "What **type** of mathematical question is this — compare, estimate, optimize, or model change?",
        "variables": "Objective, decisions, measurements, unknown parameters, constraints",
        "math_useful": "Map structure first — then probability, statistics, calculus, optimization, or simulation",
        "analyst_steps": [
            "Name the goal: predict, compare, optimize, or explain.",
            "List variables and which are controlled vs. observed.",
            "State assumptions explicitly.",
            "Pick the smallest tool that fits the structure.",
        ],
        "limitations": "Skipping structure leads to the wrong formula for the right words.",
        "math_behind": {
            "Abstraction": "Different stories can share the same equation skeleton.",
            "Modeling": "Output = f(inputs) subject to constraints and noise.",
            "Simplification": "Remove detail until the core tradeoff remains.",
        },
        "interactive": "structure",
    },
}


# Extended copy for the 7-step area flow (merged by get_analyst_brief)
FLOW_EXTENSIONS: dict[str, dict] = {
    "betting": {
        "mathematical_form": (
            "This is a **probability and expected value** question: estimate P(win), "
            "compare to the price implied by the odds, and check whether EV > 0."
        ),
        "variables_list": ["Payout if win", "Amount risked", "Estimated P(win)", "Implied P(market)", "Uncertainty in your estimate"],
        "abstract_thinking": {
            "problem_kind": "Decision under uncertainty — compare your belief to the market price.",
            "structure": "EV = P(win)×gain − P(lose)×loss; positive EV means profitable long-term.",
            "comparing": "Your probability vs. break-even probability from the odds.",
            "matters": "Long-run edge and bet sizing — not whether you win once.",
            "assumptions": "Your probability estimate is calibrated; odds won't move before you bet.",
        },
        "solution": {
            "interpretation": "Read EV in dollars per bet, not as a guarantee for one outcome.",
            "recommendation": "Bet only when your estimated P(win) exceeds the implied probability by enough to cover uncertainty.",
            "data_needed": "Tracked results, closing lines, hand/bet history.",
            "uncertainty": "Short samples confuse luck with skill — use wide probability ranges.",
        },
        "go_deeper": {
            "simulation": "Monte Carlo: simulate thousands of bets with your P(win) to see bankroll paths.",
            "analyst": "An actuary asks: can you survive variance while capturing edge?",
            "practice": "Given +150 odds and 45% true chance — compute EV and break-even probability.",
        },
    },
    "sports": {
        "mathematical_form": (
            "This is a **probability forecasting** question: estimate P(event), compare to market odds, "
            "and quantify uncertainty from sample size and context (injuries, matchups)."
        ),
        "variables_list": ["Payout", "Stake", "Estimated P(outcome)", "Historical rates", "Injury/context factors", "Sample size"],
        "abstract_thinking": {
            "problem_kind": "Forecast + decision — is the market price wrong?",
            "structure": "True talent + context → P(outcome); compare to implied odds.",
            "comparing": "Your forecast vs. market; signal vs. noise in past stats.",
            "matters": "Calibration over many predictions — not one hot streak.",
            "assumptions": "Past data informs future; injuries and role changes are modeled.",
        },
        "solution": {
            "interpretation": "A 55% win estimate with 40% implied odds suggests edge; a 52% estimate may not after fees.",
            "recommendation": "Shrink extreme stats toward league average; then compare to odds.",
            "data_needed": "Player/team logs, injury reports, closing lines, bet log.",
            "uncertainty": "Small samples — report intervals, not point estimates.",
        },
        "go_deeper": {
            "simulation": "Bootstrap seasons or simulate game outcomes from rating models.",
            "analyst": "A statistician separates regression to the mean from true improvement.",
            "practice": "Judge hits 30 HRs: estimate P(30+) from career rate and playing time.",
        },
    },
    "medicine": {
        "mathematical_form": (
            "This is a **comparison / inference** question: does treatment change an outcome "
            "relative to control, and is the effect size clinically meaningful?"
        ),
        "variables_list": ["Outcome metric", "Treatment vs. control", "Growth/kill rates", "Toxicity", "Trial size", "Follow-up time"],
        "abstract_thinking": {
            "problem_kind": "Causal comparison — not 'did some patients improve?'",
            "structure": "Outcome(treatment) vs. outcome(control) with uncertainty bands.",
            "comparing": "Treatment arm vs. control arm on the same endpoint.",
            "matters": "Survival/time-to-event often beats snapshot response rates.",
            "assumptions": "Randomization, comparable groups, measured adherence.",
        },
        "solution": {
            "interpretation": "A higher response rate without control is weak evidence.",
            "recommendation": "Demand control data; model growth vs. kill if tracking tumors.",
            "data_needed": "RCT results, survival curves, dosing and toxicity logs.",
            "uncertainty": "Patient heterogeneity widens confidence intervals.",
        },
        "go_deeper": {
            "simulation": "Simulate tumor volume with dV/dt = growth − kill under different doses.",
            "analyst": "A biostatistician focuses on hazard ratios and trial power.",
            "practice": "If 60% shrink, what would control arm shrinkage need to be to convince you?",
        },
    },
    "ai": {
        "mathematical_form": (
            "This is an **optimization** question: choose model parameters to minimize loss on "
            "**new** data, not training data."
        ),
        "variables_list": ["Features", "Labels", "Loss", "Parameters", "Train/val/test metrics", "Compute budget"],
        "abstract_thinking": {
            "problem_kind": "Generalization — patterns that repeat out of sample.",
            "structure": "Minimize loss(subject to model class and data).",
            "comparing": "Training vs. validation performance.",
            "matters": "Validation error — not training accuracy alone.",
            "assumptions": "Train distribution matches deployment; labels are reliable.",
        },
        "solution": {
            "interpretation": "A large train–val gap means overfitting, not mastery.",
            "recommendation": "Hold out test data; tune only on validation.",
            "data_needed": "Labeled data, clear splits, domain shift checks.",
            "uncertainty": "Distribution shift can erase offline gains.",
        },
        "go_deeper": {
            "simulation": "Train a small model in the AI lab and watch loss curves.",
            "analyst": "A data scientist asks: what fails on the worst slice of data?",
            "practice": "92% train / 78% val — diagnose and propose one fix.",
        },
    },
    "space": {
        "mathematical_form": (
            "This is a **dynamics / optimization** question: how position and velocity change under forces, "
            "subject to fuel and path constraints."
        ),
        "variables_list": ["Position", "Velocity", "Acceleration/thrust", "Mass", "Fuel", "Time", "Target orbit"],
        "abstract_thinking": {
            "problem_kind": "Predict motion or optimize a path.",
            "structure": "ODEs from F = ma; conserve energy/momentum where applicable.",
            "comparing": "Required Δv vs. available fuel; trajectory vs. safety corridor.",
            "matters": "Constraints (thrust, heat) often bind before optimum performance.",
            "assumptions": "Point mass, known gravity field, simplified atmosphere.",
        },
        "solution": {
            "interpretation": "Orbital speed depends on radius; more fuel enables more maneuvers.",
            "recommendation": "Integrate equations of motion; check constraints before optimizing.",
            "data_needed": "Vehicle parameters, force models, mission targets.",
            "uncertainty": "Perturbations and model error accumulate over time.",
        },
        "go_deeper": {
            "simulation": "Use Space & Motion Lab tools for orbits and trajectories.",
            "analyst": "An engineer prototypes and measures — models must match telemetry.",
            "practice": "What changes if payload mass increases by 10%?",
        },
    },
    "weather": {
        "mathematical_form": (
            "This is a **probabilistic forecasting** question: assign chances to outcomes and "
            "widen uncertainty as forecast lead time grows."
        ),
        "variables_list": ["Lead time", "Ensemble members", "Historical calibration", "Region", "Metric (rain, temp)"],
        "abstract_thinking": {
            "problem_kind": "Forecast distribution — not a single future.",
            "structure": "Many simulations → distribution of outcomes.",
            "comparing": "Forecast probability vs. observed frequency (calibration).",
            "matters": "Honest uncertainty communication.",
            "assumptions": "Models capture relevant physics; ensembles span realistic spread.",
        },
        "solution": {
            "interpretation": "70% rain means ~7 in 10 similar days — not certainty tomorrow.",
            "recommendation": "Use ensembles; shorten horizon when precision matters.",
            "data_needed": "Historical observations, model runs, calibration scores.",
            "uncertainty": "Chaos amplifies small errors — long-range detail is unreliable.",
        },
        "go_deeper": {
            "simulation": "Run many noisy trend paths in the Weather lab.",
            "analyst": "A statistician scores Brier skill and calibration curves.",
            "practice": "Why is day-7 less certain than day-2?",
        },
    },
    "abstract": {
        "mathematical_form": (
            "Translate words into: **what quantity**, **what comparison or optimization**, "
            "and **what tool** (probability, statistics, calculus, optimization, simulation)."
        ),
        "variables_list": ["Objective", "Decisions", "Measurements", "Unknowns", "Constraints", "Assumptions"],
        "abstract_thinking": {
            "problem_kind": "Identify structure before calculation.",
            "structure": "Output = f(inputs) + noise, subject to limits.",
            "comparing": "Option A vs. B on the same metric.",
            "matters": "The right question — not the first formula you remember.",
            "assumptions": "Write them down so you can test them.",
        },
        "solution": {
            "interpretation": "Same math appears in betting, medicine, and engineering — different words.",
            "recommendation": "Classify the problem, then pick one primary tool.",
            "data_needed": "Whatever makes your estimate falsifiable.",
            "uncertainty": "Always state what you do not know.",
        },
        "go_deeper": {
            "simulation": "When closed-form math is hard, simulate many scenarios.",
            "analyst": "A mathematician simplifies until the core mechanism is visible.",
            "practice": "Take your question and label: predict, compare, or optimize?",
        },
    },
    "default": {
        "mathematical_form": "Translate the question into a **measurable quantity** and a **comparison or optimization**.",
        "variables_list": ["Outcome", "Inputs you control", "External factors", "Measurement error"],
        "abstract_thinking": {
            "problem_kind": "Quantitative decision or prediction.",
            "structure": "Objective + variables + constraints + uncertainty.",
            "comparing": "Your estimate vs. baseline or market.",
            "matters": "Falsifiable claims and honest uncertainty.",
            "assumptions": "Name what must hold for your approach to work.",
        },
        "solution": {
            "interpretation": "Numbers support decisions — they rarely replace judgment.",
            "recommendation": "Pick the simplest model that answers the question.",
            "data_needed": "Whatever tests your main assumption.",
            "uncertainty": "Report ranges when data is thin.",
        },
        "go_deeper": {
            "simulation": "Explore scenarios when one equation is not enough.",
            "analyst": "Match the tool to the structure, not the domain name.",
            "practice": "Rewrite your question in one sentence with a number in it.",
        },
    },
}


def get_analyst_brief(pattern_id: str) -> dict:
    """Merge base brief with flow extensions for the area UI."""
    base = dict(ANALYST_BRIEFS.get("default", {}))
    base.update(ANALYST_BRIEFS.get(pattern_id, {}))
    ext = FLOW_EXTENSIONS.get(pattern_id, FLOW_EXTENSIONS["default"])
    base.update(ext)
    return base
