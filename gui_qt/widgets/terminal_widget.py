# Author: Christoph Merscher <dev@fmerscher.com>

"""Terminal-style output widget for the randomizer GUI.

The randomiser worker (added in a later commit) streams its stdout and
stderr into this widget line-by-line. Each line is tagged with a
:class:`LineKind` so error lines are visually distinct from normal
output without forcing the caller to do their own HTML escaping.

Lines are appended to a :class:`QPlainTextEdit` configured as
read-only; the view auto-scrolls to the bottom on every append so the
user always sees the latest output without scrolling manually.
"""

from __future__ import annotations

from enum import Enum, auto
from html import escape

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QPlainTextEdit, QWidget


# Colours for the three supported line kinds. Picked to read against
# both light and dark Qt themes.
_LINE_COLOURS = {
    "info":   "#cccccc",     # default plain output
    "change": "#a0c4ff",     # randomiser "logChange" lines
    "error":  "#ff8a8a",
}


class LineKind(Enum):
    """The category of a single line written to the terminal."""

    INFO   = auto()
    CHANGE = auto()
    ERROR  = auto()


class TerminalWidget(QPlainTextEdit):
    """Read-only auto-scrolling text view with per-line colouring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setUndoRedoEnabled(False)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        # A monospace font makes table-like log output line up.
        font = QFont("Consolas")
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def append_line(self, text: str, kind: LineKind = LineKind.INFO) -> None:
        """Append ``text`` as one HTML-coloured line and scroll to the bottom."""

        colour = _LINE_COLOURS[kind.name.lower()]
        safe_text = escape(text).replace(" ", "&nbsp;")
        html = f'<span style="color:{colour};">{safe_text}</span>'
        self.appendHtml(html)
        self._scroll_to_bottom()

    def clear_output(self) -> None:
        """Reset the buffer (used when the user starts a new randomisation)."""

        self.clear()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _scroll_to_bottom(self) -> None:
        bar = self.verticalScrollBar()
        bar.setValue(bar.maximum())
