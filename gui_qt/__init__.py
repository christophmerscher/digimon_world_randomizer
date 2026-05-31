"""PyQt6 desktop GUI for the Digimon World Randomizer.

The package replaces the legacy Electron / TypeScript GUI under ``gui/``.
Module-level imports stay PyQt-free so the rest of the project (CLI,
tests) keeps working when PyQt6 is not installed; Qt is imported lazily
from :func:`gui_qt.app.main`.
"""

__all__ = ["app", "settings_model"]
