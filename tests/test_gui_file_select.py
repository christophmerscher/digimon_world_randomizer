# Author: Christoph Merscher <dev@fmerscher.com>

"""Tests for the file picker widget.

Skipped without PyQt6. Patches :meth:`QFileDialog.getOpenFileName` to
avoid opening a real native dialog in the test process.
"""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch


try:
    import PyQt6  # noqa: F401
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@unittest.skipUnless(PYQT6_AVAILABLE, "PyQt6 not installed")
class FileSelectWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PyQt6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])

    # ------------------------------------------------------------------
    def _build_widget(self):
        from gui_qt.widgets.file_select import FileSelectWidget

        return FileSelectWidget(
            placeholder="Pick a ROM",
            dialog_title="Select ROM",
        )

    def test_starts_empty_with_placeholder(self):
        from PyQt6.QtWidgets import QLineEdit

        widget = self._build_widget()
        line_edit = widget.findChild(QLineEdit)
        self.assertEqual(line_edit.text(), "")
        self.assertEqual(line_edit.placeholderText(), "Pick a ROM")

    def test_set_path_updates_line_edit_silently(self):
        from PyQt6.QtWidgets import QLineEdit

        widget = self._build_widget()
        emitted: list[str] = []
        widget.path_changed.connect(emitted.append)

        widget.set_path("/tmp/rom.bin")
        self.assertEqual(widget.findChild(QLineEdit).text(), "/tmp/rom.bin")
        self.assertEqual(widget.path(), "/tmp/rom.bin")
        # set_path() must NOT trigger the signal — only user picks do.
        self.assertEqual(emitted, [])

    def test_browse_button_opens_dialog_and_emits_on_selection(self):
        from PyQt6.QtWidgets import QPushButton

        widget = self._build_widget()
        emitted: list[str] = []
        widget.path_changed.connect(emitted.append)

        button = widget.findChild(QPushButton)
        with patch(
            "gui_qt.widgets.file_select.QFileDialog.getOpenFileName",
            return_value=("/data/rom.bin", "ROM image (*.bin)"),
        ):
            button.click()

        self.assertEqual(widget.path(), "/data/rom.bin")
        self.assertEqual(emitted, ["/data/rom.bin"])

    def test_cancelling_dialog_keeps_previous_path(self):
        from PyQt6.QtWidgets import QPushButton

        widget = self._build_widget()
        widget.set_path("/keep/this.bin")
        emitted: list[str] = []
        widget.path_changed.connect(emitted.append)

        button = widget.findChild(QPushButton)
        with patch(
            "gui_qt.widgets.file_select.QFileDialog.getOpenFileName",
            return_value=("", ""),
        ):
            button.click()

        self.assertEqual(widget.path(), "/keep/this.bin")
        self.assertEqual(emitted, [])


if __name__ == "__main__":
    unittest.main()
