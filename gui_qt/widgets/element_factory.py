# Author: Christoph Merscher <dev@fmerscher.com>

"""Factory functions that turn an :class:`ElementConfig` into a Qt widget.

Each public ``build_*`` function returns a single :class:`QWidget` already
wired up:

* The current value is read from ``initial_value``.
* User edits call ``on_change(new_value)``.
* The widget's tooltip and (where appropriate) label come from the config.

The top-level :func:`build_element` dispatches on
:class:`~gui_qt.section_config.InputType` so callers don't have to
``if/elif`` over the variants. Adding a new input type means dropping a
new ``build_*`` function in here and one new mapping entry.

The tests for this module live in
:mod:`tests.test_gui_element_factory` and skip cleanly when PyQt6 is
not installed.
"""

from __future__ import annotations

from typing import Any, Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from gui_qt.section_config import ElementConfig, InputType


ChangeCallback = Callable[[Any], None]


# ---------------------------------------------------------------------------
# Top-level dispatch
# ---------------------------------------------------------------------------

def build_element(
    config: ElementConfig,
    initial_value: Any,
    on_change: ChangeCallback,
    parent: QWidget | None = None,
) -> QWidget:
    """Return the widget that backs ``config`` against the given value."""

    factory = _FACTORIES[config.input_type]
    return factory(config, initial_value, on_change, parent)


# ---------------------------------------------------------------------------
# Per-input-type factories
# ---------------------------------------------------------------------------

def build_checkbox(
    config: ElementConfig,
    initial_value: bool,
    on_change: ChangeCallback,
    parent: QWidget | None = None,
) -> QCheckBox:
    box = QCheckBox(config.label or "", parent)
    box.setChecked(bool(initial_value))
    box.setToolTip(config.tooltip)
    box.toggled.connect(lambda checked: on_change(bool(checked)))
    return box


def build_slider(
    config: ElementConfig,
    initial_value: int,
    on_change: ChangeCallback,
    parent: QWidget | None = None,
) -> QWidget:
    """Slider with a live value label next to it."""

    assert config.min_value is not None and config.max_value is not None, \
        f"SLIDER element '{config.attribute}' is missing min_value/max_value"

    container = QWidget(parent)
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)

    label_text = config.label or config.attribute
    title_label = QLabel(label_text, container)
    title_label.setToolTip(config.tooltip)

    slider = QSlider(Qt.Orientation.Horizontal, container)
    slider.setRange(config.min_value, config.max_value)
    slider.setValue(int(initial_value))
    slider.setToolTip(config.tooltip)

    value_label = QLabel(str(int(initial_value)), container)
    value_label.setToolTip(config.tooltip)
    value_label.setMinimumWidth(40)

    def _emit(new_value: int) -> None:
        value_label.setText(str(new_value))
        on_change(int(new_value))

    slider.valueChanged.connect(_emit)

    layout.addWidget(title_label)
    layout.addWidget(slider, 1)
    layout.addWidget(value_label)
    return container


def build_multiselect(
    config: ElementConfig,
    initial_value: str,
    on_change: ChangeCallback,
    parent: QWidget | None = None,
) -> QWidget:
    """Radio-group: N mutually exclusive options, parallel labels."""

    assert config.options, \
        f"MULTISELECT element '{config.attribute}' must have options"
    assert len(config.options) == len(config.option_labels), \
        f"MULTISELECT element '{config.attribute}' option/label arity mismatch"

    container = QWidget(parent)
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)

    if config.label:
        layout.addWidget(QLabel(config.label, container))

    group = QButtonGroup(container)
    group.setExclusive(True)

    for option_value, option_label in zip(config.options, config.option_labels):
        button = QRadioButton(option_label, container)
        button.setToolTip(config.tooltip)
        button.setChecked(option_value == initial_value)
        # Capture each option_value by default-arg, avoiding the late-binding trap.
        button.toggled.connect(
            lambda checked, value=option_value: checked and on_change(value)
        )
        group.addButton(button)
        layout.addWidget(button)

    layout.addStretch(1)
    return container


def build_dropdown(
    config: ElementConfig,
    initial_value: str,
    on_change: ChangeCallback,
    parent: QWidget | None = None,
) -> QComboBox:
    assert config.options, \
        f"DROPDOWN element '{config.attribute}' must have options"

    combo = QComboBox(parent)
    combo.setToolTip(config.tooltip)
    if config.placeholder:
        combo.setPlaceholderText(config.placeholder)

    combo.addItems(list(config.options))

    # Select the active option if it matches one of the entries.
    if initial_value in config.options:
        combo.setCurrentIndex(config.options.index(initial_value))
    else:
        combo.setCurrentIndex(-1)   # placeholder visible

    combo.currentTextChanged.connect(lambda text: on_change(text))
    return combo


# ---------------------------------------------------------------------------
# Dispatch table — keep this last so the factories are already defined.
# ---------------------------------------------------------------------------

_FACTORIES: dict[InputType, Callable[..., QWidget]] = {
    InputType.CHECKBOX:    build_checkbox,
    InputType.SLIDER:      build_slider,
    InputType.MULTISELECT: build_multiselect,
    InputType.DROPDOWN:    build_dropdown,
}
