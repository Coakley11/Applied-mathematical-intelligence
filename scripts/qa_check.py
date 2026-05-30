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
        from content.mathematical_thinking import MATHEMATICAL_THINKING
        from content.portfolio import PORTFOLIO_PROBLEMS
        from content.practical_labs import PRACTICAL_LABS, PRACTICAL_LAB_NAMES
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
    print(f"  practical labs: {len(PRACTICAL_LAB_NAMES)}")
    print(f"  tool guides: {len(TOOL_GUIDES)}")
    print(f"  domains: {len(DOMAIN_NAMES)}")
    print(f"  simulations: {len(SIMULATION_RUNNERS)}")
    print(f"  domains with case studies: {cs_domains}")
    print(f"  portfolio projects: {len(PORTFOLIO_PROBLEMS)}")
    print(f"  themes: {len(THEME_NAMES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
