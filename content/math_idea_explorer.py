"""Mathematical Idea Explorer — math idea → real-world applications."""

from __future__ import annotations

import re

MATH_IDEA_EXPLORER = {
    "title": "Mathematical Idea Explorer",
    "icon": "🔍",
    "action": "Explore a Math Idea",
    "tagline": "Start with a math idea — discover where that structure appears in the real world.",
    "intro": (
        "Enter an equation, concept, or formula. See what it means abstractly, "
        "why professionals care, and how it shows up in betting, medicine, AI, engineering, and more."
    ),
}

EXAMPLE_INPUTS = [
    "(x + 3)^2 = 7",
    "derivative",
    "integral",
    "expected value",
    "confidence interval",
    "Bayes theorem",
    "probability distribution",
    "exponential growth",
    "optimization with constraints",
    "gradient descent",
    "differential equation",
    "multivariable integral",
    "Custom input (type below)",
]

DOMAIN_LABELS = {
    "betting": "Betting & gambling",
    "sports": "Sports prediction",
    "medicine": "Medicine & healthcare",
    "ai": "AI & machine learning",
    "engineering": "Engineering & space",
    "forecasting": "Forecasting & uncertainty",
    "science": "Science & discovery",
}

_FALLBACK = {
    "id": "general",
    "plain_name": "Mathematical expression or concept",
    "mathematical_description": (
        "This input may be an **equation**, **symbol**, or **phrase** describing a relationship "
        "between quantities."
    ),
    "abstract_idea": (
        "Most school math is really one of a few structures: find an unknown, measure change, "
        "add up pieces, model uncertainty, or choose the best option under constraints."
    ),
    "real_world_applications": {
        "betting": "Odds and payouts are relationships between unknown outcomes and money.",
        "sports": "Projections link player stats to probabilities of future performance.",
        "medicine": "Dose–response curves relate treatment level to outcome.",
        "ai": "Models are equations with millions of parameters fit by optimization.",
        "engineering": "Design equations link dimensions, forces, and materials.",
        "forecasting": "Forecast models relate past state to future distributions.",
        "science": "Theories are equations tested against measurement.",
    },
    "why_it_matters": (
        "Recognizing structure lets you transfer tools across fields — the same logic "
        "appears in casinos, clinics, and rockets."
    ),
    "mini_example": (
        "Ask: **Is this solving for an unknown? Measuring change? Accumulating pieces? "
        "Modeling chance? Optimizing a choice?** Pick the closest — then explore that idea above."
    ),
    "deeper_math": "Classify first; then study the matching tool (algebra, calculus, probability, statistics, optimization).",
    "related_labs": ["Solve a Problem"],
    "interpretation_questions": [
        "Is it solving for an unknown value?",
        "Is it measuring how fast something changes?",
        "Is it adding up many small contributions?",
        "Is it describing uncertainty or randomness?",
        "Is it finding the best choice subject to limits?",
    ],
    "representation": (
        "Unknowns **x**, relationships **f(x) = …**, constraints **g(x) ≤ 0**, "
        "or objectives to maximize/minimize — pick the closest skeleton."
    ),
    "specific_examples": [
        "Break-even probability from odds: solve stake/(stake+profit) for fair P.",
        "Compare two cancer arms: difference in response rates with confidence intervals.",
        "Rocket height: position as a function of time under gravity.",
    ],
    "real_world_closing": (
        "Naming the structure tells you which lab to open: EV for bets, growth models for medicine, "
        "optimization for AI training — same logic, different quantities."
    ),
    "interactive": "optimization",
}

