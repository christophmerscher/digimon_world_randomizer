# Author: Christoph Merscher <dev@fmerscher.com>

"""Unit tests for the Qt element factory functions.

Skipped automatically when PyQt6 isn't installed so the rest of the
suite still runs in a minimal environment. When PyQt6 is available, the
tests run headlessly via the ``offscreen`` Qt platform plugin.
"""

from __future__ import annotations

import os
import unittest


try:
    import PyQt6  # noqa: F401
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False


# Force the offscreen platform plugin so tests run on CI / headless boxes.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@unittest.skipUnless(PYQT6_AVAILABLE, "PyQt6 not installed")
class ElementFactoryTests(unittest.TestCase):
    """Each factory creates the right widget type and forwards changes."""

    @classmethod
    def setUpClass(cls) -> None:
        from PyQt6.QtWidgets import QApplication

        # One QApplication per process is required for any QWidget to exist.
        cls._app = QApplication.instance() or QApplication([])

    # ------------------------------------------------------------------
    def _record_change(self):
        captured: list = []
        return captured, captured.append

    def test_checkbox_emits_on_toggle(self):
        from PyQt6.QtWidgets import QCheckBox
        from gui_qt.section_config import ElementConfig, InputType
        from gui_qt.widgets.element_factory import build_element

        config = ElementConfig(
            "DroppedItem", InputType.CHECKBOX, "tip", label="Item Dropped",
        )
        captured, on_change = self._record_change()

        widget = build_element(config, initial_value=False, on_change=on_change)
        self.assertIsInstance(widget, QCheckBox)
        self.assertFalse(widget.isChecked())
        self.assertEqual(widget.toolTip(), "tip")

        widget.setChecked(True)
        self.assertEqual(captured, [True])

    def test_slider_emits_int_on_value_change(self):
        from gui_qt.section_config import ElementConfig, InputType
        from gui_qt.widgets.element_factory import build_element

        config = ElementConfig(
            "ValuableItemCutoff", InputType.SLIDER, "tip",
            min_value=0, max_value=100,
        )
        captured, on_change = self._record_change()

        container = build_element(config, initial_value=10, on_change=on_change)
        # The container holds a QSlider somewhere in its child tree.
        from PyQt6.QtWidgets import QSlider
        slider = container.findChild(QSlider)
        self.assertIsNotNone(slider)
        self.assertEqual(slider.value(), 10)

        slider.setValue(42)
        self.assertEqual(captured, [42])

    def test_multiselect_emits_option_value_when_a_radio_is_checked(self):
        from PyQt6.QtWidgets import QRadioButton
        from gui_qt.section_config import ElementConfig, InputType
        from gui_qt.widgets.element_factory import build_element

        config = ElementConfig(
            "RandomizationMode", InputType.MULTISELECT, "tip",
            options=("shuffle", "random"),
            option_labels=("Shuffle", "Random"),
        )
        captured, on_change = self._record_change()

        container = build_element(config, initial_value="shuffle", on_change=on_change)
        radios = container.findChildren(QRadioButton)
        self.assertEqual([r.text() for r in radios], ["Shuffle", "Random"])
        self.assertTrue(radios[0].isChecked())

        radios[1].setChecked(True)
        # toggled fires twice (off for shuffle, on for random); we only act on the on event.
        self.assertEqual(captured, ["random"])

    def test_dropdown_selects_initial_value_and_emits_on_change(self):
        from PyQt6.QtWidgets import QComboBox
        from gui_qt.section_config import ElementConfig, InputType
        from gui_qt.widgets.element_factory import build_element

        config = ElementConfig(
            "Digimon", InputType.DROPDOWN, "tip",
            options=("Random", "Agumon", "Gabumon"),
            placeholder="Select Starter Digimon",
        )
        captured, on_change = self._record_change()

        combo = build_element(config, initial_value="Agumon", on_change=on_change)
        self.assertIsInstance(combo, QComboBox)
        self.assertEqual(combo.currentText(), "Agumon")

        combo.setCurrentIndex(2)
        self.assertEqual(captured, ["Gabumon"])

    def test_dropdown_falls_back_to_placeholder_for_unknown_initial(self):
        from PyQt6.QtWidgets import QComboBox
        from gui_qt.section_config import ElementConfig, InputType
        from gui_qt.widgets.element_factory import build_element

        config = ElementConfig(
            "Digimon", InputType.DROPDOWN, "tip",
            options=("Random", "Agumon"),
            placeholder="Select Starter Digimon",
        )
        _, on_change = self._record_change()

        combo: QComboBox = build_element(config, initial_value="NotAReal", on_change=on_change)
        # currentText() is "" when no item is selected; placeholder shown only in unset state.
        self.assertEqual(combo.currentIndex(), -1)


if __name__ == "__main__":
    unittest.main()
