"""Mathematical Problem Solving Lab — frameworks, patterns, and thinking prompts."""

PROBLEM_SOLVING_LAB = {
    "title": "Mathematical Problem Solving Lab",
    "icon": "🧠",
    "action": "Solve a Problem",
    "tagline": "Your mathematical consultant — discussion, modeling, and decision support before formulas.",
    "intro": (
        "Describe any problem. The consultant reframes what you're really solving, adapts follow-up "
        "questions to your answers, challenges assumptions, compares expert perspectives, and helps "
        "you build a model in plain language."
    ),
}

EXAMPLE_PROBLEMS = [
    "I want to improve my sports betting system.",
    "I want to improve my poker strategy.",
    "I want to predict baseball performance.",
    "I want to reduce traffic congestion.",
    "I want to understand why a cancer treatment works.",
    "I want to train an AI to recognize patterns.",
    "I want to increase my business profits.",
    "Custom problem (describe below)",
]

QUESTION_INTENTS = [
    ("predict", "Predict an outcome or future state"),
    ("optimize", "Find the best choice or strategy"),
    ("estimate", "Estimate an unknown quantity"),
    ("classify", "Sort cases into categories"),
    ("explain", "Explain why something happens"),
]

PROBLEM_CATEGORIES = [
    ("optimization", "Optimization — find the best feasible choice"),
    ("probability", "Probability — reason under uncertainty"),
    ("forecasting", "Forecasting — project future trends"),
    ("simulation", "Simulation — explore many possible futures"),
    ("growth", "Growth — track change over time"),
    ("pattern", "Pattern recognition — find structure in data"),
    ("decision", "Decision under uncertainty — choose with incomplete info"),
]

MATH_TOOLS = [
    "Calculus — rates of change and accumulation",
    "Probability — expected value and distributions",
    "Statistics — separating signal from noise",
    "Optimization — constraints and tradeoffs",
    "Simulation — Monte Carlo and scenario analysis",
    "Machine learning — learning patterns from data",
    "Differential equations — dynamic systems over time",
]

PROBLEM_BREAKDOWN_STEPS = [
    {
        "num": 1,
        "title": "Define objective",
        "prompt": "What are you actually trying to determine or improve?",
        "coach": "State the outcome in plain language. A good objective is specific enough to measure.",
        "question": "In one sentence, what does success look like?",
    },
    {
        "num": 2,
        "title": "Identify variables",
        "prompt": "What affects the outcome? What can you control vs. observe?",
        "coach": "List levers you can move and factors you can only measure.",
        "question": "What are the 3–5 most important variables?",
    },
    {
        "num": 3,
        "title": "Identify constraints",
        "prompt": "What limits your choices — budget, rules, physics, time, ethics?",
        "coach": "Constraints define what's actually possible. Ignoring them leads to useless models.",
        "question": "What can't you change or exceed?",
    },
    {
        "num": 4,
        "title": "Identify uncertainty",
        "prompt": "What don't you know for certain?",
        "coach": "Separate what you know from what you're guessing. Uncertainty is normal — name it.",
        "question": "What could surprise you? What ranges are plausible?",
    },
    {
        "num": 5,
        "title": "Identify data needed",
        "prompt": "What would you need to measure or collect to make progress?",
        "coach": "Good models start with honest data requirements, not wishful thinking.",
        "question": "What data do you have? What data do you still need?",
    },
    {
        "num": 6,
        "title": "Build a simple model",
        "prompt": "Write the problem in one sentence: output as a function of inputs, subject to limits.",
        "coach": "Maximize/minimize [objective] by choosing [variables], subject to [constraints], given [uncertainty].",
        "question": "Complete: I want to ___ [objective] by adjusting ___ [variables], limited by ___.",
    },
    {
        "num": 7,
        "title": "Improve the model",
        "prompt": "Where is your simple model likely wrong? What would you add next?",
        "coach": "Start simple, then add complexity only when the simple version fails.",
        "question": "What assumption would you test first? What would falsify your approach?",
    },
    {
        "num": 8,
        "title": "Interpret results",
        "prompt": "How will you use the answer? What decision changes if you're right or wrong?",
        "coach": "Math serves decisions. If the answer wouldn't change what you do, refine the question.",
        "question": "What would you do differently based on the model's output?",
    },
]

