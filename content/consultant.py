"""Mathematical consultant — branching dialogue, model templates, reframing."""

MODEL_BUILDER_FIELDS = [
    ("objective", "Objective", "What are you maximizing, minimizing, or predicting?"),
    ("variables", "Variables", "What inputs and outputs define the system?"),
    ("constraints", "Constraints", "What limits what's achievable?"),
    ("uncertainty", "Sources of uncertainty", "What don't you know for certain?"),
    ("data_inputs", "Data inputs", "What would you measure or collect?"),
    ("math_tools", "Mathematical tools", "Which approaches fit — tool types, not formulas."),
    ("simplified_model", "Simplified model", "One-sentence model in plain language."),
    ("improvements", "Potential improvements", "What would you add when the simple model breaks?"),
]

BRANCHING_FOLLOWUPS: dict[str, dict[str, list[dict]]] = {
    "sports": {
        "Profit": [
            {"question": "How are you measuring profit?", "options": ["Per bet ROI", "Weekly bankroll change", "Season-long track record", "Haven't tracked yet"]},
            {"question": "Where do you believe your edge comes from?", "options": ["Better probability estimates", "Line shopping", "Market inefficiencies", "Not sure yet"]},
        ],
        "Lower risk": [
            {"question": "What does lower risk mean for you?", "options": ["Smaller bet sizes", "Fewer bets", "Lower variance outcomes", "Avoiding ruin"]},
            {"question": "Risk tolerance for a bad month?", "options": ["<5% bankroll loss", "5–15%", ">15%", "Haven't defined this"]},
        ],
        "Consistency": [
            {"question": "Consistent in what sense?", "options": ["Winning percentage", "Monthly profit", "Beating closing line", "Emotional discipline"]},
        ],
        "Bankroll growth": [
            {"question": "Growth approach?", "options": ["Steady compounding", "Aggressive Kelly-style", "Flat unit betting", "No target yet"]},
            {"question": "Bankroll management rule?", "options": ["Fixed unit size", "Percentage of bankroll", "Kelly criterion", "No formal rule"]},
        ],
    },
    "betting": {
        "Profit": [
            {"question": "Per-hand EV or session profit?", "options": ["Per-hand EV", "Session profit", "Long-run hourly rate"]},
            {"question": "Track results over 1,000+ hands?", "options": ["Yes", "No", "Starting to"]},
        ],
        "Lower risk": [{"question": "Stop-loss or bankroll cap?", "options": ["Defined amount", "Percentage of total", "None yet"]}],
        "Consistency": [{"question": "Decisions or outcomes?", "options": ["Decision quality (EV)", "Short-term results", "Both"]}],
        "Bankroll growth": [{"question": "Bet sizing method?", "options": ["Fixed units", "Pot-relative", "Kelly-based", "Ad hoc"]}],
    },
    "medicine": {
        "Survival time": [{"question": "Survival compared to what?", "options": ["Standard of care", "No treatment", "Historical cohort", "Unsure"]}],
        "Tumor shrinkage": [{"question": "Shrinkage enough alone?", "options": ["Yes", "No — need survival too", "Unsure"]}],
        "Side-effect reduction": [{"question": "Efficacy tradeoff defined?", "options": ["Yes", "Case-by-case", "Not yet"]}],
        "Quality of life": [{"question": "How measure QoL?", "options": ["Validated survey", "Patient-reported", "No measure yet"]}],
    },
    "ai": {
        "Accuracy": [
            {"question": "Accuracy on which data?", "options": ["Training only", "Validation set", "Production data", "Haven't split data"]},
            {"question": "Is accuracy the right metric?", "options": ["Yes", "Need precision/recall", "Different metric needed"]},
        ],
        "Robustness on new data": [{"question": "What could change at deployment?", "options": ["Nothing", "Different population", "Data drift", "Unknown"]}],
        "Interpretability": [{"question": "Who must understand it?", "options": ["Regulators", "End users", "Engineers only", "Everyone"]}],
        "Speed": [{"question": "Latency requirement?", "options": ["Real-time", "Batch OK", "Not defined"]}],
    },
    "business": {
        "Profit": [
            {"question": "Largest profit lever?", "options": ["Revenue growth", "Cost reduction", "Pricing", "Retention"]},
            {"question": "Unit economics per customer?", "options": ["Yes", "Partially", "No"]},
        ],
        "Growth": [{"question": "Growth at what cost?", "options": ["Defined CAC limit", "Growth first", "Not measured"]}],
        "Customer retention": [{"question": "Why customers leave?", "options": ["Survey data", "Hypotheses only", "No data"]}],
        "Market share": [{"question": "Share vs. profitability?", "options": ["Share first", "Profit first", "Balanced"]}],
    },
    "default": {
        "Predict an outcome": [{"question": "Time horizon?", "options": ["Short-term", "Medium-term", "Long-term", "Undefined"]}],
        "Optimize a decision": [{"question": "Main tradeoff?", "options": ["Cost vs. quality", "Speed vs. accuracy", "Risk vs. reward", "Unclear"]}],
        "Explain a phenomenon": [{"question": "What confirms your explanation?", "options": ["Experiment", "Historical data", "Expert consensus", "None yet"]}],
        "Estimate a quantity": [{"question": "Required precision?", "options": ["Order of magnitude", "Within 10%", "Very precise", "Unknown"]}],
    },
}

