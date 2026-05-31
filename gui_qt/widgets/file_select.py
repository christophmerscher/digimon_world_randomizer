# Author: Christoph Merscher <dev@fmerscher.com>

"""ROM file picker widget.

A :class:`FileSelectWidget` is a horizontal line edit + browse button
pair. Clicking ``Browse...`` opens a :class:`QFileDialog`; choosing a
file updates the line edit and emits :attr:`path_changed`.

The line edit itself is read-only — users always pick via the dialog so
the path is guaranteed to be one the OS recognises. The widget exposes
:meth:`path` / :meth:`set_path` for programmatic access (used when the
surrounding form loads a settings file from disk).
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


# Default filename filter for the "open" dialog.
ROM_FILE_FILTER = "ROM image (*.bin);;All files (*)"


class FileSelectWidget(QWidget):
    """Read-only text field + Browse button for selecting one file."""

    #: Emitted with the new absolute path whenever the user picks a file.
    path_changed = pyqtSignal(str)

    def __init__(
        self,
        *,
        placeholder: str = "Select file...",
        dialog_title: str = "Select file",
        file_filter: str = ROM_FILE_FILTER,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._dialog_title = dialog_title
        self._file_filter = file_filter

        self._line_edit = QLineEdit(self)
        self._line_edit.setReadOnly(True)
        self._line_edit.setPlaceholderText(placeholder)

        self._browse_button = QPushButton("Browse...", self)
        self._browse_button.clicked.connect(self._open_dialog)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._line_edit, 1)
        layout.addWidget(self._browse_button)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def path(self) -> str:
        return self._line_edit.text()

    def set_path(self, value: str) -> None:
        """Set the displayed path silently — does NOT emit ``path_changed``."""

        self._line_edit.setText(value)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _open_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self._dialog_title,
            self._line_edit.text(),
            self._file_filter,
        )
        if path:
            self._line_edit.setText(path)
            self.path_changed.emit(path)
