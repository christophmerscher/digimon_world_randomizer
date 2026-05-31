# Author: Christoph Merscher <dev@fmerscher.com>

"""Tests for the header bar widget.

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
class HeaderBarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PyQt6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])

    def _build_widget(self):
        from gui_qt.settings_model import SettingsModel
        from gui_qt.widgets.header_bar import HeaderBar

        model = SettingsModel()
        bar = HeaderBar(model.General)
        return model, bar

    def test_initial_radios_reflect_default_log_level(self):
        model, bar = self._build_widget()
        # Default LogLevel is "casual".
        self.assertTrue(bar._log_radios["casual"].isChecked())
        self.assertFalse(bar._log_radios["full"].isChecked())
        self.assertFalse(bar._log_radios["race"].isChecked())

    def test_output_filename_writes_back_to_model(self):
        from PyQt6.QtWidgets import QLineEdit

        model, bar = self._build_widget()
        edits = bar.findChildren(QLineEdit)
        # Two QLineEdits: the FileSelectWidget's read-only one + the output one.
        output_edit = next(e for e in edits if not e.isReadOnly())
        # Seed has its own edit too; the output edit is the one with the matching placeholder.
        output_edit = next(
            e for e in edits if e.placeholderText() == "Destination file name..."
        )

        output_edit.setText("rand.bin")
        self.assertEqual(model.General.OutputFile, "rand.bin")

    def test_seed_writes_back_to_model(self):
        from PyQt6.QtWidgets import QLineEdit

        model, bar = self._build_widget()
        seed_edit = next(
            e for e in bar.findChildren(QLineEdit)
            if e.placeholderText() == "Random"
        )
        seed_edit.setText("42")
        self.assertEqual(model.General.Seed, "42")

    def test_log_level_radio_change_writes_back_to_model(self):
        model, bar = self._build_widget()
        bar._log_radios["race"].setChecked(True)
        self.assertEqual(model.General.LogLevel, "race")

    def test_action_buttons_emit_their_signals(self):
        from PyQt6.QtWidgets import QPushButton

        _, bar = self._build_widget()
        buttons = {b.text(): b for b in bar.findChildren(QPushButton)
                   if b.text() in {"Load Settings", "Save Settings", "Randomize"}}

        captured: list[str] = []
        bar.load_clicked.connect(lambda: captured.append("load"))
        bar.save_clicked.connect(lambda: captured.append("save"))
        bar.randomize_clicked.connect(lambda: captured.append("randomize"))

        buttons["Load Settings"].click()
        buttons["Save Settings"].click()
        buttons["Randomize"].click()

        self.assertEqual(captured, ["load", "save", "randomize"])

    def test_set_busy_disables_inputs_and_renames_randomize(self):
        from PyQt6.QtWidgets import QPushButton

        _, bar = self._build_widget()
        randomize = next(
            b for b in bar.findChildren(QPushButton)
            if b.text() in {"Randomize", "Randomizing..."}
        )

        bar.set_busy(True)
        self.assertFalse(randomize.isEnabled())
        self.assertEqual(randomize.text(), "Randomizing...")

        bar.set_busy(False)
        self.assertTrue(randomize.isEnabled())
        self.assertEqual(randomize.text(), "Randomize")

    def test_randomize_button_carries_primary_object_name_for_accent_styling(self):
        from PyQt6.QtWidgets import QPushButton

        _, bar = self._build_widget()
        randomize = next(
            b for b in bar.findChildren(QPushButton)
            if b.text() in {"Randomize", "Randomizing..."}
        )
        self.assertEqual(randomize.objectName(), "primaryButton")

    def test_refresh_from_model_updates_every_input(self):
        from PyQt6.QtWidgets import QLineEdit

        model, bar = self._build_widget()
        model.General.InputFile  = "/tmp/rom.bin"
        model.General.OutputFile = "out.bin"
        model.General.Seed       = "1234"
        model.General.LogLevel   = "race"
        bar.refresh_from_model()

        output_edit = next(
            e for e in bar.findChildren(QLineEdit)
            if e.placeholderText() == "Destination file name..."
        )
        seed_edit = next(
            e for e in bar.findChildren(QLineEdit)
            if e.placeholderText() == "Random"
        )

        self.assertEqual(output_edit.text(), "out.bin")
        self.assertEqual(seed_edit.text(), "1234")
        self.assertTrue(bar._log_radios["race"].isChecked())


if __name__ == "__main__":
    unittest.main()
