"""Saved Session sidebar must render at startup like other suite apps."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STREAMLIT_APP = REPO_ROOT / "streamlit_app.py"


def test_saved_session_rendered_at_startup() -> None:
    source = STREAMLIT_APP.read_text(encoding="utf-8")
    assert "render_reset_controls(" in source
    reset_idx = source.index("render_reset_controls(")
    sidebar_title_idx = source.index('st.sidebar.title("Applied Mathematical Intelligence")')
    assert reset_idx < sidebar_title_idx, "Reset controls should render before main sidebar nav"


def test_saved_session_expander_title() -> None:
    source = (REPO_ROOT / "suite_user_persistence.py").read_text(encoding="utf-8")
    assert 'expander("Saved Session"' in source
