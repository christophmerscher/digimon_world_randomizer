# Author: Christoph Merscher <dev@fmerscher.com>

"""Qt application bootstrap.

Opens the main window. Kept tiny on purpose; all UI assembly happens in
later commits inside :mod:`gui_qt.main_window` and the per-widget
modules under :mod:`gui_qt.widgets`.

The PyQt6 import is performed inside :func:`main` so the rest of the
``gui_qt`` package can be imported (for tests, type-checking) on systems
that do not have PyQt6 installed.
"""

from __future__ import annotations

import sys


APP_TITLE = "Digimon World Randomizer"

# Initial window size matches the legacy Electron BrowserWindow.
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 730


def main(argv: list[str] | None = None) -> int:
    """Launch the Qt event loop and return its exit code."""

    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow
    except ImportError as exc:
        print(
            "PyQt6 is required to launch the GUI. Install it with:\n"
            "    pip install 'digimon-world-randomizer[gui]'\n"
            "or:\n"
            "    pip install PyQt6",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc

    qt_argv = argv if argv is not None else sys.argv
    qt_app = QApplication(qt_argv)

    window = QMainWindow()
    window.setWindowTitle(APP_TITLE)
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.show()

    return qt_app.exec()
