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


# ---------------------------------------------------------------------------
# Similar problems, real-world use, failure modes, alternative models
# ---------------------------------------------------------------------------

SIMILAR_PROBLEMS: dict[str, dict] = {
    "sports": {
        "related_fields": ["Poker & casino betting", "Insurance pricing", "Investing", "Weather forecasting"],
        "shared_concepts": ["Probability", "Expected value", "Uncertainty quantification", "Risk management", "Calibration"],
        "transfer_insight": "All of these require estimating hidden probabilities and comparing them to market prices.",
    },
    "betting": {
        "related_fields": ["Sports betting", "Insurance", "Trading", "Game theory"],
        "shared_concepts": ["Expected value", "Pot odds / implied probability", "Bankroll management", "Variance", "Long-run vs. single outcome"],
        "transfer_insight": "Every EV decision shares the same logic: compare your estimate to the price, then size for survival.",
    },
    "medicine": {
        "related_fields": ["Clinical trials", "Epidemiology", "Drug development", "Public health policy"],
        "shared_concepts": ["Control groups", "Survival analysis", "Growth vs. kill rates", "Risk-benefit tradeoffs", "Heterogeneity"],
        "transfer_insight": "Treatment evaluation always needs a comparison baseline and explicit toxicity constraints.",
    },
    "ai": {
        "related_fields": ["Statistics", "Forecasting", "Recommendation systems", "Computer vision"],
        "shared_concepts": ["Generalization", "Train/validation/test splits", "Loss functions", "Overfitting", "Distribution shift"],
        "transfer_insight": "The core question is always: will this pattern hold on data I haven't seen yet?",
    },
    "business": {
        "related_fields": ["Operations research", "Marketing analytics", "Supply chain", "Finance"],
        "shared_concepts": ["Optimization", "Unit economics", "Forecasting", "Constraints", "Scenario planning"],
        "transfer_insight": "Find the binding constraint first — optimizing the wrong lever wastes effort.",
    },
    "traffic": {
        "related_fields": ["Queueing theory", "Urban planning", "Supply chain logistics", "Network flow"],
        "shared_concepts": ["Capacity constraints", "Flow rates", "Bottlenecks", "Simulation", "Tradeoffs"],
        "transfer_insight": "Traffic is a queueing problem — demand, capacity, and delay are linked.",
    },
    "engineering": {
        "related_fields": ["Physics modeling", "Quality control", "Operations", "Reliability engineering"],
        "shared_concepts": ["Constraints", "Tolerance analysis", "Failure modes", "Optimization", "Prototyping"],
        "transfer_insight": "Engineering models must survive real-world tolerances, not just ideal conditions.",
    },
    "weather": {
        "related_fields": ["Epidemic forecasting", "Financial risk", "Sports prediction", "Climate modeling"],
        "shared_concepts": ["Ensemble forecasts", "Uncertainty growth", "Calibration", "Chaos sensitivity", "Probabilistic outputs"],
        "transfer_insight": "Forecast quality degrades with lead time — communicate ranges, not point predictions.",
    },
    "default": {
        "related_fields": ["Statistics", "Operations research", "Decision analysis", "Simulation"],
        "shared_concepts": ["Objective definition", "Variables & constraints", "Uncertainty", "Data requirements", "Validation"],
        "transfer_insight": "Most quantitative problems share the same skeleton: objective, levers, limits, and unknowns.",
    },
}

