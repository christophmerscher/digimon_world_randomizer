# Author: Christoph Merscher <dev@fmerscher.com>

"""Qt application bootstrap.

Opens the main window. Kept tiny on purpose; UI assembly lives in
:mod:`gui_qt.main_window` and the per-widget modules under
:mod:`gui_qt.widgets`.

The PyQt6 import is performed inside :func:`main` so the rest of the
``gui_qt`` package can be imported (for tests, type-checking) on systems
that do not have PyQt6 installed.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """Launch the Qt event loop and return its exit code."""

    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError as exc:
        print(
            "PyQt6 is required to launch the GUI. Install it with:\n"
            "    pip install 'digimon-world-randomizer[gui]'\n"
            "or:\n"
            "    pip install PyQt6",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc

    # Defer the import so the bare ``gui_qt`` package stays Qt-free.
    from gui_qt.main_window import MainWindow

    qt_argv = argv if argv is not None else sys.argv
    qt_app = QApplication(qt_argv)

    window = MainWindow()
    window.show()

    return qt_app.exec()