REAL_PROBLEM_REFRAMES = {
    "sports": {
        "underlying": "Finding situations where your estimated win probability exceeds the market's implied probability.",
        "measurable": "Expected value per bet, ROI over 100+ bets, calibration of probability estimates.",
        "optimization_target": "Maximize long-term expected value subject to bankroll and risk constraints.",
        "wrong_problem_examples": [
            ("I want to win more bets", "Win rate ≠ profit. A 40% win rate can be profitable at the right odds."),
            ("I want to pick more winners", "Picking winners ignores whether the bet had positive expected value."),
        ],
    },
    "betting": {
        "underlying": "Maximizing expected chip value across many decisions, not winning any single hand.",
        "measurable": "EV per decision, hourly rate, ROI over thousands of hands.",
        "optimization_target": "Maximize long-term EV subject to bankroll survival.",
        "wrong_problem_examples": [("I want to win this hand", "Single-hand outcomes are dominated by variance.")],
    },
    "medicine": {
        "underlying": "Comparing treatment effect against control — not just observing improvement.",
        "measurable": "Survival time, tumor volume trajectory, adverse event rates.",
        "optimization_target": "Maximize patient outcome subject to toxicity constraints.",
        "wrong_problem_examples": [("The drug shrinks tumors", "Without a control, you can't attribute shrinkage to the drug.")],
    },
    "ai": {
        "underlying": "Minimizing prediction error on unseen data — not memorizing training examples.",
        "measurable": "Validation loss, precision/recall on holdout set, calibration.",
        "optimization_target": "Minimize generalization error subject to compute constraints.",
        "wrong_problem_examples": [("I want higher training accuracy", "Training accuracy rewards memorization.")],
    },
    "business": {
        "underlying": "Identifying the binding constraint on profit and optimizing that lever first.",
        "measurable": "Unit economics, conversion, CAC, LTV, margin.",
        "optimization_target": "Maximize profit subject to budget and capacity.",
        "wrong_problem_examples": [("I want more revenue", "Revenue without margin can destroy value.")],
    },
    "traffic": {
        "underlying": "Matching traffic demand to road capacity.",
        "measurable": "Average travel time, throughput, queue length.",
        "optimization_target": "Minimize travel time subject to safety and budget.",
        "wrong_problem_examples": [("Add more lanes everywhere", "Induced demand may erase gains.")],
    },
    "engineering": {
        "underlying": "Maximize performance per unit cost within physical limits.",
        "measurable": "Efficiency, failure rate, cost per unit.",
        "optimization_target": "Maximize performance/cost subject to safety.",
        "wrong_problem_examples": [("Make it as fast as possible", "Speed may trade off reliability.")],
    },
    "weather": {
        "underlying": "Quantifying uncertainty that grows with forecast lead time.",
        "measurable": "Calibration scores, Brier score, ensemble spread.",
        "optimization_target": "Minimize forecast error while communicating uncertainty.",
        "wrong_problem_examples": [("Which app is right tomorrow?", "Single forecasts hide uncertainty.")],
    },
    "default": {
        "underlying": "Translating a vague goal into a measurable objective with levers and constraints.",
        "measurable": "One primary metric that proves success or failure.",
        "optimization_target": "State what you maximize/minimize subject to what limits.",
        "wrong_problem_examples": [],
    },
}

