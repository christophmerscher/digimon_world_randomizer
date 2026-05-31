# Author: Christoph Merscher <dev@fmerscher.com>

"""Top-of-window header bar.

The header bar is everything above the per-tab settings: the file
inputs (ROM + output filename), the seed, the log-level selector, and
the three action buttons (Load Settings, Save Settings, Randomize).

The widget owns no business logic. It edits the
:class:`~gui_qt.settings_model.GeneralSettings` of the model it was
constructed with and emits a signal for each button so the main window
can decide what to do (open dialogs, kick off the worker, etc).
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from gui_qt.settings_model import GeneralSettings
from gui_qt.widgets.file_select import FileSelectWidget


# Log-level options exposed via the radio group (value → display label).
_LOG_LEVELS = (
    ("full",   "Full"),
    ("casual", "Casual"),
    ("race",   "Race"),
)

# Text shown on the Randomize button in the two states.
_RANDOMIZE_IDLE_LABEL = "Randomize"
_RANDOMIZE_BUSY_LABEL = "Randomizing..."


class HeaderBar(QWidget):
    """Top section of the main window."""

    #: Emitted when the user clicks "Load Settings".
    load_clicked      = pyqtSignal()
    #: Emitted when the user clicks "Save Settings".
    save_clicked      = pyqtSignal()
    #: Emitted when the user clicks "Randomize".
    randomize_clicked = pyqtSignal()

    def __init__(self, general: GeneralSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._general = general
        self._build_layout()

    # ------------------------------------------------------------------
    # External API used by the main window
    # ------------------------------------------------------------------

    def set_busy(self, busy: bool) -> None:
        """Disable inputs and rename the Randomize button while a run is in flight."""

        for widget in self._toggle_during_run:
            widget.setEnabled(not busy)

        self._randomize_button.setText(
            _RANDOMIZE_BUSY_LABEL if busy else _RANDOMIZE_IDLE_LABEL
        )

    def refresh_from_model(self) -> None:
        """Re-read every field from ``self._general`` (used after Load Settings)."""

        self._rom_picker.set_path(self._general.InputFile)
        self._output_edit.setText(self._general.OutputFile)
        self._seed_edit.setText(self._general.Seed or "")
        self._select_log_level(self._general.LogLevel)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        outer = QHBoxLayout(self)
        outer.addLayout(self._build_left_column(), 2)
        outer.addLayout(self._build_right_column(), 1)

        self._toggle_during_run: list[QWidget] = [
            self._rom_picker,
            self._output_edit,
            self._seed_edit,
            *self._log_radios.values(),
            self._load_button,
            self._save_button,
            self._randomize_button,
        ]

    def _build_left_column(self) -> QVBoxLayout:
        column = QVBoxLayout()

        # Two file-style rows on top.
        form = QFormLayout()
        form.setLabelAlignment(form.labelAlignment())   # default-aligned

        self._rom_picker = FileSelectWidget(
            placeholder="Select ROM file...",
            dialog_title="Select ROM",
        )
        self._rom_picker.set_path(self._general.InputFile)
        self._rom_picker.path_changed.connect(self._on_rom_picked)
        form.addRow(QLabel("ROM:"), self._rom_picker)

        self._output_edit = QLineEdit()
        self._output_edit.setText(self._general.OutputFile)
        self._output_edit.setPlaceholderText("Destination file name...")
        self._output_edit.textChanged.connect(self._on_output_changed)
        form.addRow(QLabel("Output:"), self._output_edit)

        column.addLayout(form)
        column.addLayout(self._build_seed_and_log_row())
        return column

    def _build_seed_and_log_row(self) -> QGridLayout:
        grid = QGridLayout()

        # Seed input.
        grid.addWidget(QLabel("Seed:"), 0, 0)
        self._seed_edit = QLineEdit(self._general.Seed or "")
        self._seed_edit.setPlaceholderText("Random")
        self._seed_edit.textChanged.connect(self._on_seed_changed)
        grid.addWidget(self._seed_edit, 0, 1)

        # Log-level radio group.
        grid.addWidget(QLabel("Logging:"), 0, 2)
        radio_row = QHBoxLayout()
        self._log_group = QButtonGroup(self)
        self._log_group.setExclusive(True)
        self._log_radios: dict[str, QRadioButton] = {}

        for value, label in _LOG_LEVELS:
            radio = QRadioButton(label)
            radio.setChecked(value == self._general.LogLevel)
            radio.toggled.connect(
                lambda checked, v=value: checked and self._on_log_level_changed(v)
            )
            self._log_group.addButton(radio)
            self._log_radios[value] = radio
            radio_row.addWidget(radio)

        grid.addLayout(radio_row, 0, 3)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        return grid

    def _build_right_column(self) -> QVBoxLayout:
        column = QVBoxLayout()

        self._load_button      = QPushButton("Load Settings")
        self._save_button      = QPushButton("Save Settings")
        self._randomize_button = QPushButton(_RANDOMIZE_IDLE_LABEL)

        self._load_button.clicked.connect(self.load_clicked.emit)
        self._save_button.clicked.connect(self.save_clicked.emit)
        self._randomize_button.clicked.connect(self.randomize_clicked.emit)

        column.addWidget(self._load_button)
        column.addWidget(self._save_button)
        column.addWidget(self._randomize_button)
        column.addStretch(1)
        return column

    # ------------------------------------------------------------------
    # Internal handlers
    # ------------------------------------------------------------------

    def _on_rom_picked(self, path: str) -> None:
        self._general.InputFile = path

    def _on_output_changed(self, value: str) -> None:
        self._general.OutputFile = value

    def _on_seed_changed(self, value: str) -> None:
        self._general.Seed = value

    def _on_log_level_changed(self, value: str) -> None:
        self._general.LogLevel = value

    def _select_log_level(self, value: str) -> None:
        """Programmatically check the matching radio (used by refresh_from_model)."""

        for option_value, radio in self._log_radios.items():
            radio.setChecked(option_value == value)
