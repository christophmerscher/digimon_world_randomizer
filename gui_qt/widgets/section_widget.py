# Author: Christoph Merscher <dev@fmerscher.com>

"""Section card widget.

A :class:`SectionWidget` renders one box in the UI:

* The section title (top of the card).
* A master ``Enabled`` checkbox controlled by the section's ``Enabled``
  flag. When unchecked, every child element below is disabled but
  remains visible (matches the Electron behaviour and helps the user
  see what would happen if the section were turned on).
* One widget per :class:`~gui_qt.section_config.ElementConfig`,
  produced by :func:`gui_qt.widgets.element_factory.build_element`.

The section binds to a single dataclass attribute on the settings
model. All read/write of user choices happens through that dataclass so
the surrounding code (Save, Randomize, hash) sees a single source of
truth.
"""

from __future__ import annotations

from typing import Any

from PyQt6.QtWidgets import QCheckBox, QGroupBox, QVBoxLayout, QWidget

from gui_qt.section_config import SectionConfig
from gui_qt.widgets.element_factory import build_element


class SectionWidget(QGroupBox):
    """One settings card, bound to one section dataclass."""

    def __init__(
        self,
        config: SectionConfig,
        section_data: Any,
        parent: QWidget | None = None,
    ) -> None:
        """Construct the card.

        ``section_data`` must be the live dataclass instance attached to
        the parent :class:`~gui_qt.settings_model.SettingsModel` (e.g.
        ``model.Digimon``). The widget mutates it in place as the user
        toggles controls.
        """

        super().__init__(config.title, parent)
        self._config = config
        self._section = section_data
        self._element_widgets: list[QWidget] = []
        self._build_layout()
        self._sync_enabled_state(self._section.Enabled)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(self._build_master_checkbox())

        for element in self._config.elements:
            widget = build_element(
                element,
                initial_value=getattr(self._section, element.attribute),
                on_change=self._make_setter(element.attribute),
                parent=self,
            )
            self._element_widgets.append(widget)
            layout.addWidget(widget)

        layout.addStretch(1)

    def _build_master_checkbox(self) -> QCheckBox:
        checkbox = QCheckBox("Enabled", self)
        checkbox.setChecked(bool(self._section.Enabled))
        checkbox.setToolTip(self._config.tooltip)

        def _on_toggled(checked: bool) -> None:
            self._section.Enabled = bool(checked)
            self._sync_enabled_state(bool(checked))

        checkbox.toggled.connect(_on_toggled)
        return checkbox

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_setter(self, attribute: str):
        """Return a closure that writes the new value back to ``section_data``."""

        section = self._section

        def _set(value: Any) -> None:
            setattr(section, attribute, value)

        return _set

    def _sync_enabled_state(self, enabled: bool) -> None:
        """Enable/disable every child element widget (the master stays editable)."""

        for widget in self._element_widgets:
            widget.setEnabled(enabled)
