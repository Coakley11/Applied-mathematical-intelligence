"""Legacy lab module — redirects to practical_labs."""

from components.practical_labs import render_action_hub as render_labs_hub
from components.practical_labs import render_practical_lab as render_lab_page

__all__ = ["render_labs_hub", "render_lab_page"]
