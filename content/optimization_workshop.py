"""Optimization Workshop — guided consultant flow for real-world improvement problems."""

OPTIMIZATION_WORKSHOP = {
    "title": "Optimization Workshop",
    "icon": "⚙",
    "action": "Optimize a Decision",
    "tagline": "Define your problem, build a framework, and find the best feasible choice.",
    "intro": (
        "Optimization is everywhere: poker strategy, traffic routing, treatment protocols, "
        "sports systems, machine design, and business processes. This workshop walks you through "
        "how a mathematical consultant would structure your problem — step by step."
    ),
}

WORKSHOP_STEPS = [
    {
        "num": 1,
        "title": "Define the objective",
        "prompt": "What are you trying to maximize or minimize?",
        "guidance": """
        Every optimization problem starts with a clear objective:
        - **Maximize** expected profit, win rate, patient survival, forecast accuracy
        - **Minimize** cost, risk, travel time, error, resource waste

        Be specific. "Improve my poker game" is vague. "Maximize long-term chip EV per hand" is optimizable.
        """,
        "examples": [
            "Maximize expected value of my poker calling range",
            "Minimize average commute time across the city",
            "Maximize tumor reduction while limiting side effects",
            "Maximize ROI of a sports betting model",
        ],
    },
    {
        "num": 2,
        "title": "Define the variables",
        "prompt": "What can you control or adjust?",
        "guidance": """
        Variables are the levers you can move:
        - **Decision variables** — things you choose (bet size, route, drug dose, model parameters)
        - **State variables** — things that describe the current situation (stack size, traffic density, tumor volume)
        - **Parameters** — fixed inputs you estimate from data (win rate, growth rate, conversion rate)

        List every lever. Optimization finds the best combination.
        """,
        "examples": [
            "Bet frequency, bet sizing, hand selection thresholds",
            "Traffic light timing, lane allocation, speed limits",
            "Drug dosage schedule, treatment intervals",
            "Feature weights in a prediction model",
        ],
    },
    {
        "num": 3,
        "title": "Define the constraints",
        "prompt": "What limits your choices?",
        "guidance": """
        Constraints define the feasible region — what is actually possible:
        - **Budget constraints** — limited money, time, or resources
        - **Physical constraints** — capacity, speed limits, safety margins
        - **Rule constraints** — regulations, game rules, ethical boundaries
        - **Risk constraints** — maximum acceptable loss or failure probability

        Without constraints, "optimize" has no meaning — you could always bet everything or ignore safety.
        """,
        "examples": [
            "Stack size limits bet sizing; pot odds constrain calling range",
            "Road capacity limits throughput; budget limits infrastructure",
            "Toxicity caps drug dosage; FDA rules constrain trial design",
            "Bankroll management limits bet size regardless of edge",
        ],
    },
    {
        "num": 4,
        "title": "Identify uncertainty",
        "prompt": "What don't you know for certain?",
        "guidance": """
        Real optimization happens under uncertainty:
        - **Stochastic inputs** — you don't know opponent cards, tomorrow's weather, or exact tumor response
        - **Parameter uncertainty** — your estimates of win rate or growth rate have error bars
        - **Model uncertainty** — your framework might be structurally wrong

        Strategy: optimize expected outcomes, but stress-test against worst-case scenarios.
        """,
        "examples": [
            "Unknown opponent hands → optimize expected value, not outcome of one hand",
            "Uncertain demand → robust optimization across scenarios",
            "Variable patient response → optimize for population average with safety margins",
        ],
    },
    {
        "num": 5,
        "title": "Identify relevant mathematics",
        "prompt": "Which mathematical tools apply?",
        "guidance": """
        Match the problem structure to the tool:
        - **Linear programming** — linear objectives and constraints (resource allocation)
        - **Calculus / gradients** — smooth objectives where small changes matter (ML training, physics)
        - **Dynamic programming** — sequential decisions (poker streets, inventory over time)
        - **Simulation + search** — complex systems where formulas fail (Monte Carlo optimization)
        - **Statistics** — when you need to estimate parameters from data first
        """,
        "examples": [
            "Portfolio allocation → constrained quadratic optimization",
            "AI training → gradient descent (calculus-based optimization)",
            "Poker → game theory + expected value (probability + optimization)",
        ],
    },
    {
        "num": 6,
        "title": "Build a mathematical framework",
        "prompt": "Write the problem in mathematical form.",
        "guidance": """
        The standard form:

        **Maximize** f(x)  (objective function)
        **Subject to** g(x) ≤ 0  (constraints)
        **Where** x = decision variables

        Example: Maximize EV(bet_size) subject to bet_size ≤ stack_size and risk ≤ tolerance.

        Even a rough framework clarifies thinking and reveals what data you need.
        """,
        "examples": [
            "max Σ (win_rate_i × payout_i × bet_i)  s.t.  Σ bet_i ≤ bankroll",
            "min travel_time(route)  s.t.  capacity(route) ≤ max_flow",
            "max tumor_kill(dose) − λ × side_effects(dose)  s.t.  dose ≤ safe_limit",
        ],
    },
    {
        "num": 7,
        "title": "How optimization works",
        "prompt": "Understand the search for the best feasible point.",
        "guidance": """
        Optimization algorithms systematically search for the best choice:
        1. **Evaluate** the objective at a candidate solution
        2. **Check** constraints — discard infeasible options
        3. **Move** toward better solutions (gradient direction, grid search, or evolutionary methods)
        4. **Stop** when improvements are negligible

        The interactive tool below lets you allocate a budget under risk constraints — the same pattern at work.
        """,
        "examples": [
            "Grid search tries many allocations and picks the best feasible one",
            "Gradient descent follows the slope downhill on a loss surface",
            "Simplex method navigates corners of a linear feasible region",
        ],
    },
    {
        "num": 8,
        "title": "Why calculus, statistics, and probability matter",
        "prompt": "Connect the math to your problem.",
        "guidance": """
        - **Calculus** — finds where functions peak or valley (derivatives = rate of change = gradient)
        - **Statistics** — estimates the parameters your optimizer needs (win rates, growth rates, correlations)
        - **Probability** — handles uncertainty in the objective (expected value = probability-weighted outcomes)
        - **Simulation** — evaluates objectives too complex for formulas (run many scenarios, optimize average)

        These are not separate subjects — they combine in every real optimization problem.
        """,
        "examples": [
            "AI training: calculus (gradients) + statistics (data) + probability (predictions)",
            "Sports betting: statistics (ratings) + probability (win odds) + optimization (bet sizing)",
            "Medicine: calculus (growth rates) + statistics (trial data) + optimization (dose scheduling)",
        ],
    },
]

