# Author: Christoph Merscher <dev@fmerscher.com>

"""Generic tab widget driven entirely by a :class:`TabConfig`.

One class renders every tab in the GUI. Iterating the tab's
:attr:`TabConfig.sections` builds a :class:`SectionWidget` for each
section and stacks them vertically inside a :class:`QScrollArea` so
content-heavy tabs (notably ``Misc. Patches``) scroll naturally instead
of forcing the window to be 1500 px tall.

Composition over inheritance: callers don't subclass this. They build
``TabWidget(tab_config, settings_model)`` and drop the result into a
:class:`QTabWidget`.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from gui_qt.section_config import TabConfig
from gui_qt.settings_model import SettingsModel
from gui_qt.widgets.section_widget import SectionWidget


class TabWidget(QWidget):
    """One tab's content: a scrollable column of :class:`SectionWidget`."""

    def __init__(
        self,
        tab_config: TabConfig,
        settings: SettingsModel,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tab_config = tab_config
        self._settings = settings
        self._section_widgets: list[SectionWidget] = []
        self._build_layout()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        body = QWidget(scroll)
        body_layout = QVBoxLayout(body)

        for section in self._tab_config.sections:
            section_data = getattr(self._settings, section.model_attr)
            widget = SectionWidget(section, section_data, parent=body)
            self._section_widgets.append(widget)
            body_layout.addWidget(widget)

        body_layout.addStretch(1)
        scroll.setWidget(body)
        outer.addWidget(scroll)

    # ------------------------------------------------------------------
    # Inspection helpers (used by tests and the main window)
    # ------------------------------------------------------------------

    @property
    def section_widgets(self) -> tuple[SectionWidget, ...]:
        return tuple(self._section_widgets)