_DEFAULT_MODEL = {
    "model_types": [
        {"name": "Structural model", "purpose": "Core relationships", "plain": "Output = f(inputs) subject to constraints"},
    ],
    "defaults": {
        "objective": "Define your measurable goal",
        "variables": "Inputs you control, outputs you care about",
        "constraints": "Budget, time, rules, physical limits",
        "uncertainty": "Unknown parameters, future events",
        "data_inputs": "What you can measure today",
        "math_tools": "Statistics, probability, optimization as needed",
        "simplified_model": "Maximize/minimize [objective] by choosing [variables] subject to [constraints]",
        "improvements": "Add complexity only when the simple model fails validation",
    },
}

MODEL_TEMPLATES: dict[str, dict] = {
    "sports": {
        "model_types": [
            {"name": "Probability model", "purpose": "Estimate true win probability.", "plain": "P(win) = f(team rating, injuries, context)"},
            {"name": "Expected value model", "purpose": "Compare your probability to market odds.", "plain": "EV = P(your est) × profit − P(lose) × stake"},
            {"name": "Bankroll model", "purpose": "Size bets to limit ruin.", "plain": "Bet size = f(edge, bankroll, risk tolerance)"},
        ],
        "defaults": {
            "objective": "Maximize long-term expected value per bet",
            "variables": "Win probability, odds, bet size, bankroll",
            "constraints": "Bankroll limits, max bet size",
            "uncertainty": "True win probability unknown; short-sample variance",
            "data_inputs": "Historical results, closing lines, bet log with ROI",
            "math_tools": "Probability, expected value, statistics, Kelly sizing",
            "simplified_model": "Bet when estimated P(win) > implied P(odds), size by edge",
            "improvements": "Injury data, line movement, sport-specific ratings",
        },
    },
    "betting": {
        "model_types": [
            {"name": "Expected value model", "purpose": "Per-decision chip EV", "plain": "EV = P(win)×pot − P(lose)×call"},
            {"name": "Pot odds model", "purpose": "Required equity vs. pot odds", "plain": "Call if equity > pot odds required"},
            {"name": "Bankroll model", "purpose": "Survive variance", "plain": "Risk of ruin vs. bet sizing"},
        ],
        "defaults": {
            "objective": "Maximize long-term chip EV",
            "variables": "Win probability, pot size, bet/call amount, stack size",
            "constraints": "Stack limits, table rules, bankroll",
            "uncertainty": "Unknown cards, opponent actions, variance",
            "data_inputs": "Hand histories, session results, tracked ROI",
            "math_tools": "Probability, expected value, game theory",
            "simplified_model": "Call when EV > 0 given estimated equity and pot odds",
            "improvements": "Opponent modeling, position, multi-street planning",
        },
    },
    "medicine": {
        "model_types": [
            {"name": "Growth model", "purpose": "Tumor volume over time", "plain": "dV/dt = growth rate − treatment kill rate"},
            {"name": "Treatment model", "purpose": "Drug effect vs. toxicity", "plain": "Response = f(dose, schedule) subject to toxicity cap"},
            {"name": "Survival model", "purpose": "Time-to-event outcomes", "plain": "Compare survival curves treatment vs. control"},
        ],
        "defaults": {
            "objective": "Maximize treatment benefit subject to safety",
            "variables": "Tumor volume, drug dose, schedule, side-effect score",
            "constraints": "Toxicity limits, patient tolerance, regulatory rules",
            "uncertainty": "Individual patient response, tumor heterogeneity",
            "data_inputs": "Trial data with control arm, biomarkers, dosing records",
            "math_tools": "Calculus (growth rates), statistics (trials), optimization (dosing)",
            "simplified_model": "Compare growth rate vs. kill rate; require control group",
            "improvements": "Patient subgroups, pharmacokinetics, adaptive trials",
        },
    },
    "business": {
        "model_types": [
            {"name": "Revenue model", "purpose": "Drivers of revenue", "plain": "Revenue = customers × conversion × price × frequency"},
            {"name": "Cost model", "purpose": "Fixed vs. variable costs", "plain": "Profit = revenue − fixed − variable costs"},
            {"name": "Optimization model", "purpose": "Best budget allocation", "plain": "Maximize profit subject to budget and capacity"},
        ],
        "defaults": {
            "objective": "Maximize profit or sustainable growth",
            "variables": "Conversion rate, CAC, LTV, pricing, costs",
            "constraints": "Budget, team capacity, market size",
            "uncertainty": "Customer response, competition, seasonality",
            "data_inputs": "Sales history, cohort retention, A/B test results",
            "math_tools": "Statistics, optimization, simulation",
            "simplified_model": "Find binding constraint on profit; optimize that lever first",
            "improvements": "Cohort models, elasticity estimates, scenario planning",
        },
    },
    "ai": {
        "model_types": [
            {"name": "Prediction model", "purpose": "Map inputs to outputs", "plain": "ŷ = f(x; weights) learned from data"},
            {"name": "Training model", "purpose": "How weights update", "plain": "Minimize loss via gradient descent"},
            {"name": "Loss minimization model", "purpose": "Define what wrong means", "plain": "Optimize weights to minimize error on new data"},
        ],
        "defaults": {
            "objective": "Minimize prediction error on unseen data",
            "variables": "Model parameters, learning rate, training/validation metrics",
            "constraints": "Compute budget, latency, interpretability",
            "uncertainty": "Generalization gap, label noise, distribution shift",
            "data_inputs": "Train/validation/test splits, labeled examples",
            "math_tools": "Optimization (gradients), statistics, machine learning",
            "simplified_model": "Train on train, tune on validation, report test performance once",
            "improvements": "Regularization, data augmentation, ensembles",
        },
    },
    "default": _DEFAULT_MODEL,
}