MATHEMATICIAN_MODE_TOPICS = [
    {
        "id": "abstraction",
        "name": "Abstraction",
        "idea": "Strip away detail until you see the underlying structure.",
        "prompt": "What is the core mechanism — in one sentence, without domain jargon?",
        "example": "Poker, insurance, and A/B tests all share expected-value thinking.",
    },
    {
        "id": "simplification",
        "name": "Simplification",
        "idea": "Ignore what barely matters. Focus on levers with large impact.",
        "prompt": "What could you safely ignore for this decision?",
        "example": "Traffic models start with flow rate, not every driver's personality.",
    },
    {
        "id": "modeling",
        "name": "Modeling",
        "idea": "Translate words into variables, relationships, and rules.",
        "prompt": "What are your inputs, outputs, and the rule connecting them?",
        "example": "Tumor volume = growth rate − treatment kill rate.",
    },
    {
        "id": "assumptions",
        "name": "Assumptions",
        "idea": "Every model assumes something. Make assumptions explicit so you can challenge them.",
        "prompt": "What are you assuming that might not be true?",
        "example": "Assuming win rate is constant ignores opponent adaptation.",
    },
    {
        "id": "variables",
        "name": "Variables",
        "idea": "Separate what you control from what you observe from what you infer.",
        "prompt": "Which variables are decisions vs. measurements vs. unknowns?",
        "example": "Bet size = decision. Win rate = unknown to estimate.",
    },
    {
        "id": "constraints",
        "name": "Constraints",
        "idea": "Constraints shape the feasible region — what's actually achievable.",
        "prompt": "What hard limits bound your options?",
        "example": "Bankroll caps bet size regardless of perceived edge.",
    },
    {
        "id": "uncertainty",
        "name": "Uncertainty",
        "idea": "Work with ranges and probabilities, not false precision.",
        "prompt": "What's the plausible range, not just your best guess?",
        "example": "Forecast 60–70% win rate, not exactly 64.2%.",
    },
    {
        "id": "optimization",
        "name": "Optimization",
        "idea": "Every 'best' implies a tradeoff. Name the objective and what you sacrifice.",
        "prompt": "What are you maximizing or minimizing, and at what cost?",
        "example": "Maximize long-term EV subject to risk of ruin.",
    },
]

