"""Polished Home / landing page."""

import html

import streamlit as st

from content.domains import DOMAINS, DOMAIN_NAMES
from content.interactive_labs import INTERACTIVE_LABS, LAB_NAMES, NUM_LABS
from content.platform_meta import (
    FEATURED_DOMAINS,
    NUM_CASE_STUDY_LIBRARY,
    NUM_DOMAINS,
    NUM_DOMAINS_WITH_CASE_STUDIES,
    NUM_PORTFOLIO,
    NUM_SIMULATIONS,
    NUM_THEMES,
    ROADMAP,
    VERSION,
)
from content.portfolio import PORTFOLIO_PROBLEMS


def _card(title: str, badge: str, body: str, accent: str = "ami-card-accent") -> str:
    return f"""
    <div class="ami-card {accent}">
        <span class="ami-badge">{html.escape(badge)}</span>
        <h4>{html.escape(title)}</h4>
        <p>{html.escape(body)}</p>
    </div>
    """


def _lab_card(name: str) -> str:
    lab = INTERACTIVE_LABS[name]
    return f"""
    <div class="ami-card ami-card-lab">
        <span class="ami-lab-icon">{html.escape(lab["icon"])}</span>
        <span class="ami-badge">{html.escape(lab["badge"])}</span>
        <h4>{html.escape(name)}</h4>
        <p>{html.escape(lab["tagline"])}</p>
    </div>
    """


