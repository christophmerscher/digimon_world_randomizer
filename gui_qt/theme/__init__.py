# Author: Christoph Merscher <dev@fmerscher.com>

"""Modern dark theme for the PyQt6 GUI.

The public surface is intentionally tiny: :func:`apply_theme` takes a
:class:`QApplication`, switches it to Fusion (consistent across
Windows/Linux/macOS), installs the matching :class:`QPalette`, and
attaches a stylesheet built from :data:`DARK_PALETTE`. Callers don't
need to know anything about the QSS itself.

The stylesheet body is added by later commits; this commit just
establishes the foundation (palette + Fusion + an empty stylesheet).
"""

from __future__ import annotations

from gui_qt.theme.palette import DARK_PALETTE, Palette


__all__ = ["DARK_PALETTE", "Palette", "apply_theme", "build_palette"]


def build_palette(palette: Palette):
    """Return a :class:`QPalette` mirroring the colour roles."""

    from PyQt6.QtGui import QColor, QPalette

    qp = QPalette()

    # Window / general surfaces.
    qp.setColor(QPalette.ColorRole.Window,          QColor(palette.background))
    qp.setColor(QPalette.ColorRole.WindowText,      QColor(palette.text))
    qp.setColor(QPalette.ColorRole.Base,            QColor(palette.surface))
    qp.setColor(QPalette.ColorRole.AlternateBase,   QColor(palette.surface_hover))
    qp.setColor(QPalette.ColorRole.Text,            QColor(palette.text))
    qp.setColor(QPalette.ColorRole.PlaceholderText, QColor(palette.text_muted))

    # Buttons (default state — the QSS overrides hover / pressed styling).
    qp.setColor(QPalette.ColorRole.Button,          QColor(palette.surface))
    qp.setColor(QPalette.ColorRole.ButtonText,      QColor(palette.text))

    # Highlighted / selected items (used in list-views and the active tab).
    qp.setColor(QPalette.ColorRole.Highlight,        QColor(palette.accent))
    qp.setColor(QPalette.ColorRole.HighlightedText,  QColor(palette.accent_text))

    # Tooltips.
    qp.setColor(QPalette.ColorRole.ToolTipBase,     QColor(palette.surface_pressed))
    qp.setColor(QPalette.ColorRole.ToolTipText,     QColor(palette.text))

    # Disabled colours: dim the text so disabled controls are clearly inert.
    disabled = QPalette.ColorGroup.Disabled
    qp.setColor(disabled, QPalette.ColorRole.Text,        QColor(palette.text_muted))
    qp.setColor(disabled, QPalette.ColorRole.ButtonText,  QColor(palette.text_muted))
    qp.setColor(disabled, QPalette.ColorRole.WindowText,  QColor(palette.text_muted))

    return qp


def build_stylesheet(palette: Palette) -> str:
    """Return the QSS body for the given palette.

    The body grows over the next theme commits; for now it just sets
    the global window/text colours so anything not yet themed picks
    them up automatically.
    """

    return f"""
QWidget {{
    background-color: {palette.background};
    color: {palette.text};
}}
""".strip()


def apply_theme(app, palette: Palette = DARK_PALETTE) -> None:
    """Switch ``app`` to the modern dark theme."""

    from PyQt6.QtWidgets import QStyleFactory

    app.setStyle(QStyleFactory.create("Fusion"))
    app.setPalette(build_palette(palette))
    app.setStyleSheet(build_stylesheet(palette))