REAL_WORLD_EXAMPLES: dict[str, list[dict]] = {
    "sports": [
        {"name": "Moneyball (Oakland A's)", "use": "Used on-base percentage and undervalued stats to find market inefficiencies — same EV logic as betting."},
        {"name": "Professional betting syndicates", "use": "Build probability models, track closing line value, and size bets for long-run edge — not single-game wins."},
        {"name": "FiveThirtyEight forecasts", "use": "Combine statistical models with calibration tracking — publish probabilities, not certainties."},
    ],
    "betting": [
        {"name": "Poker solvers", "use": "Game-theory optimal strategies computed via simulation — EV per decision, not per hand."},
        {"name": "Blackjack card counting teams", "use": "Track running count to estimate edge, then adjust bet size — classic bankroll math."},
    ],
    "medicine": [
        {"name": "Randomized clinical trials", "use": "Gold standard for treatment evaluation — control group isolates drug effect from natural history."},
        {"name": "COVID forecasting (IHME, Imperial)", "use": "Epidemic models with uncertainty ranges updated as data arrived — showed limits of early predictions."},
        {"name": "Pharmacokinetic dosing", "use": "Calculus-based models optimize drug dose vs. toxicity for individual patients."},
    ],
    "ai": [
        {"name": "ChatGPT / LLM training", "use": "Massive data, loss minimization, validation on held-out text — generalization is the product."},
        {"name": "Netflix recommendations", "use": "Collaborative filtering predicts preferences — tested on users the model hasn't seen."},
        {"name": "AlphaFold", "use": "Deep learning for protein structure — validated against experimental structures not in training."},
    ],
    "business": [
        {"name": "Amazon supply chain", "use": "Optimization models for warehouse placement, inventory, and delivery routing."},
        {"name": "Uber surge pricing", "use": "Dynamic pricing balances supply and demand — real-time optimization under uncertainty."},
        {"name": "A/B testing at Google", "use": "Statistical experiments isolate causal effect of product changes on conversion."},
    ],
    "traffic": [
        {"name": "London congestion charging", "use": "Pricing model reduces demand during peak — optimization under political constraints."},
        {"name": "Waze routing", "use": "Real-time traffic simulation reroutes drivers — crowd-sourced data updates the model."},
    ],
    "engineering": [
        {"name": "Boeing wing stress testing", "use": "Simulation models tested against physical prototypes — safety margins built in."},
        {"name": "Tesla battery optimization", "use": "Thermal and degradation models constrain charging speed vs. battery life."},
    ],
    "weather": [
        {"name": "Hurricane ensemble forecasts (NHC)", "use": "Run dozens of models, show cone of uncertainty — never a single track."},
        {"name": "ECMWF vs. GFS", "use": "Competing global models compared continuously — calibration over decades."},
    ],
    "default": [
        {"name": "NASA mission planning", "use": "Trajectory optimization under fuel, time, and safety constraints."},
        {"name": "Insurance actuarial tables", "use": "Probability models priced from historical data with explicit tail-risk reserves."},
    ],
}

