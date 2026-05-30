#!/usr/bin/env python3
"""QA validation — run before merging dev → main."""

from __future__ import annotations

import compileall
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    errors: list[str] = []

    try:
        from content.domains import DOMAINS, DOMAIN_NAMES
        from content.idea_analysis import IDEA_ANALYSIS, ANALYSIS_DIMENSIONS
        from content.mathematical_thinking import MATHEMATICAL_THINKING
        from content.navigation import PRIMARY_ACTIONS as NAV_PRIMARY_ACTIONS
        from content.problem_solving import (
            LAB_THINKING_PROMPTS,
            MATHEMATICIAN_MODE_TOPICS,
            PROBLEM_BREAKDOWN_STEPS,
            PROBLEM_SOLVING_LAB,
        )
        from content.optimization_workshop import OPTIMIZATION_WORKSHOP, WORKSHOP_STEPS
        from content.portfolio import PORTFOLIO_PROBLEMS
        from content.practical_labs import (
            ACTION_SECTION_TYPES,
            ACTION_TO_LAB,
            NAV_HELP,
            NUM_PRIMARY_ACTIONS,
            PRIMARY_ACTIONS,
            PRACTICAL_LABS,
            PRACTICAL_LAB_NAMES,
            SECONDARY_LAB_NAMES,
        )
        from content.thinking_lab import THINKING_LAB, THINKING_TOPICS
        from content.themes import THEME_NAMES
        from content.tool_guides import TOOL_GUIDES
        from simulations.labs import LAB_RUNNERS
        from simulations.registry import SIMULATION_RUNNERS
    except Exception as exc:
        print(f"IMPORT FAIL: {exc}")
        return 1

    all_runners = {**LAB_RUNNERS, **SIMULATION_RUNNERS}
    for name in PRACTICAL_LAB_NAMES:
        lab = PRACTICAL_LABS[name]
        for tool in lab.get("tools", []):
            rid = tool.get("runner_id")
            if not rid or rid not in all_runners:
                errors.append(f"Missing tool runner '{rid}' in lab '{name}'")
            elif not callable(all_runners[rid]):
                errors.append(f"Tool runner not callable: {rid}")
            if rid and rid not in TOOL_GUIDES:
                errors.append(f"Missing tool guide for '{rid}' in lab '{name}'")
            elif rid:
                guide = TOOL_GUIDES[rid]
                for key in ("what", "why", "figuring_out", "math_used", "controls", "interpret", "math_behind"):
                    if not guide.get(key):
                        errors.append(f"Tool guide '{rid}' missing key: {key}")

    if len(PRACTICAL_LAB_NAMES) != 7:
        errors.append(f"Expected 7 practical labs, got {len(PRACTICAL_LAB_NAMES)}")

    if len(SECONDARY_LAB_NAMES) != 3:
        errors.append(f"Expected 3 secondary labs, got {len(SECONDARY_LAB_NAMES)}")

    if len(PRIMARY_ACTIONS) != 7:
        errors.append(f"Expected 7 primary actions, got {len(PRIMARY_ACTIONS)}")

    if NAV_PRIMARY_ACTIONS is not PRIMARY_ACTIONS:
        errors.append("content.navigation re-export mismatch for PRIMARY_ACTIONS")

    for action in PRIMARY_ACTIONS:
        if action not in ACTION_SECTION_TYPES:
            errors.append(f"Primary action missing section type: {action}")

    lab_actions = [a for a, t in ACTION_SECTION_TYPES.items() if t == "lab"]
    if len(lab_actions) != 4:
        errors.append(f"Expected 4 primary lab actions, got {len(lab_actions)}")

    for action in lab_actions:
        if action not in ACTION_TO_LAB:
            errors.append(f"Lab action missing ACTION_TO_LAB mapping: {action}")

    if len(THINKING_TOPICS) != 11:
        errors.append(f"Expected 11 thinking topics, got {len(THINKING_TOPICS)}")

    if len(WORKSHOP_STEPS) != 8:
        errors.append(f"Expected 8 workshop steps, got {len(WORKSHOP_STEPS)}")

    if len(ANALYSIS_DIMENSIONS) != 5:
        errors.append(f"Expected 5 idea analysis dimensions, got {len(ANALYSIS_DIMENSIONS)}")

    if len(PROBLEM_BREAKDOWN_STEPS) != 8:
        errors.append(f"Expected 8 problem breakdown steps, got {len(PROBLEM_BREAKDOWN_STEPS)}")

    if len(MATHEMATICIAN_MODE_TOPICS) != 8:
        errors.append(f"Expected 8 mathematician mode topics, got {len(MATHEMATICIAN_MODE_TOPICS)}")

    if len(LAB_THINKING_PROMPTS) != 4:
        errors.append(f"Expected 4 lab thinking prompts, got {len(LAB_THINKING_PROMPTS)}")

    for key in ("title", "action", "tagline", "intro"):
        if not PROBLEM_SOLVING_LAB.get(key):
            errors.append(f"PROBLEM_SOLVING_LAB missing key: {key}")
        if not THINKING_LAB.get(key):
            errors.append(f"THINKING_LAB missing key: {key}")
        if not OPTIMIZATION_WORKSHOP.get(key):
            errors.append(f"OPTIMIZATION_WORKSHOP missing key: {key}")
        if not IDEA_ANALYSIS.get(key):
            errors.append(f"IDEA_ANALYSIS missing key: {key}")

    if "Investing & Wealth Lab" in PRACTICAL_LAB_NAMES:
        errors.append("Investing lab should not be a main section")

    for name in DOMAIN_NAMES:
        sid = DOMAINS[name].get("simulation_id")
        if not sid or sid not in SIMULATION_RUNNERS:
            errors.append(f"Missing simulation '{sid}' for domain '{name}'")

    required = {
        "title", "domain", "systems", "question", "data_needed",
        "excel", "python", "methods", "visualizations", "interview", "github_readme",
    }
    for i, proj in enumerate(PORTFOLIO_PROBLEMS):
        missing = required - proj.keys()
        if missing:
            errors.append(f"Portfolio project {i} missing keys: {missing}")

    if len(THEME_NAMES) != 6:
        errors.append(f"Expected 6 themes, got {len(THEME_NAMES)}")
    if len(MATHEMATICAL_THINKING.get("pillars", [])) != 10:
        errors.append("Mathematical Thinking should have 10 pillars")

    targets = [
        ROOT / "streamlit_app.py",
        ROOT / "components",
        ROOT / "content",
        ROOT / "simulations",
        ROOT / "data",
        ROOT / "scripts",
    ]
    for target in targets:
        ok = (
            compileall.compile_file(str(target), quiet=1)
            if target.is_file()
            else compileall.compile_dir(str(target), quiet=1)
        )
        if not ok:
            errors.append(f"py_compile failed: {target}")

    if errors:
        print("QA FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    cs_domains = sum(1 for d in DOMAINS.values() if d.get("case_studies"))
    print("QA PASSED")
    print(f"  primary actions: {len(PRIMARY_ACTIONS)}")
    print(f"  practical labs: {len(PRACTICAL_LAB_NAMES)} (secondary: {len(SECONDARY_LAB_NAMES)})")
    print(f"  thinking topics: {len(THINKING_TOPICS)}")
    print(f"  tool guides: {len(TOOL_GUIDES)}")
    print(f"  domains: {len(DOMAIN_NAMES)}")
    print(f"  simulations: {len(SIMULATION_RUNNERS)}")
    print(f"  domains with case studies: {cs_domains}")
    print(f"  portfolio projects: {len(PORTFOLIO_PROBLEMS)}")
    print(f"  themes: {len(THEME_NAMES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
