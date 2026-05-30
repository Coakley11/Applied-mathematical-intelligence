"""Shared UI components for Applied Mathematical Intelligence."""

import streamlit as st


LENS_KEYS = {
    "Calculus / Accumulation": "calculus",
    "Probability / Uncertainty": "probability",
    "Statistics / Pattern Detection": "statistics",
    "Optimization / Improvement": "optimization",
    "Simulation / Alternate Futures": "simulation",
    "AI / Learning Systems": "ai",
}


def section(title: str) -> None:
    st.markdown("---")
    st.header(title)


def bullet_block(items: list[str]) -> None:
    st.markdown("\n".join(f"- {item}" for item in items))


def render_depth_notice(depth: str) -> None:
    if depth == "Professional Overview":
        st.caption(
            "Viewing at professional overview depth — concepts and impact first, "
            "with lighter technical detail."
        )
    elif depth == "Portfolio / Interview Framing":
        st.caption(
            "Portfolio / interview depth — emphasis on projects, deliverables, "
            "and how to discuss this domain professionally."
        )


def render_lens_highlight(primary_lenses: list[str], active_lens: str) -> None:
    if active_lens in primary_lenses:
        st.success(
            f"This domain is strongly connected to **{active_lens}**. "
            "Sections below are framed through that mathematical lens."
        )
    else:
        st.info(
            f"Viewing through **{active_lens}**. This domain also draws on other "
            "mathematical systems — see Mathematical Concepts Used."
        )


def render_theme_page(theme: dict, depth: str) -> None:
    section(theme["title"])
    st.markdown(theme["tagline"])

    render_depth_notice(depth)

    st.subheader("Why This Mathematical Idea Matters")
    st.markdown(theme["why_matters"])

    st.subheader("Real-World Systems That Depend On It")
    bullet_block(theme["systems"])

    st.subheader("How Professionals Use It")
    for item in theme["professional_use"]:
        st.markdown(f"**{item['role']}** — {item['detail']}")

    st.subheader("What Becomes Possible")
    bullet_block(theme["enables"])

    st.subheader("Deep Examples Across Domains")
    cols = st.columns(2)
    for i, example in enumerate(theme["examples"]):
        with cols[i % 2]:
            st.markdown(f"**{example['name']}**")
            st.markdown(example["description"])

    if depth != "Professional Overview":
        st.subheader("Core Mathematical Structure")
        st.markdown(theme["mathematical_core"])

    if depth == "Portfolio / Interview Framing":
        st.subheader("How to Discuss This in Interviews")
        bullet_block(theme["interview_framing"])

    st.subheader("How Modern AI Uses This")
    st.markdown(theme["ai_connection"])

    if theme.get("exploration_prompts"):
        st.subheader("Laboratory Questions")
        bullet_block(theme["exploration_prompts"])


def render_domain_page(
    domain: dict,
    depth: str,
    active_lens: str,
    run_simulation,
) -> None:
    section(domain["title"])
    st.markdown(domain["tagline"])
    render_depth_notice(depth)
    render_lens_highlight(domain.get("primary_lenses", []), active_lens)

    st.subheader("Why This Matters")
    st.markdown(domain["why_matters"])

    st.subheader("Mathematical Concepts Used")
    concepts = domain["concepts"]
    if active_lens in domain.get("primary_lenses", []):
        lens_key = LENS_KEYS.get(active_lens)
        prioritized = [c for c in concepts if lens_key and lens_key in c.lower()]
        other = [c for c in concepts if c not in prioritized]
        if prioritized:
            st.markdown("**Highlighted for your current lens:**")
            bullet_block(prioritized)
        if other and depth != "Professional Overview":
            st.markdown("**Also central to this domain:**")
            bullet_block(other)
    else:
        bullet_block(concepts)

    st.subheader("Real Professional Applications")
    bullet_block(domain["professional_applications"])

    st.subheader("Historical Breakthroughs")
    for item in domain["breakthroughs"]:
        st.markdown(f"**{item['title']}** ({item.get('era', '—')})")
        st.markdown(item["description"])

    if depth != "Portfolio / Interview Framing":
        st.subheader("Interactive Simulation")
        st.caption(domain.get("simulation_caption", "Explore the system dynamics below."))
        run_simulation(domain.get("simulation_id"))
        if domain.get("interpretation"):
            st.markdown("### System Interpretation")
            st.markdown(domain["interpretation"])

    st.subheader("How Modern AI Uses This")
    st.markdown(domain["ai_connection"])

    col_excel, col_python = st.columns(2)
    with col_excel:
        st.subheader("Example Excel Projects")
        bullet_block(domain["excel_projects"])
    with col_python:
        st.subheader("Example Python Projects")
        bullet_block(domain["python_projects"])

    st.subheader("Interview / Portfolio Project Ideas")
    bullet_block(domain["portfolio_ideas"])

    if depth == "Portfolio / Interview Framing":
        st.success(domain.get("portfolio_tip", domain["portfolio_ideas"][0]))


def render_portfolio_lab(problems: list[dict]) -> None:
    section("Portfolio & Interview Laboratory")

    st.markdown("""
    Professional applied mathematics is demonstrated through **projects**, not worksheets.
    Each problem below is designed as a portfolio artifact: a model, a simulation,
    a forecast, or an optimization study you can discuss in interviews.
    """)

    for problem in problems:
        with st.expander(problem["title"]):
            st.markdown(f"**Domain:** {problem['domain']}")
            st.markdown(f"**Mathematical systems:** {problem['systems']}")
            st.markdown("### Problem Statement")
            st.write(problem["prompt"])
            st.markdown("### Excel Deliverable")
            st.write(problem["excel"])
            st.markdown("### Python Deliverable")
            st.write(problem["python"])
            st.markdown("### Interview Talking Points")
            st.write(problem["interview"])

    st.success(
        "Strong portfolios combine domain context, mathematical structure, uncertainty quantification, "
        "and a clear decision or prediction the model supports."
    )