MODEL_FAILURE_MODES: dict[str, dict] = {
    "sports": {
        "categories": [
            {"type": "Bad assumptions", "examples": ["Injuries don't matter", "Past performance predicts future exactly", "Your edge is constant"]},
            {"type": "Missing information", "examples": ["Lineup changes", "Travel fatigue", "Motivation (elimination games)", "Closing line movement"]},
            {"type": "External shocks", "examples": ["Key player injury mid-season", "Rule changes", "Weather extremes"]},
            {"type": "Measurement errors", "examples": ["Small sample ROI", "Not tracking closing line value", "Survivorship bias in tipsters"]},
            {"type": "Overfitting", "examples": ["Backtesting on too few games", "Optimizing on last season only"]},
            {"type": "Bias", "examples": ["Favorite team bias", "Recency bias after hot streak", "Confirmation bias in stats"]},
        ],
    },
    "betting": {
        "categories": [
            {"type": "Bad assumptions", "examples": ["Opponents play perfectly", "Your reads are always accurate", "Short-term results reflect skill"]},
            {"type": "Missing information", "examples": ["Opponent range", "Stack depths", "Table dynamics", "Rake structure"]},
            {"type": "External shocks", "examples": ["Tilt after bad beat", "Fatigue", "Table change to tougher opponents"]},
            {"type": "Measurement errors", "examples": ["Incorrect pot odds calculation", "Not enough hands for ROI estimate"]},
            {"type": "Overfitting", "examples": ["Memorizing specific opponent tells", "Adjusting strategy after 50 hands"]},
            {"type": "Bias", "examples": ["Sunk cost fallacy (calling because already invested)", "Result-oriented thinking"]},
        ],
    },
    "medicine": {
        "categories": [
            {"type": "Bad assumptions", "examples": ["All patients respond identically", "Tumor shrinkage equals cure", "Side effects are rare enough to ignore"]},
            {"type": "Missing information", "examples": ["Patient comorbidities", "Tumor subtype", "Prior treatments", "Adherence rates"]},
            {"type": "External shocks", "examples": ["New standard of care emerges", "Supply chain disruption", "Unexpected toxicity signal"]},
            {"type": "Measurement errors", "examples": ["Response rate without control", "Surrogate endpoint that doesn't predict survival"]},
            {"type": "Overfitting", "examples": ["Subgroup analysis on small trial", "Cherry-picking responders post hoc"]},
            {"type": "Bias", "examples": ["Selection bias (healthier patients enrolled)", "Publication bias"]},
        ],
    },
    "ai": {
        "categories": [
            {"type": "Bad assumptions", "examples": ["Training data represents production", "More parameters always help", "Accuracy is the right metric"]},
            {"type": "Missing information", "examples": ["Label noise", "Class imbalance", "Feature drift at deployment"]},
            {"type": "External shocks", "examples": ["New user population", "Adversarial inputs", "Regulatory change"]},
            {"type": "Measurement errors", "examples": ["Data leakage between train and test", "Evaluating on training set"]},
            {"type": "Overfitting", "examples": ["Model memorizes training examples", "Too many hyperparameter tuning rounds on validation set"]},
            {"type": "Bias", "examples": ["Historical bias in training data", "Underrepresented groups in data"]},
        ],
    },
    "business": {
        "categories": [
            {"type": "Bad assumptions", "examples": ["Demand is stable", "Competitors won't react", "Past CAC predicts future CAC"]},
            {"type": "Missing information", "examples": ["Churn reasons", "True unit economics", "Capacity constraints"]},
            {"type": "External shocks", "examples": ["Market downturn", "New competitor", "Regulatory change"]},
            {"type": "Measurement errors", "examples": ["Vanity metrics vs. profit", "Attribution errors in marketing"]},
            {"type": "Overfitting", "examples": ["Optimizing on one quarter's data", "Over-segmenting customers"]},
            {"type": "Bias", "examples": ["Optimism bias in forecasts", "Sunk cost in failing projects"]},
        ],
    },
    "default": {
        "categories": [
            {"type": "Bad assumptions", "examples": ["Relationships stay linear", "Past patterns continue", "Missing variables don't matter"]},
            {"type": "Missing information", "examples": ["Confounders", "Unmeasured inputs", "Feedback loops"]},
            {"type": "External shocks", "examples": ["Black swan events", "Policy changes", "Technology disruption"]},
            {"type": "Measurement errors", "examples": ["Noisy data", "Small samples", "Survivorship bias"]},
            {"type": "Overfitting", "examples": ["Model fits noise in historical data", "Too many parameters for available data"]},
            {"type": "Bias", "examples": ["Confirmation bias", "Selection bias in data collection"]},
        ],
    },
}

