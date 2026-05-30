"""Six mathematical intelligence systems — deep thematic content."""

THEMES = {
    "Accumulation Systems (Calculus)": {
        "title": "Accumulation Systems — Calculus as Continuous Change",
        "tagline": (
            "Calculus is the mathematics of **how small changes accumulate into large outcomes** — "
            "the language of growth, decay, flow, and motion in real systems."
        ),
        "why_matters": """
        Most important real-world quantities are not static. Drug levels rise and fall. Tumors grow.
        Populations change. Portfolios compound. Neural network weights update continuously during training.
        Climate systems store energy. Without calculus, we cannot model **rates**, **accumulation**, or
        **competing flows** — only snapshots that miss the dynamics professionals actually manage.
        """,
        "systems": [
            "Pharmacokinetics — drug concentration over time in the body",
            "Oncology — tumor growth vs treatment kill rates",
            "Demography and epidemiology — population and infection dynamics",
            "Compound interest and continuous compounding in finance",
            "Physics — position, velocity, acceleration under forces",
            "Climate — energy balance and heat accumulation in oceans/atmosphere",
            "AI optimization — gradient-driven parameter updates as discrete calculus",
        ],
        "professional_use": [
            {
                "role": "Pharmacologists",
                "detail": "Model absorption, distribution, metabolism, and elimination (ADME) using differential equations.",
            },
            {
                "role": "Quantitative biologists",
                "detail": "Fit growth curves, compare treatment arms, and simulate competing rate processes.",
            },
            {
                "role": "Physicists & aerospace engineers",
                "detail": "Integrate equations of motion for trajectories, orbits, and control systems.",
            },
            {
                "role": "Climate scientists",
                "detail": "Track fluxes and reservoirs in Earth system models — accumulation of heat and carbon.",
            },
            {
                "role": "ML engineers",
                "detail": "Use gradients (derivatives) to minimize loss across billions of parameter updates.",
            },
        ],
        "enables": [
            "Predicting when drug concentration crosses therapeutic or toxic thresholds",
            "Forecasting whether treatment can outpace tumor growth",
            "Designing rocket trajectories and autonomous vehicle paths",
            "Understanding long-run climate response to emissions",
            "Training AI models that improve through incremental error reduction",
            "Pricing derivatives whose value depends on continuous underlying processes",
        ],
        "examples": [
            {
                "name": "Drug concentration",
                "description": "dC/dt models infusion, metabolism, and half-life — dosing schedules depend on integrals of exposure.",
            },
            {
                "name": "Tumor dynamics",
                "description": "Exponential or logistic growth minus treatment effect — calculus compares competing rates.",
            },
            {
                "name": "AI gradient descent",
                "description": "Each training step is a discrete approximation to moving along the negative gradient of loss.",
            },
            {
                "name": "Climate heat budget",
                "description": "Incoming solar minus outgoing radiation integrates into temperature change over decades.",
            },
        ],
        "mathematical_core": """
        - **Derivative** dX/dt: instantaneous rate of change  
        - **Integral** ∫ f(t) dt: total accumulated effect over an interval  
        - **ODEs**: equations linking a quantity to its rate (growth, decay, SIR models)  
        - **Competing rates**: net change = growth − treatment − clearance  
        Professionals rarely compute integrals by hand — they build models whose **structure** is calculus.
        """,
        "interview_framing": [
            "Describe a system as stocks and flows, not just levels.",
            "Explain what drives the derivative (forces, rates, gradients).",
            "Connect discrete ML updates to continuous optimization intuition.",
            "Give one domain example where integration answers a decision question.",
        ],
        "ai_connection": """
        Neural network training is gradient-based optimization — multivariate calculus at scale.
        Diffusion models, physics-informed neural networks, and neural ODEs explicitly embed
        continuous-time dynamics. Understanding accumulation separates engineers who tune hyperparameters
        from those who understand **why** learning dynamics behave as they do.
        """,
        "exploration_prompts": [
            "If a rate doubles, how does the accumulated outcome change over 10 years?",
            "When do two competing rates produce stability vs runaway growth?",
            "What decision requires an integral rather than a snapshot value?",
        ],
    },
    "Uncertainty Systems (Probability)": {
        "title": "Uncertainty Systems — Probability as Risk & Reasoning",
        "tagline": (
            "Probability is the mathematics of **what we do not know for certain** — "
            "and how to make disciplined decisions anyway."
        ),
        "why_matters": """
        Real systems are rarely deterministic. Markets move randomly. Patients respond differently.
        Games of chance, weather, cyber attacks, and election outcomes all require reasoning about
        **likelihood**, not certainty. Probability turns vague risk into quantified structure:
        expected value, tail risk, conditional belief, and optimal bets under uncertainty.
        """,
        "systems": [
            "Insurance and actuarial loss modeling",
            "Gambling, poker, and casino house-edge design",
            "Medical diagnosis with imperfect tests",
            "Weather and hurricane landfall probabilities",
            "Credit risk and loan default modeling",
            "A/B testing and experimentation in tech products",
            "Bayesian filters in robotics and tracking",
        ],
        "professional_use": [
            {
                "role": "Actuaries",
                "detail": "Price policies using frequency-severity distributions and ruin probabilities.",
            },
            {
                "role": "Poker players & quants",
                "detail": "Compute pot odds, implied probability, and expected value of actions.",
            },
            {
                "role": "Physicians & diagnosticians",
                "detail": "Update disease probability given test results (Bayes' theorem).",
            },
            {
                "role": "Risk managers",
                "detail": "Stress portfolios and institutions against tail scenarios.",
            },
        ],
        "enables": [
            "Pricing insurance fairly while remaining solvent",
            "Detecting whether a clinical trial result could be chance",
            "Building spam filters and fraud detectors",
            "Calibrating weather forecasts as probabilities, not yes/no",
            "Designing casino games with guaranteed long-run edge",
            "Quantifying cyber intrusion risk over a planning horizon",
        ],
        "examples": [
            {"name": "Insurance", "description": "Aggregate random claims into a distribution of annual loss."},
            {"name": "Poker", "description": "Win rate × pot size vs cost to call — expected value drives decisions."},
            {"name": "Medical testing", "description": "P(disease | positive test) depends on base rate and test accuracy."},
            {"name": "Election forecasting", "description": "Polls + historical error → probability of each outcome."},
        ],
        "mathematical_core": """
        - Random variables, distributions, expectation E[X]  
        - Conditional probability P(A|B) and Bayes' rule  
        - Law of large numbers and central limit theorem (why aggregates stabilize)  
        - Decision theory: maximize expected utility under constraints  
        """,
        "interview_framing": [
            "Always state the base rate before interpreting a test or signal.",
            "Distinguish outcome probability from model uncertainty.",
            "Explain expected value vs variance for a business decision.",
        ],
        "ai_connection": """
        Modern AI is probabilistic at its core: softmax outputs, Bayesian neural networks,
        variational inference, Thompson sampling in bandits, and calibrated uncertainty in
        medical AI. LLMs produce distributions over tokens; reinforcement learning estimates
        value under stochastic environments.
        """,
        "exploration_prompts": [
            "When does a positive test still imply low disease probability?",
            "Why can a positive-expectation bet still ruin you?",
            "How does Bayes update beliefs as new evidence arrives?",
        ],
    },
    "Pattern Detection Systems (Statistics)": {
        "title": "Pattern Detection Systems — Statistics as Signal from Noise",
        "tagline": (
            "Statistics extracts **structure hidden in noisy data** — "
            "the foundation of forecasting, experimentation, and scientific inference."
        ),
        "why_matters": """
        Raw data lies. Small samples exaggerate effects. Correlation masquerades as causation.
        Statistics provides tools to estimate true relationships, quantify uncertainty in those
        estimates, and decide whether patterns are real or plausibly random. Every recommendation
        engine, election model, quality control system, and clinical trial depends on this discipline.
        """,
        "systems": [
            "Sports analytics — separating talent from luck",
            "Election forecasting — aggregating polls with uncertainty",
            "Market factor models and econometrics",
            "Epidemiological surveillance and trend detection",
            "Manufacturing quality control (SPC)",
            "Clinical trials and treatment effect estimation",
            "Tech experimentation — conversion lift measurement",
        ],
        "professional_use": [
            {
                "role": "Data scientists",
                "detail": "Build regression, classification, and forecasting models with validated error metrics.",
            },
            {
                "role": "Biostatisticians",
                "detail": "Design trials with power analysis; estimate treatment effects with confidence intervals.",
            },
            {
                "role": "Forecasters",
                "detail": "Combine heterogeneous signals (polls, fundamentals, economic indicators).",
            },
        ],
        "enables": [
            "Projecting player performance with regression to the mean",
            "Detecting manufacturing defects before they scale",
            "Estimating vaccine efficacy with quantified uncertainty",
            "Building credit scores from historical default patterns",
            "Ranking search results from click and relevance signals",
        ],
        "examples": [
            {"name": "Sports projections", "description": "Shrink extreme seasons toward career true talent."},
            {"name": "Election models", "description": "Simulate electoral college from state-level poll errors."},
            {"name": "Disease surveillance", "description": "Detect outbreaks above expected seasonal noise."},
            {"name": "Recommendation engines", "description": "Collaborative filtering estimates preference structure."},
        ],
        "mathematical_core": """
        - Regression, correlation, and regularization  
        - Sampling distributions and confidence intervals  
        - Hypothesis tests and p-values (with caution)  
        - Bias-variance tradeoff in prediction  
        - Causal inference (experiments, instrumental variables, DAGs)  
        """,
        "interview_framing": [
            "Explain why a great rookie season might over-forecast future performance.",
            "Describe how you would validate a predictive model out-of-sample.",
            "Discuss signal vs noise in a domain you know well.",
        ],
        "ai_connection": """
        Machine learning is computational statistics at scale: regularized regression, cross-validation,
        ensemble methods, and deep learning as flexible function approximation. LLM fine-tuning,
        embedding models, and retrieval metrics all inherit statistical thinking about generalization.
        """,
        "exploration_prompts": [
            "What sample size is needed to detect a 2% conversion lift?",
            "When does correlation fail to imply a useful policy intervention?",
        ],
    },
    "Optimization Systems": {
        "title": "Optimization Systems — Finding Best Decisions Under Constraints",
        "tagline": (
            "Optimization is the mathematics of **the best possible choice** when resources, "
            "physics, time, and rules limit what is feasible."
        ),
        "why_matters": """
        Every organization faces allocation problems: routes, portfolios, schedules, hyperparameters,
        rocket fuel, ad spend. Optimization formalizes objectives (minimize cost, maximize return)
        and constraints (capacity, budget, safety) into solvable structures. Linear programming,
        convex optimization, and gradient methods power logistics, AI training, engineering design,
        and financial construction.
        """,
        "systems": [
            "AI training — minimize loss over millions of parameters",
            "Supply chain and route planning",
            "Portfolio construction with risk constraints",
            "Robotics motion planning and control",
            "Engineering design — lightest structure that survives load",
            "Ad bidding and budget allocation in tech platforms",
            "Power grid and energy dispatch",
        ],
        "professional_use": [
            {
                "role": "Operations researchers",
                "detail": "Solve routing, scheduling, and inventory problems at national scale.",
            },
            {
                "role": "Portfolio managers",
                "detail": "Optimize weights subject to risk, sector, and liquidity constraints.",
            },
            {
                "role": "ML engineers",
                "detail": "Tune learning rates, architectures, and losses via constrained search.",
            },
        ],
        "enables": [
            "Delivering packages with minimal fuel and time",
            "Training neural networks that would be impossible to configure by hand",
            "Designing antennas, wings, and chips via topology optimization",
            "Running autonomous vehicles that minimize risk subject to traffic rules",
        ],
        "examples": [
            {"name": "Gradient descent", "description": "Iterative improvement toward a minimum loss surface."},
            {"name": "Linear programming", "description": "Allocate warehouse shipments at lowest cost."},
            {"name": "Trajectory optimization", "description": "Launch angle and thrust profile for missions."},
        ],
        "mathematical_core": """
        - Objective function f(x) to minimize or maximize  
        - Feasible region defined by constraints  
        - Convexity, duality, KKT conditions (advanced)  
        - Discrete optimization (integer programs) for routing  
        """,
        "interview_framing": [
            "State objective, decision variables, and constraints clearly.",
            "Explain tradeoffs when no single solution dominates (Pareto frontier).",
        ],
        "ai_connection": """
        All deep learning is optimization: SGD, Adam, second-order methods, RL policy gradients,
        hyperparameter search (Bayesian optimization), and alignment objectives. ChatGPT's training
        is a massive constrained optimization over data, compute, and safety objectives.
        """,
        "exploration_prompts": [
            "What changes if you add one more constraint to a routing problem?",
            "Why do non-convex losses still yield useful AI models?",
        ],
    },
    "Simulation Systems": {
        "title": "Simulation Systems — Exploring Alternate Futures",
        "tagline": (
            "When systems are too complex for closed-form answers, simulation generates "
            "**many possible futures** and studies their distribution."
        ),
        "why_matters": """
        Financial crises, pandemics, hurricanes, playoff series, and nuclear reliability cannot be
        captured by one formula. Monte Carlo and agent-based simulation sample randomness repeatedly
        to estimate probabilities, percentiles, and worst-case scenarios. Institutions stress-test
        before disasters; engineers test million virtual flights before one real launch.
        """,
        "systems": [
            "Financial risk and derivative pricing",
            "Insurance catastrophe modeling",
            "Epidemic spread (SIR and beyond)",
            "Climate ensembles — many model runs",
            "Sports season and tournament simulation",
            "Engineering reliability and failure analysis",
            "Military wargaming and logistics under disruption",
        ],
        "professional_use": [
            {
                "role": "Risk quants",
                "detail": "Simulate portfolio paths for VaR, CVaR, and stress scenarios.",
            },
            {
                "role": "Epidemiologists",
                "detail": "Run compartment models with uncertain parameters.",
            },
            {
                "role": "Actuaries",
                "detail": "Aggregate simulated losses for capital requirements.",
            },
        ],
        "enables": [
            "Estimating π — and any integral via random sampling",
            "Pricing options and insurance reserves",
            "Planning hospital surge capacity for pandemic scenarios",
            "Evaluating climate policy under uncertainty bands",
            "Testing autonomous vehicle policies in synthetic traffic",
        ],
        "examples": [
            {"name": "Monte Carlo finance", "description": "Thousands of return paths → distribution of wealth."},
            {"name": "Disease spread", "description": "Stochastic contacts produce epidemic curves."},
            {"name": "Climate ensembles", "description": "Many runs bracket future temperature ranges."},
        ],
        "mathematical_core": """
        - Random sampling and law of large numbers  
        - Variance reduction techniques (antithetic, importance sampling)  
        - Agent-based vs equation-based simulation  
        - Sensitivity analysis across parameter uncertainty  
        """,
        "interview_framing": [
            "Explain when simulation beats a formula.",
            "Describe inputs, randomness source, and output metrics.",
        ],
        "ai_connection": """
        Simulation trains reinforcement learning (AlphaGo, robotics simulators), generates synthetic
        data for rare events, and powers diffusion models that simulate denoising trajectories.
        Digital twins combine simulation with live sensor updates.
        """,
        "exploration_prompts": [
            "What tail risk only appears after 10,000 simulated years?",
            "How sensitive is the output to one input parameter?",
        ],
    },
    "AI and Learning Systems": {
        "title": "AI & Learning Systems — Mathematics of Adaptive Intelligence",
        "tagline": (
            "Modern AI is not magic — it is **optimization, statistics, probability, and calculus** "
            "composed at scale to recognize patterns and make predictions."
        ),
        "why_matters": """
        ChatGPT, computer vision, medical diagnosis AI, and autonomous vehicles all inherit the same
        mathematical stack: learn parameters that minimize prediction error on data, represent
        uncertainty where needed, and generalize to new examples. Understanding AI mathematically
        means understanding generalization, loss landscapes, gradients, and probabilistic outputs.
        """,
        "systems": [
            "Large language models — next-token prediction at scale",
            "Computer vision — convolutional pattern detection",
            "Recommendation systems — collaborative and content filtering",
            "Medical imaging AI — classification with calibrated risk",
            "Autonomous vehicles — perception, prediction, planning stack",
            "Reinforcement learning — agents learning via simulated experience",
            "Fraud and cybersecurity anomaly detection",
        ],
        "professional_use": [
            {
                "role": "ML researchers",
                "detail": "Design architectures, losses, and training regimes with theoretical and empirical tools.",
            },
            {
                "role": "MLOps engineers",
                "detail": "Deploy models with monitoring for drift, bias, and calibration.",
            },
            {
                "role": "AI safety teams",
                "detail": "Align objectives, evaluate tail failures, and stress-test behaviors.",
            },
        ],
        "enables": [
            "Natural language interfaces that reason over vast text corpora",
            "Real-time object detection for robotics and security",
            "Personalized feeds that optimize engagement and relevance",
            "Drug discovery acceleration via learned molecular representations",
        ],
        "examples": [
            {"name": "ChatGPT", "description": "Transformer + cross-entropy loss + massive gradient-based training."},
            {"name": "Recommendation engines", "description": "Matrix factorization and deep ranking models."},
            {"name": "Autonomous vehicles", "description": "Fusion of perception nets, trajectory forecasting, planning optimization."},
        ],
        "mathematical_core": """
        - Loss functions and empirical risk minimization  
        - Backpropagation (chain rule from calculus)  
        - Generalization, overfitting, regularization  
        - Attention, embeddings, and representation learning  
        - RL: Bellman equations and policy gradients  
        """,
        "interview_framing": [
            "Map a business problem to prediction, classification, or ranking.",
            "Explain train/validation/test and why leakage invalidates models.",
            "Connect model failure modes to bias, variance, or distribution shift.",
        ],
        "ai_connection": """
        This theme *is* the AI layer — but it rests on all five other systems. Accumulation (gradients),
        uncertainty (calibration), statistics (generalization), optimization (training), and simulation
        (RL environments) are inseparable from modern machine intelligence.
        """,
        "exploration_prompts": [
            "Which part of the stack fails if labels leak from test into train?",
            "Where would you demand probabilistic outputs vs point predictions?",
        ],
    },
}

THEME_NAMES = list(THEMES.keys())
