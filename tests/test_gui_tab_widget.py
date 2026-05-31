# Author: Christoph Merscher <dev@fmerscher.com>

"""Tests for the generic TabWidget.

Skipped without PyQt6.
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
class TabWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PyQt6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication([])

    # ------------------------------------------------------------------
    def test_renders_one_section_widget_per_section_in_config(self):
        from gui_qt.section_config import TABS
        from gui_qt.settings_model import SettingsModel
        from gui_qt.widgets.tab_widget import TabWidget

        for tab in TABS:
            with self.subTest(tab=tab.title):
                model = SettingsModel()
                widget = TabWidget(tab, model)
                self.assertEqual(
                    len(widget.section_widgets), len(tab.sections),
                    f"Tab {tab.title!r} should render {len(tab.sections)} sections",
                )

    def test_section_widget_titles_match_config(self):
        from gui_qt.section_config import TABS
        from gui_qt.settings_model import SettingsModel
        from gui_qt.widgets.tab_widget import TabWidget

        tab = TABS[0]   # Digimon tab — three sections
        widget = TabWidget(tab, SettingsModel())
        titles = [s.title() for s in widget.section_widgets]
        self.assertEqual(titles, [s.title for s in tab.sections])

    def test_tab_widget_uses_a_scroll_area(self):
        from PyQt6.QtWidgets import QScrollArea

        from gui_qt.section_config import TABS
        from gui_qt.settings_model import SettingsModel
        from gui_qt.widgets.tab_widget import TabWidget

        widget = TabWidget(TABS[-1], SettingsModel())  # patches tab — large
        self.assertIsNotNone(widget.findChild(QScrollArea))

    def test_section_widgets_share_the_settings_model_state(self):
        from PyQt6.QtWidgets import QCheckBox

        from gui_qt.section_config import TABS
        from gui_qt.settings_model import SettingsModel
        from gui_qt.widgets.tab_widget import TabWidget

        # Find the Digimon-Data section in the Digimon tab.
        digimon_tab = TABS[0]
        model = SettingsModel()
        widget = TabWidget(digimon_tab, model)

        digi_section = next(
            s for s in widget.section_widgets if s.title() == "Digimon Data"
        )
        master = digi_section.findChild(QCheckBox)
        master.setChecked(True)

        # Toggling the section's master must mutate the model in place.
        self.assertTrue(model.Digimon.Enabled)


if __name__ == "__main__":
    unittest.main()