INTUITION_SOURCES = {"Personal judgment", "Intuition", "Gut feeling", "Mostly guesses"}


def get_critical_pushbacks(adaptive: dict, pattern_id: str) -> list[str]:
    """Return consultant pushback messages based on user's answers."""
    messages: list[str] = []
    sources = adaptive.get("info_sources", [])
    if isinstance(sources, list) and sources and all(s in INTUITION_SOURCES for s in sources):
        messages.append(
            "**Pushback:** Gut feeling alone is not a model. What one measurement could replace "
            "guesswork and give you a falsifiable claim?"
        )
    if adaptive.get("optimizing") in ("Profit", "Bankroll growth") and adaptive.get("challenge") in (
        "Picking winners", "Calculating EV",
    ):
        messages.append(
            "**Wait.** You want profit but your challenge is picking winners. Those aren't the same — "
            "you can win more bets and still lose money. Should your real target be positive *expected value*?"
        )
    branch_answers = adaptive.get("branch_answers", {})
    if adaptive.get("optimizing") == "Profit" and branch_answers.get("How are you measuring profit?") == "Haven't tracked yet":
        messages.append(
            "**Challenge:** You want profit but aren't tracking results. Without data, you can't know "
            "if you're improving. What's the smallest dataset you could start collecting this week?"
        )
    if pattern_id == "medicine" and adaptive.get("optimizing") == "Tumor shrinkage":
        messages.append(
            "**Important:** Tumor shrinkage alone can mislead without a control group. "
            "What comparison would make this evidence credible?"
        )
    if pattern_id == "ai" and adaptive.get("optimizing") == "Accuracy":
        branch = branch_answers.get("Accuracy on which data?", "")
        if branch in ("Training only", "Haven't split data", ""):
            messages.append(
                "**Challenge:** High training accuracy often means overfitting. "
                "How would your approach perform on data the model hasn't seen?"
            )
    if not messages:
        messages.append(
            "**Good.** You're engaging with the structure. Now stress-test one assumption — "
            "what would have to be true for your approach to fail?"
        )
    return messages
