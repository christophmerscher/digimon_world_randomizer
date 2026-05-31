# Author: Christoph Merscher <dev@fmerscher.com>

"""Top-level window: header bar, tabs, terminal.

The :class:`MainWindow` is the assembly point. It owns one
:class:`SettingsModel` and stitches three sub-widgets together:

* :class:`HeaderBar` at the top (ROM picker, output, seed, log level,
  action buttons).
* A :class:`QTabWidget` with one :class:`TabWidget` per
  :class:`TabConfig`.
* :class:`TerminalWidget` at the bottom.

Each button click on the header bar is forwarded to a private slot.
Load Settings, Save Settings and the actual randomiser are wired in
the following commits; this commit is purely structural assembly so
the launcher finally shows the full UI.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
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


APP_TITLE = "Digimon World Randomizer"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 800


class MainWindow(QMainWindow):
    """Assembles the full GUI from the reusable widgets."""

    def __init__(self, settings: SettingsModel | None = None) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self._settings = settings if settings is not None else SettingsModel()

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
        # Implemented in the next commit (load/save dialogs).
        self._terminal.append_line(
            "Load Settings is not wired up yet.", LineKind.INFO,
        )

    def _on_save_settings_clicked(self) -> None:
        # Implemented in the next commit (load/save dialogs).
        self._terminal.append_line(
            "Save Settings is not wired up yet.", LineKind.INFO,
        )

    def _on_randomize_clicked(self) -> None:
        # Implemented in the worker commit.
        self._terminal.append_line(
            "Randomize is not wired up yet.", LineKind.INFO,
        )

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
