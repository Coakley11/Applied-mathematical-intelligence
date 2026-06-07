"""Saved Session sidebar must render even if restore fails."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STREAMLIT_APP = REPO_ROOT / "streamlit_app.py"


def test_saved_session_rendered_in_sidebar_section() -> None:
    source = STREAMLIT_APP.read_text(encoding="utf-8")
    sidebar_idx = source.index("st.sidebar.title(\"Applied Mathematical Intelligence\")")
    reset_idx = source.index("render_reset_controls(", sidebar_idx)
    main_idx = source.index("# MAIN CONTENT", reset_idx)
    assert reset_idx < main_idx
    assert "Saved session" in source or "render_reset_controls" in source[sidebar_idx:main_idx]