_CONCEPTS: list[dict] = [
    {
        "id": "derivative",
        "aliases": ["derivative", "derivatives", "rate of change", "dy/dx", "d/dx", "differentiation"],
        "plain_name": "Derivative (rate of change)",
        "mathematical_description": (
            "A **derivative** measures how fast one quantity changes when another changes — "
            "the instantaneous slope of a relationship."
        ),
        "abstract_idea": (
            "At its core: **if you nudge an input slightly, how much does the output move?** "
            "That sensitivity is everywhere in dynamic systems."
        ),
        "real_world_applications": {
            "betting": "How fast odds move after news — sensitivity of price to information.",
            "sports": "Trend in player stats: is improvement accelerating or flattening?",
            "medicine": "Tumor **growth speed**; how quickly drug concentration rises or falls.",
            "ai": "**Gradient descent** uses derivatives of loss to update model weights.",
            "engineering": "Velocity is the derivative of position; acceleration of velocity.",
            "forecasting": "How quickly temperature or storm risk changes along a path.",
            "science": "Marginal effects — how much yield changes per unit of fertilizer.",
        },
        "why_it_matters": (
            "Scientists and engineers care about **rates**, not just levels — "
            "is risk increasing? Is the model still improving? Is the rocket gaining speed?"
        ),
        "mini_example": (
            "If tumor volume V grows so that dV/dt = 0.08V per month, "
            "the tumor is growing **8% per month** in proportional terms — "
            "a simple derivative model clinicians discuss."
        ),
        "deeper_math": "f′(x) = lim(h→0) [f(x+h)−f(x)]/h; chain rule links composed systems.",
        "related_labs": ["Model a Disease", "Train an AI"],
        "representation": "Function **f(x)**; sensitivity **f′(a)** at a point **a**; linear approximation f(a)+f′(a)(x−a).",
        "specific_examples": [
            "Odds move after injury news — how fast does implied probability change?",
            "Tumor volume: dV/dt proportional to V gives exponential-looking growth early on.",
            "Neural net training: gradient of loss w.r.t. each weight updates the model.",
        ],
        "real_world_closing": "Derivatives answer 'how sensitive is the outcome?' — critical for risk, dosing, and learning rates.",
        "interactive": "derivative",
    },
    {
        "id": "integral",
        "aliases": ["integral", "integrals", "integration", "area under a curve", "accumulate", "∫"],
        "plain_name": "Integral (accumulation)",
        "mathematical_description": (
            "An **integral** adds up infinitely many tiny pieces — total effect when something "
            "varies continuously."
        ),
        "abstract_idea": (
            "**Many small contributions → one total.** Distance is the integral of speed; "
            "total exposure is the integral of concentration over time."
        ),
        "real_world_applications": {
            "betting": "Long-run profit is the accumulation of many +EV and −EV bets.",
            "sports": "Total season wins integrate game-by-game performance (with noise).",
            "medicine": "**Total drug exposure** (AUC) integrates concentration × time in the body.",
            "ai": "Loss over a training set is an average (discrete integral) of per-example error.",
            "engineering": "Total distance traveled; total fuel burned over a flight.",
            "forecasting": "Total rainfall over a week — sum/integral of intensity.",
            "science": "Work as ∫ force·distance; charge from current over time.",
        },
        "why_it_matters": (
            "Totals drive decisions: cumulative dose, cumulative risk, total cost — "
            "not just what happens in one instant."
        ),
        "mini_example": (
            "If you drive 60 mph for 2 hours, distance ≈ ∫ speed dt = **120 miles**. "
            "If speed varies, you still add up the pieces — that's integration."
        ),
        "deeper_math": "Fundamental theorem links integrals and derivatives; numerical quadrature on computers.",
        "related_labs": ["Model a Disease", "Advanced reference"],
        "representation": "∫ f(x) dx over an interval; region sums for multivariable ∫∫ f(x,y) dA.",
        "specific_examples": [
            "Total drug exposure (AUC) integrates concentration over hours in the body.",
            "Season bankroll path integrates many +EV and −EV bets over time.",
            "Work done moving an object integrates force along the path.",
        ],
        "real_world_closing": "When the question is 'how much total?' — integrate rate, risk, or exposure over time or space.",
        "interactive": "integral",
    },
    {
        "id": "quadratic",
        "aliases": [
            "quadratic", "quadratic equation", "parabola", "x^2", "x²",
            "(x", "ax^2", "ax²",
        ],
        "plain_name": "Quadratic relationship",
        "mathematical_description": (
            "A **quadratic** involves x² terms — curves that bend once (parabolas). "
            "Equations like (x+3)² = 7 ask which x makes a squared expression equal a number."
        ),
        "abstract_idea": (
            "Many real relationships **rise then fall** (or fall then rise) — one peak or trough. "
            "Quadratics are the simplest curved model for that shape."
        ),
        "real_world_applications": {
            "betting": "Profit vs. bet size can curve — too small or too large is suboptimal.",
            "sports": "Projectile path of a ball; trajectory peaks at one height.",
            "medicine": "Drug effect vs. dose often peaks then drops (toxicity).",
            "ai": "Loss surfaces can be locally curved; some models use quadratic approximations.",
            "engineering": "Rocket height vs. time under gravity is quadratic (idealized).",
            "forecasting": "Some short-range error models use parabolic trends.",
            "science": "Classic physics: height = v₀t − ½gt².",
        },
        "why_it_matters": (
            "When effects are nonlinear but smooth, quadratics give **first good approximations** "
            "and teach where maxima/minima occur."
        ),
        "mini_example": (
            "Solve (x+3)² = 7 ⇒ x+3 = ±√7 ⇒ x = −3±√7. "
            "**Rocket:** height h(t) = −16t² + v₀t — when is h = 100 ft? Set quadratic = 100 and solve."
        ),
        "deeper_math": "Quadratic formula; vertex at x = −b/(2a); discriminant tells number of real solutions.",
        "related_labs": ["Optimize a Decision", "Advanced reference"],
        "equation_pattern": re.compile(r"\([^)]+\)\s*\^\s*2|=\s*7|\bx\s*\^?\s*2|x²|quadratic", re.I),
    },
    {
        "id": "expected_value",
        "aliases": ["expected value", "expectation", "ev", "e[v]", "long-run average"],
        "plain_name": "Expected value",
        "mathematical_description": (
            "**Expected value** is the probability-weighted average of outcomes — "
            "what you'd expect long-term if you repeated a risky situation many times."
        ),
        "abstract_idea": (
            "Don't ask 'will I win this once?' — ask **what happens on average** if I repeat the decision. "
            "EV = Σ P(outcome) × value(outcome)."
        ),
        "real_world_applications": {
            "betting": "Core of sports betting and poker — +EV vs. −EV.",
            "sports": "Season-long profit from repeated +edge bets.",
            "medicine": "Expected survival benefit vs. expected toxicity.",
            "ai": "Expected loss over a data distribution is what models minimize.",
            "engineering": "Expected cost over failure scenarios in design.",
            "forecasting": "Expected rainfall or demand for planning.",
            "science": "Decision analysis under risk in policy and finance.",
        },
        "why_it_matters": (
            "Professionals separate **luck from structure** — EV is how casinos, insurers, "
            "and quantitative bettors think."
        ),
        "mini_example": (
            "Win $150 with P=0.45, lose $100 with P=0.55 ⇒ "
            "EV = 0.45×150 − 0.55×100 = **+$12.50** per bet."
        ),
        "deeper_math": "Linearity of expectation; variance measures spread around the mean.",
        "related_labs": ["Analyze a Bet", "Predict a Game"],
        "representation": "Outcomes **xᵢ** with probabilities **pᵢ**; EV = Σ pᵢ xᵢ.",
        "specific_examples": [
            "Risk $200 on Judge 30+ HR: EV = P(hit)×profit − P(miss)×stake.",
            "Insurer pricing: expected claim cost vs. premium collected.",
            "Clinical trial: expected survival months under treatment vs. control.",
        ],
        "real_world_closing": "EV separates one lucky outcome from a repeatable decision — use it before sizing any bet or policy.",
        "interactive": "ev_bet",
    },
    {
        "id": "standard_deviation",
        "aliases": ["standard deviation", "std dev", "std", "sigma", "σ", "spread"],
        "plain_name": "Standard deviation",
        "mathematical_description": (
            "**Standard deviation** measures typical distance from the average — "
            "how spread out data or outcomes are."
        ),
        "abstract_idea": (
            "The mean tells you the center; **standard deviation tells you how noisy** life is around it."
        ),
        "real_world_applications": {
            "betting": "Bankroll swings — even +EV strategies have volatile short runs.",
            "sports": "Player stat volatility; why one hot month misleads.",
            "medicine": "Variability in patient response beyond average effect.",
            "ai": "Spread of model errors; calibration of uncertainty.",
            "engineering": "Manufacturing tolerance — parts within ±σ of spec.",
            "forecasting": "Forecast error bands often scale with estimated σ.",
            "science": "Experimental uncertainty reported as mean ± SD.",
        },
        "why_it_matters": (
            "Ignoring spread causes overconfidence — a 55% model can still lose many bets in a row."
        ),
        "mini_example": (
            "Heights with mean 70 in and SD 3 in ⇒ most people within **64–76 in** (rough 2σ range)."
        ),
        "deeper_math": "σ = √(average squared deviation); variance is σ².",
        "related_labs": ["Predict a Game", "Train an AI"],
    },
    {
        "id": "confidence_interval",
        "aliases": ["confidence interval", "confidence intervals", "ci", "95% ci", "margin of error"],
        "plain_name": "Confidence interval",
        "mathematical_description": (
            "A **confidence interval** is a range of plausible values for a parameter, "
            "consistent with the data and a chosen confidence level (e.g. 95%)."
        ),
        "abstract_idea": (
            "Instead of 'the effect is exactly 5%,' say **'plausibly between 2% and 8%'** — "
            "honest uncertainty after limited data."
        ),
        "real_world_applications": {
            "betting": "Interval on true win rate from historical bet log.",
            "sports": "Projection intervals on player stats or team win totals.",
            "medicine": "CI on treatment effect in trials — FDA cares about these.",
            "ai": "Bootstrap CIs on model metrics; A/B test lift intervals.",
            "engineering": "CI on measured strength of materials from samples.",
            "forecasting": "Prediction intervals for demand or weather.",
            "science": "Poll margins of error; experimental effect sizes.",
        },
        "why_it_matters": (
            "Decisions with wide intervals should be **cautious** — the data may not pin down the truth tightly."
        ),
        "mini_example": (
            "Trial estimates 40% response rate, 95% CI **[32%, 48%]** ⇒ "
            "compatible with modest and strong effects — don't overclaim precision."
        ),
        "deeper_math": "Often mean ± 1.96×SE for large samples; bootstrap for complex stats.",
        "related_labs": ["Model a Disease", "Predict a Game"],
        "representation": "Estimate **θ̂** ± margin from sample mean, SD, and n.",
        "specific_examples": [
            "Trial reports 40% response, 95% CI [32%, 48%] — honest uncertainty.",
            "Poll: candidate 52% ± 3% — true support plausibly 49–55%.",
            "Model accuracy on n=50 test points — wide CI, don't overtrust.",
        ],
        "real_world_closing": "CIs stop you from pretending precision you don't have — essential for medicine, polls, and ML metrics.",
        "interactive": "confidence_interval",
    },
    {
        "id": "bayes_theorem",
        "aliases": ["bayes", "bayes theorem", "bayesian", "bayes' theorem", "posterior", "prior"],
        "plain_name": "Bayes' theorem",
        "mathematical_description": (
            "**Bayes' theorem** updates beliefs when new evidence arrives: "
            "P(hypothesis|data) combines prior belief with how likely the data is under each hypothesis."
        ),
        "abstract_idea": (
            "**Start with what you believed, then revise with evidence** — not all information is equal."
        ),
        "real_world_applications": {
            "betting": "Update win probability after injury news or line moves.",
            "sports": "Combine preseason prior with in-season performance.",
            "medicine": "Diagnostic testing: disease probability given a positive test.",
            "ai": "Bayesian neural nets, spam filters, some forecasting models.",
            "engineering": "Reliability updating as components fail or pass tests.",
            "forecasting": "Ensemble methods blend models like weighted beliefs.",
            "science": "A/B testing, epidemiology, and scientific inference broadly.",
        },
        "why_it_matters": (
            "Much of quantitative work is **learning from evidence** without throwing away prior knowledge."
        ),
        "mini_example": (
            "Rare disease (1%), test 95% accurate, you test positive ⇒ "
            "posterior still might be only ~16% sick — Bayes explains why."
        ),
        "deeper_math": "P(A|B) = P(B|A)P(A)/P(B); odds form multiplies by likelihood ratio.",
        "related_labs": ["Predict a Game", "Model a Disease"],
    },
    {
        "id": "optimization",
        "aliases": ["optimization", "optimize", "maximize", "minimize", "linear programming", "best choice"],
        "plain_name": "Optimization",
        "mathematical_description": (
            "**Optimization** finds the best choice (max or min) subject to constraints — "
            "best portfolio, dose, route, or model parameters."
        ),
        "abstract_idea": (
            "Every 'best' decision has a **goal** and **limits**. Optimization makes that explicit."
        ),
        "real_world_applications": {
            "betting": "Kelly criterion sizes bets to maximize long-run growth.",
            "sports": "Lineup or budget allocation across players/markets.",
            "medicine": "Dose that maximizes benefit subject to toxicity cap.",
            "ai": "Training minimizes loss — optimization over millions of weights.",
            "engineering": "Minimize fuel for a trajectory; maximize structural strength per weight.",
            "forecasting": "Best ensemble weights across weather models.",
            "science": "Operations research, supply chain, energy grid dispatch.",
        },
        "why_it_matters": (
            "Resources are scarce — optimization is how organizations **allocate under constraints**."
        ),
        "mini_example": (
            "Maximize profit = price×demand − cost, but factory capacity ≤ 1000 units/day — "
            "the optimum usually hits a **constraint** (capacity binds)."
        ),
        "deeper_math": "Derivatives for unconstrained; Lagrange multipliers for constraints; convexity matters.",
        "related_labs": ["Optimize a Decision", "Train an AI"],
    },
    {
        "id": "exponential_growth",
        "aliases": ["exponential", "exponential growth", "doubling", "e^", "exp(", "compound"],
        "plain_name": "Exponential growth",
        "mathematical_description": (
            "**Exponential growth** means a quantity changes by a fixed **percentage per unit time** — "
            "doubling again and again."
        ),
        "abstract_idea": (
            "Proportional growth: the bigger something is, the faster it grows — "
            "epidemics, compound interest, unchecked cell division."
        ),
        "real_world_applications": {
            "betting": "Compound bankroll growth (or ruin) over many bets.",
            "sports": "Rarely sustained — performance regresses; exponentials often short-lived.",
            "medicine": "Early epidemic spread; tumor growth before treatment.",
            "ai": "Some training curves; explosion of activations if unstable.",
            "engineering": "Radioactive decay (negative exponential); capacitor charge.",
            "forecasting": "Early viral trends before saturation.",
            "science": "Population models, bacterial growth, Moore's law narratives.",
        },
        "why_it_matters": (
            "Exponentials **surprise people** — small early changes become huge; critical for epidemics and finance."
        ),
        "mini_example": (
            "10% monthly growth: V(t) = V₀×1.1^t. "
            "Double time ≈ 7 months. **SIR models** slow exponential spread as susceptibles run out."
        ),
        "deeper_math": "dN/dt = rN ⇒ N(t) = N₀e^(rt); log scale turns exponentials into lines.",
        "related_labs": ["Model a Disease", "Advanced reference"],
    },
    {
        "id": "probability_distribution",
        "aliases": [
            "probability distribution", "distribution", "normal distribution",
            "binomial", "poisson", "pdf", "pmf", "histogram",
        ],
        "plain_name": "Probability distribution",
        "mathematical_description": (
            "A **probability distribution** describes all possible outcomes and their chances — "
            "not one answer, but a map of uncertainty."
        ),
        "abstract_idea": (
            "Replace 'the result is X' with **'X has these probabilities'** — the language of risk and forecasting."
        ),
        "real_world_applications": {
            "betting": "Model win/loss as Bernoulli; bankroll paths as sums of bets.",
            "sports": "Distribution of player stats; win probability as Beta-like belief.",
            "medicine": "Survival time distributions; response rates in trials.",
            "ai": "Softmax outputs; generative models sample from learned distributions.",
            "engineering": "Failure time of parts; load distributions in safety analysis.",
            "forecasting": "Ensemble forecast spread; rain probability as Bernoulli.",
            "science": "Measurement error modeled as Normal; counts as Poisson.",
        },
        "why_it_matters": (
            "Pros think in **distributions**, not certainties — tails and spreads drive real decisions."
        ),
        "mini_example": (
            "Fair coin: 50% heads. Ten flips — binomial gives P(exactly 6 heads) ≈ **20.5%**. "
            "Many bets → approximate normal for totals."
        ),
        "deeper_math": "PDF/PMF; Central Limit Theorem; mean, variance, skew, tails.",
        "related_labs": ["Analyze a Bet", "Predict a Game"],
    },
    {
        "id": "linear_equation",
        "aliases": ["linear equation", "solve for x", "ax+b", "straight line"],
        "plain_name": "Linear equation",
        "mathematical_description": (
            "A **linear** equation has x to the first power only — graph is a straight line. "
            "Solving finds the unknown where the relationship holds."
        ),
        "abstract_idea": (
            "**Constant rate of change** — each step in x changes y by the same amount."
        ),
        "real_world_applications": {
            "betting": "Break-even points; simple bankroll depletion lines.",
            "sports": "Linear trend lines on stats (with caution — often approximate).",
            "medicine": "Dose–response approximated linearly over a narrow range.",
            "ai": "Linear regression baseline; last layer of many models.",
            "engineering": "Ohm's law V=IR; Hooke's law in elastic range.",
            "forecasting": "Short-term linear extrapolation of trends.",
            "science": "First-order approximations near a operating point.",
        },
        "why_it_matters": (
            "Linear models are **simple, interpretable baselines** before adding curvature."
        ),
        "mini_example": "Cost = 50 + 12×units ⇒ linear; doubling units adds fixed marginal $12 each.",
        "deeper_math": "y = mx + b; one unknown ⇒ one equation; systems for multiple unknowns.",
        "related_labs": ["Optimize a Decision"],
        "equation_pattern": re.compile(r"=\s*[^=]+$|ax\s*\+|linear", re.I),
    },
    {
        "id": "gradient_descent",
        "aliases": ["gradient descent", "grad descent", "sgd", "stochastic gradient", "backprop"],
        "plain_name": "Gradient descent",
        "mathematical_description": (
            "**Gradient descent** updates parameters in the direction that **reduces loss** — "
            "each step uses the gradient (vector of partial derivatives)."
        ),
        "abstract_idea": (
            "When you can't solve for weights in closed form, **walk downhill** on the loss surface "
            "using local slope information."
        ),
        "representation": "Parameters **w**; loss **L(w)**; update **w ← w − η∇L(w)** with learning rate **η**.",
        "real_world_applications": {
            "betting": "Fit a model to historical outcomes by minimizing prediction error.",
            "sports": "Train rating systems from game results.",
            "medicine": "Fit dose–response curves to trial data.",
            "ai": "Standard training for neural nets and large linear models.",
            "engineering": "Calibrate simulation parameters to match flight data.",
            "forecasting": "Estimate trend coefficients from past series.",
            "science": "Nonlinear least squares in physics and chemistry.",
        },
        "specific_examples": [
            "Train/val gap 14 pts: lower learning rate or add regularization — same gradient idea.",
            "Spam filter: adjust weights until misclassification loss drops on new emails.",
            "Weather bias correction: nudge model weights so ensemble mean matches observations.",
        ],
        "why_it_matters": "Most modern AI is gradient descent (or variants) on a loss you define.",
        "mini_example": "Loss high, gradient points uphill → step opposite gradient; repeat until validation loss plateaus.",
        "deeper_math": "η too large diverges; momentum and Adam adapt step sizes; convex losses have one minimum.",
        "related_labs": ["Train an AI", "Solve a Problem"],
        "real_world_closing": "Gradient descent is how models **learn from data** — tie every training knob to validation loss.",
        "interactive": "ml_split",
    },
    {
        "id": "differential_equation",
        "aliases": [
            "differential equation", "differential equations", "ode", "odes",
            "rate equation", "dV/dt", "dy/dx =",
        ],
        "plain_name": "Differential equation",
        "mathematical_description": (
            "A **differential equation** relates a quantity to its **rates of change** — "
            "how the system evolves over time or space."
        ),
        "abstract_idea": (
            "Instead of 'what is V at t=10?' you specify **how V changes moment by moment**, then integrate forward."
        ),
        "representation": "Unknown function **x(t)**; equation like **dx/dt = f(x,t)**; initial condition **x(0)**.",
        "real_world_applications": {
            "betting": "Bankroll dynamics under repeated proportional betting (stochastic DEs).",
            "sports": "Fatigue and recovery models over a season.",
            "medicine": "Tumor growth dV/dt = rV − k·dose; pharmacokinetics dC/dt = in − out.",
            "ai": "Continuous-time neural ODEs (research); training dynamics approximated as DEs.",
            "engineering": "Rocket F=ma; orbital motion; heat flow.",
            "forecasting": "SIR epidemic models; weather fluid dynamics.",
            "science": "Population ecology, chemical kinetics, neuron models.",
        },
        "specific_examples": [
            "Exponential tumor growth: dV/dt = 0.08V until treatment adds a kill term.",
            "Cooling coffee: dT/dt = −k(T − T_room).",
            "Rocket coast phase: dv/dt = −g after engines cut off.",
        ],
        "why_it_matters": "Dynamics questions — growth, decay, motion — are DEs whether you write them or not.",
        "mini_example": "dV/dt = 0.1V ⇒ V(t) = V₀e^{0.1t} — doubling time from the rate constant.",
        "deeper_math": "Order, linearity, stability; numerical solvers (Euler, Runge–Kutta) on computers.",
        "related_labs": ["Model a Disease", "Advanced reference"],
        "real_world_closing": "If the question is 'how does it evolve?' — write a rate equation, then simulate or solve.",
        "interactive": "exponential",
    },
    {
        "id": "constrained_optimization",
        "aliases": [
            "constrained optimization", "optimization with constraints", "lagrange",
            "linear programming", "maximize subject to", "minimize subject to",
        ],
        "plain_name": "Constrained optimization",
        "mathematical_description": (
            "**Constrained optimization** maximizes or minimizes an **objective** while satisfying "
            "**constraints** (budgets, laws of physics, safety limits)."
        ),
        "abstract_idea": (
            "The best feasible choice often sits **on a constraint boundary** — not in the interior."
        ),
        "representation": "Maximize **f(x)** subject to **gᵢ(x) ≤ 0**, **hⱼ(x) = 0**.",
        "real_world_applications": {
            "betting": "Kelly bet sizing under bankroll and risk caps.",
            "sports": "Lineup selection under salary cap.",
            "medicine": "Maximize tumor kill subject to toxicity limits.",
            "ai": "Train with GPU memory and latency constraints; constrained fairness metrics.",
            "engineering": "Min fuel to orbit subject to thrust and heat limits.",
            "forecasting": "Best ensemble weights with weights summing to 1.",
            "science": "Portfolio risk/return, supply chain, energy dispatch.",
        },
        "specific_examples": [
            "Factory: max profit = price×units − cost×units s.t. units ≤ 1000/day.",
            "Rocket: min fuel s.t. final velocity = orbital speed.",
            "ML: max accuracy s.t. model size < 10 MB for deployment.",
        ],
        "why_it_matters": "Real decisions always have limits — unconstrained 'optima' are often infeasible.",
        "mini_example": "If profit per unit is flat, optimum is at the **capacity** constraint — not 'infinite production'.",
        "deeper_math": "Lagrange multipliers; KKT conditions; convex problems easier than general nonconvex.",
        "related_labs": ["Optimize a Decision", "Train an AI"],
        "real_world_closing": "List objective + constraints before any formula — that's how engineers and quants actually decide.",
        "interactive": "optimization",
    },
    {
        "id": "multivariable_integral",
        "aliases": [
            "multivariable integral", "multiple integral", "double integral", "triple integral",
            "four-dimensional integral", "∫∫", "volume integral", "integral with constraints",
        ],
        "plain_name": "Multivariable integral",
        "mathematical_description": (
            "A **multivariable integral** adds up a quantity over a **region** in 2D, 3D, or higher dimensions — "
            "often with **constraints** defining the region."
        ),
        "abstract_idea": (
            "When outcomes depend on **several variables at once**, total exposure or probability is an integral "
            "over the allowed region."
        ),
        "representation": "∫∫_R f(x,y) dA or ∫∫∫_V f(x,y,z,t) dV; region **R** from constraints.",
        "real_world_applications": {
            "betting": "Joint distribution of correlated bets — risk over a region of outcomes.",
            "sports": "Expected points over joint player-performance regions.",
            "medicine": "Tumor dose integrated over 3D space and time; total drug in organ.",
            "ai": "Expected loss over high-dimensional parameter neighborhoods; Bayesian integrals.",
            "engineering": "Mass, center of mass, and stress integrated over volumes.",
            "forecasting": "Probability of rain summed over a geographic grid.",
            "science": "Physics expectations over state space; statistical mechanics.",
        },
        "specific_examples": [
            "Total radiation dose = ∫∫∫ dose(x,y,z) dV through the tumor volume.",
            "Probability both stocks drop: integrate joint density over the loss region.",
            "Expected cost under uncertain demand and supply: integral over constraint set.",
        ],
        "why_it_matters": "High-dimensional integrals appear wherever **several uncertainties combine**.",
        "mini_example": "Mass of a non-uniform object = ∫∫∫ density(x,y,z) dV — same idea as probability over a region.",
        "deeper_math": "Fubini's theorem; change of variables; Monte Carlo when analytic integrals are hard.",
        "related_labs": ["Model a Disease", "Advanced reference"],
        "real_world_closing": "If risk or exposure lives in several dimensions, you're integrating — simulate when pen-and-paper fails.",
        "interactive": "integral",
    },
]