EXAMPLE_PROBLEMS = [
    "Improve a poker strategy",
    "Reduce traffic congestion",
    "Improve cancer treatment outcomes",
    "Improve a sports betting system",
    "Design a more efficient machine",
    "Improve a business process",
    "Optimize ad spending across channels",
    "Custom problem (describe below)",
]

PROBLEM_HINTS = {
    "Improve a poker strategy": {
        "objective": "Maximize long-term expected chip value (EV)",
        "variables": "Hand selection, bet sizing, bluff frequency, position awareness",
        "constraints": "Stack sizes, pot odds, opponent tendencies, table dynamics",
        "uncertainty": "Unknown opponent cards and future actions",
        "math": "Game theory, expected value, pot odds, Kelly criterion",
    },
    "Reduce traffic congestion": {
        "objective": "Minimize average travel time or maximize throughput",
        "variables": "Signal timing, lane allocation, toll pricing, route recommendations",
        "constraints": "Road capacity, budget, safety regulations, geographic layout",
        "uncertainty": "Variable demand, accidents, weather events",
        "math": "Network flow optimization, simulation, queueing theory",
    },
    "Improve cancer treatment outcomes": {
        "objective": "Maximize tumor reduction while minimizing side effects",
        "variables": "Drug dosage, treatment schedule, combination protocols",
        "constraints": "Toxicity limits, patient tolerance, regulatory approval",
        "uncertainty": "Individual patient response, tumor heterogeneity",
        "math": "Pharmacokinetics (calculus), clinical statistics, multi-objective optimization",
    },
    "Improve a sports betting system": {
        "objective": "Maximize long-term ROI subject to risk limits",
        "variables": "Bet sizing, model weights, market selection, confidence thresholds",
        "constraints": "Bankroll, maximum drawdown, available markets",
        "uncertainty": "True win probabilities, line movement, variance",
        "math": "Statistics (ratings), probability (EV), Kelly criterion (optimization)",
    },
    "Design a more efficient machine": {
        "objective": "Maximize output per unit energy or minimize material cost",
        "variables": "Dimensions, materials, operating speed, component geometry",
        "constraints": "Physical laws, safety standards, manufacturing limits",
        "uncertainty": "Material properties, wear, environmental conditions",
        "math": "Calculus of variations, finite element simulation, constrained optimization",
    },
    "Improve a business process": {
        "objective": "Minimize cost or maximize throughput per unit time",
        "variables": "Staffing levels, batch sizes, scheduling, automation investment",
        "constraints": "Budget, labor laws, quality standards, customer demand",
        "uncertainty": "Demand fluctuations, supply delays, employee availability",
        "math": "Linear programming, queueing theory, simulation, statistics",
    },
    "Optimize ad spending across channels": {
        "objective": "Maximize conversions or ROI for a fixed budget",
        "variables": "Budget allocation per channel, bid levels, targeting parameters",
        "constraints": "Total budget, minimum per-channel spend, brand guidelines",
        "uncertainty": "Conversion rates, auction dynamics, seasonality",
        "math": "Constrained optimization, regression (response curves), A/B testing statistics",
    },
}
