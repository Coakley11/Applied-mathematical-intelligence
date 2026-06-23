"""Tests for clipboard image paste helpers."""

from __future__ import annotations

import base64
import unittest

from components.clipboard_image_paste import (
    clipboard_paste_available,
    data_url_to_bytes,
    extension_for_mime,
    image_bytes_meta,
)


class TestClipboardImagePaste(unittest.TestCase):
    def test_data_url_roundtrip(self) -> None:
        raw = b"\x89PNG\r\n\x1a\n"
        b64 = base64.b64encode(raw).decode("ascii")
        data_url = f"data:image/png;base64,{b64}"
        decoded, mime = data_url_to_bytes(data_url)
        self.assertEqual(decoded, raw)
        self.assertEqual(mime, "image/png")

    def test_invalid_data_url_returns_empty(self) -> None:
        decoded, mime = data_url_to_bytes("not-a-data-url")
        self.assertEqual(decoded, b"")
        self.assertEqual(mime, "")

    def test_extension_for_mime(self) -> None:
        self.assertEqual(extension_for_mime("image/png"), "png")
        self.assertEqual(extension_for_mime("image/jpeg"), "jpg")

    def test_image_bytes_meta(self) -> None:
        meta = image_bytes_meta(b"abc", filename="clip.png", mime="image/png", source="clipboard_paste")
        self.assertEqual(meta["source"], "clipboard_paste")
        self.assertEqual(meta["size_bytes"], 3)

    def test_clipboard_paste_available(self) -> None:
        info = clipboard_paste_available()
        self.assertTrue(info["paste_zone"])
        self.assertIn("paste_button", info)


if __name__ == "__main__":
    unittest.main()
