# Author: Christoph Merscher <dev@fmerscher.com>

import unittest

from digimon.rom.feature_support import (
    PatchRequest,
    RECRUITMENT_REQUIRED_PATCHES,
    patch_requests_from_settings,
    requested_patch_names,
    unsupported_features_for_layout,
    validate_layout_feature_support,
)
from digimon.rom.layouts import PAL_DE_LAYOUT
from digimon.settings import SettingsError
from tests.pal_de_evidence import PAL_DE_RECRUITMENT_REQUIRED_PATCH_NAMES
from tests.test_settings import _validConfig


class _HandlerStub:
    _layout = PAL_DE_LAYOUT


class PalDeFeatureSupportTests(unittest.TestCase):
    def test_recruitment_gate_uses_documented_patch_dependencies(self):
        self.assertEqual(RECRUITMENT_REQUIRED_PATCHES, PAL_DE_RECRUITMENT_REQUIRED_PATCH_NAMES)

    def test_pal_de_allows_mapped_global_feature_subset(self):
        config = _validConfig()
        config["digimon"]["Enabled"] = True
        config["digimon"]["DroppedItem"] = True
        config["digimon"]["DropRate"] = True
        config["digimon"]["MatchValue"] = True
        config["techs"]["Enabled"] = True
        config["techs"]["Power"] = True
        config["techs"]["Cost"] = True
        config["techs"]["Accuracy"] = True
        config["techs"]["Effect"] = True
        config["techs"]["EffectChance"] = True
        config["techs"]["TypeEffectiveness"] = True
        config["starter"]["Enabled"] = True
        config["starter"]["UseWeakestTech"] = True
        config["recruitment"]["Enabled"] = True
        config["chests"]["Enabled"] = True
        config["mapItems"]["Enabled"] = True
        config["mapItems"]["FoodOnly"] = True
        config["tokomon"]["Enabled"] = True
        config["tokomon"]["ConsumableOnly"] = True
        config["techGifts"]["Enabled"] = True
        config["evolution"]["Enabled"] = True
        config["evolution"]["Requirements"] = True
        config["evolution"]["ObtainAllMode"] = True
        config["evolution"]["SpecialEvolutions"] = True
        config["patches"]["Enabled"] = True
        config["patches"]["EvoItemStatGain"] = True
        config["patches"]["QuestItemsDroppable"] = True
        config["patches"]["BrainTrainTierOne"] = True
        config["patches"]["JukeboxGlitch"] = True
        config["patches"]["IncreaseLearnChance"] = True
        config["general"]["Hash"] = "abcdef1234567890abcdef1234567890"
        config["patches"]["ShowHashIntro"] = True
        config["patches"]["SkipIntro"] = True
        config["patches"]["UnlockAreas"] = True
        config["patches"]["SpawnRateEnabled"] = "1"
        config["patches"]["SpawnRate"] = 42

        self.assertEqual(unsupported_features_for_layout(config, PAL_DE_LAYOUT), [])
        validate_layout_feature_support(config, _HandlerStub())

    def test_pal_de_allows_dynamic_recruitment_offsets(self):
        config = _validConfig()
        config["recruitment"]["Enabled"] = True

        unsupported = unsupported_features_for_layout(config, PAL_DE_LAYOUT)

        self.assertNotIn("$.recruitment.Enabled", unsupported)
        self.assertNotIn("$.recruitment.Enabled (pp)", unsupported)
        self.assertNotIn("$.recruitment.Enabled (ogremon)", unsupported)
        self.assertNotIn("$.chests.Enabled", unsupported)
        self.assertNotIn("$.mapItems.Enabled", unsupported)

    def test_pal_de_allows_mapped_user_selected_patches(self):
        config = _validConfig()
        config["patches"]["Enabled"] = True
        config["patches"]["UnlockAreas"] = True
        config["patches"]["SkipIntro"] = True
        config["patches"]["ShowHashIntro"] = True
        config["patches"]["SpawnRateEnabled"] = "1"
        config["patches"]["Woah"] = True
        config["patches"]["Gabu"] = True
        config["patches"]["UnrigSlots"] = True
        config["patches"]["Softlock"] = True
        config["patches"]["LearnMoveAndCommand"] = True
        config["patches"]["FixDVChips"] = True
        config["patches"]["HappyVending"] = True

        unsupported = unsupported_features_for_layout(config, PAL_DE_LAYOUT)

        self.assertNotIn("$.patches.EvoItemStatGain (fixEvoItems)", unsupported)
        self.assertNotIn("$.patches.UnlockAreas (unlock)", unsupported)
        self.assertNotIn("$.patches.ShowHashIntro (hash)", unsupported)
        self.assertNotIn("$.patches.SkipIntro (intro)", unsupported)
        self.assertNotIn("$.patches.SpawnRateEnabled (spawn)", unsupported)
        self.assertNotIn("$.patches.HappyVending (happyVending)", unsupported)
        self.assertNotIn("$.patches.FixDVChips (fixDVChips)", unsupported)
        self.assertNotIn("$.patches.LearnMoveAndCommand (learnmoveandcommand)", unsupported)
        self.assertNotIn("$.patches.Gabu (gabumon)", unsupported)
        self.assertNotIn("$.patches.Woah (woah)", unsupported)
        self.assertNotIn("$.patches.UnrigSlots (slots)", unsupported)
        self.assertNotIn("$.patches.Softlock (softlock)", unsupported)

        self.assertEqual(unsupported, [])
        validate_layout_feature_support(config, _HandlerStub())

    def test_requested_patch_names_match_settings_paths(self):
        config = _validConfig()
        config["patches"]["EvoItemStatGain"] = True
        config["patches"]["UnlockAreas"] = True
        config["patches"]["SpawnRateEnabled"] = "1"

        self.assertEqual(
            requested_patch_names(config["patches"]),
            [
                ("fixEvoItems", "$.patches.EvoItemStatGain"),
                ("spawn", "$.patches.SpawnRateEnabled"),
                ("unlock", "$.patches.UnlockAreas"),
            ],
        )

    def test_patch_requests_from_settings_carry_runtime_values(self):
        config = _validConfig()
        config["general"]["Hash"] = "abcdef1234567890abcdef1234567890"
        config["patches"]["Enabled"] = True
        config["patches"]["ShowHashIntro"] = True
        config["patches"]["SpawnRateEnabled"] = "1"
        config["patches"]["SpawnRate"] = 42

        self.assertEqual(
            patch_requests_from_settings(config),
            [
                PatchRequest("spawn", "$.patches.SpawnRateEnabled", 42),
                PatchRequest("hash", "$.patches.ShowHashIntro", config["general"]["Hash"]),
            ],
        )

    def test_boolean_false_spawn_toggle_is_not_requested(self):
        config = _validConfig()
        config["patches"]["Enabled"] = True
        config["patches"]["SpawnRateEnabled"] = False

        self.assertNotIn(
            ("spawn", "$.patches.SpawnRateEnabled"),
            requested_patch_names(config["patches"]),
        )
        self.assertEqual(patch_requests_from_settings(config), [])

    def test_app_queue_uses_shared_patch_requests(self):
        from digimon.app import _queue_patches

        class HandlerStub:
            def __init__(self):
                self.queued = []

            def applyPatch(self, name, value):
                self.queued.append((name, value))

        config = _validConfig()
        config["general"]["Hash"] = "racehash"
        config["patches"]["Enabled"] = True
        config["patches"]["EvoItemStatGain"] = True
        config["patches"]["ShowHashIntro"] = True
        config["patches"]["SpawnRateEnabled"] = True
        config["patches"]["SpawnRate"] = 73
        handler = HandlerStub()

        _queue_patches(config, handler)

        self.assertEqual(
            handler.queued,
            [
                ("fixEvoItems", 0),
                ("spawn", 73),
                ("hash", "racehash"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
