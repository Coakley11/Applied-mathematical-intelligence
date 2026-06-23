"""Clipboard image paste for AMI Importer — Ctrl+V zone + optional paste button."""

from __future__ import annotations

import base64
import io
import os
from typing import Any

import streamlit.components.v1 as components

_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "clipboard_paste_frontend")

_clipboard_paste = components.declare_component(
    "ami_clipboard_image_paste",
    path=_FRONTEND_DIR,
)


def clipboard_paste_available() -> dict[str, Any]:
    """Report clipboard paste capabilities."""
    button_ok = False
    try:
        import streamlit_paste_button  # noqa: F401

        button_ok = True
    except ImportError:
        pass
    return {
        "paste_zone": True,
        "paste_button": button_ok,
        "note": (
            "Use the paste zone: Snipping Tool → Copy → click box → Ctrl+V. "
            "Requires HTTPS (Streamlit Cloud) or localhost."
        ),
    }


def render_clipboard_paste_zone(
    *,
    label: str = "Paste screenshot here (Ctrl+V)",
    key: str = "ami_clipboard_paste",
) -> str | None:
    """
    Render focusable paste zone. Returns data-URL string when user pastes/drops an image.
    """
    try:
        result = _clipboard_paste(label=label, key=key, default=None)
    except Exception:
        return None
    if result is None or result == "":
        return None
    return str(result)


def render_paste_button(*, key: str = "ami_paste_button") -> tuple[bytes, str, str] | None:
    """
    Optional streamlit-paste-button fallback. Returns (bytes, mime, filename) or None.
    """
    try:
        from streamlit_paste_button import paste_image_button
    except ImportError:
        return None

    try:
        paste_result = paste_image_button(
            label="📋 Paste from clipboard (button)",
            background_color="#6366f1",
            hover_background_color="#4f46e5",
            key=key,
        )
    except Exception:
        return None

    if paste_result is None or paste_result.image_data is None:
        return None

    img = paste_result.image_data
    buf = io.BytesIO()
    fmt = str(getattr(img, "format", None) or "PNG")
    img.save(buf, format=fmt)
    mime = f"image/{fmt.lower()}"
    return buf.getvalue(), mime, f"clipboard-paste.{fmt.lower()}"


def data_url_to_bytes(data_url: str) -> tuple[bytes, str]:
    """Decode a data:image/...;base64,... URL to bytes and mime type."""
    raw = str(data_url or "").strip()
    if not raw.startswith("data:") or "," not in raw:
        return b"", ""
    header, payload = raw.split(",", 1)
    mime = header.split(";")[0].replace("data:", "").strip() or "image/png"
    try:
        return base64.b64decode(payload), mime
    except (ValueError, base64.binascii.Error):
        return b"", ""


def extension_for_mime(mime: str) -> str:
    mapping = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/webp": "webp",
        "image/gif": "gif",
    }
    return mapping.get(mime.lower(), "png")


def image_bytes_meta(image_bytes: bytes, *, filename: str, mime: str, source: str) -> dict[str, Any]:
    return {
        "filename": filename,
        "mime": mime,
        "size_bytes": len(image_bytes),
        "source": source,
    }
