# Author: Christoph Merscher <dev@fmerscher.com>

"""Coverage and invariant tests for the player-facing ``data/`` enums."""

import unittest

import digimon.data as legacy_data
from data.digimon import (
    ChampionDigimon,
    DigimonLevel,
    FreshDigimon,
    InTrainingDigimon,
    PerfectDigimon,
    RookieDigimon,
    all_partner_digimon,
    find_by_display_name,
    find_by_id,
    partner_digimon_by_level,
)
from data.item import (
    BANNED_ITEM_IDS,
    CONSUMABLE_ITEM_IDS,
    EVO_ITEM_FIRST_ID,
    ItemCategory,
    QUEST_ITEM_IDS,
    is_banned,
    is_consumable,
    is_evo_item,
    is_quest,
)
from data.technique import TechniqueEffect, Techniques, TechniquesRange, tech_id


class DigimonEnumTests(unittest.TestCase):
    def test_every_partner_id_is_unique(self):
        ids = [member.id for member in all_partner_digimon()]
        self.assertEqual(len(ids), len(set(ids)), "duplicate digimon IDs in enums")

    def test_level_enum_values_match_legacy_byte_values(self):
        self.assertEqual(int(DigimonLevel.FRESH.value, 16),       legacy_data.levelsByName["FRESH"])
        self.assertEqual(int(DigimonLevel.IN_TRAINING.value, 16), legacy_data.levelsByName["IN-TRAINING"])
        self.assertEqual(int(DigimonLevel.ROOKIE.value, 16),      legacy_data.levelsByName["ROOKIE"])
        self.assertEqual(int(DigimonLevel.CHAMPION.value, 16),    legacy_data.levelsByName["CHAMPION"])
        self.assertEqual(int(DigimonLevel.ULTIMATE.value, 16),    legacy_data.levelsByName["ULTIMATE"])

    def test_koromon_is_in_training_not_fresh(self):
        # Regression: the partial rewrite labelled Koromon FRESH.
        self.assertIs(InTrainingDigimon.KOROMON.level, DigimonLevel.IN_TRAINING)

    def test_lookups_round_trip_by_id_and_name(self):
        self.assertIs(find_by_id(0x03),                 RookieDigimon.AGUMON)
        self.assertIs(find_by_display_name("Agumon"),   RookieDigimon.AGUMON)
        self.assertIs(find_by_id(0x05),                 ChampionDigimon.GREYMON)
        self.assertIs(find_by_id(0x41),                 PerfectDigimon.METALETEMON)
        self.assertIsNone(find_by_id(0x42))
        self.assertIsNone(find_by_display_name("NotAPartnerDigimon"))

    def test_by_level_returns_only_members_of_that_level(self):
        rookies = partner_digimon_by_level(DigimonLevel.ROOKIE)
        self.assertEqual(set(rookies), set(RookieDigimon))
        for member in rookies:
            self.assertIs(member.level, DigimonLevel.ROOKIE)

    def test_starter_flag_matches_legacy_rookies_tuple(self):
        starters = {m.id for m in RookieDigimon if m.value.starter}
        # Only Agumon and Gabumon are tagged starter=True in the dataclass —
        # legacy `digimon.data.rookies` is a wider "candidate" list that was
        # never used as the authoritative starter set.
        self.assertEqual(starters, {0x03, 0x11})

    def test_fresh_and_in_training_enums_are_non_empty(self):
        self.assertGreaterEqual(len(list(FreshDigimon)), 1)
        self.assertGreaterEqual(len(list(InTrainingDigimon)), 1)


class TechniqueEnumTests(unittest.TestCase):
    def test_tech_id_helper_decodes_hex_values(self):
        self.assertEqual(tech_id(Techniques.FIRE_TOWER),    0x00)
        self.assertEqual(tech_id(Techniques.BUBBLE_8),      0x78)

    def test_techniques_cover_all_legacy_tech_ids(self):
        legacy_ids = set(legacy_data.techs.keys())
        enum_ids = {tech_id(t) for t in Techniques}
        missing = legacy_ids - enum_ids
        self.assertEqual(missing, set(), f"Techniques enum is missing ids: {sorted(missing)}")

    def test_effect_and_range_enums_match_legacy_tables(self):
        self.assertEqual(int(TechniqueEffect.POISON.value,   16), 0x01)
        self.assertEqual(int(TechniquesRange.SHORT.value,    16), 0x01)
        self.assertEqual(int(TechniquesRange.SELF.value,     16), 0x04)


class ItemRangeTests(unittest.TestCase):
    def test_consumable_set_matches_legacy_constants(self):
        from digimon.models.item import Item

        self.assertEqual(set(Item.consumableItems), CONSUMABLE_ITEM_IDS)
        self.assertEqual(set(Item.questItems),      QUEST_ITEM_IDS)
        self.assertEqual(set(Item.bannedItems),     BANNED_ITEM_IDS)

    def test_predicates_match_set_membership(self):
        self.assertTrue(is_consumable(0x00))
        self.assertTrue(is_consumable(0x7F))
        self.assertFalse(is_consumable(0x73))

        self.assertTrue(is_quest(0x73))
        self.assertFalse(is_quest(0x00))

        self.assertTrue(is_banned(0x53))
        self.assertFalse(is_banned(0x52))

    def test_is_evo_item_requires_both_sort_and_id_threshold(self):
        statevo_byte = ItemCategory.STATEVO.value
        food_byte    = ItemCategory.FOOD.value

        self.assertTrue (is_evo_item(EVO_ITEM_FIRST_ID,     statevo_byte))
        self.assertFalse(is_evo_item(EVO_ITEM_FIRST_ID - 1, statevo_byte))
        self.assertFalse(is_evo_item(EVO_ITEM_FIRST_ID,     food_byte))


if __name__ == "__main__":
    unittest.main()
