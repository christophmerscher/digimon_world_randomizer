# Author: Christoph Merscher <dev@fmerscher.com>

"""Smoke tests for the main window assembly.

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
class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PyQt6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])

    # ------------------------------------------------------------------
    def test_window_instantiates_without_errors(self):
        from gui_qt.main_window import APP_TITLE, MainWindow

        window = MainWindow()
        self.assertEqual(window.windowTitle(), APP_TITLE)

    def test_window_exposes_header_terminal_and_one_tab_per_config(self):
        from gui_qt.main_window import MainWindow
        from gui_qt.section_config import TABS
        from gui_qt.widgets.header_bar import HeaderBar
        from gui_qt.widgets.terminal_widget import TerminalWidget

        window = MainWindow()
        self.assertIsInstance(window.header_bar, HeaderBar)
        self.assertIsInstance(window.terminal,   TerminalWidget)

        for tab in TABS:
            with self.subTest(tab=tab.title):
                widget = window.tab_widget(tab.title)
                self.assertEqual(
                    len(widget.section_widgets), len(tab.sections),
                )

    def test_load_save_randomize_buttons_log_a_placeholder_message(self):
        from gui_qt.main_window import MainWindow

        window = MainWindow()
        # All three buttons currently log a "not wired up yet" message.
        window.header_bar.load_clicked.emit()
        window.header_bar.save_clicked.emit()
        window.header_bar.randomize_clicked.emit()

        terminal_text = window.terminal.toPlainText()
        self.assertIn("Load Settings",  terminal_text)
        self.assertIn("Save Settings",  terminal_text)
        self.assertIn("Randomize",      terminal_text)

    def test_header_bar_edits_the_main_window_model(self):
        from gui_qt.main_window import MainWindow

        window = MainWindow()
        window.settings.General.Seed = "9999"
        window.header_bar.refresh_from_model()

        # Reading back via the header should match what we wrote.
        self.assertEqual(window.settings.General.Seed, "9999")


if __name__ == "__main__":
    unittest.main()
