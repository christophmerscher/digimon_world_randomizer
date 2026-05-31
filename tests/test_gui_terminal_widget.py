# Author: Christoph Merscher <dev@fmerscher.com>

"""Tests for the terminal output widget.

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


@unittest.skipUnless(PYQT6_AVAILABLE, "PyQt6 not installed")
class TerminalWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PyQt6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])

    def test_starts_empty_and_read_only(self):
        from gui_qt.widgets.terminal_widget import TerminalWidget

        widget = TerminalWidget()
        self.assertTrue(widget.isReadOnly())
        self.assertEqual(widget.toPlainText(), "")

    def test_append_line_writes_visible_text(self):
        from gui_qt.widgets.terminal_widget import LineKind, TerminalWidget

        widget = TerminalWidget()
        widget.append_line("hello world", LineKind.INFO)
        widget.append_line("oh no", LineKind.ERROR)
        widget.append_line("change applied", LineKind.CHANGE)

        plain = widget.toPlainText()
        self.assertIn("hello world", plain)
        self.assertIn("oh no", plain)
        self.assertIn("change applied", plain)

    def test_html_special_chars_are_escaped(self):
        from gui_qt.widgets.terminal_widget import LineKind, TerminalWidget

        widget = TerminalWidget()
        widget.append_line("<script>", LineKind.INFO)

        # The script tag must NOT be parsed as HTML.
        self.assertIn("<script>", widget.toPlainText())
        # And the document HTML should contain the escaped form.
        self.assertIn("&lt;script&gt;", widget.toHtml())

    def test_error_lines_use_a_different_colour_than_info(self):
        from gui_qt.widgets.terminal_widget import LineKind, TerminalWidget

        widget = TerminalWidget()
        widget.append_line("err", LineKind.ERROR)
        err_html = widget.toHtml()

        widget.clear_output()
        widget.append_line("info", LineKind.INFO)
        info_html = widget.toHtml()

        self.assertNotEqual(err_html, info_html)

    def test_clear_output_resets_the_buffer(self):
        from gui_qt.widgets.terminal_widget import LineKind, TerminalWidget

        widget = TerminalWidget()
        widget.append_line("noise", LineKind.INFO)
        self.assertNotEqual(widget.toPlainText(), "")

        widget.clear_output()
        self.assertEqual(widget.toPlainText(), "")


if __name__ == "__main__":
    unittest.main()
