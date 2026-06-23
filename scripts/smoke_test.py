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
        from components.problem_solving import render_problem_solving_lab  # noqa: F401
        from components.problem_thinking import render_lab_thinking_gate  # noqa: F401
        from components.thinking_lab import render_thinking_topics_panel  # noqa: F401
        from components.thinking_workshop import render_thinking_workshop  # noqa: F401
        from content.thinking_workshop import (
            WORKSHOP_MODES,
            WORKSHOP_STYLES,
            classify_problem,
            get_mode_walkthrough,
            get_walkthrough,
            infer_problem_domain,
        )
        from components.math_idea_explorer import render_math_idea_explorer  # noqa: F401
        from content.math_idea_explorer import MATH_CONCEPTS, detect_concept
        from content.analyst_briefs import ANALYST_BRIEFS, get_analyst_brief
        from content.worked_examples import WORKED_EXAMPLES, get_worked_example
        from content.quant_areas import QUANT_AREAS
        from content.consultant import (
            ALTERNATIVE_MODELS,
            BRANCHING_FOLLOWUPS,
            MODEL_TEMPLATES,
            SIMILAR_PROBLEMS,
            critique_model,
        )
        from content.problem_coach import EXPERT_PERSPECTIVES, PROBLEM_LIBRARY
        from content.problem_solving import (
            ADAPTIVE_QUESTIONS,
            PROBLEM_BREAKDOWN_STEPS,
            PROBLEM_SOLVING_LAB,
        )
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
        from decision_registry import DECISION_TYPES, ENABLED_DECISION_TYPES
        from decision_router import route_imported_problem
        from decision_ocr import ocr_availability
        from decision_parser import parse_prediction_market_text as _parse_bet
        from decision_templates import assess_completeness
        from components.clipboard_image_paste import clipboard_paste_available, data_url_to_bytes
        from components.importer_ui import render_ami_importer  # noqa: F401
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
    if len(PRIMARY_ACTIONS) != 8:
        errors.append(f"Expected 8 primary actions, got {len(PRIMARY_ACTIONS)}")
    if len(ACTION_SECTION_TYPES) != 8:
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

    if len(PROBLEM_LIBRARY) != 7:
        errors.append("Problem library != 7")

    if len(EXPERT_PERSPECTIVES) != 6:
        errors.append("Expert perspectives != 6")

    if len(MODEL_TEMPLATES) < 5:
        errors.append("Model templates < 5")

    if len(BRANCHING_FOLLOWUPS) < 5:
        errors.append("Branching followups < 5")

    if len(SIMILAR_PROBLEMS) < 5:
        errors.append("Similar problems < 5")

    if len(ALTERNATIVE_MODELS) < 5:
        errors.append("Alternative models < 5")

    if len(ANALYST_BRIEFS) < 5:
        errors.append("Analyst briefs < 5")

    if len(QUANT_AREAS) != 7:
        errors.append("Quant areas != 7")

    if len(WORKED_EXAMPLES) < 28:
        errors.append("Worked examples < 28")

    if not get_worked_example(
        "Is this +150 bet worth it if I think the true win probability is 45%?", "betting"
    ):
        errors.append("get_worked_example failed")

    if len(MATH_CONCEPTS) < 14:
        errors.append("Math concepts < 10")

    if detect_concept("expected value").get("id") != "expected_value":
        errors.append("detect_concept failed")

    if not ANALYST_BRIEFS.get("default", {}).get("analyst_steps"):
        errors.append("default analyst brief invalid")

    if len(ADAPTIVE_QUESTIONS) < 8:
        errors.append("Adaptive question sets < 8")

    if len(PROBLEM_BREAKDOWN_STEPS) != 8:
        errors.append("Problem breakdown steps != 8")

    for key in ("title", "action", "tagline", "intro"):
        if not PROBLEM_SOLVING_LAB.get(key):
            errors.append(f"PROBLEM_SOLVING_LAB missing key: {key}")

    if "problem_solving" not in ACTION_SECTION_TYPES.values():
        errors.append("Missing problem_solving section type")

    if len(THINKING_TOPICS) != 11:
        errors.append("Thinking Lab topics != 11")

    if len(WORKSHOP_MODES) != 6:
        errors.append(f"Expected 6 workshop modes, got {len(WORKSHOP_MODES)}")

    if not get_mode_walkthrough("Is this bet worth it at +150?", "abstraction").get("deeper_structure"):
        errors.append("get_mode_walkthrough failed")
    if len(WORKSHOP_STYLES) != 6:
        errors.append(f"Expected 6 workshop styles, got {len(WORKSHOP_STYLES)}")

    domain = infer_problem_domain("Is this sports bet worth making at +150?")
    if domain not in ("betting", "sports"):
        errors.append(f"infer_problem_domain betting/sports failed: {domain}")

    wt = get_walkthrough("betting", "abstraction")
    if not wt.get("structures") and not wt.get("matters"):
        errors.append("get_walkthrough betting/abstraction empty")

    if classify_problem("test").get("domain_key") != infer_problem_domain("test"):
        errors.append("classify_problem domain_key mismatch")

    for i, p in enumerate(PORTFOLIO_PROBLEMS):
        if not p.get("question"):
            errors.append(f"Portfolio {i} missing question")

    if len(list_sources()) < 6:
        errors.append("Expected at least 6 data source modules")

    req_text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    if "supabase>=" not in req_text:
        errors.append("requirements.txt must include supabase>=2.0.0 for Streamlit Cloud auth")
    if "pytesseract" not in req_text:
        errors.append("requirements.txt must include pytesseract for screenshot OCR")
    if "Pillow" not in req_text:
        errors.append("requirements.txt must include Pillow for screenshot OCR")
    packages_file = ROOT / "packages.txt"
    if not packages_file.is_file():
        errors.append("packages.txt missing — needed for tesseract-ocr on Streamlit Cloud")
    elif "tesseract-ocr" not in packages_file.read_text(encoding="utf-8"):
        errors.append("packages.txt must include tesseract-ocr")
    try:
        import supabase  # noqa: F401
    except ImportError:
        errors.append("supabase package not installed in this environment (required for deploy)")
    try:
        import pytesseract  # noqa: F401
        from PIL import Image  # noqa: F401
    except ImportError:
        errors.append("pytesseract/Pillow not installed in this environment (required for OCR)")

    if "prediction_market_bet" not in ENABLED_DECISION_TYPES:
        errors.append("prediction_market_bet should be enabled in Phase 0")
    sample = "Will team X win?\nYes: 45¢\nNo: 55¢"
    route = route_imported_problem(sample)
    if route.get("decision_type") != "prediction_market_bet":
        errors.append("Kalshi-style text should route to prediction_market_bet")
    fields = _parse_bet(sample)
    if fields.get("price") != 45.0:
        errors.append(f"Expected yes price 45, got {fields.get('price')}")
    from decision_math import enrich_bet_fields

    complete_fields = enrich_bet_fields({**fields, "stake": 100, "user_probability": 0.50, "contract_side": "Yes"})
    if not assess_completeness("prediction_market_bet", complete_fields).get("can_solve"):
        errors.append("Complete bet fields should be solvable")

    matchup = "Team A 50%\nTeam B 50%\nTeam A 1.95x\nVolume: 10,000"
    mfields = _parse_bet(matchup)
    if not mfields.get("team_options"):
        errors.append("Matchup text should extract team_options")
    if mfields.get("volume") != 10000.0:
        errors.append(f"Expected volume 10000, got {mfields.get('volume')}")
    ocr_info = ocr_availability()
    if "ready" not in ocr_info:
        errors.append("ocr_availability should return ready flag")
    if not ocr_info.get("pytesseract_installed"):
        errors.append("pytesseract should be installed after requirements update")
    clip_info = clipboard_paste_available()
    if not clip_info.get("paste_zone"):
        errors.append("clipboard paste zone should be available")
    sample_png = "data:image/png;base64,iVBORw0KGgo="
    if not data_url_to_bytes(sample_png)[1]:
        errors.append("data_url_to_bytes should parse mime")

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
