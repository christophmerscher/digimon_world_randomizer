# Author: Christoph Merscher <dev@fmerscher.com>

"""Tests for the Load Settings / Save Settings dialogs.

The native :class:`QFileDialog` is patched out so the tests never open
a real dialog. Skipped without PyQt6.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


try:
    import PyQt6  # noqa: F401
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@unittest.skipUnless(PYQT6_AVAILABLE, "PyQt6 not installed")
class LoadSaveDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PyQt6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])

    # ------------------------------------------------------------------
    def _build_window(self):
        from gui_qt.main_window import MainWindow

        return MainWindow()

    def _write_settings_file(self, payload: dict) -> Path:
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8",
        )
        tmp.write(json.dumps(payload))
        tmp.close()
        self.addCleanup(lambda: os.unlink(tmp.name))
        return Path(tmp.name)

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def test_load_replaces_model_state_and_rebuilds_ui(self):
        window = self._build_window()
        path = self._write_settings_file({
            "general": {
                "InputFile":  "/data/rom.bin",
                "OutputFile": "out.bin",
                "LogLevel":   "race",
                "Seed":       "777",
                "Hash":       "",
            },
            "digimon": {
                "Enabled": True, "DroppedItem": True, "DropRate": False,
                "MatchValue": False, "ValuableItemCutoff": 1000,
            },
        })

        with patch(
            "gui_qt.main_window.QFileDialog.getOpenFileName",
            return_value=(str(path), "Settings file (*.json)"),
        ):
            window.header_bar.load_clicked.emit()

        self.assertEqual(window.settings.General.Seed,     "777")
        self.assertEqual(window.settings.General.LogLevel, "race")
        self.assertTrue(window.settings.Digimon.Enabled)
        self.assertTrue(window.settings.Digimon.DroppedItem)
        self.assertIn("Loaded settings", window.terminal.toPlainText())

    def test_load_cancel_keeps_existing_settings(self):
        window = self._build_window()
        before_seed = window.settings.General.Seed

        with patch(
            "gui_qt.main_window.QFileDialog.getOpenFileName",
            return_value=("", ""),
        ):
            window.header_bar.load_clicked.emit()

        self.assertEqual(window.settings.General.Seed, before_seed)
        self.assertEqual(window.terminal.toPlainText(), "")

    def test_load_reports_error_for_invalid_json(self):
        window = self._build_window()

        bad = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8",
        )
        bad.write("{ not json")
        bad.close()
        self.addCleanup(lambda: os.unlink(bad.name))

        with patch(
            "gui_qt.main_window.QFileDialog.getOpenFileName",
            return_value=(bad.name, ""),
        ):
            window.header_bar.load_clicked.emit()

        self.assertIn("Failed to load settings", window.terminal.toPlainText())

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def test_save_writes_a_valid_json_payload_to_disk(self):
        window = self._build_window()
        window.settings.General.InputFile  = "/tmp/rom.bin"
        window.settings.General.OutputFile = "rand.bin"
        window.settings.Digimon.Enabled    = True
        window.settings.Patches.SpawnRate  = 50

        out = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        out.close()
        self.addCleanup(lambda: os.unlink(out.name))

        with patch(
            "gui_qt.main_window.QFileDialog.getSaveFileName",
            return_value=(out.name, "Settings file (*.json)"),
        ):
            window.header_bar.save_clicked.emit()

        data = json.loads(Path(out.name).read_text(encoding="utf-8"))
        self.assertEqual(data["general"]["Seed"],     "")
        self.assertTrue(data["digimon"]["Enabled"])
        self.assertEqual(data["patches"]["SpawnRate"], 50)
        # Hash field should be populated after to_json().
        self.assertTrue(data["general"]["Hash"])
        self.assertIn("Saved settings", window.terminal.toPlainText())

    def test_save_cancel_writes_nothing(self):
        window = self._build_window()

        with patch(
            "gui_qt.main_window.QFileDialog.getSaveFileName",
            return_value=("", ""),
        ):
            window.header_bar.save_clicked.emit()

        self.assertEqual(window.terminal.toPlainText(), "")


if __name__ == "__main__":
    unittest.main()
