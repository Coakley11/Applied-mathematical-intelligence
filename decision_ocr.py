"""Optional OCR for screenshot/image import — never crashes if unavailable."""

from __future__ import annotations

import hashlib
from typing import Any

_OCR_ENGINES: list[str] = []


def ocr_availability() -> dict[str, Any]:
    """Report which OCR backends are importable."""
    engines: list[str] = []
    try:
        import pytesseract  # noqa: F401

        engines.append("pytesseract")
    except ImportError:
        pass
    try:
        from PIL import Image  # noqa: F401

        if "pillow" not in engines:
            engines.append("pillow")
    except ImportError:
        pass
    return {
        "available": bool(engines) and "pytesseract" in engines,
        "engines": engines,
        "note": (
            "OCR requires pytesseract + Pillow and a system Tesseract install. "
            "Without it, paste visible text manually."
        ),
    }


def image_metadata(image_bytes: bytes, *, filename: str = "", mime: str = "") -> dict[str, Any]:
    meta: dict[str, Any] = {
        "filename": filename or "upload",
        "mime": mime or "application/octet-stream",
        "size_bytes": len(image_bytes),
        "sha256": hashlib.sha256(image_bytes).hexdigest()[:16],
    }
    try:
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_bytes))
        meta["width"] = img.width
        meta["height"] = img.height
        meta["format"] = str(img.format or "")
    except Exception:
        pass
    return meta


def extract_text_from_image(image_bytes: bytes, *, filename: str = "", mime: str = "") -> dict[str, Any]:
    """
    Run OCR on image bytes. Returns text, success flag, engine info, and metadata.

    Never raises — callers get a safe fallback dict.
    """
    meta = image_metadata(image_bytes, filename=filename, mime=mime)
    result: dict[str, Any] = {
        "text": "",
        "success": False,
        "engine": "none",
        "error": "",
        "image_meta": meta,
    }

    try:
        import io

        from PIL import Image
        import pytesseract

        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img)
        cleaned = str(text or "").strip()
        result["text"] = cleaned
        result["engine"] = "pytesseract"
        result["success"] = bool(cleaned)
        if not cleaned:
            result["error"] = "OCR returned empty text — try manual paste or a clearer screenshot."
    except ImportError as exc:
        result["error"] = (
            f"OCR not installed ({exc}). Paste the visible market text below."
        )
    except Exception as exc:
        result["error"] = f"OCR failed: {exc}. Paste the visible text manually."

    return result
