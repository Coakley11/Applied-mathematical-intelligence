"""Mathematical Thinking Lab — thinking frameworks, not formulas."""

THINKING_LAB = {
    "title": "Mathematical Thinking Lab",
    "icon": "🧭",
    "action": "Explore Mathematical Thinking",
    "tagline": "How mathematical thinkers approach problems — not procedures, but thinking.",
    "intro": (
        "Professional mathematicians, data scientists, and quants do not start with formulas. "
        "They start with questions: What matters? What can change? What is uncertain? "
        "This lab teaches that mindset — applicable to betting, medicine, AI, business, and invention."
    ),
}

THINKING_TOPICS = [
    {
        "id": "analyze_any_problem",
        "name": "How to Analyze Any Problem",
        "summary": "Break a messy situation into a decision, a question, and measurable pieces.",
        "approach": """
        1. **State the decision or prediction** — What would you actually do differently if you knew the answer?
        2. **Separate facts from assumptions** — What do you know vs. what are you guessing?
        3. **Identify the stakes** — What happens if you're wrong? Tail risks often dominate.
        4. **Ask what would change your mind** — Good analysis is falsifiable.
        """,
        "questions": [
            "What decision am I actually trying to make?",
            "What would success look like in numbers?",
            "What is the cost of being wrong?",
        ],
        "example": "Before analyzing a poker call, ask: 'Am I deciding whether to call this one hand, or whether this strategy wins long-term?'",
        "math_connection": "Problem framing determines whether you need probability (uncertainty), optimization (best choice), or simulation (complex systems).",
    },
    {
        "id": "build_model",
        "name": "How to Build a Mathematical Model",
        "summary": "Translate reality into variables, relationships, and rules — deliberately simplified.",
        "approach": """
        1. **Choose state variables** — What quantities describe the system right now?
        2. **Write relationships** — How do variables influence each other?
        3. **Set boundaries** — What are you ignoring on purpose?
        4. **Validate qualitatively** — Does the model behave sensibly in extreme cases?
        """,
        "questions": [
            "What are the inputs and outputs?",
            "What rate of change matters most?",
            "What feedback loops exist?",
        ],
        "example": "Tumor growth models track volume over time: growth rate minus treatment kill rate. Simple, but captures the core tradeoff.",
        "math_connection": "Models use algebra, calculus (rates of change), differential equations, or statistical relationships depending on complexity.",
    },
    {
        "id": "identify_variables",
        "name": "How to Identify Important Variables",
        "summary": "Not every detail matters — find the levers that actually move outcomes.",
        "approach": """
        1. **List everything that might matter** — brainstorm without filtering.
        2. **Rank by impact and controllability** — focus on high-impact levers you can change.
        3. **Check for hidden variables** — selection bias, missing data, confounders.
        4. **Test sensitivity** — if changing a variable barely moves the result, deprioritize it.
        """,
        "questions": [
            "Which inputs would change the outcome by more than 10%?",
            "Which variables can I actually control?",
            "What am I not measuring?",
        ],
        "example": "In sports betting, team strength and sample size matter more than recent streak narratives.",
        "math_connection": "Sensitivity analysis and partial derivatives (calculus) formalize which variables matter most.",
    },
    {
        "id": "simplify_systems",
        "name": "How to Simplify Complex Systems",
        "summary": "Complex systems become tractable when you find the right level of abstraction.",
        "approach": """
        1. **Find the core mechanism** — What single process drives most of the behavior?
        2. **Aggregate when possible** — Replace thousands of details with a few summary statistics.
        3. **Use symmetry and scaling** — Many systems behave similarly at different scales.
        4. **Iterate** — Start simple, add complexity only when the simple model fails.
        """,
        "questions": [
            "What can I safely ignore for this decision?",
            "Is there a standard template for this type of problem?",
            "Where does my simple model break down?",
        ],
        "example": "Traffic flow can start as 'cars per hour' rather than modeling every driver individually.",
        "math_connection": "Abstraction, linearization, and dimensional analysis are the mathematician's simplification toolkit.",
    },
    {
        "id": "think_uncertainty",
        "name": "How to Think About Uncertainty",
        "summary": "Uncertainty is not ignorance to eliminate — it is structure to quantify.",
        "approach": """
        1. **Distinguish types** — randomness, measurement error, model error, unknown unknowns.
        2. **Use ranges and probabilities** — not single-point guesses.
        3. **Update with evidence** — Bayes: prior beliefs + new data = posterior beliefs.
        4. **Plan for tails** — rare events often dominate long-term outcomes.
        """,
        "questions": [
            "What is the range of plausible outcomes?",
            "How confident am I, and why?",
            "What would surprise me?",
        ],
        "example": "Weather forecasts widen uncertainty cones over time — the math reflects growing chaos, not forecaster error.",
        "math_connection": "Probability distributions, confidence intervals, and Bayesian updating quantify uncertainty rigorously.",
    },
    {
        "id": "evaluate_claims",
        "name": "How to Evaluate Claims",
        "summary": "Separate signal from noise when someone presents numbers or predictions.",
        "approach": """
        1. **Ask for the base rate** — How often does this happen in general?
        2. **Check sample size** — Small samples produce extreme results by chance.
        3. **Look for selection bias** — Are you only seeing survivors or winners?
        4. **Demand out-of-sample tests** — Does the claim hold on new data?
        """,
        "questions": [
            "Compared to what baseline?",
            "How many observations support this?",
            "Who might be missing from the data?",
        ],
        "example": "A medical treatment claiming '50% improvement' means little without knowing the control group rate.",
        "math_connection": "Statistics — hypothesis testing, regression to the mean, and effect sizes — evaluates claims systematically.",
    },
    {
        "id": "think_data_scientist",
        "name": "How to Think Like a Data Scientist",
        "summary": "Extract patterns from data while avoiding overfitting and false discovery.",
        "approach": """
        1. **Start with a question, not a dataset** — data mining without hypotheses finds noise.
        2. **Split train/test** — validate on data the model hasn't seen.
        3. **Prefer simple models** — complexity should earn its keep with better predictions.
        4. **Communicate uncertainty** — stakeholders need ranges, not false precision.
        """,
        "questions": [
            "Would this pattern appear in new data?",
            "Is the model simpler than the noise in the data?",
            "What features actually drive the prediction?",
        ],
        "example": "Sports shrinkage adjusts extreme early-season stats toward league average — a data scientist's instinct formalized.",
        "math_connection": "Regression, cross-validation, regularization, and loss functions are the data scientist's core math.",
    },
    {
        "id": "think_actuary",
        "name": "How to Think Like an Actuary",
        "summary": "Price risk over long horizons — where tail events and compounding dominate.",
        "approach": """
        1. **Think in distributions, not averages** — the average hurricane year and the catastrophic year are different worlds.
        2. **Use base rates and experience** — historical frequency grounds expectations.
        3. **Model dependencies** — correlated risks compound (pandemics, market crashes).
        4. **Reserve for uncertainty** — solvency requires surviving bad scenarios, not just expected outcomes.
        """,
        "questions": [
            "What is the 1-in-100 year scenario?",
            "Are risks independent or correlated?",
            "Can the system survive the worst case?",
        ],
        "example": "Insurance pricing uses expected value plus a margin for variance — the Kelly Criterion applies the same logic to betting.",
        "math_connection": "Probability, expected value, variance, and extreme value theory underpin actuarial thinking.",
    },
    {
        "id": "think_ai_researcher",
        "name": "How to Think Like an AI Researcher",
        "summary": "Frame learning as optimization — find parameters that minimize prediction error.",
        "approach": """
        1. **Define a loss function** — what does 'wrong' mean numerically?
        2. **Choose a model class** — what patterns can the architecture represent?
        3. **Optimize iteratively** — gradient descent follows the slope toward better predictions.
        4. **Evaluate generalization** — performance on unseen data is the only honest score.
        """,
        "questions": [
            "What am I trying to predict or classify?",
            "What would a wrong prediction cost?",
            "Does the model work on new examples?",
        ],
        "example": "Training a neural network adjusts millions of weights to minimize loss — the same optimization pattern as tuning a strategy.",
        "math_connection": "Calculus (gradients), linear algebra (weight matrices), and probability (softmax outputs) power modern AI.",
    },
    {
        "id": "think_quant",
        "name": "How to Think Like a Quantitative Analyst",
        "summary": "Combine models, data, and optimization to make decisions under market-like uncertainty.",
        "approach": """
        1. **Build a quantitative thesis** — what relationship or inefficiency do you believe exists?
        2. **Backtest rigorously** — does the edge persist out-of-sample?
        3. **Size positions by risk** — Kelly criterion and portfolio theory manage exposure.
        4. **Monitor and adapt** — markets and systems change; models decay.
        """,
        "questions": [
            "What is my edge, and why should it persist?",
            "How much should I bet given uncertainty?",
            "What would invalidate this strategy?",
        ],
        "example": "Comparing model win probability to implied odds from betting markets is classic quant thinking applied to sports.",
        "math_connection": "Statistics, optimization, stochastic processes, and expected value calculations are the quant toolkit.",
    },
    {
        "id": "real_world_to_math",
        "name": "How to Turn Real-World Problems Into Mathematics",
        "summary": "The translation step — from words and intuition to equations and simulations.",
        "approach": """
        1. **Name the unknown** — what are you solving for?
        2. **Write what you know as equations or rules** — constraints, relationships, rates.
        3. **Pick the tool** — algebra, calculus, probability, optimization, or simulation.
        4. **Interpret the output** — translate the math answer back into the real-world decision.
        """,
        "questions": [
            "Can I write this as 'maximize X subject to Y'?",
            "Is this a prediction problem or a decision problem?",
            "Do I need one answer or a distribution of possibilities?",
        ],
        "example": "'Should I call this poker bet?' becomes: EV = P(win)×pot − P(lose)×call. One sentence, one equation, one decision.",
        "math_connection": "Every lab in this app demonstrates this translation — from real question to mathematical framework to actionable insight.",
    },
]
