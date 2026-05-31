# Author: Christoph Merscher <dev@fmerscher.com>

"""Tests for the section card widget.

Skipped without PyQt6; otherwise run headlessly via the offscreen Qt
platform plugin.
"""

from __future__ import annotations

import os
import unittest


try:
    import PyQt6  # noqa: F401
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@unittest.skipUnless(PYQT6_AVAILABLE, "PyQt6 not installed")
class SectionWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PyQt6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])

    # ------------------------------------------------------------------
    def _build_chests_section(self):
        from gui_qt.section_config import CHESTS_SECTION
        from gui_qt.settings_model import SettingsModel
        from gui_qt.widgets.section_widget import SectionWidget

        model = SettingsModel()
        widget = SectionWidget(CHESTS_SECTION, model.Chests)
        return model, widget

    def test_section_title_matches_config(self):
        from gui_qt.section_config import CHESTS_SECTION
        _, widget = self._build_chests_section()
        self.assertEqual(widget.title(), CHESTS_SECTION.title)

    def test_master_checkbox_writes_back_to_section_dataclass(self):
        from PyQt6.QtWidgets import QCheckBox

        model, widget = self._build_chests_section()
        master = widget.findChild(QCheckBox)
        self.assertFalse(model.Chests.Enabled)

        master.setChecked(True)
        self.assertTrue(model.Chests.Enabled)

        master.setChecked(False)
        self.assertFalse(model.Chests.Enabled)

    def test_child_element_writes_back_to_section_dataclass(self):
        from PyQt6.QtWidgets import QCheckBox

        model, widget = self._build_chests_section()
        # Two checkboxes exist: master "Enabled" + the AllowEvolutionItems toggle.
        checkboxes = widget.findChildren(QCheckBox)
        evo_box = next(cb for cb in checkboxes if cb.text() == "Digivolution Items")

        evo_box.setChecked(True)
        self.assertTrue(model.Chests.AllowEvolutionItems)

    def test_enabling_master_enables_child_widgets(self):
        from PyQt6.QtWidgets import QCheckBox

        model, widget = self._build_chests_section()
        evo_box = next(
            cb for cb in widget.findChildren(QCheckBox)
            if cb.text() == "Digivolution Items"
        )

        # Section starts disabled, so the child element is too.
        self.assertFalse(evo_box.isEnabled())

        master = widget.findChild(QCheckBox)
        master.setChecked(True)
        self.assertTrue(evo_box.isEnabled())

    def test_empty_section_renders_master_only(self):
        from PyQt6.QtWidgets import QCheckBox

        from gui_qt.section_config import RECRUITMENT_SECTION
        from gui_qt.settings_model import SettingsModel
        from gui_qt.widgets.section_widget import SectionWidget

        model = SettingsModel()
        widget = SectionWidget(RECRUITMENT_SECTION, model.Recruitment)

        # Only the master checkbox should exist.
        self.assertEqual(len(widget.findChildren(QCheckBox)), 1)


if __name__ == "__main__":
    unittest.main()