# Adaptive follow-up questions — change based on problem type
ADAPTIVE_QUESTIONS = {
    "betting": [
        {
            "id": "optimizing",
            "question": "What are you optimizing?",
            "options": ["Profit", "Bankroll growth", "Consistency", "Lower risk"],
            "multi": False,
        },
        {
            "id": "info_sources",
            "question": "What information are you using?",
            "options": ["Pot odds", "Hand history", "Opponent reads", "Intuition"],
            "multi": True,
        },
        {
            "id": "challenge",
            "question": "What's your biggest challenge?",
            "options": ["Calculating EV", "Bankroll management", "Reading opponents", "Handling variance"],
            "multi": False,
        },
    ],
    "sports": [
        {
            "id": "optimizing",
            "question": "What are you optimizing?",
            "options": ["Profit", "Bankroll growth", "Consistency", "Lower risk"],
            "multi": False,
        },
        {
            "id": "info_sources",
            "question": "What information are you using?",
            "options": ["Odds", "Team statistics", "Injuries", "Personal judgment"],
            "multi": True,
        },
        {
            "id": "challenge",
            "question": "What's your biggest challenge?",
            "options": ["Picking winners", "Managing bankroll", "Understanding probability", "Finding value bets"],
            "multi": False,
        },
    ],
    "medicine": [
        {
            "id": "optimizing",
            "question": "What outcome matters most?",
            "options": ["Survival time", "Tumor shrinkage", "Side-effect reduction", "Quality of life"],
            "multi": False,
        },
        {
            "id": "info_sources",
            "question": "What evidence do you have?",
            "options": ["Clinical trial data", "Patient biomarkers", "Expert opinion", "Case reports"],
            "multi": True,
        },
        {
            "id": "challenge",
            "question": "What's hardest to account for?",
            "options": ["Individual variation", "Long-term effects", "Ethical constraints", "Small sample sizes"],
            "multi": False,
        },
    ],
    "traffic": [
        {
            "id": "optimizing",
            "question": "What are you optimizing?",
            "options": ["Travel time", "Throughput", "Cost", "Safety"],
            "multi": False,
        },
        {
            "id": "info_sources",
            "question": "What data do you have?",
            "options": ["Traffic sensors", "Commute surveys", "GPS traces", "Estimates only"],
            "multi": True,
        },
        {
            "id": "challenge",
            "question": "What's the main bottleneck?",
            "options": ["Capacity limits", "Demand peaks", "Routing choices", "Unpredictable incidents"],
            "multi": False,
        },
    ],
    "ai": [
        {
            "id": "optimizing",
            "question": "What are you optimizing?",
            "options": ["Accuracy", "Speed", "Interpretability", "Robustness on new data"],
            "multi": False,
        },
        {
            "id": "info_sources",
            "question": "What data do you have?",
            "options": ["Labeled training set", "Unlabeled data", "Expert rules", "Simulated data"],
            "multi": True,
        },
        {
            "id": "challenge",
            "question": "What's your biggest challenge?",
            "options": ["Overfitting", "Not enough data", "Biased data", "Choosing the right model"],
            "multi": False,
        },
    ],
    "business": [
        {
            "id": "optimizing",
            "question": "What are you optimizing?",
            "options": ["Profit", "Growth", "Customer retention", "Market share"],
            "multi": False,
        },
        {
            "id": "info_sources",
            "question": "What information are you using?",
            "options": ["Sales data", "Customer feedback", "Market research", "Gut feeling"],
            "multi": True,
        },
        {
            "id": "challenge",
            "question": "What's your biggest uncertainty?",
            "options": ["Customer demand", "Competition", "Pricing", "Execution capacity"],
            "multi": False,
        },
    ],
    "engineering": [
        {
            "id": "optimizing",
            "question": "What are you optimizing?",
            "options": ["Efficiency", "Cost", "Reliability", "Speed of development"],
            "multi": False,
        },
        {
            "id": "info_sources",
            "question": "What do you know so far?",
            "options": ["Prototype tests", "Physics equations", "Material specs", "Rough estimates"],
            "multi": True,
        },
        {
            "id": "challenge",
            "question": "What's the hardest constraint?",
            "options": ["Physical limits", "Budget", "Safety standards", "Manufacturing feasibility"],
            "multi": False,
        },
    ],
    "weather": [
        {
            "id": "optimizing",
            "question": "What are you trying to improve?",
            "options": ["Accuracy", "Lead time", "Uncertainty communication", "Regional precision"],
            "multi": False,
        },
        {
            "id": "info_sources",
            "question": "What inputs does your forecast use?",
            "options": ["Satellite data", "Historical records", "Multiple models", "Single app output"],
            "multi": True,
        },
        {
            "id": "challenge",
            "question": "What's hardest about this problem?",
            "options": ["Chaos / sensitivity", "Limited observations", "Communicating uncertainty", "Extreme events"],
            "multi": False,
        },
    ],
    "default": [
        {
            "id": "optimizing",
            "question": "What are you trying to achieve?",
            "options": ["Predict an outcome", "Optimize a decision", "Explain a phenomenon", "Estimate a quantity"],
            "multi": False,
        },
        {
            "id": "info_sources",
            "question": "What information do you have?",
            "options": ["Hard data", "Expert opinion", "Past experience", "Mostly guesses"],
            "multi": True,
        },
        {
            "id": "challenge",
            "question": "What's your biggest obstacle?",
            "options": ["Not enough data", "Too much uncertainty", "Unclear objective", "Too many variables"],
            "multi": False,
        },
    ],
}

