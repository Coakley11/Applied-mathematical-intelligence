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
        from components.practical_labs import render_action_hub, render_practical_lab  # noqa: F401
        from components.reference import render_reference_library  # noqa: F401
        from components.layout import render_domain_page, render_portfolio_lab, render_theme_page  # noqa: F401
        from components.thinking import render_mathematical_thinking  # noqa: F401
        from content.case_studies import CASE_STUDIES
        from content.domains import DOMAINS, DOMAIN_NAMES
        from content.practical_labs import ACTION_TO_LAB, PRACTICAL_LABS, PRACTICAL_LAB_NAMES
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

    if len(PRACTICAL_LAB_NAMES) != 5:
        errors.append(f"Expected 5 practical labs, got {len(PRACTICAL_LAB_NAMES)}")
    for name in PRACTICAL_LAB_NAMES:
        lab = PRACTICAL_LABS[name]
        for key in ("action", "goal", "tagline", "math_tools", "tools", "practice_challenge"):
            if not lab.get(key):
                errors.append(f"Lab '{name}' missing key: {key}")
        for tool in lab["tools"]:
            rid = tool.get("runner_id")
            if rid not in all_runners or not callable(all_runners[rid]):
                errors.append(f"Lab '{name}' tool bad runner_id: {rid}")

    if len(ACTION_TO_LAB) != 5:
        errors.append("ACTION_TO_LAB mapping incomplete")

    if len(THEME_NAMES) != len(THEMES):
        errors.append("THEME_NAMES / THEMES mismatch")
    for name in THEME_NAMES:
        if name not in THEMES:
            errors.append(f"Missing theme: {name}")

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
        if not callable(SIMULATION_RUNNERS.get(sid)):
            errors.append(f"Simulation not callable: {sid}")

    for sid, fn in SIMULATION_RUNNERS.items():
        if not callable(fn):
            errors.append(f"Registry entry not callable: {sid}")

    if len(MATHEMATICAL_THINKING.get("pillars", [])) != 10:
        errors.append("Mathematical Thinking pillars != 10")

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
    print(f"  commit check: imports OK")
    print(f"  practical labs: {len(PRACTICAL_LAB_NAMES)}")
    print(f"  domains: {len(DOMAIN_NAMES)}")
    print(f"  simulations: {len(SIMULATION_RUNNERS)}")
    print(f"  case study library: {len(CASE_STUDIES)}")
    print(f"  domains w/ case studies: {sum(1 for d in DOMAINS.values() if d.get('case_studies'))}")
    print(f"  portfolio: {len(PORTFOLIO_PROBLEMS)}")
    print(f"  themes: {len(THEME_NAMES)}")
    print(f"  data sources: {len(DATA_SOURCES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
