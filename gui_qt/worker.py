# Author: Christoph Merscher <dev@fmerscher.com>

"""Background worker that runs the randomiser without blocking the UI.

The Electron app shelled out to ``digimon_randomize.exe`` as a separate
process. The PyQt6 GUI imports :mod:`digimon.app` directly and runs it
on a :class:`QThread`, which is simpler (no process management) but
requires routing all ``print()`` output through Qt signals so the
terminal widget can update from the GUI thread.

Public API
----------

:class:`RandomizerWorker`
    A :class:`QThread` subclass. Construct it with a settings JSON
    string, connect to its three signals, then call :meth:`start`.

    * ``stdout_line(str)`` — one line of normal output.
    * ``stderr_line(str)`` — one line of error output.
    * ``completed(bool, str)`` — fires once when the run finishes;
      first arg is success, second is a human-readable summary.
"""

from __future__ import annotations

import sys
from typing import Callable, TextIO

from PyQt6.QtCore import QThread, pyqtSignal

from digimon.app import run as _run_randomizer
from digimon.settings import (
    SettingsError,
    SettingsJsonError,
    loadSettings,
    validateSettings,
)


class _LineEmitter(TextIO):
    """File-like adapter that emits one Qt-side callback per complete line."""

    def __init__(self, emit: Callable[[str], None]) -> None:
        self._emit = emit
        self._buffer = ""

    def write(self, text: str) -> int:
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._emit(line)
        return len(text)

    def flush(self) -> None:
        if self._buffer:
            self._emit(self._buffer)
            self._buffer = ""


class RandomizerWorker(QThread):
    """Run :func:`digimon.app.run` on a background thread."""

    #: Emitted once per line of stdout produced by the randomiser.
    stdout_line = pyqtSignal(str)
    #: Emitted once per line of stderr produced by the randomiser.
    stderr_line = pyqtSignal(str)
    #: Emitted exactly once when the run finishes — args: (success, summary).
    completed   = pyqtSignal(bool, str)

    def __init__(self, settings_json: str, parent=None) -> None:
        super().__init__(parent)
        self._settings_json = settings_json

    # ------------------------------------------------------------------
    def run(self) -> None:                          # called on the worker thread
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = _LineEmitter(self.stdout_line.emit)
        sys.stderr = _LineEmitter(self.stderr_line.emit)

        try:
            config = loadSettings(self._settings_json)
            validateSettings(config)
            _run_randomizer(config)
            self._flush_streams()
            self.completed.emit(True, "Randomization complete.")
        except SettingsJsonError as exc:
            self._flush_streams()
            self.completed.emit(False, f"Failed to parse settings JSON: {exc.error}")
        except SettingsError as exc:
            self._flush_streams()
            self.completed.emit(False, str(exc))
        except SystemExit:
            # Logger.fatalError() calls exit() — surface it as a friendly error.
            self._flush_streams()
            self.completed.emit(False, "Randomization aborted (fatal error).")
        except Exception as exc:                    # noqa: BLE001 — surface everything
            self._flush_streams()
            self.completed.emit(False, f"Unexpected error: {exc}")
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

    # ------------------------------------------------------------------
    def _flush_streams(self) -> None:
        if isinstance(sys.stdout, _LineEmitter):
            sys.stdout.flush()
        if isinstance(sys.stderr, _LineEmitter):
            sys.stderr.flush()
