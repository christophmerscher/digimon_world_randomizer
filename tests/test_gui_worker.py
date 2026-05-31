# Author: Christoph Merscher <dev@fmerscher.com>

"""Tests for the background randomizer worker.

The worker's :meth:`run` method is invoked directly on the test thread
(not via :meth:`start`) so we can assert on the captured signals
without dealing with QThread scheduling. The real
:func:`digimon.app.run` is monkey-patched out so we don't need a ROM
fixture; one test does drive a real ``SettingsError`` path through the
loader to verify the user-error reporting branch end to end.

Skipped without PyQt6.
"""

from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch


try:
    import PyQt6  # noqa: F401
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _valid_settings_json() -> str:
    """Minimum settings string that passes the schema validator."""

    return json.dumps({
        "general": {
            "InputFile": "/tmp/in.bin", "OutputFile": "/tmp/out.bin",
            "LogLevel": "casual", "Seed": "1", "Hash": "",
        },
        "digimon":     {"Enabled": False, "DroppedItem": False, "DropRate": False,
                        "MatchValue": False, "ValuableItemCutoff": 1000},
        "techs":       {"Enabled": False, "RandomizationMode": "random",
                        "Power": False, "Cost": False, "Accuracy": False,
                        "Effect": False, "EffectChance": False,
                        "TypeEffectiveness": False},
        "starter":     {"Enabled": False, "UseWeakestTech": False,
                        "Digimon": "Random", "Fresh": False, "InTraining": False,
                        "Rookie": True, "Champion": False, "Ultimate": False},
        "recruitment": {"Enabled": False},
        "chests":      {"Enabled": False, "AllowEvolutionItems": False},
        "tokomon":     {"Enabled": False, "ConsumableOnly": False},
        "techGifts":   {"Enabled": False},
        "mapItems":    {"Enabled": False, "FoodOnly": False, "MatchValue": False,
                        "ValuableItemCutoff": 1000},
        "evolution":   {"Enabled": False, "Requirements": False,
                        "SpecialEvolutions": False, "ObtainAllMode": False},
        "patches":     {"Enabled": False, "EvoItemStatGain": False,
                        "QuestItemsDroppable": False, "BrainTrainTierOne": False,
                        "JukeboxGlitch": False, "IncreaseLearnChance": False,
                        "SpawnRateEnabled": False, "SpawnRate": 50,
                        "ShowHashIntro": False, "SkipIntro": False,
                        "Woah": False, "Gabu": False, "Softlock": False,
                        "UnlockAreas": False, "UnrigSlots": False,
                        "LearnMoveAndCommand": False, "FixDVChips": False,
                        "HappyVending": False},
    })


