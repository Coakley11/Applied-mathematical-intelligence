"""Plain-language guides for every lab tool — shown before each simulation."""

TOOL_GUIDES: dict[str, dict] = {
    "lab_poker": {
        "plain_name": "Is This Call Worth It?",
        "what": "A poker decision checker. You describe a hand situation — your chance of winning, the pot size, and what it costs to call — and the app tells you if the math supports your decision.",
        "why": "Poker is not pure luck over many hands. Players who consistently make positive expected-value (+EV) decisions win long-term. The same logic applies to insurance, trading, and any risk decision.",
        "figuring_out": "Whether calling, folding, or raising is the mathematically correct play in this spot.",
        "math_used": "Expected value, pot odds, and Kelly criterion for bet sizing.",
        "controls": "Win probability, pot size, call cost, and your chosen action (fold / call / raise).",
        "interpret": "Positive EV means the decision is profitable over many identical situations. If your equity exceeds pot odds, a call is justified. Kelly fraction suggests how much bankroll to risk.",
        "math_behind": (
            "**Expected value:** EV = P(win) × pot − P(lose) × call cost. If EV > 0, calling earns money long-run.\n\n"
            "**Pot odds:** Required equity = call / (pot + call). You need at least this win rate to break even.\n\n"
            "**Kelly criterion:** Sizes bets to maximize long-run growth: f* = edge / odds. Half-Kelly is common in practice.\n\n"
            "These are probability tools — they do not guarantee winning any single hand."
        ),
        "practice_id": "ev_pot_odds",
        "portfolio_idea": "Build a Poker EV Calculator in Python or Excel with Monte Carlo bankroll paths.",
    },
    "casino_edge": {
        "plain_name": "Why the House Always Wins",
        "what": "Shows what happens to your money when you play many casino bets against a built-in house edge.",
        "why": "Casinos are profitable because every game has a small mathematical edge. Understanding this prevents believing in 'lucky streaks' or betting systems that beat the math.",
        "figuring_out": "How quickly a small per-bet disadvantage compounds into large losses over time.",
        "math_used": "Expected value per bet and cumulative random walks.",
        "controls": "House edge percentage and number of bets simulated.",
        "interpret": "The line trends downward because each bet has negative EV. Short winning streaks happen, but the long-run direction is predictable.",
        "math_behind": (
            "Each bet returns roughly (1 − edge) × wager on average. Over *n* bets, expected loss ≈ n × edge × wager.\n\n"
            "Variance creates bumps, but **expectation** is negative — this is why no betting system beats a negative-EV game long-term."
        ),
        "practice_id": "ev_bet",
        "portfolio_idea": "Simulate 10,000 gamblers playing roulette and plot the distribution of final bankrolls.",
    },
    "lab_sports_betting": {
        "plain_name": "Is This Bet Worth It?",
        "what": "Compare your estimated win probability to the bookmaker's odds and see if a sports bet has positive expected value.",
        "why": "Odds look like random numbers, but they encode implied probabilities. If you believe a team wins more often than the odds suggest, you may have an edge.",
        "figuring_out": "Whether a wager is mathematically favorable before you stake money.",
        "math_used": "Implied probability, expected value, and variance over many bets.",
        "controls": "Team win probabilities, odds format, stake, and your pick.",
        "interpret": "+EV means you expect to profit over many similar bets — but you can still lose many in a row. Edge is not a guarantee on one game.",
        "math_behind": (
            "**Implied probability** (decimal odds): P = 1 / odds.\n\n"
            "**Expected value:** EV = P(win) × profit − P(lose) × stake.\n\n"
            "**Edge:** Your estimated probability minus implied probability.\n\n"
            "Sports outcomes are noisy — even 60% favorites lose 40% of the time."
        ),
        "practice_id": "ev_bet",
        "portfolio_idea": "Build a sports EV dashboard that flags +EV bets and simulates a full season.",
    },
    "sports_shrinkage": {
        "plain_name": "Separate Signal from Noise",
        "what": "Adjusts a team's observed performance toward the league average when you do not have much data — avoiding overreaction to small samples.",
        "why": "A team that wins 8 of 10 games may just be lucky. Shrinkage (regression to the mean) produces smarter forecasts with limited information.",
        "figuring_out": "What a team's true strength probably is after accounting for sample size and luck.",
        "math_used": "Bayesian shrinkage / regression to the mean.",
        "controls": "Observed win rate, number of games, and league average.",
        "interpret": "The adjusted estimate sits between the team's raw rate and the average. More games → less shrinkage → more trust in observed data.",
        "math_behind": (
            "Raw rate = wins / games. Shrinkage pulls extreme rates toward the mean:\n\n"
            "Adjusted ≈ (wins + prior) / (games + prior_weight)\n\n"
            "This is the same idea behind Nate Silver's election models and player rating systems."
        ),
        "practice_id": "shrinkage",
        "portfolio_idea": "Implement an Elo or Bayesian rating system for a sports league.",
    },
    "lab_forecasting": {
        "plain_name": "Separate Signal from Noise",
        "what": "Generates noisy data, finds the underlying trend, and forecasts future values with uncertainty bands.",
        "why": "Real data is messy. Fitting a trend and showing confidence intervals helps you distinguish real patterns from random fluctuation.",
        "figuring_out": "What the future might look like — and how uncertain that forecast is.",
        "math_used": "Linear regression, R², and confidence intervals.",
        "controls": "Trend slope, noise level, sample size, and forecast horizon.",
        "interpret": "Wide bands = low confidence. R² near 1 = strong trend; near 0 = mostly noise. Forecasts far ahead are less reliable.",
        "math_behind": (
            "Linear regression finds the best-fit line: ŷ = β₀ + β₁t.\n\n"
            "R² = 1 − (sum of squared errors / total variance) — fraction of variation explained by the trend.\n\n"
            "Uncertainty grows when extrapolating further from the data (wider confidence bands)."
        ),
        "practice_id": "forecast_slope",
        "portfolio_idea": "Backtest a forecasting model on historical sports or weather data.",
    },
    "epidemic_sir": {
        "plain_name": "Disease Spread Simulator",
        "what": "Shows how a disease spreads through a population. People move from **susceptible** → **infected** → **recovered**. You change how contagious the disease is, how fast people recover, and how many start infected — the app shows how large the outbreak could become.",
        "why": "Public health decisions (lockdowns, vaccination, hospital planning) depend on predicting outbreak size. This model is the foundation of epidemiology.",
        "figuring_out": "How big the epidemic peak could get and how many people eventually recover.",
        "math_used": "Differential equations (SIR model) — rates of change in each group.",
        "controls": "Transmission rate (β), recovery rate (γ), and simulation length in days.",
        "interpret": "Higher β → faster spread → higher peak. Higher γ → faster recovery → smaller peak. The peak infectious count tells you hospital capacity needs.",
        "math_behind": (
            "SIR equations (continuous approximation):\n\n"
            "dS/dt = −βSI/N  ·  dI/dt = βSI/N − γI  ·  dR/dt = γI\n\n"
            "β controls how fast infection spreads; γ controls how fast people recover. "
            "This is **calculus** — rates of change interacting over time."
        ),
        "practice_id": "sir_rates",
        "portfolio_idea": "Fit an SIR model to real COVID or flu case data and estimate R₀.",
    },
    "tumor_growth": {
        "plain_name": "Tumor Growth vs Treatment",
        "what": "Models how a tumor grows over time and how treatment slows or reverses that growth. You set the growth rate and treatment strength — the app shows whether the tumor shrinks or keeps growing.",
        "why": "Oncologists compare treatment protocols by modeling whether growth or treatment wins. Exponential models capture rapid early growth.",
        "figuring_out": "Whether treatment is strong enough to overcome tumor proliferation.",
        "math_used": "Exponential growth (calculus — rate of change accumulates).",
        "controls": "Initial tumor size, growth rate, treatment effect, and time periods.",
        "interpret": "If net growth (growth − treatment) is positive, the tumor expands. Negative net growth means treatment is winning.",
        "math_behind": (
            "Size(t) = Size₀ × e^((r − d)t)\n\n"
            "r = proliferation rate, d = treatment kill rate. "
            "This is exponential **accumulation** — small per-period changes compound into large outcomes."
        ),
        "practice_id": "tumor_growth",
        "portfolio_idea": "Compare two treatment schedules and plot tumor burden over 12 months.",
    },
    "pharmacokinetics": {
        "plain_name": "Drug Concentration Over Time",
        "what": "Shows how drug concentration in the body rises after a dose and falls as the body eliminates it. Change the dose and elimination rate to see exposure over time.",
        "why": "Doctors need to know whether drug levels stay in the therapeutic window — too low is ineffective, too high is toxic.",
        "figuring_out": "How much drug exposure (AUC) a patient receives from a given dose.",
        "math_used": "Exponential decay (calculus — elimination as a continuous rate).",
        "controls": "Dose, elimination rate constant (k), and hours tracked.",
        "interpret": "Higher dose → higher peak. Faster elimination → shorter duration. AUC summarizes total exposure.",
        "math_behind": (
            "C(t) = (Dose/V) × e^(−kt)\n\n"
            "AUC = ∫ C(t) dt — the **integral** of concentration over time measures total exposure.\n\n"
            "Pharmacokinetics is calculus applied to medicine."
        ),
        "practice_id": "accumulation",
        "portfolio_idea": "Model a two-dose vaccine schedule and compare peak concentrations.",
    },
    "lab_ai_training": {
        "plain_name": "How AI Learns",
        "what": "Watch an optimizer 'walk downhill' on a loss surface — the same process that trains ChatGPT, image classifiers, and recommendation engines.",
        "why": "AI is not magic — it is gradient descent repeatedly improving a score (loss). Understanding this demystifies how models learn.",
        "figuring_out": "How learning rate and training steps affect whether a model converges to a good solution.",
        "math_used": "Gradient descent, derivatives (calculus), and loss minimization.",
        "controls": "Learning rate, training steps, starting position, and data noise.",
        "interpret": "Loss should decrease. Too-high learning rate overshoots; too-low crawls. The red path shows the optimizer's journey.",
        "math_behind": (
            "Gradient descent: θ_new = θ_old − α × ∇Loss(θ)\n\n"
            "α = learning rate. ∇Loss is the **gradient** (partial derivatives) pointing uphill — "
            "we step opposite to go downhill. This is multivariable **calculus** driving modern AI."
        ),
        "practice_id": "gradient_step",
        "portfolio_idea": "Animate gradient descent on a 2D loss surface with different learning rates.",
    },
    "ai_ml_suite": {
        "plain_name": "Train a Mini Neural Network",
        "what": "A small neural network learns to classify data points. Adjust epochs, learning rate, and hidden units — watch training loss fall.",
        "why": "Real AI systems use the same loop: predict → measure error → adjust weights. This is the core of deep learning.",
        "figuring_out": "Whether the network can learn the pattern and how training settings affect accuracy.",
        "math_used": "Backpropagation (chain rule from calculus), cross-entropy loss, optimization.",
        "controls": "Training epochs, learning rate, and hidden layer size.",
        "interpret": "Falling loss = learning. Gap between training and validation loss = overfitting risk.",
        "math_behind": (
            "Forward pass: compute prediction. Loss = cross-entropy(error). "
            "Backward pass: chain rule computes ∂Loss/∂weight for each parameter.\n\n"
            "Weight update: w ← w − α × ∂Loss/∂w. Repeat thousands of times."
        ),
        "practice_id": "gradient_step",
        "portfolio_idea": "Train a classifier on a real dataset and report precision/recall.",
    },
    "weather_uncertainty_cone": {
        "plain_name": "Why Forecasts Get Less Certain",
        "what": "Runs many possible weather futures and shows how temperature forecasts spread into a widening cone over time.",
        "why": "A 3-day forecast is more reliable than a 10-day forecast. Uncertainty cones communicate this honestly.",
        "figuring_out": "How much confidence you should have in a forecast at different lead times.",
        "math_used": "Ensemble simulation, percentiles, and growing variance.",
        "controls": "Forecast horizon, starting temperature, daily uncertainty growth, and ensemble size.",
        "interpret": "The shaded cone widens with lead time — the median is the best guess, but the range shows what could happen.",
        "math_behind": (
            "Each ensemble member adds random daily shocks. Spread grows as √t (roughly) — "
            "uncertainty **accumulates** over time.\n\n"
            "10th–90th percentile bands show where 80% of scenarios fall — honest uncertainty quantification."
        ),
        "practice_id": "forecast_slope",
        "portfolio_idea": "Compare forecast cone width at day 3 vs day 10 using historical weather data.",
    },
    "orbital_mechanics": {
        "plain_name": "Predict an Orbit",
        "what": "Draws the path of a satellite or planet around a central body. Change eccentricity to see circles become ellipses.",
        "why": "NASA, SpaceX, and satellite operators use orbital mechanics to predict where objects will be — critical for launches and collision avoidance.",
        "figuring_out": "What shape an orbit takes and how eccentricity affects the path.",
        "math_used": "Kepler's laws, inverse-square gravity, parametric curves.",
        "controls": "Orbital eccentricity and time steps.",
        "interpret": "e = 0 is a circle. Higher e = more elongated ellipse. The central body sits at one focus.",
        "math_behind": (
            "Orbit equation: r(θ) = a(1 − e²) / (1 + e cos θ)\n\n"
            "Comes from F = GMm/r² and energy conservation — **calculus and physics** predict motion "
            "without simulating every timestep (though we plot it parametrically here)."
        ),
        "practice_id": "accumulation",
        "portfolio_idea": "Compute orbital period from semi-major axis using Kepler's third law.",
    },
    "exoplanet_transit": {
        "plain_name": "Detect a Planet by Its Shadow",
        "what": "Simulates how a planet passing in front of a star dims the star's light slightly — the method used to discover thousands of exoplanets.",
        "why": "We cannot see most exoplanets directly. Measuring tiny brightness dips reveals planet size and orbit.",
        "figuring_out": "How deep the light dip is and whether it is detectable above noise.",
        "math_used": "Geometry (area ratios), photometry, signal vs noise.",
        "controls": "Star radius, planet radius, and photometry noise level.",
        "interpret": "Larger planets create deeper dips. More noise makes detection harder — like finding a whisper in a crowd.",
        "math_behind": (
            "Transit depth ≈ (R_planet / R_star)² — the fraction of starlight blocked.\n\n"
            "Kepler detected dips as small as ~100 ppm. This is **ratio geometry** plus statistical signal detection."
        ),
        "practice_id": "probability_compare",
        "portfolio_idea": "Write a transit detector that flags dips above a noise threshold in light-curve data.",
    },
    "projectile": {
        "plain_name": "Calculate a Trajectory",
        "what": "Shows the arc of an object launched at an angle — a ball, rocket stage, or spacecraft. Change speed and angle to see where it lands.",
        "why": "Trajectory math is used in sports analytics, artillery, space missions, and game physics engines.",
        "figuring_out": "Maximum height and range for a given launch speed and angle.",
        "math_used": "Kinematics — position as function of time under gravity.",
        "controls": "Initial velocity and launch angle.",
        "interpret": "45° maximizes range in vacuum. Higher speed → higher arc and longer range.",
        "math_behind": (
            "x(t) = v cos(θ) × t  ·  y(t) = v sin(θ) × t − ½gt²\n\n"
            "Parabolic motion from **calculus**: velocity is the derivative of position, "
            "acceleration (gravity) is the derivative of velocity."
        ),
        "practice_id": "accumulation",
        "portfolio_idea": "Add air resistance and compare vacuum vs realistic range.",
    },
    "monte_carlo_pi": {
        "plain_name": "Run Many Possible Futures",
        "what": "Throws random darts at a square and estimates π from the fraction landing inside a circle. Shows how repeated random sampling converges to an answer.",
        "why": "When equations are too hard, simulate thousands of scenarios and count outcomes — used in finance, engineering, and AI.",
        "figuring_out": "How random sampling approximates a precise mathematical constant.",
        "math_used": "Monte Carlo method, probability, law of large numbers.",
        "controls": "Number of random samples.",
        "interpret": "More samples → estimate closer to π. This is the core idea behind all Monte Carlo simulation.",
        "math_behind": (
            "Area(circle)/Area(square) = π/4. Count fraction of points inside circle × 4 ≈ π.\n\n"
            "Law of large numbers: sample average converges to true probability as n → ∞."
        ),
        "practice_id": "probability_compare",
        "portfolio_idea": "Use Monte Carlo to estimate the probability of a complex event with no closed-form formula.",
    },
    "lab_optimization": {
        "plain_name": "Find the Best Decision",
        "what": "Split a budget across options with different returns and risk scores. Find the allocation that maximizes return while staying within your risk limit.",
        "why": "Real decisions have constraints — you cannot maximize everything. Optimization finds the best feasible choice.",
        "figuring_out": "The best allocation given your budget and risk tolerance.",
        "math_used": "Constrained optimization, objective functions, feasible regions.",
        "controls": "Budget, max risk, and manual allocation sliders.",
        "interpret": "If your risk exceeds the cap, shift toward safer options. The optimal mix maximizes return within constraints.",
        "math_behind": (
            "Maximize Σ wᵢ × returnᵢ  subject to  Σ wᵢ × riskᵢ ≤ R_max  and  Σ wᵢ = 1.\n\n"
            "This is **linear/convex optimization** — the same framework used in logistics, ML hyperparameter tuning, and scheduling."
        ),
        "practice_id": "ev_bet",
        "portfolio_idea": "Implement an optimizer with scipy.optimize for a 5-project portfolio.",
    },
}