# Keyword patterns → tailored coaching (no external API)
PROBLEM_PATTERNS = {
    r"poker|gambl|wager|casino|pot odds|blackjack": {
        "id": "betting",
        "intents": ["optimize", "estimate"],
        "categories": ["probability", "decision"],
        "variables": "Win probability, pot size, bet size, bankroll, opponent behavior",
        "constraints": "Stack size, table rules, bankroll management limits",
        "uncertainty": "Unknown opponent cards, future actions, short-term variance",
        "data": "Hand histories, pot odds, long-run ROI tracking",
        "tools": ["Probability", "Optimization", "Simulation"],
        "simple_model": "Maximize expected chip value of each decision subject to bankroll limits.",
        "suggested_lab": "Analyze a Bet",
        "tradeoff": "Aggressive play increases EV but also variance — survival matters long-term.",
    },
    r"sport|baseball|game|team|forecast|predict|betting system": {
        "id": "sports",
        "intents": ["predict", "estimate"],
        "categories": ["forecasting", "pattern", "probability"],
        "variables": "Team strength, sample size, injuries, home advantage, schedule",
        "constraints": "Limited data, market odds, budget for bets",
        "uncertainty": "True talent vs. luck, small samples, lineup changes",
        "data": "Historical results, player stats, betting market lines",
        "tools": ["Statistics", "Probability", "Machine learning"],
        "simple_model": "Estimate win probability from team ratings, compare to market odds.",
        "suggested_lab": "Predict a Game",
        "tradeoff": "Complex models fit history better but may not generalize to new seasons.",
    },
    r"cancer|tumor|treatment|drug|disease|medic|health|clinical": {
        "id": "medicine",
        "intents": ["explain", "predict", "optimize"],
        "categories": ["growth", "simulation", "optimization"],
        "variables": "Tumor growth rate, treatment efficacy, drug concentration, side effects",
        "constraints": "Toxicity limits, patient tolerance, regulatory rules",
        "uncertainty": "Individual patient response, tumor heterogeneity",
        "data": "Clinical trial results, biomarkers, dosing records",
        "tools": ["Calculus", "Differential equations", "Statistics", "Simulation"],
        "simple_model": "Compare tumor growth rate vs. treatment kill rate over time.",
        "suggested_lab": "Model a Disease",
        "tradeoff": "Higher dose may kill more tumor cells but increases side-effect risk.",
    },
    r"traffic|transport|congest|route|commute|logistic": {
        "id": "traffic",
        "intents": ["optimize", "predict"],
        "categories": ["simulation", "optimization"],
        "variables": "Flow rate, capacity, signal timing, demand patterns, routes",
        "constraints": "Road capacity, budget, safety regulations, geography",
        "uncertainty": "Accidents, demand spikes, weather disruptions",
        "data": "Traffic sensors, travel times, demand by hour/day",
        "tools": ["Optimization", "Simulation", "Statistics"],
        "simple_model": "Minimize average travel time by adjusting flow controls subject to capacity.",
        "suggested_lab": "Optimize a Decision",
        "tradeoff": "Optimizing one corridor may shift congestion elsewhere.",
    },
    r"machine|design|engineer|device|invent|hardware|efficien": {
        "id": "engineering",
        "intents": ["optimize", "explain"],
        "categories": ["optimization", "simulation"],
        "variables": "Efficiency, materials, dimensions, operating speed, cost",
        "constraints": "Physical laws, safety standards, manufacturing limits, budget",
        "uncertainty": "Material properties, wear, environmental conditions",
        "data": "Prototype tests, material specs, performance measurements",
        "tools": ["Calculus", "Optimization", "Simulation"],
        "simple_model": "Maximize output per unit cost subject to physical and safety constraints.",
        "suggested_lab": "Optimize a Decision",
        "tradeoff": "Lighter design saves cost but may reduce durability.",
    },
    r"ai|machine learning|neural|train|model learn|algorithm": {
        "id": "ai",
        "intents": ["predict", "classify", "optimize"],
        "categories": ["pattern", "optimization"],
        "variables": "Training data, model parameters, loss, learning rate, validation accuracy",
        "constraints": "Compute budget, data quality, overfitting risk",
        "uncertainty": "Generalization to new data, label noise",
        "data": "Labeled training set, validation set, test set",
        "tools": ["Machine learning", "Optimization", "Statistics"],
        "simple_model": "Minimize prediction error on new data by tuning model parameters.",
        "suggested_lab": "Train an AI",
        "tradeoff": "More complex models fit training data better but may fail on new examples.",
    },
    r"business|startup|idea|strategy|revenue|market|profit": {
        "id": "business",
        "intents": ["optimize", "predict", "estimate"],
        "categories": ["decision", "forecasting"],
        "variables": "Conversion rate, cost, demand, pricing, customer lifetime value",
        "constraints": "Budget, time, team capacity, regulations",
        "uncertainty": "Market response, competition, seasonality",
        "data": "Sales history, experiments, customer feedback",
        "tools": ["Statistics", "Optimization", "Simulation"],
        "simple_model": "Maximize profit by choosing pricing and spend subject to budget.",
        "suggested_lab": "Analyze an Idea",
        "tradeoff": "Growth speed vs. burn rate — faster scaling costs more upfront.",
    },
    r"weather|forecast|rain|storm|climate|temperature": {
        "id": "weather",
        "intents": ["predict", "estimate"],
        "categories": ["forecasting", "probability"],
        "variables": "Initial conditions, model ensemble, lead time, regional factors",
        "constraints": "Observation density, compute limits, communication clarity",
        "uncertainty": "Chaos sensitivity, model disagreement, extreme events",
        "data": "Historical observations, satellite data, ensemble model outputs",
        "tools": ["Statistics", "Probability", "Simulation"],
        "simple_model": "Weighted ensemble of models with widening uncertainty over lead time.",
        "suggested_lab": "Advanced reference",
        "tradeoff": "Longer lead times increase usefulness but also uncertainty.",
    },
}