ALTERNATIVE_MODELS: dict[str, list[dict]] = {
    "sports": [
        {"name": "Statistical rating model", "when": "You have historical results and want baseline team strength.", "tradeoff": "Simple and interpretable, but misses real-time context."},
        {"name": "Machine learning model", "when": "You have rich feature data (injuries, travel, rest days).", "tradeoff": "Can capture complex patterns, but risks overfitting."},
        {"name": "Simulation model", "when": "You want to explore many season scenarios.", "tradeoff": "Flexible, but requires assumptions about distributions."},
    ],
    "betting": [
        {"name": "EV calculator", "when": "You know your equity and pot odds per decision.", "tradeoff": "Exact for one decision, doesn't model opponent adaptation."},
        {"name": "Game theory model", "when": "You want optimal strategy vs. rational opponents.", "tradeoff": "Theoretically sound, but opponents aren't always rational."},
        {"name": "Simulation (Monte Carlo)", "when": "You want to estimate long-run bankroll outcomes.", "tradeoff": "Shows variance ranges, but depends on input distributions."},
    ],
    "medicine": [
        {"name": "Growth model", "when": "You want to track tumor volume over time.", "tradeoff": "Intuitive calculus, but assumes homogeneous tumor."},
        {"name": "Treatment effect model", "when": "You want to compare drug vs. control.", "tradeoff": "Rigorous with RCT data, but expensive and slow."},
        {"name": "Survival model", "when": "Time-to-event is the outcome that matters.", "tradeoff": "Handles censored data, but needs long follow-up."},
    ],
    "ai": [
        {"name": "Linear / logistic model", "when": "You need interpretability and have limited data.", "tradeoff": "Fast and explainable, but misses nonlinear patterns."},
        {"name": "Deep learning model", "when": "You have large labeled datasets and complex patterns.", "tradeoff": "Powerful, but black-box and data-hungry."},
        {"name": "Ensemble model", "when": "You want robustness by combining multiple approaches.", "tradeoff": "Often best performance, but harder to debug."},
    ],
    "business": [
        {"name": "Revenue driver model", "when": "You want to understand what moves the top line.", "tradeoff": "Clear levers, but may ignore cost structure."},
        {"name": "Optimization model", "when": "You need to allocate budget or resources optimally.", "tradeoff": "Finds best allocation, but sensitive to constraint assumptions."},
        {"name": "Forecasting model", "when": "You need to project future demand or revenue.", "tradeoff": "Useful for planning, but uncertainty grows with horizon."},
    ],
    "default": [
        {"name": "Deterministic model", "when": "Relationships are well understood and stable.", "tradeoff": "Simple, but ignores uncertainty."},
        {"name": "Probabilistic model", "when": "Outcomes are uncertain and you need ranges.", "tradeoff": "Honest about uncertainty, but harder to communicate."},
        {"name": "Simulation model", "when": "The system is too complex for closed-form math.", "tradeoff": "Flexible, but output quality depends on input assumptions."},
    ],
}


def _field_quality(text: str, min_good: int = 40, min_ok: int = 15) -> str:
    """Return 'good', 'ok', 'weak', or 'empty' based on text length."""
    n = len(text.strip())
    if n >= min_good:
        return "good"
    if n >= min_ok:
        return "ok"
    if n > 0:
        return "weak"
    return "empty"


