"""OCR for screenshot/image import — Tesseract via pytesseract; never crashes."""

from __future__ import annotations

import hashlib
import io
import os
import shutil
from typing import Any

OCR_UNAVAILABLE_USER_MESSAGE = (
    "Screenshot received, but OCR is unavailable. Paste or correct visible text below."
)

_TESSERACT_CANDIDATES = (
    "/usr/bin/tesseract",
    "/usr/local/bin/tesseract",
)


def resolve_tesseract_cmd() -> str | None:
    """Find the tesseract executable (Streamlit Cloud, Linux, Windows, macOS)."""
    env = str(os.environ.get("TESSERACT_CMD") or "").strip()
    if env and os.path.isfile(env):
        return env
    found = shutil.which("tesseract")
    if found:
        return found
    for path in _TESSERACT_CANDIDATES:
        if os.path.isfile(path):
            return path
    return None


def _pytesseract_installed() -> bool:
    try:
        import pytesseract  # noqa: F401

        return True
    except ImportError:
        return False


def _pillow_installed() -> bool:
    try:
        from PIL import Image  # noqa: F401

        return True
    except ImportError:
        return False


def ocr_availability() -> dict[str, Any]:
    """Report OCR readiness: Python packages + tesseract binary."""
    engines: list[str] = []
    if _pillow_installed():
        engines.append("pillow")
    if _pytesseract_installed():
        engines.append("pytesseract")

    tesseract_cmd = resolve_tesseract_cmd() if _pytesseract_installed() else None
    ready = bool(_pytesseract_installed() and _pillow_installed() and tesseract_cmd)

    note = "OCR ready — pasted/uploaded screenshots will be read automatically."
    if not _pytesseract_installed() or not _pillow_installed():
        note = (
            "OCR Python packages missing (pytesseract, Pillow). "
            + OCR_UNAVAILABLE_USER_MESSAGE
        )
    elif not tesseract_cmd:
        note = (
            "Tesseract binary not found (add tesseract-ocr to packages.txt on Streamlit Cloud). "
            + OCR_UNAVAILABLE_USER_MESSAGE
        )

    return {
        "available": ready,
        "ready": ready,
        "pytesseract_installed": _pytesseract_installed(),
        "pillow_installed": _pillow_installed(),
        "tesseract_available": bool(tesseract_cmd),
        "tesseract_cmd": tesseract_cmd or "",
        "engines": engines,
        "note": note,
    }


def ocr_fallback_message(result: dict[str, Any] | None = None) -> str:
    """User-facing message when OCR cannot produce text."""
    if not result:
        return OCR_UNAVAILABLE_USER_MESSAGE
    if result.get("success"):
        return ""
    err = str(result.get("error") or "").strip()
    if err and "Screenshot received" in err:
        return err
    if err:
        return f"{OCR_UNAVAILABLE_USER_MESSAGE} ({err})"
    return OCR_UNAVAILABLE_USER_MESSAGE


def image_metadata(image_bytes: bytes, *, filename: str = "", mime: str = "") -> dict[str, Any]:
    meta: dict[str, Any] = {
        "filename": filename or "upload",
        "mime": mime or "application/octet-stream",
        "size_bytes": len(image_bytes),
        "sha256": hashlib.sha256(image_bytes).hexdigest()[:16],
    }
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes))
        meta["width"] = img.width
        meta["height"] = img.height
        meta["format"] = str(img.format or "")
    except Exception:
        pass
    return meta


def _configure_pytesseract() -> tuple[Any, str]:
    import pytesseract

    cmd = resolve_tesseract_cmd()
    if not cmd:
        raise FileNotFoundError(
            "tesseract executable not found — install tesseract-ocr (packages.txt on Streamlit Cloud)."
        )
    pytesseract.pytesseract.tesseract_cmd = cmd
    return pytesseract, cmd


def extract_text_from_image(image_bytes: bytes, *, filename: str = "", mime: str = "") -> dict[str, Any]:
    """
    Run Tesseract OCR on image bytes. Returns text, success flag, engine info, and metadata.

    Never raises — callers get a safe fallback dict.
    """
    meta = image_metadata(image_bytes, filename=filename, mime=mime)
    result: dict[str, Any] = {
        "text": "",
        "success": False,
        "engine": "none",
        "error": "",
        "image_meta": meta,
        "tesseract_cmd": "",
    }

    if not image_bytes:
        result["error"] = OCR_UNAVAILABLE_USER_MESSAGE
        return result

    if not _pillow_installed() or not _pytesseract_installed():
        missing = []
        if not _pillow_installed():
            missing.append("Pillow")
        if not _pytesseract_installed():
            missing.append("pytesseract")
        result["error"] = (
            f"{OCR_UNAVAILABLE_USER_MESSAGE} Missing: {', '.join(missing)}."
        )
        return result

    try:
        from PIL import Image

        pytesseract, cmd = _configure_pytesseract()
        result["tesseract_cmd"] = cmd

        img = Image.open(io.BytesIO(image_bytes))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        text = pytesseract.image_to_string(img, lang="eng")
        cleaned = str(text or "").strip()
        result["text"] = cleaned
        result["engine"] = "pytesseract"
        result["success"] = bool(cleaned)
        if not cleaned:
            result["error"] = (
                "OCR returned empty text — try a sharper screenshot or paste text manually."
            )
    except ImportError as exc:
        result["error"] = f"{OCR_UNAVAILABLE_USER_MESSAGE} ({exc})"
    except FileNotFoundError as exc:
        result["error"] = f"{OCR_UNAVAILABLE_USER_MESSAGE} ({exc})"
    except Exception as exc:
        result["error"] = f"{OCR_UNAVAILABLE_USER_MESSAGE} ({exc})"

    return result
