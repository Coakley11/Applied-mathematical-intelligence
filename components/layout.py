"""Shared UI components for Applied Mathematical Intelligence."""

import importlib

import streamlit as st

from data.registry import describe_source


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

    case_studies = domain.get("case_studies", [])
    if case_studies:
        st.subheader("Professional Case Studies")
        for cs in case_studies:
            with st.expander(f"**{cs['title']}** — {cs.get('setting', 'Industry')}"):
                st.markdown(f"**Problem:** {cs['problem']}")
                st.markdown(f"**Approach:** {cs['approach']}")
                st.markdown("**Methods:** " + ", ".join(cs.get("methods", [])))
                st.markdown(f"**Impact:** {cs['impact']}")
                st.markdown(f"*Insight:* {cs['lesson']}")

    data_key = domain.get("data_source")
    if data_key:
        _render_data_readiness(data_key)

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


def _render_data_readiness(source_key: str) -> None:
    meta = describe_source(source_key)
    if not meta:
        return
    st.subheader("Real Data Integration (Ready to Wire)")
    st.caption(
        "Placeholder loaders exist — swap in live APIs when you are ready without restructuring the app."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Source:** {meta['label']}")
        st.markdown(f"**Provider:** {meta['provider']}")
        st.markdown(f"**Install:** `{meta['install_hint']}`")
    with c2:
        st.markdown(f"**Module:** `{meta['module']}`")
        st.markdown("**Functions:**")
        bullet_block(meta["functions"])
    try:
        mod = importlib.import_module(meta["module"])
        status = getattr(mod, "INTEGRATION_STATUS", "unknown")
        st.info(f"Integration status: **{status}** — returns schema-ready empty frames until connected.")
    except ImportError:
        st.warning("Data module not found.")


def render_portfolio_lab(problems: list[dict]) -> None:
    section("Portfolio & Interview Laboratory")

    st.markdown("""
    Build **GitHub-ready quantitative projects** — each specification below includes the business or scientific
    question, data requirements, Excel and Python deliverables, methods, visualizations, interview narrative,
    and a README summary suitable for recruiters and technical interviews.
    """)

    for problem in problems:
        with st.expander(f"**{problem['title']}**", expanded=False):
            st.markdown(f"**Domain:** {problem['domain']} · **Systems:** {problem['systems']}")
            st.markdown("#### Business / Scientific Question")
            st.write(problem["question"])
            st.markdown("#### Data Needed")
            st.write(problem["data_needed"])
            st.markdown("#### Statistical & Mathematical Methods")
            bullet_block(problem["methods"])
            st.markdown("#### Visualizations to Build")
            bullet_block(problem["visualizations"])
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Excel Version")
                st.write(problem["excel"])
            with col2:
                st.markdown("#### Python Version")
                st.write(problem["python"])
            st.markdown("#### Interview Talking Points")
            st.write(problem["interview"])
            st.markdown("#### GitHub README Summary")
            st.code(problem["github_readme"], language=None)

    st.success(
        "Ship each project as a repo with: `README.md`, `notebooks/analysis.ipynb`, `src/`, sample `data/`, "
        "and one chart that answers the decision question in the first screen."
    )
