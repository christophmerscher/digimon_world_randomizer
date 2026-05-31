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
from gui_qt.theme.stylesheet import build_stylesheet


# Font stack preferred for UI text. The first available family wins.
# Picks a modern variable / humanist sans on each platform; falls back
# to the platform default if none are installed.
UI_FONT_FAMILIES = (
    "Segoe UI Variable",   # Windows 11
    "Segoe UI",            # Windows 10
    "Inter",               # cross-platform modern open-source
    "SF Pro Text",         # macOS Big Sur+
    "Helvetica Neue",
    "Roboto",
    "Cantarell",           # GNOME
    "Noto Sans",
    "sans-serif",
)

UI_FONT_POINT_SIZE = 10


__all__ = [
    "DARK_PALETTE",
    "Palette",
    "apply_theme",
    "build_palette",
    "build_stylesheet",
]


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


def build_ui_font():
    """Return the modern UI :class:`QFont`.

    Sets a fallback list so Windows 11, Windows 10, macOS, and major
    Linux desktops all land on a humanist sans without shipping our
    own font file.
    """

    from PyQt6.QtGui import QFont

    font = QFont()
    font.setFamilies(list(UI_FONT_FAMILIES))
    font.setPointSize(UI_FONT_POINT_SIZE)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    return font


def apply_theme(app, palette: Palette = DARK_PALETTE) -> None:
    """Switch ``app`` to the modern dark theme."""

    from PyQt6.QtWidgets import QStyleFactory

    app.setStyle(QStyleFactory.create("Fusion"))
    app.setPalette(build_palette(palette))
    app.setFont(build_ui_font())
    app.setStyleSheet(build_stylesheet(palette))
