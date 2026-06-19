# Author: Christoph Merscher <dev@fmerscher.com>

import unittest
from pathlib import Path

import script.util as scrutil
from data.digimon import find_by_id
from digimon.rom import script_offsets
from digimon.rom.pal_de_scenarios import (
    PAL_DE_ACTIVE_SCENARIO_PATH as PRODUCTION_PAL_DE_ACTIVE_SCENARIO_PATH,
    PAL_DE_RECRUITMENT_SCENARIO_PATH,
    PAL_DE_SCENARIO_BANKS,
    PAL_DE_SCENARIO_PATHS,
    load_pal_de_active_scenario,
    load_pal_de_scenarios,
    pal_de_scenario_bank,
    pal_de_scenario_bank_containing,
)
from digimon.rom.pal_de_script_offsets import PAL_DE_CHEST_ITEM_OFFSETS, PAL_DE_MAP_ITEM_OFFSETS
from digimon.rom.recruitment_offsets import pal_de_recruit_offsets_from_scenario
from digimon.rom.scenario import (
    CdFileEntry,
    RawCdImage,
    ScenarioCommandScanner,
    ScenarioFile,
    equivalent_run_count,
    group_adjacent_candidates,
    parse_scenario_pointers,
)
from tests.pal_de_evidence import (
    PAL_DE_ACTIVE_SCENARIO_FIRST_POINTER,
    PAL_DE_ACTIVE_SCENARIO_LAST_POINTER,
    PAL_DE_ACTIVE_SCENARIO_LBA,
    PAL_DE_ACTIVE_SCENARIO_ALLOCATED_SIZE,
    PAL_DE_ACTIVE_SCENARIO_PATH,
    PAL_DE_ACTIVE_SCENARIO_POINTER_COUNT,
    PAL_DE_ACTIVE_SCENARIO_RAW_OFFSET,
    PAL_DE_ACTIVE_SCENARIO_REPORTED_SIZE,
    PAL_DE_CHEST_OBJECT_CANDIDATE_COUNT,
    PAL_DE_CHEST_OBJECT_LOGICAL_GROUP_COUNT,
    PAL_DE_HASH_DG4_CANDIDATE_CONTEXT,
    PAL_DE_HASH_DG4_CANDIDATE_OFFSET,
    PAL_DE_HASH_RELATIVE_CANDIDATE_OFFSET,
    PAL_DE_LEARN_MOVE_OFFSETS,
    PAL_DE_MAP_ITEM_CANDIDATE_COUNT,
    PAL_DE_MONZAEMON_SPEC_EVO_OFFSETS,
    PAL_DE_RECRUITMENT_NAME_OFFSETS_PROMOTED,
    PAL_DE_RECRUITMENT_PROMOTED_TRIGGER_CHECK_COUNT,
    PAL_DE_RECRUITMENT_SCAN_EVIDENCE,
    PAL_DE_RESULT_TABLE_SPEC_EVO_OFFSETS,
    PAL_DE_SCENARIO_BANK_EVIDENCE,
    PAL_DE_SPAWN_RATE_ACTIVE_RANDOM_COMMAND_CANDIDATE_COUNT,
    PAL_DE_SPAWN_RATE_ALL_BANK_RANDOM_COMMAND_CANDIDATE_COUNTS,
    PAL_DE_TOKOMON_ITEM_OFFSETS,
)


PAL_DE_ROM = Path(__file__).resolve().parents[1] / "roms" / "Digimon World (Germany).bin"


class ScenarioParserTests(unittest.TestCase):
    def test_parse_scenario_pointers_stops_before_non_pointer_data(self):
        data = (
            b"\x08\x00\x00\x00"
            b"\x10\x00\x00\x00"
            b"\x20\x00\x00\x00"
            + (b"\x00" * 0x14)
            + b"SCN\\DG2.SCN"
        )

        self.assertEqual(parse_scenario_pointers(data), (0x08, 0x10, 0x20))

    def test_scanner_reports_value_candidates_and_encoded_text_hits(self):
        scenario = ScenarioFile(
            CdFileEntry(path="SCN/TEST.SCN", lba=1, size=0x20, is_directory=False),
            b"\x08\x00\x00\x00" + b"\xcc\x00AB" + scrutil.encode("Beta") + b"\xcc\x00",
            (0, 4, 8),
        )
        scanner = ScenarioCommandScanner(scenario)

        values = scanner.recruitment_trigger_candidates(204)
        text_hits = scanner.encoded_text_hits(scrutil.encode("Beta"))

        self.assertEqual([candidate.relative_offset for candidate in values], [4, 16])
        self.assertEqual([candidate.absolute_offset for candidate in values], [2380, 2392])
        self.assertEqual(values[0].pointer_index, 1)
        self.assertEqual(values[1].pointer_index, 2)
        self.assertEqual(text_hits[0].relative_offset, 8)
        self.assertEqual(text_hits[0].pointer_index, 2)


