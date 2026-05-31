# Author: Christoph Merscher <dev@fmerscher.com>

"""CLI launcher for the PyQt6 desktop GUI.

Equivalent of ``digimon_randomize.py`` for the graphical interface.
Delegates everything to :func:`gui_qt.app.main`.
"""

from __future__ import annotations

from gui_qt.app import main


if __name__ == "__main__":
    raise SystemExit(main())