def critique_model(
    model: dict[str, str],
    breakdown: dict[int, str],
    adaptive: dict,
    pattern_id: str,
) -> dict[str, list[dict[str, str]]]:
    """Evaluate user's model — strengths, weaknesses, blind spots, improvements with WHY."""
    strengths: list[dict[str, str]] = []
    weaknesses: list[dict[str, str]] = []
    blind_spots: list[dict[str, str]] = []
    improvements: list[dict[str, str]] = []

    objective = model.get("objective", "") or breakdown.get(1, "")
    variables = model.get("variables", "") or breakdown.get(2, "")
    constraints = model.get("constraints", "") or breakdown.get(3, "")
    uncertainty = model.get("uncertainty", "") or breakdown.get(4, "")
    data_inputs = model.get("data_inputs", "") or breakdown.get(5, "")
    simplified = model.get("simplified_model", "") or breakdown.get(6, "")
    improvements_text = model.get("improvements", "")

    obj_q = _field_quality(objective, 30, 12)
    var_q = _field_quality(variables, 25, 10)
    con_q = _field_quality(constraints, 15, 5)
    unc_q = _field_quality(uncertainty, 15, 5)
    data_q = _field_quality(data_inputs, 15, 5)
    simp_q = _field_quality(simplified, 30, 12)

    if obj_q in ("good", "ok"):
        strengths.append({
            "text": "Objective is stated",
            "why": f"You defined what success looks like ({objective[:60]}…). Without this, no model can be evaluated.",
        })
    else:
        weaknesses.append({
            "text": "Objective clarity is weak",
            "why": "A consultant can't advise you if the goal is vague. Specify one measurable outcome.",
        })

    if var_q in ("good", "ok"):
        strengths.append({
            "text": "Key variables identified",
            "why": "Naming levers and outputs shows you understand what drives the system.",
        })
    else:
        weaknesses.append({
            "text": "Variables are underspecified",
            "why": "Without variables, you can't build equations, collect data, or test assumptions.",
        })

    if con_q in ("good", "ok"):
        strengths.append({
            "text": "Constraints acknowledged",
            "why": "Constraints define what's feasible — ignoring them produces unrealistic recommendations.",
        })
    else:
        blind_spots.append({
            "text": "Constraints may be missing",
            "why": "Unstated limits (budget, rules, capacity) often cause models to recommend impossible actions.",
        })

    if unc_q in ("good", "ok"):
        strengths.append({
            "text": "Uncertainty is named",
            "why": "Good models explicitly state what you don't know — this prevents false confidence.",
        })
    else:
        blind_spots.append({
            "text": "Sources of uncertainty not addressed",
            "why": "Every model has unknowns. Unnamed uncertainty becomes hidden risk.",
        })

    if data_q in ("good", "ok"):
        strengths.append({
            "text": "Data requirements specified",
            "why": "Knowing what to measure makes the model testable rather than theoretical.",
        })
    else:
        weaknesses.append({
            "text": "Data inputs unclear",
            "why": "A model without a data plan can't be validated — you'll never know if it's right.",
        })

    if simp_q in ("good",):
        strengths.append({
            "text": "Simplified model is well articulated",
            "why": "A one-sentence model proves you can explain the logic to someone else.",
        })
    elif simp_q == "ok":
        improvements.append({
            "text": "Sharpen the simplified model",
            "why": "Try: 'Maximize [X] by choosing [Y] subject to [Z], given [uncertainty].'",
        })
    else:
        weaknesses.append({
            "text": "No simplified model in plain language",
            "why": "If you can't say it in one sentence, the model isn't clear enough to use.",
        })

    if improvements_text.strip():
        strengths.append({
            "text": "You've thought about model evolution",
            "why": "Planning improvements shows you expect the simple model to break — that's mature thinking.",
        })
    else:
        improvements.append({
            "text": "Add a plan for when the simple model fails",
            "why": "Every model breaks eventually. Knowing what to add next saves time later.",
        })

    sources = adaptive.get("info_sources", [])
    if isinstance(sources, list) and sources and any(s in INTUITION_SOURCES for s in sources):
        blind_spots.append({
            "text": "Heavy reliance on intuition without data",
            "why": "Intuition isn't falsifiable. One measurement would let you test whether your gut is calibrated.",
        })

    branch = adaptive.get("branch_answers", {})
    if branch.get("How are you measuring profit?") == "Haven't tracked yet" or branch.get("Track results over 1,000+ hands?") == "No":
        blind_spots.append({
            "text": "No tracking system for outcomes",
            "why": "Without recorded results, you can't distinguish skill from luck or know if you're improving.",
        })

    failure_modes = MODEL_FAILURE_MODES.get(pattern_id, MODEL_FAILURE_MODES["default"])
    for cat in failure_modes["categories"][:2]:
        blind_spots.append({
            "text": f"Watch for: {cat['type'].lower()}",
            "why": f"Common in this domain: {', '.join(cat['examples'][:2])}.",
        })

    complexity_fields = sum(1 for q in (obj_q, var_q, con_q, unc_q, data_q, simp_q) if q == "good")
    if complexity_fields >= 5 and not improvements_text.strip():
        improvements.append({
            "text": "Model may be getting complex without a validation plan",
            "why": "Rich models need testing. Define one experiment that would prove or disprove your core claim.",
        })
    elif complexity_fields <= 2:
        improvements.append({
            "text": "Flesh out more model components",
            "why": "A consultant needs objective, variables, constraints, uncertainty, and data before giving advice.",
        })

    if not strengths:
        strengths.append({
            "text": "You've started structuring the problem",
            "why": "Even an incomplete model is better than unstructured guessing.",
        })

    return {
        "strengths": strengths[:4],
        "weaknesses": weaknesses[:4],
        "blind_spots": blind_spots[:4],
        "improvements": improvements[:4],
    }


