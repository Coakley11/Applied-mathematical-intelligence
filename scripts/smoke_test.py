#!/usr/bin/env python3
"""Smoke test — imports, registry, and content structure without Streamlit UI."""

from __future__ import annotations

import compileall
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    errors: list[str] = []

    for target in [ROOT / "components", ROOT / "content", ROOT / "simulations", ROOT / "data", ROOT / "scripts"]:
        if not compileall.compile_dir(str(target), quiet=1):
            errors.append(f"py_compile: {target}")

    if not compileall.compile_file(str(ROOT / "streamlit_app.py"), quiet=1):
        errors.append("py_compile: streamlit_app.py")

    try:
        from components.home import render_home  # noqa: F401
        from components.idea_analysis import render_idea_analysis  # noqa: F401
        from components.lab_guide import render_guided_tool  # noqa: F401
        from components.nav import navigate_to, render_action_grid  # noqa: F401
        from components.optimization_workshop import render_optimization_workshop  # noqa: F401
        from components.practical_labs import render_practical_lab  # noqa: F401
        from components.reference import render_reference_library  # noqa: F401
        from components.thinking_lab import render_thinking_lab  # noqa: F401
        from content.case_studies import CASE_STUDIES
        from content.domains import DOMAINS, DOMAIN_NAMES
        from content.navigation import PRIMARY_ACTIONS  # noqa: F401 — re-export shim
        from content.practical_labs import (
            ACTION_SECTION_TYPES,
            PRACTICAL_LABS,
            PRACTICAL_LAB_NAMES,
            SECONDARY_LAB_NAMES,
        )
        from content.thinking_lab import THINKING_TOPICS
        from content.tool_guides import TOOL_GUIDES
        from content.mathematical_thinking import MATHEMATICAL_THINKING
        from content.portfolio import PORTFOLIO_PROBLEMS
        from content.themes import THEMES, THEME_NAMES
        from data.registry import DATA_SOURCES, list_sources
        from simulations.labs import LAB_RUNNERS
        from simulations.registry import SIMULATION_RUNNERS, run_simulation  # noqa: F401
    except Exception as exc:
        errors.append(f"import: {exc}")
        print("SMOKE FAILED (imports)")
        for e in errors:
            print(f"  - {e}")
        return 1

    all_runners = {**LAB_RUNNERS, **SIMULATION_RUNNERS}

    if len(PRACTICAL_LAB_NAMES) != 7:
        errors.append(f"Expected 7 labs, got {len(PRACTICAL_LAB_NAMES)}")
    if len(SECONDARY_LAB_NAMES) != 3:
        errors.append(f"Expected 3 secondary labs, got {len(SECONDARY_LAB_NAMES)}")
    if len(PRIMARY_ACTIONS) != 7:
        errors.append(f"Expected 7 primary actions, got {len(PRIMARY_ACTIONS)}")
    if len(ACTION_SECTION_TYPES) != 7:
        errors.append("ACTION_SECTION_TYPES incomplete")

    for name in PRACTICAL_LAB_NAMES:
        lab = PRACTICAL_LABS[name]
        for key in ("action", "tagline", "intro", "tools"):
            if not lab.get(key):
                errors.append(f"Lab '{name}' missing key: {key}")
        for tool in lab["tools"]:
            rid = tool.get("runner_id")
            if rid not in all_runners or not callable(all_runners[rid]):
                errors.append(f"Lab '{name}' tool bad runner_id: {rid}")
            if rid not in TOOL_GUIDES:
                errors.append(f"Lab '{name}' tool missing guide: {rid}")

    if len(THEME_NAMES) != len(THEMES):
        errors.append("THEME_NAMES / THEMES mismatch")

    required_domain_keys = {
        "title", "tagline", "why_matters", "concepts", "professional_applications",
        "breakthroughs", "ai_connection", "simulation_id", "interpretation",
    }
    for name in DOMAIN_NAMES:
        d = DOMAINS[name]
        missing = required_domain_keys - d.keys()
        if missing:
            errors.append(f"Domain '{name}' missing keys: {missing}")
        sid = d.get("simulation_id")
        if sid not in SIMULATION_RUNNERS:
            errors.append(f"Domain '{name}' bad simulation_id: {sid}")

    if len(MATHEMATICAL_THINKING.get("pillars", [])) != 10:
        errors.append("Mathematical Thinking pillars != 10")

    if len(THINKING_TOPICS) != 11:
        errors.append("Thinking Lab topics != 11")

    for i, p in enumerate(PORTFOLIO_PROBLEMS):
        if not p.get("question"):
            errors.append(f"Portfolio {i} missing question")

    if len(list_sources()) < 6:
        errors.append("Expected at least 6 data source modules")

    if errors:
        print("SMOKE FAILED")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("SMOKE PASSED")
    print(f"  primary actions: {len(PRIMARY_ACTIONS)}")
    print(f"  practical labs: {len(PRACTICAL_LAB_NAMES)}")
    print(f"  thinking topics: {len(THINKING_TOPICS)}")
    print(f"  tool guides: {len(TOOL_GUIDES)}")
    print(f"  domains: {len(DOMAIN_NAMES)}")
    print(f"  simulations: {len(SIMULATION_RUNNERS)}")
    print(f"  portfolio: {len(PORTFOLIO_PROBLEMS)}")
    print(f"  themes: {len(THEME_NAMES)}")
    print(f"  data sources: {len(DATA_SOURCES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
