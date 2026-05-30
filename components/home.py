"""Polished Home / landing page."""

import html

import streamlit as st

from content.domains import DOMAINS, DOMAIN_NAMES
from content.platform_meta import (
    FEATURED_DOMAINS,
    NUM_DOMAINS,
    NUM_PORTFOLIO,
    NUM_SIMULATIONS,
    NUM_THEMES,
    ROADMAP,
    VERSION,
)
from content.portfolio import PORTFOLIO_PROBLEMS
from content.themes import THEME_NAMES


def _card(title: str, badge: str, body: str, accent: str = "ami-card-accent") -> str:
    return f"""
    <div class="ami-card {accent}">
        <span class="ami-badge">{html.escape(badge)}</span>
        <h4>{html.escape(title)}</h4>
        <p>{html.escape(body)}</p>
    </div>
    """


def render_home() -> None:
    purpose = (
        "Applied Mathematical Intelligence shows how calculus, probability, statistics, "
        "optimization, simulation, and AI are used to model, predict, and improve real-world systems."
    )

    st.markdown(
        f"""
        <div class="ami-hero">
            <h1>Applied Mathematical Intelligence</h1>
            <p class="ami-tagline">{html.escape(purpose)}</p>
            <p class="ami-purpose">
                A quantitative reasoning laboratory — not a textbook. Explore how professional
                fields use mathematics to make predictions, manage risk, and build intelligent systems.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Platform stats
    st.markdown(
        f"""
        <div class="ami-stat-row">
            <div class="ami-stat"><div class="ami-stat-num">v{VERSION}</div><div class="ami-stat-label">Current version</div></div>
            <div class="ami-stat"><div class="ami-stat-num">{NUM_THEMES}</div><div class="ami-stat-label">Mathematical systems</div></div>
            <div class="ami-stat"><div class="ami-stat-num">{NUM_DOMAINS}</div><div class="ami-stat-label">Applied domains</div></div>
            <div class="ami-stat"><div class="ami-stat-num">{NUM_SIMULATIONS}</div><div class="ami-stat-label">Simulation engines</div></div>
            <div class="ami-stat"><div class="ami-stat-num">{NUM_PORTFOLIO}</div><div class="ami-stat-label">Portfolio projects</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Six systems
    st.markdown('<p class="ami-section-title">Six Mathematical Intelligence Systems</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ami-section-sub">The deep mathematical structures that power modern technology and high-stakes decisions.</p>',
        unsafe_allow_html=True,
    )

    theme_cards = [
        ("Accumulation Systems", "Calculus", "Continuous change, rates, integrals, compounding small effects into large outcomes."),
        ("Uncertainty Systems", "Probability", "Risk, Bayes, expected value, and decisions when outcomes are not certain."),
        ("Pattern Detection Systems", "Statistics", "Signal vs noise, regression, inference, and validated forecasting."),
        ("Optimization Systems", "Optimization", "Best decisions under constraints — resources, physics, time, and capital."),
        ("Simulation Systems", "Monte Carlo", "Alternate futures, stress tests, and distributions when formulas fail."),
        ("AI & Learning Systems", "Machine learning", "Gradients, pattern recognition, and prediction at scale."),
    ]

    rows = [theme_cards[i : i + 3] for i in range(0, 6, 3)]
    for row in rows:
        cols = st.columns(3)
        for col, (name, badge, desc) in zip(cols, row):
            with col:
                st.markdown(_card(name, badge, desc, "ami-card-theme"), unsafe_allow_html=True)

    st.caption("Open **Mathematical Themes** in the sidebar for full professional depth on each system.")

    # Featured domains
    st.markdown('<p class="ami-section-title">Featured Applied Domains</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ami-section-sub">Where mathematics meets real institutions — finance, medicine, space, AI, elections, and more.</p>',
        unsafe_allow_html=True,
    )

    featured = [d for d in FEATURED_DOMAINS if d in DOMAINS]
    domain_rows = [featured[i : i + 4] for i in range(0, len(featured), 4)]
    for row in domain_rows:
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            tagline = DOMAINS[name]["tagline"].replace("**", "").strip()[:140]
            if len(DOMAINS[name]["tagline"]) > 140:
                tagline += "…"
            with col:
                st.markdown(_card(name, "Applied domain", tagline, "ami-card-domain"), unsafe_allow_html=True)

    st.caption(f"Browse all **{len(DOMAIN_NAMES)} domains** under **Applied Domains** in the sidebar.")

    # How to use
    st.markdown('<p class="ami-section-title">How to Use This App</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ami-section-sub">Designed for exploration — use the sidebar to switch sections, lens, and depth.</p>',
        unsafe_allow_html=True,
    )

    steps = [
        (
            "Mathematical Thinking",
            "Read the signature framework: modeling, uncertainty, optimization, simulation, and AI as one intelligence stack.",
        ),
        (
            "Mathematical Themes",
            "Study the six intelligence systems: why they matter, how professionals use them, and how AI inherits them.",
        ),
        (
            "Applied Domains",
            "Enter a professional field — concepts, breakthroughs, simulations, Excel/Python projects, and interview ideas.",
        ),
        (
            "Mathematical lens",
            "Frame content through calculus, probability, statistics, optimization, simulation, or AI; filter domains by primary system.",
        ),
        (
            "Depth level",
            "Professional overview for executives; technical depth for analysts; portfolio framing for interviews.",
        ),
        (
            "Portfolio Lab",
            "Build deliverables: Monte Carlo risk, SIR models, calibration studies, recommenders, and more.",
        ),
    ]

    for i, (title, body) in enumerate(steps, 1):
        st.markdown(
            f"""
            <div class="ami-step">
                <div class="ami-step-num">{i}</div>
                <div class="ami-step-body">
                    <h5>{html.escape(title)}</h5>
                    <p>{html.escape(body)}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Portfolio value
    st.markdown('<p class="ami-section-title">Portfolio & Professional Value</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="ami-value-box">
            <p style="margin:0 0 1rem 0; color:#334155; line-height:1.6;">
                This project demonstrates <strong>applied mathematics</strong>, <strong>data analytics</strong>,
                <strong>AI-oriented thinking</strong>, and <strong>quantitative modeling</strong> in one coherent platform.
                Each domain connects theory to deliverables you can discuss in interviews: simulations, uncertainty
                quantification, optimization tradeoffs, and prediction under noise.
            </p>
            <p style="margin:0; color:#475569; font-size:0.9rem; line-height:1.55;">
                Suitable for portfolios in: quantitative finance, data science, actuarial science, biostatistics,
                operations research, sports analytics, ML engineering, and public-policy modeling.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Featured portfolio cards
    st.markdown('<p class="ami-section-title">Featured Portfolio Projects</p>', unsafe_allow_html=True)
    featured_projects = PORTFOLIO_PROBLEMS[:3]
    pcols = st.columns(3)
    for col, proj in zip(pcols, featured_projects):
        with col:
            st.markdown(
                _card(
                    proj["title"],
                    proj["domain"],
                    proj["prompt"][:120] + ("…" if len(proj["prompt"]) > 120 else ""),
                    "ami-card-portfolio",
                ),
                unsafe_allow_html=True,
            )

    st.caption(f"See all **{len(PORTFOLIO_PROBLEMS)} projects** in **Portfolio Lab**.")

    # Development status
    st.markdown('<p class="ami-section-title">Development Status</p>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ami-card ami-card-accent">
            <h4>Platform roadmap</h4>
            <p><strong>Version {VERSION}</strong> — domain-specific simulations, professional case studies,
            data-ready modules, {NUM_DOMAINS} domains, {NUM_SIMULATIONS} simulation engines.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for item in ROADMAP:
        st.markdown(f"- {item}")

    st.info(
        "Use the sidebar **Navigate** section to begin. Start with a **Mathematical Theme** for foundations, "
        "then an **Applied Domain** that matches your career interest."
    )