MATH_CONCEPTS: dict[str, dict] = {c["id"]: c for c in _CONCEPTS}


def detect_concept(text: str) -> dict:
    """Match user input to a known concept or equation pattern; else fallback."""
    raw = text.strip()
    if not raw:
        return dict(_FALLBACK)

    lower = raw.lower()

    if re.search(r"gradient\s*descent|backprop|sgd", lower):
        return dict(MATH_CONCEPTS["gradient_descent"])
    if re.search(r"differential\s*equat|rate\s*equation|\bdv/dt\b|\bode\b", lower):
        return dict(MATH_CONCEPTS["differential_equation"])
    if re.search(r"constrained\s*optim|lagrange|subject\s*to|with\s*constraints", lower):
        return dict(MATH_CONCEPTS["constrained_optimization"])
    if re.search(
        r"multivariable\s*integral|multiple\s*integral|double\s*integral|"
        r"four[- ]dimensional\s*integral|∫∫",
        lower,
    ):
        return dict(MATH_CONCEPTS["multivariable_integral"])

    # Equation: squared term
    if re.search(r"\([^)]+\)\s*\^\s*2|\([^)]+\)\s*²|\)\s*2\s*=", lower) or "x^2" in lower or "x²" in lower:
        return dict(MATH_CONCEPTS["quadratic"])

    # Scan concepts by alias (longer aliases first)
    alias_hits: list[tuple[int, str]] = []
    for cid, concept in MATH_CONCEPTS.items():
        for alias in concept.get("aliases", []):
            if alias.lower() in lower:
                alias_hits.append((len(alias), cid))
    if alias_hits:
        alias_hits.sort(reverse=True)
        return dict(MATH_CONCEPTS[alias_hits[0][1]])

    # Equation patterns on concepts
    for concept in _CONCEPTS:
        pat = concept.get("equation_pattern")
        if pat and pat.search(raw):
            return dict(concept)

    # Generic equation with =
    if "=" in raw and any(c in raw for c in "xyz"):
        out = dict(MATH_CONCEPTS.get("quadratic", _FALLBACK))
        if "quadratic" not in lower and "^2" not in lower and "²" not in lower:
            out = dict(MATH_CONCEPTS.get("linear_equation", _FALLBACK))
        out["user_input"] = raw
        return out

    out = dict(_FALLBACK)
    out["user_input"] = raw
    return out