class PalDeScenarioEvidenceTests(unittest.TestCase):
    def setUp(self):
        if not PAL_DE_ROM.exists():
            self.skipTest("local PAL-DE ROM is not present")

    def _scenario(self):
        return RawCdImage(PAL_DE_ROM).read_scenario(PAL_DE_ACTIVE_SCENARIO_PATH)

    def test_finds_active_german_scenario_file(self):
        image = RawCdImage(PAL_DE_ROM)
        entry = image.find(PAL_DE_ACTIVE_SCENARIO_PATH)
        scenario = image.read_scenario(PAL_DE_ACTIVE_SCENARIO_PATH)

        self.assertEqual(PRODUCTION_PAL_DE_ACTIVE_SCENARIO_PATH, PAL_DE_ACTIVE_SCENARIO_PATH)
        self.assertEqual(PAL_DE_RECRUITMENT_SCENARIO_PATH, PAL_DE_ACTIVE_SCENARIO_PATH)
        self.assertFalse(entry.is_directory)
        self.assertEqual(entry.lba, PAL_DE_ACTIVE_SCENARIO_LBA)
        self.assertEqual(entry.data_offset, PAL_DE_ACTIVE_SCENARIO_RAW_OFFSET)
        self.assertEqual(entry.size, PAL_DE_ACTIVE_SCENARIO_REPORTED_SIZE)
        self.assertEqual(entry.allocation_size, PAL_DE_ACTIVE_SCENARIO_ALLOCATED_SIZE)
        self.assertEqual(scenario.size, PAL_DE_ACTIVE_SCENARIO_ALLOCATED_SIZE)
        self.assertEqual(scenario.reported_size, PAL_DE_ACTIVE_SCENARIO_REPORTED_SIZE)
        self.assertEqual(scenario.allocation_size, PAL_DE_ACTIVE_SCENARIO_ALLOCATED_SIZE)
        self.assertEqual(len(scenario.pointers), PAL_DE_ACTIVE_SCENARIO_POINTER_COUNT)
        self.assertEqual(scenario.pointers[0], PAL_DE_ACTIVE_SCENARIO_FIRST_POINTER)
        self.assertEqual(scenario.pointers[-1], PAL_DE_ACTIVE_SCENARIO_LAST_POINTER)

    def test_pal_de_scenario_bank_metadata_matches_local_rom(self):
        image = RawCdImage(PAL_DE_ROM)
        expected_paths = tuple(evidence.path for evidence in PAL_DE_SCENARIO_BANK_EVIDENCE)

        self.assertEqual(PAL_DE_SCENARIO_PATHS, expected_paths)
        self.assertEqual(tuple(bank.path for bank in PAL_DE_SCENARIO_BANKS), expected_paths)

        for expected, bank in zip(PAL_DE_SCENARIO_BANK_EVIDENCE, PAL_DE_SCENARIO_BANKS):
            entry = image.find(expected.path)
            scenario = image.read_scenario(expected.path)

            self.assertIs(pal_de_scenario_bank(expected.path), bank)
            self.assertEqual(bank.lba, expected.lba)
            self.assertEqual(bank.raw_offset, expected.raw_offset)
            self.assertEqual(bank.reported_size, expected.reported_size)
            self.assertEqual(bank.allocation_size, expected.allocated_size)
            self.assertEqual(bank.pointer_count, expected.pointer_count)
            self.assertEqual(bank.first_pointer, expected.first_pointer)
            self.assertEqual(bank.last_pointer, expected.last_pointer)
            self.assertEqual(entry.lba, expected.lba)
            self.assertEqual(entry.data_offset, expected.raw_offset)
            self.assertEqual(entry.size, expected.reported_size)
            self.assertEqual(entry.allocation_size, expected.allocated_size)
            self.assertEqual(scenario.reported_size, expected.reported_size)
            self.assertEqual(scenario.allocation_size, expected.allocated_size)
            self.assertEqual(len(scenario.pointers), expected.pointer_count)
            self.assertEqual(scenario.pointers[0], expected.first_pointer)
            self.assertEqual(scenario.pointers[-1], expected.last_pointer)

    def test_pal_de_scenario_loaders_preserve_disc_order(self):
        scenarios = load_pal_de_scenarios(PAL_DE_ROM)
        active = load_pal_de_active_scenario(PAL_DE_ROM)

        self.assertEqual(tuple(scenario.entry.path for scenario in scenarios), PAL_DE_SCENARIO_PATHS)
        self.assertEqual(active.entry.path, PAL_DE_ACTIVE_SCENARIO_PATH)
        self.assertEqual(active.data_offset, PAL_DE_ACTIVE_SCENARIO_RAW_OFFSET)

    def test_ntsc_relative_hash_candidate_is_deferred_scenario_padding(self):
        candidate_locations = []
        for bank in PAL_DE_SCENARIO_BANKS:
            candidate_offset = bank.raw_offset + PAL_DE_HASH_RELATIVE_CANDIDATE_OFFSET
            if bank.contains_allocated_offset(candidate_offset):
                candidate_locations.append(
                    (bank.path, candidate_offset, bank.contains_reported_offset(candidate_offset))
                )

        self.assertEqual(
            candidate_locations,
            [("SCN/DG4.SCN", PAL_DE_HASH_DG4_CANDIDATE_OFFSET, False)],
        )
        self.assertIs(
            pal_de_scenario_bank_containing(PAL_DE_HASH_DG4_CANDIDATE_OFFSET),
            pal_de_scenario_bank("SCN/DG4.SCN"),
        )

        scenario = RawCdImage(PAL_DE_ROM).read_scenario("SCN/DG4.SCN")
        relative = scenario.relative_offset(PAL_DE_HASH_DG4_CANDIDATE_OFFSET)
        self.assertFalse(scenario.contains_reported_relative(relative))
        self.assertEqual(
            scenario.data[relative:relative + len(PAL_DE_HASH_DG4_CANDIDATE_CONTEXT)],
            PAL_DE_HASH_DG4_CANDIDATE_CONTEXT,
        )

    def test_verified_pal_offsets_are_inside_active_scenario_pointer_slices(self):
        scenario = self._scenario()
        offsets = (
            ("seadramon-tech-gift", PAL_DE_LEARN_MOVE_OFFSETS[1], 10),
            ("beetle-tech-gift", PAL_DE_LEARN_MOVE_OFFSETS[0], 115),
            ("monzaemon-special-evo", PAL_DE_MONZAEMON_SPEC_EVO_OFFSETS[0], 161),
            ("tokomon-gifts", PAL_DE_TOKOMON_ITEM_OFFSETS[0], 200),
            ("special-evo-result-table", PAL_DE_RESULT_TABLE_SPEC_EVO_OFFSETS[0][0], 222),
        )

        for name, absolute_offset, pointer_index in offsets:
            relative_offset = scenario.relative_offset(absolute_offset)
            self.assertEqual(scenario.absolute_offset(relative_offset), absolute_offset, name)
            self.assertEqual(scenario.pointer_index_for_relative(relative_offset), pointer_index, name)

    def test_pal_de_chest_and_map_item_layouts_match_scenario_scans(self):
        scanner = ScenarioCommandScanner(self._scenario())
        chest_candidates = scanner.chest_object_candidates()
        map_candidates = scanner.map_item_candidates()
        logical_chest_count = equivalent_run_count(
            group_adjacent_candidates(chest_candidates, record_size=12),
            max_gap=0x2000,
        )

        self.assertEqual(len(chest_candidates), PAL_DE_CHEST_OBJECT_CANDIDATE_COUNT)
        self.assertEqual(logical_chest_count, PAL_DE_CHEST_OBJECT_LOGICAL_GROUP_COUNT)
        self.assertEqual(len(map_candidates), PAL_DE_MAP_ITEM_CANDIDATE_COUNT)
        self.assertEqual(
            tuple(candidate.absolute_offset for candidate in chest_candidates),
            PAL_DE_CHEST_ITEM_OFFSETS,
        )
        self.assertEqual(
            tuple(candidate.absolute_offset for candidate in map_candidates),
            PAL_DE_MAP_ITEM_OFFSETS,
        )
        self.assertGreater(len(PAL_DE_CHEST_ITEM_OFFSETS), len(script_offsets.chestItemOffsets))
        self.assertGreater(len(PAL_DE_MAP_ITEM_OFFSETS), len(script_offsets.mapItemOffsets))

    def test_pal_de_recruitment_scan_evidence_documents_noisy_raw_matches(self):
        scanner = ScenarioCommandScanner(self._scenario())
        recruit_table_by_trigger = {
            trigger: (name_offsets, digimon_id)
            for _trigger_offsets, name_offsets, trigger, digimon_id in script_offsets.recruitOffsets
        }

        for evidence in PAL_DE_RECRUITMENT_SCAN_EVIDENCE:
            name_offsets, digimon_id = recruit_table_by_trigger[evidence.trigger]
            digimon = find_by_id(digimon_id)
            self.assertIsNotNone(digimon)

            name_hits = scanner.encoded_text_hits(scrutil.encode(digimon.display_name))
            trigger_candidates = scanner.recruitment_trigger_candidates(evidence.trigger)

            self.assertEqual(digimon.display_name, evidence.name)
            self.assertEqual(len(name_offsets), evidence.ntsc_name_offsets)
            self.assertEqual(len(name_hits), evidence.pal_name_hits)
            self.assertEqual(len(trigger_candidates), evidence.pal_trigger_candidates)
            self.assertEqual(evidence.confidence, "raw-scan-audit")

    def test_pal_de_recruitment_offsets_are_promoted_from_status_checks(self):
        scenario = self._scenario()
        promoted = pal_de_recruit_offsets_from_scenario(scenario)

        self.assertEqual(len(promoted), len(script_offsets.recruitOffsets))
        self.assertEqual(
            sum(len(trigger_offsets) for trigger_offsets, _names, _trigger, _digi in promoted),
            PAL_DE_RECRUITMENT_PROMOTED_TRIGGER_CHECK_COUNT,
        )
        self.assertEqual(
            sum(len(name_offsets) for _triggers, name_offsets, _trigger, _digi in promoted),
            PAL_DE_RECRUITMENT_NAME_OFFSETS_PROMOTED,
        )

        for promoted_record, ntsc_record in zip(promoted, script_offsets.recruitOffsets):
            trigger_offsets, name_offsets, trigger, digimon_id = promoted_record
            ntsc_trigger_offsets, _ntsc_name_offsets, ntsc_trigger, ntsc_digimon_id = ntsc_record

            self.assertEqual(trigger, ntsc_trigger)
            self.assertEqual(digimon_id, ntsc_digimon_id)
            self.assertEqual(name_offsets, ())
            self.assertEqual(bool(trigger_offsets), bool(ntsc_trigger_offsets))

            for absolute_offset in trigger_offsets:
                relative = scenario.relative_offset(absolute_offset)
                self.assertEqual(scenario.data[relative - 4:relative - 2], bytes.fromhex("19 00"))
                self.assertEqual(
                    scenario.data[relative:relative + 2],
                    trigger.to_bytes(2, "little"),
                )

    def test_pal_de_spawn_rate_scan_is_too_noisy_to_promote(self):
        active_candidates = ScenarioCommandScanner(
            load_pal_de_active_scenario(PAL_DE_ROM)
        ).random_command_candidates()
        bank_counts = tuple(
            (
                scenario.entry.path,
                len(ScenarioCommandScanner(scenario).random_command_candidates()),
            )
            for scenario in load_pal_de_scenarios(PAL_DE_ROM)
        )

        self.assertEqual(
            len(active_candidates),
            PAL_DE_SPAWN_RATE_ACTIVE_RANDOM_COMMAND_CANDIDATE_COUNT,
        )
        self.assertEqual(
            bank_counts,
            PAL_DE_SPAWN_RATE_ALL_BANK_RANDOM_COMMAND_CANDIDATE_COUNTS,
        )
        self.assertGreater(sum(count for _path, count in bank_counts), 10_000)


if __name__ == "__main__":
    unittest.main()
