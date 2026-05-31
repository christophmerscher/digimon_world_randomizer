# Author: Christoph Merscher <dev@fmerscher.com>

"""Tests for the PyQt6 GUI settings model.

The model has no Qt dependency so these tests run in the normal
``unittest`` suite. They check the four invariants the GUI relies on:

1. Defaults match the legacy Electron MainModel.ts behaviour.
2. JSON round-trips preserve every field that survives to_json.
3. The MD5 settings hash is stable, ignores the three excluded keys,
   and changes when any other field changes.
4. JSON produced by ``to_json`` validates against the existing schema in
   :mod:`digimon.settings.schema`, so the CLI can consume it unchanged.
"""

from __future__ import annotations

import json
import unittest

from digimon.settings.schema import validateSettings
from gui_qt.settings_model import (
    SPAWN_RATE_DEFAULT,
    SettingsModel,
    compute_settings_hash,
)


class DefaultsTests(unittest.TestCase):
    def test_defaults_match_electron_mainmodel(self):
        m = SettingsModel()

        # General
        self.assertEqual(m.General.InputFile,  "")
        self.assertEqual(m.General.OutputFile, "")
        self.assertEqual(m.General.LogLevel,   "casual")

        # Per-section Enabled flags default to False.
        self.assertFalse(m.Digimon.Enabled)
        self.assertFalse(m.Techs.Enabled)
        self.assertFalse(m.Starter.Enabled)
        self.assertFalse(m.Recruitment.Enabled)
        self.assertFalse(m.Chests.Enabled)
        self.assertFalse(m.Tokomon.Enabled)
        self.assertFalse(m.TechGifts.Enabled)
        self.assertFalse(m.MapItems.Enabled)
        self.assertFalse(m.Evolution.Enabled)
        self.assertFalse(m.Patches.Enabled)

        # Specific defaults that the GUI relies on.
        self.assertEqual(m.Digimon.ValuableItemCutoff,  1000)
        self.assertEqual(m.MapItems.ValuableItemCutoff, 1000)
        self.assertEqual(m.Techs.RandomizationMode,     "random")
        self.assertEqual(m.Starter.Digimon,             "Random")
        self.assertTrue(m.Starter.Rookie)
        self.assertEqual(m.Patches.SpawnRate, SPAWN_RATE_DEFAULT)


class JsonRoundTripTests(unittest.TestCase):
    def test_round_trip_preserves_user_choices(self):
        original = SettingsModel()
        original.General.InputFile  = "/tmp/rom.bin"
        original.General.OutputFile = "out.bin"
        original.General.Seed       = "12345"
        original.Digimon.Enabled    = True
        original.Digimon.DroppedItem = True
        original.Techs.Enabled      = True
        original.Techs.RandomizationMode = "shuffle"
        original.Patches.Enabled    = True
        original.Patches.SpawnRate  = 42

        reloaded = SettingsModel.from_json(original.to_json())

        self.assertEqual(reloaded.General.Seed,             "12345")
        self.assertEqual(reloaded.General.LogLevel,         "casual")
        self.assertTrue(reloaded.Digimon.Enabled)
        self.assertTrue(reloaded.Digimon.DroppedItem)
        self.assertEqual(reloaded.Techs.RandomizationMode,  "shuffle")
        self.assertEqual(reloaded.Patches.SpawnRate,        42)

    def test_load_collapses_output_to_basename_for_editability(self):
        # Mirrors the legacy Electron behaviour: when loading, the
        # user-facing OutputFile becomes a basename so changing the
        # input ROM later doesn't strand the output in the wrong dir.
        payload = json.dumps({
            "general": {
                "InputFile":  "/data/rom.bin",
                "OutputFile": "/data/randomized/out.bin",
                "LogLevel":   "race",
                "Seed":       "",
                "Hash":       "",
            },
        })
        m = SettingsModel.from_json(payload)
        self.assertEqual(m.General.OutputFile, "out.bin")

    def test_to_json_appends_bin_suffix_when_missing(self):
        m = SettingsModel()
        m.General.InputFile  = "/tmp/rom.bin"
        m.General.OutputFile = "no-suffix"
        raw = json.loads(m.to_json())
        self.assertTrue(raw["general"]["OutputFile"].endswith(".bin"))

    def test_to_json_forces_rookie_when_every_starter_level_is_unchecked(self):
        m = SettingsModel()
        m.Starter.Enabled    = True
        m.Starter.Rookie     = False     # user accidentally turned them all off
        m.Starter.Fresh      = False
        m.Starter.InTraining = False
        m.Starter.Champion   = False
        m.Starter.Ultimate   = False

        raw = json.loads(m.to_json())
        self.assertTrue(raw["starter"]["Rookie"])

    def test_to_json_output_path_is_empty_when_no_output_filename_set(self):
        m = SettingsModel()
        m.General.InputFile = "/tmp/rom.bin"
        m.General.OutputFile = ""
        raw = json.loads(m.to_json())
        self.assertEqual(raw["general"]["OutputFile"], "")


class HashTests(unittest.TestCase):
    def test_hash_is_stable_across_calls(self):
        a = SettingsModel()
        a.Digimon.Enabled = True
        b = SettingsModel()
        b.Digimon.Enabled = True
        self.assertEqual(a.to_json() and a.General.Hash,
                         b.to_json() and b.General.Hash)

    def test_hash_ignores_input_output_and_self_reference(self):
        a = SettingsModel(); a.General.InputFile  = "/x/rom.bin"
        b = SettingsModel(); b.General.InputFile  = "/y/rom.bin"
        a.to_json(); b.to_json()
        self.assertEqual(a.General.Hash, b.General.Hash)

        c = SettingsModel(); c.General.OutputFile = "alpha.bin"
        d = SettingsModel(); d.General.OutputFile = "beta.bin"
        c.to_json(); d.to_json()
        self.assertEqual(c.General.Hash, d.General.Hash)

    def test_hash_changes_when_a_meaningful_field_changes(self):
        a = SettingsModel()
        b = SettingsModel(); b.Digimon.Enabled = True
        a.to_json(); b.to_json()
        self.assertNotEqual(a.General.Hash, b.General.Hash)

    def test_compute_hash_strips_excluded_keys_at_every_depth(self):
        raw = {
            "general": {"InputFile": "x", "OutputFile": "y", "Hash": "z", "Seed": "42"},
            "nested":  {"Hash": "should-be-ignored", "value": 1},
        }
        digest_a = compute_settings_hash(raw)

        raw["general"]["InputFile"]  = "ANOTHER"
        raw["general"]["OutputFile"] = "ALSO"
        raw["general"]["Hash"]       = "DIFFERENT"
        raw["nested"]["Hash"]        = "STILL-IGNORED"
        digest_b = compute_settings_hash(raw)

        self.assertEqual(digest_a, digest_b)


class SchemaCompatibilityTests(unittest.TestCase):
    def test_output_validates_against_existing_settings_schema(self):
        m = SettingsModel()
        m.General.InputFile  = "/tmp/rom.bin"
        m.General.OutputFile = "out.bin"
        m.General.LogLevel   = "casual"
        m.Patches.SpawnRate  = 50

        config = json.loads(m.to_json())
        validateSettings(config)   # raises on failure


if __name__ == "__main__":
    unittest.main()