@unittest.skipUnless(PYQT6_AVAILABLE, "PyQt6 not installed")
class RandomizerWorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PyQt6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])

    # ------------------------------------------------------------------
    def _capture(self, worker):
        """Connect every worker signal to a Python list."""

        stdout: list[str] = []
        stderr: list[str] = []
        completed: list[tuple[bool, str]] = []
        worker.stdout_line.connect(stdout.append)
        worker.stderr_line.connect(stderr.append)
        worker.completed.connect(lambda ok, msg: completed.append((ok, msg)))
        return stdout, stderr, completed

    # ------------------------------------------------------------------
    def test_success_path_emits_stdout_lines_and_completed_true(self):
        from gui_qt.worker import RandomizerWorker

        def _fake_run(config: dict) -> None:
            print("Reading data...")
            print("Modifying data...")
            print("Done.")

        worker = RandomizerWorker(_valid_settings_json())
        stdout, stderr, completed = self._capture(worker)

        with patch("gui_qt.worker._run_randomizer", _fake_run):
            worker.run()

        self.assertEqual(
            stdout,
            ["Reading data...", "Modifying data...", "Done."],
        )
        self.assertEqual(stderr, [])
        self.assertEqual(len(completed), 1)
        ok, summary = completed[0]
        self.assertTrue(ok)
        self.assertIn("complete", summary.lower())

    def test_stderr_is_routed_to_stderr_line_signal(self):
        from gui_qt.worker import RandomizerWorker

        def _fake_run(config: dict) -> None:
            import sys
            print("warning!", file=sys.stderr)

        worker = RandomizerWorker(_valid_settings_json())
        stdout, stderr, completed = self._capture(worker)

        with patch("gui_qt.worker._run_randomizer", _fake_run):
            worker.run()

        self.assertEqual(stdout, [])
        self.assertEqual(stderr, ["warning!"])
        self.assertTrue(completed[0][0])

    def test_invalid_json_reports_failure_without_running_randomizer(self):
        from gui_qt.worker import RandomizerWorker

        worker = RandomizerWorker("{ not json")
        _, _, completed = self._capture(worker)

        with patch("gui_qt.worker._run_randomizer") as mock_run:
            worker.run()

        mock_run.assert_not_called()
        ok, summary = completed[0]
        self.assertFalse(ok)
        self.assertIn("parse", summary.lower())

    def test_schema_violation_reports_failure_without_running_randomizer(self):
        from gui_qt.worker import RandomizerWorker

        # Missing the entire "techs" section → schema validation fails.
        broken = json.loads(_valid_settings_json())
        del broken["techs"]
        worker = RandomizerWorker(json.dumps(broken))
        _, _, completed = self._capture(worker)

        with patch("gui_qt.worker._run_randomizer") as mock_run:
            worker.run()

        mock_run.assert_not_called()
        self.assertFalse(completed[0][0])
        self.assertIn("$.techs is required", completed[0][1])

    def test_unexpected_exception_is_caught_and_reported(self):
        from gui_qt.worker import RandomizerWorker

        def _boom(config: dict) -> None:
            raise RuntimeError("boom")

        worker = RandomizerWorker(_valid_settings_json())
        _, _, completed = self._capture(worker)

        with patch("gui_qt.worker._run_randomizer", _boom):
            worker.run()

        ok, summary = completed[0]
        self.assertFalse(ok)
        self.assertIn("boom", summary)

    def test_stdout_and_stderr_are_restored_after_run(self):
        import sys

        from gui_qt.worker import RandomizerWorker

        original_out, original_err = sys.stdout, sys.stderr
        worker = RandomizerWorker(_valid_settings_json())

        with patch("gui_qt.worker._run_randomizer", lambda c: None):
            worker.run()

        self.assertIs(sys.stdout, original_out)
        self.assertIs(sys.stderr, original_err)


@unittest.skipUnless(PYQT6_AVAILABLE, "PyQt6 not installed")
class MainWindowRandomizeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PyQt6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])

    def test_clicking_randomize_disables_inputs_and_starts_a_worker(self):
        from gui_qt.main_window import MainWindow
        from gui_qt.worker import RandomizerWorker

        window = MainWindow()
        window.settings.General.InputFile  = "/tmp/in.bin"
        window.settings.General.OutputFile = "out.bin"
        window.header_bar.refresh_from_model()

        # Replace the worker class with a stub so we don't kick off the
        # real randomizer (and so we can inspect the construction).
        constructed: list[RandomizerWorker] = []

        class _StubWorker(RandomizerWorker):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)
                constructed.append(self)
            def start(self) -> None:           # noqa: D401 — match QThread signature
                pass

        with patch("gui_qt.main_window.RandomizerWorker", _StubWorker):
            window.header_bar.randomize_clicked.emit()

        self.assertEqual(len(constructed), 1)
        # set_busy(True) should have renamed the button.
        from PyQt6.QtWidgets import QPushButton
        randomize_button = next(
            b for b in window.header_bar.findChildren(QPushButton)
            if b.text() in {"Randomize", "Randomizing..."}
        )
        self.assertEqual(randomize_button.text(), "Randomizing...")

    def test_worker_completion_restores_busy_state_and_logs_summary(self):
        from gui_qt.main_window import MainWindow

        window = MainWindow()
        window._on_worker_completed(True, "Randomization complete.")

        # Button must return to the idle label.
        from PyQt6.QtWidgets import QPushButton
        randomize_button = next(
            b for b in window.header_bar.findChildren(QPushButton)
            if b.text() in {"Randomize", "Randomizing..."}
        )
        self.assertEqual(randomize_button.text(), "Randomize")
        self.assertIn("complete", window.terminal.toPlainText().lower())


if __name__ == "__main__":
    unittest.main()