def assess_confidence(
    model: dict[str, str],
    breakdown: dict[int, str],
    adaptive: dict,
    pattern_id: str,
) -> dict:
    """Assess how confident we should be in the model."""
    factors: list[dict[str, str]] = []
    score = 50

    data_q = _field_quality(model.get("data_inputs", "") or breakdown.get(5, ""))
    unc_q = _field_quality(model.get("uncertainty", "") or breakdown.get(4, ""))
    obj_q = _field_quality(model.get("objective", "") or breakdown.get(1, ""))

    if data_q == "good":
        score += 15
        factors.append({"factor": "Data plan exists", "impact": "positive", "detail": "You know what to measure — the model can be tested."})
    elif data_q == "empty":
        score -= 15
        factors.append({"factor": "No data plan", "impact": "negative", "detail": "Without data, confidence should stay low regardless of logic."})

    if unc_q in ("good", "ok"):
        score += 10
        factors.append({"factor": "Uncertainty acknowledged", "impact": "positive", "detail": "Naming unknowns prevents overconfidence."})
    else:
        score -= 10
        factors.append({"factor": "Unnamed uncertainty", "impact": "negative", "detail": "Hidden unknowns are the main source of model failure."})

    if obj_q in ("good", "ok"):
        score += 10
        factors.append({"factor": "Clear objective", "impact": "positive", "detail": "A measurable goal makes validation possible."})
    else:
        score -= 10
        factors.append({"factor": "Vague objective", "impact": "negative", "detail": "You can't calibrate confidence without knowing what you're predicting."})

    sources = adaptive.get("info_sources", [])
    if isinstance(sources, list):
        if any(s in INTUITION_SOURCES for s in sources):
            score -= 15
            factors.append({"factor": "Intuition-based inputs", "impact": "negative", "detail": "Gut feelings aren't calibrated — track and measure instead."})
        if len(sources) >= 2 and not all(s in INTUITION_SOURCES for s in sources):
            score += 10
            factors.append({"factor": "Multiple information sources", "impact": "positive", "detail": "Triangulating sources reduces single-source bias."})

    branch = adaptive.get("branch_answers", {})
    if branch.get("Accuracy on which data?") in ("Training only", "Haven't split data"):
        score -= 20
        factors.append({"factor": "No out-of-sample validation", "impact": "negative", "detail": "Training performance overstates real-world reliability."})

    score = max(10, min(90, score))
    if score >= 65:
        level, label = "moderate-high", "Moderately confident — but validate before acting"
    elif score >= 40:
        level, label = "moderate", "Moderate confidence — key assumptions need testing"
    else:
        level, label = "low", "Low confidence — gather data before relying on this model"

    return {
        "score": score,
        "level": level,
        "label": label,
        "factors": factors,
        "guidance": (
            "Good mathematical thinking includes honest uncertainty. "
            "Confidence should come from validated data, not from how polished the model sounds."
        ),
    }