def render_home() -> None:
    st.markdown(
        """
        <div class="ami-hero">
            <h1>Applied Mathematical Intelligence</h1>
            <p class="ami-tagline">See how math powers real-world prediction, risk, and decision-making.</p>
            <p class="ami-purpose">
                A hands-on quantitative laboratory — explore themes, run interactive labs,
                and study how professionals use mathematics in finance, medicine, AI, and beyond.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="ami-stat-row">
            <div class="ami-stat"><div class="ami-stat-num">{NUM_LABS}</div><div class="ami-stat-label">Interactive labs</div></div>
            <div class="ami-stat"><div class="ami-stat-num">{NUM_THEMES}</div><div class="ami-stat-label">Math themes</div></div>
            <div class="ami-stat"><div class="ami-stat-num">{NUM_DOMAINS}</div><div class="ami-stat-label">Applied domains</div></div>
            <div class="ami-stat"><div class="ami-stat-num">{NUM_SIMULATIONS}</div><div class="ami-stat-label">Simulations</div></div>
            <div class="ami-stat"><div class="ami-stat-num">{NUM_PORTFOLIO}</div><div class="ami-stat-label">Portfolio projects</div></div>
        </div>
        <p style="text-align:center;color:#64748b;font-size:0.85rem;margin-top:-0.5rem;">
            v{VERSION} · {NUM_DOMAINS_WITH_CASE_STUDIES} domains with case studies · {NUM_CASE_STUDY_LIBRARY} in library
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Explore navigation
    st.markdown('<p class="ami-section-title">Choose what to explore</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ami-section-sub">Start with Interactive Labs for hands-on practice, or dive into themes and domains.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="ami-nav-grid">
            <div class="ami-nav-tile"><div class="ami-nav-icon">🧪</div><h5>Interactive Labs</h5><p>Poker, finance, forecasting, optimization, AI training</p></div>
            <div class="ami-nav-tile"><div class="ami-nav-icon">🧠</div><h5>Mathematical Thinking</h5><p>How quantitative intelligence works across fields</p></div>
            <div class="ami-nav-tile"><div class="ami-nav-icon">📐</div><h5>Mathematical Themes</h5><p>Calculus, probability, stats, optimization, simulation, AI</p></div>
            <div class="ami-nav-tile"><div class="ami-nav-icon">🌍</div><h5>Applied Domains</h5><p>Finance, epidemiology, robotics, climate, and 28+ more</p></div>
            <div class="ami-nav-tile"><div class="ami-nav-icon">💼</div><h5>Portfolio Lab</h5><p>Excel, Python, and interview-ready project specs</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Interactive Labs highlight
    st.markdown('<p class="ami-section-title">Interactive Labs — start here</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ami-section-sub">Make predictions, test strategies, and compare decisions with real controls.</p>',
        unsafe_allow_html=True,
    )

    lab_rows = [LAB_NAMES[i : i + 3] for i in range(0, len(LAB_NAMES), 3)]
    for row in lab_rows:
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            with col:
                st.markdown(_lab_card(name), unsafe_allow_html=True)

    st.caption("Open **Interactive Labs** in the sidebar to run any lab.")

    # Six systems
    st.markdown('<p class="ami-section-title">Six Mathematical Intelligence Systems</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ami-section-sub">The core structures behind modern prediction and decision systems.</p>',
        unsafe_allow_html=True,
    )

    theme_cards = [
        ("Accumulation", "Calculus", "Rates, integrals, and compounding small changes into large outcomes."),
        ("Uncertainty", "Probability", "Risk, Bayes, expected value, and decisions under unknown outcomes."),
        ("Pattern Detection", "Statistics", "Signal vs noise, regression, and validated forecasting."),
        ("Optimization", "Constraints", "Best choices when resources, time, and physics limit you."),
        ("Simulation", "Monte Carlo", "Stress-test alternate futures when closed-form math fails."),
        ("AI & Learning", "Machine learning", "Gradients, pattern recognition, and prediction at scale."),
    ]

    rows = [theme_cards[i : i + 3] for i in range(0, 6, 3)]
    for row in rows:
        cols = st.columns(3)
        for col, (name, badge, desc) in zip(cols, row):
            with col:
                st.markdown(_card(name, badge, desc, "ami-card-theme"), unsafe_allow_html=True)

    # Featured domains
    st.markdown('<p class="ami-section-title">Featured Applied Domains</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="ami-section-sub">Professional fields where math drives predictions and high-stakes decisions.</p>',
        unsafe_allow_html=True,
    )

    featured = [d for d in FEATURED_DOMAINS if d in DOMAINS]
    domain_rows = [featured[i : i + 4] for i in range(0, len(featured), 4)]
    for row in domain_rows:
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            tagline = DOMAINS[name]["tagline"].replace("**", "").strip()[:120]
            if len(DOMAINS[name]["tagline"]) > 120:
                tagline += "…"
            with col:
                st.markdown(_card(name, "Domain", tagline, "ami-card-domain"), unsafe_allow_html=True)

    st.caption(f"Browse all **{len(DOMAIN_NAMES)} domains** under **Applied Domains**.")

    # How to use — simplified
    st.markdown('<p class="ami-section-title">Quick start</p>', unsafe_allow_html=True)

    steps = [
        ("Run a lab", "Pick Interactive Labs → choose Poker, Finance, or Forecasting. Adjust sliders and read the recommendation."),
        ("Study a theme", "Mathematical Themes explains why calculus, probability, or optimization matter in practice."),
        ("Enter a domain", "Applied Domains connects math to finance, medicine, AI, climate, and more — with simulations."),
        ("Build your portfolio", "Portfolio Lab gives Excel/Python specs and interview talking points."),
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

    # Featured portfolio
    st.markdown('<p class="ami-section-title">Featured Portfolio Projects</p>', unsafe_allow_html=True)
    featured_projects = PORTFOLIO_PROBLEMS[:3]
    pcols = st.columns(3)
    for col, proj in zip(pcols, featured_projects):
        with col:
            st.markdown(
                _card(
                    proj["title"],
                    proj["domain"],
                    proj["question"][:100] + ("…" if len(proj["question"]) > 100 else ""),
                    "ami-card-portfolio",
                ),
                unsafe_allow_html=True,
            )

    st.caption(f"See all **{len(PORTFOLIO_PROBLEMS)} projects** in **Portfolio Lab**.")

    st.info(
        "**New to the platform?** Start with **Interactive Labs**, then explore **Applied Domains** "
        "for field-specific depth."
    )
