# Author: Christoph Merscher <dev@fmerscher.com>

"""Top-level window: header bar, tabs, terminal.

The :class:`MainWindow` is the assembly point. It owns one
:class:`SettingsModel` and stitches three sub-widgets together:

* :class:`HeaderBar` at the top (ROM picker, output, seed, log level,
  action buttons).
* A :class:`QTabWidget` with one :class:`TabWidget` per
  :class:`TabConfig`.
* :class:`TerminalWidget` at the bottom.

Each button on the header bar is wired to a private slot:

* Load Settings opens a file dialog, parses the JSON via
  :meth:`SettingsModel.from_json`, swaps the model, and rebuilds the
  header + tabs.
* Save Settings writes :meth:`SettingsModel.to_json` to a chosen file.
* Randomize launches a :class:`RandomizerWorker` on a background
  thread so the UI stays responsive while the randomizer runs.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from gui_qt.section_config import TABS
from gui_qt.settings_model import SettingsModel
from gui_qt.widgets.header_bar import HeaderBar
from gui_qt.widgets.tab_widget import TabWidget
from gui_qt.widgets.terminal_widget import LineKind, TerminalWidget
from gui_qt.worker import RandomizerWorker


APP_TITLE = "Digimon World Randomizer"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 800

SETTINGS_FILE_FILTER = "Settings file (*.json);;All files (*)"


class MainWindow(QMainWindow):
    """Assembles the full GUI from the reusable widgets."""

    def __init__(self, settings: SettingsModel | None = None) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self._settings = settings if settings is not None else SettingsModel()
        self._worker: RandomizerWorker | None = None

        self._header   = HeaderBar(self._settings.General)
        self._tabs     = self._build_tabs()
        self._terminal = TerminalWidget()

        self._wire_signals()
        self.setCentralWidget(self._build_central_widget())

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_central_widget(self) -> QWidget:
        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.addWidget(self._header)
        layout.addWidget(self._tabs, 1)        # tabs expand to fill space
        layout.addWidget(self._terminal, 1)    # terminal takes the rest
        return central

    def _build_tabs(self) -> QTabWidget:
        tabs = QTabWidget(self)
        self._tab_widgets: dict[str, TabWidget] = {}

        for tab_config in TABS:
            widget = TabWidget(tab_config, self._settings, parent=tabs)
            tabs.addTab(widget, tab_config.title)
            self._tab_widgets[tab_config.title] = widget

        return tabs

    # ------------------------------------------------------------------
    # Signal wiring (action handlers fleshed out in the next commits)
    # ------------------------------------------------------------------

    def _wire_signals(self) -> None:
        self._header.load_clicked.connect(self._on_load_settings_clicked)
        self._header.save_clicked.connect(self._on_save_settings_clicked)
        self._header.randomize_clicked.connect(self._on_randomize_clicked)

    def _on_load_settings_clicked(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load settings", "", SETTINGS_FILE_FILTER,
        )
        if not path:
            return

        try:
            payload = Path(path).read_text(encoding="utf-8")
            new_settings = SettingsModel.from_json(payload)
        except (OSError, ValueError) as exc:
            self._terminal.append_line(
                f"Failed to load settings: {exc}", LineKind.ERROR,
            )
            return

        self._replace_settings(new_settings)
        self._terminal.append_line(
            f"Loaded settings from {path}", LineKind.CHANGE,
        )

    def _on_save_settings_clicked(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save settings", "settings.json", SETTINGS_FILE_FILTER,
        )
        if not path:
            return

        try:
            Path(path).write_text(self._settings.to_json(), encoding="utf-8")
        except OSError as exc:
            self._terminal.append_line(
                f"Failed to save settings: {exc}", LineKind.ERROR,
            )
            return

        # to_json() also updates self.General.Hash; refresh the header so
        # the displayed Seed/LogLevel/etc. stay in sync.
        self._header.refresh_from_model()
        self._terminal.append_line(
            f"Saved settings to {path}", LineKind.CHANGE,
        )

    def _on_randomize_clicked(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            # Defensive: the header bar disables the button while busy,
            # but ignore double-clicks just in case.
            return

        self._terminal.clear_output()
        self._terminal.append_line(
            "Starting randomization...", LineKind.CHANGE,
        )

        # to_json() also refreshes self._settings.General.Hash.
        payload = self._settings.to_json()

        self._worker = RandomizerWorker(payload, parent=self)
        self._worker.stdout_line.connect(self._on_worker_stdout)
        self._worker.stderr_line.connect(self._on_worker_stderr)
        self._worker.completed.connect(self._on_worker_completed)
        self._header.set_busy(True)
        self._worker.start()

    def _on_worker_stdout(self, line: str) -> None:
        self._terminal.append_line(line, LineKind.INFO)

    def _on_worker_stderr(self, line: str) -> None:
        self._terminal.append_line(line, LineKind.ERROR)

    def _on_worker_completed(self, success: bool, summary: str) -> None:
        self._header.set_busy(False)
        kind = LineKind.CHANGE if success else LineKind.ERROR
        self._terminal.append_line(summary, kind)

        if success and self._settings.General.Hash:
            self._terminal.append_line(
                f"Settings hash: {self._settings.General.Hash}",
                LineKind.CHANGE,
            )

    # ------------------------------------------------------------------
    # Settings replacement
    # ------------------------------------------------------------------

    def _replace_settings(self, new_settings: SettingsModel) -> None:
        """Swap the active model and rebuild the inputs that bind to it.

        The header bar and tab widgets all hold direct references to the
        previous model's dataclasses, so they have to be rebuilt for the
        new values to appear in the UI. The terminal is preserved so
        load/save messages remain visible across the rebuild.
        """

        self._settings = new_settings
        self._header   = HeaderBar(self._settings.General)
        self._tabs     = self._build_tabs()
        self._wire_signals()
        self.setCentralWidget(self._build_central_widget())

    # ------------------------------------------------------------------
    # Inspection helpers (used by tests)
    # ------------------------------------------------------------------

    @property
    def settings(self) -> SettingsModel:
        return self._settings

    @property
    def header_bar(self) -> HeaderBar:
        return self._header

    @property
    def terminal(self) -> TerminalWidget:
        return self._terminal

    def tab_widget(self, title: str) -> TabWidget:
        return self._tab_widgets[title]
