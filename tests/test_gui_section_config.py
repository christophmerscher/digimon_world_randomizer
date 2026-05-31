# Author: Christoph Merscher <dev@fmerscher.com>

"""Verify the static UI config matches the settings model shape.

The config table in :mod:`gui_qt.section_config` is what the widget
layer walks at runtime. If an attribute name is wrong here, the GUI
would silently bind to a non-existent field; these tests catch that
mismatch in CI instead.
"""

from __future__ import annotations

import unittest
from dataclasses import fields, is_dataclass

from gui_qt.section_config import (
    DIGIMON_NAMES,
    ElementConfig,
    InputType,
    SectionConfig,
    TABS,
    TabConfig,
)
from gui_qt.settings_model import SettingsModel


def _walk_sections():
    for tab in TABS:
        for section in tab.sections:
            yield tab, section


def _walk_elements():
    for tab, section in _walk_sections():
        for element in section.elements:
            yield tab, section, element


class SectionToModelBindingTests(unittest.TestCase):
    def test_every_section_model_attr_resolves_on_settings_model(self):
        model = SettingsModel()
        for tab, section in _walk_sections():
            with self.subTest(tab=tab.title, section=section.title):
                self.assertTrue(
                    hasattr(model, section.model_attr),
                    f"SettingsModel has no attribute '{section.model_attr}' "
                    f"required by section '{section.title}'",
                )
                self.assertTrue(
                    is_dataclass(getattr(model, section.model_attr)),
                    f"SettingsModel.{section.model_attr} must be a dataclass",
                )

    def test_every_element_attribute_is_a_field_on_its_section_dataclass(self):
        model = SettingsModel()
        for tab, section, element in _walk_elements():
            section_obj = getattr(model, section.model_attr)
            field_names = {f.name for f in fields(section_obj)}
            with self.subTest(section=section.title, attr=element.attribute):
                self.assertIn(
                    element.attribute, field_names,
                    f"{type(section_obj).__name__} has no field "
                    f"'{element.attribute}' (section '{section.title}')",
                )


class ElementShapeTests(unittest.TestCase):
    """Per-input-type invariants: sliders need ranges, dropdowns need options."""

    def test_slider_elements_have_a_min_and_max(self):
        for _, section, element in _walk_elements():
            if element.input_type is InputType.SLIDER:
                with self.subTest(section=section.title, attr=element.attribute):
                    self.assertIsNotNone(element.min_value)
                    self.assertIsNotNone(element.max_value)
                    self.assertLess(element.min_value, element.max_value)

    def test_dropdown_elements_have_options_and_placeholder(self):
        for _, section, element in _walk_elements():
            if element.input_type is InputType.DROPDOWN:
                with self.subTest(section=section.title, attr=element.attribute):
                    self.assertGreater(len(element.options), 0)
                    self.assertTrue(element.placeholder)

    def test_multiselect_elements_have_parallel_options_and_labels(self):
        for _, section, element in _walk_elements():
            if element.input_type is InputType.MULTISELECT:
                with self.subTest(section=section.title, attr=element.attribute):
                    self.assertGreater(len(element.options), 0)
                    self.assertEqual(
                        len(element.options), len(element.option_labels),
                        "options and option_labels must be parallel arrays",
                    )

    def test_every_element_has_a_tooltip(self):
        for _, section, element in _walk_elements():
            with self.subTest(section=section.title, attr=element.attribute):
                self.assertTrue(element.tooltip)


class UniquenessTests(unittest.TestCase):
    def test_tab_titles_are_unique(self):
        titles = [t.title for t in TABS]
        self.assertEqual(len(titles), len(set(titles)))

    def test_section_titles_are_unique_within_each_tab(self):
        for tab in TABS:
            titles = [s.title for s in tab.sections]
            with self.subTest(tab=tab.title):
                self.assertEqual(len(titles), len(set(titles)))

    def test_element_attributes_are_unique_within_each_section(self):
        for _, section in _walk_sections():
            attrs = [e.attribute for e in section.elements]
            with self.subTest(section=section.title):
                self.assertEqual(len(attrs), len(set(attrs)))


class RosterTests(unittest.TestCase):
    def test_digimon_names_roster_is_non_empty_and_unique(self):
        self.assertGreater(len(DIGIMON_NAMES), 0)
        self.assertEqual(len(DIGIMON_NAMES), len(set(DIGIMON_NAMES)))

    def test_starter_dropdown_first_option_is_random(self):
        starter_section = next(
            s for _, s in _walk_sections() if s.model_attr == "Starter"
        )
        digimon_element = next(
            e for e in starter_section.elements if e.attribute == "Digimon"
        )
        self.assertEqual(digimon_element.options[0], "Random")


if __name__ == "__main__":
    unittest.main()