DEFAULT_PATTERN = {
    "id": "default",
    "intents": ["predict", "optimize"],
    "categories": ["decision"],
    "variables": "Outcome you care about, inputs you control, external factors",
    "constraints": "Budget, time, rules, physical limits",
    "uncertainty": "Unknown parameters, future events, measurement error",
    "data": "What you can measure today vs. what you'd need to collect",
    "tools": ["Statistics", "Probability", "Optimization"],
    "simple_model": "Define objective → identify variables → add constraints → quantify uncertainty.",
    "suggested_lab": "Solve a Problem",
    "tradeoff": "Simple models are easier to use but may miss important effects.",
}

LAB_THINKING_PROMPTS = {
    "Betting & Poker Lab": {
        "lead_question": "Before we calculate — what are we trying to optimize?",
        "prompts": [
            ("What are we trying to optimize?", "Long-term expected value — not winning one hand."),
            ("What outcome matters most?", "Chip EV over many hands, not short-term luck."),
            ("What's uncertain?", "Opponent cards, future actions, variance in small samples."),
        ],
    },
    "Sports Prediction Lab": {
        "lead_question": "Before we forecast — what question are we actually answering?",
        "prompts": [
            ("What are we trying to predict?", "Win probability, score margin, or season performance?"),
            ("What variables drive the outcome?", "Team strength, sample size, injuries, schedule."),
            ("What's signal vs. noise?", "Early-season extremes often regress toward average."),
        ],
    },
    "Medicine & Disease Lab": {
        "lead_question": "Before we simulate — what outcome matters most?",
        "prompts": [
            ("What outcome matters most?", "Tumor shrinkage, infection peak, or drug concentration?"),
            ("What rates compete?", "Growth vs. treatment, infection vs. recovery."),
            ("What assumptions are we making?", "Homogeneous population, constant parameters, etc."),
        ],
    },
    "AI Learning Lab": {
        "lead_question": "Before we train — what is the model trying to minimize?",
        "prompts": [
            ("What is being optimized?", "Prediction error (loss) on training examples."),
            ("What could go wrong?", "Overfitting — memorizing noise instead of learning pattern."),
            ("How will you know it works?", "Performance on data the model hasn't seen."),
        ],
    },
}
