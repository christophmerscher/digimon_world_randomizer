# Author: Christoph Merscher <dev@fmerscher.com>

"""Tests for the dark-theme bootstrap.

The widget-level visual tweaks land in later commits; for now we just
verify the theme module assembles the right primitives without raising.
Skipped without PyQt6.
"""

from __future__ import annotations

import os
import unittest


try:
    import PyQt6  # noqa: F401
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class PaletteValueTests(unittest.TestCase):
    """Pure-data checks that don't need PyQt6 at all."""

    def test_dark_palette_fields_are_hex_strings(self):
        from dataclasses import fields

        from gui_qt.theme.palette import DARK_PALETTE

        for f in fields(DARK_PALETTE):
            value = getattr(DARK_PALETTE, f.name)
            with self.subTest(field=f.name):
                self.assertIsInstance(value, str)
                self.assertTrue(value.startswith("#"))
                # 7 chars = "#RRGGBB"
                self.assertEqual(len(value), 7)


@unittest.skipUnless(PYQT6_AVAILABLE, "PyQt6 not installed")
class ApplyThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PyQt6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])

    def test_apply_theme_sets_fusion_style_and_installs_palette(self):
        from gui_qt.theme import DARK_PALETTE, apply_theme

        apply_theme(self._app)

        self.assertEqual(self._app.style().objectName().lower(), "fusion")
        # Window background colour must match the palette's background.
        from PyQt6.QtGui import QColor, QPalette

        bg = self._app.palette().color(QPalette.ColorRole.Window)
        self.assertEqual(bg, QColor(DARK_PALETTE.background))

    def test_apply_theme_sets_a_non_empty_stylesheet(self):
        from gui_qt.theme import apply_theme

        apply_theme(self._app)
        self.assertGreater(len(self._app.styleSheet()), 0)


if __name__ == "__main__":
    unittest.main()
