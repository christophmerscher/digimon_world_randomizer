# Author: Christoph Merscher <dev@fmerscher.com>

import struct
import unittest
from pathlib import Path

import script.util as scrutil
from digimon.util import animIDTechSlot
from digimon.rom import patch_data
from digimon.rom.layouts import PAL_DE_LAYOUT, layout_for_region
from digimon.rom.pal_de_script_offsets import PAL_DE_CHEST_ITEM_OFFSETS, PAL_DE_MAP_ITEM_OFFSETS
from digimon.rom.patches.registry import ALWAYS_ON_PATCHES, PATCHES
from digimon.rom.region import RomRegion, detect_rom_region
from digimon.rom.struct_codec import read_block_with_exclusions
from tests.pal_de_evidence import (
    GLOBAL_DISABLED_PATCH_NAMES,
    KAEFER_POKAL,
    MUELLBERG_BEI_NACHT,
    PAL_DE_CHECK_MOVE_OFFSETS,
    PAL_DE_DEVI_CHIP_NAME_CONTEXTS,
    PAL_DE_DEVI_CHIP_NAME_OFFSETS,
    PAL_DE_DV_CHIP_DESCRIPTION_CANDIDATE_OFFSETS,
    PAL_DE_DV_CHIP_DESCRIPTION_CANDIDATE_CONTEXTS,
    PAL_DE_DV_CHIP_DESCRIPTION_CONTEXTS,
    PAL_DE_DV_CHIP_DESCRIPTION_OFFSETS,
    PAL_DE_EVO_TARGET_UNIFY_CONTEXT_OFFSET,
    PAL_DE_EVO_TARGET_UNIFY_OFFSETS,
    PAL_DE_EVO_TARGET_UNIFY_ORIGINAL_CONTEXT,
    PAL_DE_FIX_EVO_ITEMS_CONTEXT,
    PAL_DE_FIX_EVO_ITEMS_OFFSET,
    PAL_DE_GABUMON_NAIVE_DELTA_CANDIDATE_OFFSET,
    PAL_DE_GABUMON_NTSC_RAW_CANDIDATE_OFFSET,
    PAL_DE_GABUMON_PATCH_ORIGINAL_CONTEXT,
    PAL_DE_GABUMON_TFS_OFFSET,
    PAL_DE_GABUMON_TFS_PATH,
    PAL_DE_GABUMON_TFS_RELATIVE_PATCH_OFFSET,
    PAL_DE_GIROMON_SPEC_EVO_OFFSETS,
    PAL_DE_HAPPY_VENDING_ACTIVE_TEXT_CANDIDATE_OFFSET,
    PAL_DE_HAPPY_VENDING_ITEM_ID_OFFSETS,
    PAL_DE_HAPPY_VENDING_MENU_CONTEXTS,
    PAL_DE_HAPPY_VENDING_MENU_OFFSETS,
    PAL_DE_HAPPY_VENDING_PRICE_OFFSETS,
    PAL_DE_HAPPY_VENDING_RESULT_CONTEXTS,
    PAL_DE_HAPPY_VENDING_RESULT_OFFSETS,
    PAL_DE_HASH_DG4_CANDIDATE_OFFSET,
    PAL_DE_INCOMPATIBLE_ROM_PATCH_NAMES,
    PAL_DE_INTRO_HASH_OFFSET,
    PAL_DE_INTRO_HASH_ORIGINAL_TEXT,
    PAL_DE_INTRO_HASH_SIZE,
    PAL_DE_INTRO_SKIP_INSIDE_DEST,
    PAL_DE_INTRO_SKIP_INSIDE_OFFSET,
    PAL_DE_INTRO_SKIP_INSIDE_ORIGINAL_COMMAND,
    PAL_DE_INTRO_SKIP_INSIDE_TARGET_COMMAND,
    PAL_DE_INTRO_SKIP_INSIDE_TARGET_OFFSET,
    PAL_DE_INTRO_SKIP_OUTSIDE_DEST,
    PAL_DE_INTRO_SKIP_OUTSIDE_OFFSET,
    PAL_DE_INTRO_SKIP_OUTSIDE_ORIGINAL_COMMAND,
    PAL_DE_INTRO_SKIP_OUTSIDE_TARGET_COMMAND,
    PAL_DE_INTRO_SKIP_OUTSIDE_TARGET_OFFSET,
    PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_CONTEXT,
    PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_OFFSET,
    PAL_DE_LEARN_MOVE_AND_COMMAND_REJECTED_CANDIDATE_CONTEXT,
    PAL_DE_LEARN_MOVE_AND_COMMAND_REJECTED_CANDIDATE_OFFSET,
    PAL_DE_LEARN_MOVE_OFFSETS,
    PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES,
    PAL_DE_MAMEMON_SPEC_EVO_LANGUAGE_COPY_CANDIDATE_OFFSETS,
    PAL_DE_MAMEMON_SPEC_EVO_CANDIDATE_OFFSETS,
    PAL_DE_METALMAMEMON_SPEC_EVO_OFFSETS,
    PAL_DE_MONZAEMON_BOX_CHOICE_CONTEXT_OFFSETS,
    PAL_DE_MONZAEMON_REACTION_CONTEXT_OFFSETS,
    PAL_DE_MONZAEMON_SPEC_EVO_OFFSETS,
    PAL_DE_OGREMON_SOFTLOCK_OFFSETS,
    PAL_DE_PATCH_EVIDENCE,
    PAL_DE_PP_CALCULATION_CANDIDATE_OFFSET,
    PAL_DE_PP_CALCULATION_ORIGINAL_CONTEXT,
    PAL_DE_PP_CALCULATION_PATCH_VALUE,
    PAL_DE_RESET_BUTTON_NAIVE_SLES_DELTA_CANDIDATE_OFFSETS,
    PAL_DE_RESET_BUTTON_CUSTOM_FUNCTION_OFFSET,
    PAL_DE_RESET_BUTTON_CUSTOM_FUNCTION_ORIGINAL_BYTES,
    PAL_DE_RESET_BUTTON_HOOK_CONTEXT_OFFSET,
    PAL_DE_RESET_BUTTON_HOOK_OFFSET,
    PAL_DE_RESET_BUTTON_HOOK_ORIGINAL_CONTEXT,
    PAL_DE_RECRUITMENT_REQUIRED_PATCH_NAMES,
    PAL_DE_RECRUITMENT_NAME_OFFSETS_PROMOTED,
    PAL_DE_RECRUITMENT_PROMOTED_TRIGGER_CHECK_COUNT,
    PAL_DE_RESULT_TABLE_SPEC_EVO_LANGUAGE_COPY_CANDIDATES,
    PAL_DE_RESULT_TABLE_SPEC_EVO_CANDIDATE_OFFSETS,
    PAL_DE_RESULT_TABLE_SPEC_EVO_OFFSETS,
    PAL_DE_SCRIPT_EVIDENCE,
    PAL_DE_SHELLMON_STATUS_CHECK_OFFSET,
    PAL_DE_SPAWN_RATE_ACTIVE_RANDOM_COMMAND_CANDIDATE_COUNT,
    PAL_DE_SPAWN_RATE_COMMANDS,
    PAL_DE_SPAWN_RATE_MAMEMON_OFFSETS,
    PAL_DE_SPAWN_RATE_METALMAMEMON_OFFSETS,
    PAL_DE_SPAWN_RATE_OTAMAMON_OFFSETS,
    PAL_DE_SPAWN_RATE_PIXIMON_OFFSETS,
    PAL_DE_STARTER_CHECK_OFFSETS,
    PAL_DE_STARTER_EQUIP_ANIM_OFFSETS,
    PAL_DE_STARTER_LEARN_TECH_OFFSETS,
    PAL_DE_STARTER_SET_OFFSETS,
    PAL_DE_STARTER_STAT_CHECK_OFFSET,
    PAL_DE_SOFTLOCK_MOVE_TO_BRANCH_CONTEXT,
    PAL_DE_SOFTLOCK_MOVE_TO_BRANCH_OFFSETS,
    PAL_DE_SOFTLOCK_LEOMON_CAVE_CONTEXTS,
    PAL_DE_SOFTLOCK_LEOMON_CAVE_OFFSETS,
    PAL_DE_SOFTLOCK_NAIVE_SLES_DELTA_CANDIDATE_OFFSETS,
    PAL_DE_SOFTLOCK_ROTATION_BRANCH_CONTEXTS,
    PAL_DE_SOFTLOCK_ROTATION_BRANCH_OFFSETS,
    PAL_DE_SOFTLOCK_TOY_TOWN_COMMAND_CONTEXTS,
    PAL_DE_SOFTLOCK_TOY_TOWN_COORDINATE_OFFSETS,
    PAL_DE_SPEC_EVO_EVIDENCE,
    PAL_DE_SUKAMON_SPEC_EVO_LANGUAGE_COPY_CANDIDATE_OFFSETS,
    PAL_DE_SUKAMON_SPEC_EVO_CANDIDATE_OFFSETS,
    PAL_DE_SUKAMON_SPEC_EVO_OFFSETS,
    PAL_DE_TOKOMON_ITEM_OFFSETS,
    PAL_DE_TOY_TOWN_LOCK_CHECK_OFFSETS,
    PAL_DE_TOY_TOWN_UNLOCK_CANDIDATE_VALUE,
    PAL_DE_UNLOCK_GREYLORD_OFFSETS,
    PAL_DE_UNLOCK_GREYLORD_VALUE,
    PAL_DE_UNLOCK_ICE_OFFSETS,
    PAL_DE_UNLOCK_ICE_VALUE,
    PAL_DE_UNRIG_SLOTS_CANDIDATE_CONTEXTS,
    PAL_DE_UNRIG_SLOTS_CANDIDATE_OFFSETS,
    PAL_DE_WOAH_ENCODED_TEXT,
    PAL_DE_WOAH_NAIVE_SLES_DELTA_CANDIDATE_OFFSET,
    PAL_DE_WOAH_NTSC_REPLACEMENT_AS_PAL_TEXT,
    PAL_DE_WOAH_PAYLOAD,
    PAL_DE_WOAH_TEXT_CONTEXTS,
    PAL_DE_WOAH_TEXT_OFFSETS,
    PAL_DE_STATE_SAFE_PATCH_NAMES,
    PAL_DE_UNMAPPED_ALWAYS_ON_PATCH_NAMES,
    PAL_DE_UNMAPPED_ROM_PATCH_NAMES,
    TYPE_EFFECTIVENESS_VALUES,
)


PAL_DE_ROM = Path(__file__).resolve().parents[1] / "roms" / "Digimon World (Germany).bin"


def _read_block(handle, name: str) -> bytes:
    block = PAL_DE_LAYOUT.require_block(name)
    return read_block_with_exclusions(
        handle,
        block.offset,
        block.size,
        block.exclusion_offsets,
        block.exclusion_size,
    )


def _unpack_block(handle, name: str) -> list[tuple]:
    block = PAL_DE_LAYOUT.require_block(name)
    assert block.count is not None
    raw = _read_block(handle, name)
    record_size = struct.calcsize(block.format)
    assert len(raw) == record_size * block.count
    return [
        struct.unpack_from(block.format, raw, index * record_size)
        for index in range(block.count)
    ]


class PalDeLayoutTests(unittest.TestCase):
    def setUp(self):
        if not PAL_DE_ROM.exists():
            self.skipTest("local PAL-DE ROM is not present")

    def test_detects_layout_for_local_german_disc(self):
        with PAL_DE_ROM.open("rb") as rom:
            info = detect_rom_region(rom)

        self.assertEqual(info.region, RomRegion.PAL)
        self.assertEqual(info.serial, "SLES_034.34")
        self.assertIs(layout_for_region(info), PAL_DE_LAYOUT)
        self.assertFalse(PAL_DE_LAYOUT.complete)

    def test_handler_loads_pal_de_name_less_records_and_special_evolutions(self):
        from digimon.handler import DigimonWorldHandler
        from log.logger import Logger

        logger = Logger("race")
        handler = DigimonWorldHandler(str(PAL_DE_ROM), logger, seed=1)

        self.assertFalse(logger.error)
        self.assertIs(handler._layout, PAL_DE_LAYOUT)
        self.assertEqual(handler.digimonData[3].name, "Agumon")
        self.assertEqual(handler.itemData[0].name, "Item 00")
        self.assertEqual(len(handler.chestItems), len(PAL_DE_CHEST_ITEM_OFFSETS))
        self.assertEqual(len(handler.mapItems), len(PAL_DE_MAP_ITEM_OFFSETS))
        self.assertEqual(len(handler.recruitData), 40)
        self.assertEqual(
            sum(len(offsets) for offsets, _digimon_id, _name_offsets in handler.recruitData.values()),
            PAL_DE_RECRUITMENT_PROMOTED_TRIGGER_CHECK_COUNT,
        )
        self.assertEqual(
            sum(len(name_offsets) for _offsets, _digimon_id, name_offsets in handler.recruitData.values()),
            PAL_DE_RECRUITMENT_NAME_OFFSETS_PROMOTED,
        )
        self.assertEqual(len(handler.specEvos), len(PAL_DE_SPEC_EVO_EVIDENCE))

    def test_pal_de_writer_strips_synthetic_names_from_name_less_records(self):
        from digimon.handler import DigimonWorldHandler
        from digimon.rom.struct_codec import pack_array
        from digimon.rom.writer import RomWriter
        from log.logger import Logger

        logger = Logger("race")
        handler = DigimonWorldHandler(str(PAL_DE_ROM), logger, seed=1)
        writer = RomWriter(logger, PAL_DE_LAYOUT)

        digimon_record = writer._record_for_block(
            "digimonData",
            handler.digimonData[3].unpackedFormat(),
        )
        item_record = writer._record_for_block(
            "itemData",
            handler.itemData[0].unpackedFormat(),
        )

        self.assertNotIsInstance(digimon_record[0], bytes)
        self.assertNotIsInstance(item_record[0], bytes)
        self.assertEqual(
            len(pack_array([digimon_record], PAL_DE_LAYOUT.require_block("digimonData").format)),
            struct.calcsize(PAL_DE_LAYOUT.require_block("digimonData").format),
        )
        self.assertEqual(
            len(pack_array([item_record], PAL_DE_LAYOUT.require_block("itemData").format)),
            struct.calcsize(PAL_DE_LAYOUT.require_block("itemData").format),
        )

    def test_pal_de_writer_updates_only_chest_and_map_item_command_bytes(self):
        from digimon.rom.state import RomState
        from digimon.rom.writer import RomWriter
        from log.logger import Logger

        class RecordingHandle:
            def __init__(self):
                self.offset = 0
                self.writes = []

            def seek(self, offset, whence=0):
                self.offset = offset

            def write(self, payload):
                self.writes.append((self.offset, payload))
                return len(payload)

        state = RomState()
        state.chestItems = {PAL_DE_CHEST_ITEM_OFFSETS[0]: 0x12}
        state.mapItems = {PAL_DE_MAP_ITEM_OFFSETS[0]: 0x2C}
        handle = RecordingHandle()
        writer = RomWriter(Logger("race"), PAL_DE_LAYOUT)

        writer._write_chest_items(handle, state)
        writer._write_map_items(handle, state)

        self.assertEqual(
            handle.writes,
            [
                (PAL_DE_CHEST_ITEM_OFFSETS[0], bytes([scrutil.spawnChest, 0x12])),
                (PAL_DE_MAP_ITEM_OFFSETS[0], bytes([scrutil.spawnItem, 0x2C])),
            ],
        )

    def test_verified_offsets_match_pal_de_structures(self):
        with PAL_DE_ROM.open("rb") as rom:
            rom.seek(PAL_DE_LAYOUT.patch_offsets["typeEffectivenessOffset"])
            type_chart = rom.read(49)
            self.assertEqual(set(type_chart), TYPE_EFFECTIVENESS_VALUES)

            tech_learn = _unpack_block(rom, "techLearn")
            self.assertEqual(len(tech_learn), 0x3A)
            self.assertLessEqual(max(value for row in tech_learn for value in row), 40)
            self.assertGreater(sum(1 for row in tech_learn for value in row if value), 100)

            tech_brain = _unpack_block(rom, "techBrain")
            self.assertEqual(tech_brain[0], (0, 0, 0))
            self.assertEqual(tech_brain[-1], (80, 50, 50))

            tech_data = _unpack_block(rom, "techData")
            sensible_techs = sum(
                1
                for row in tech_data
                if row[2] <= 2500
                and 0 <= row[3] <= 255
                and 1 <= row[5] <= 4
                and 0 <= row[6] <= 6
                and 0 <= row[7] <= 4
                and 0 <= row[8] <= 100
                and 0 <= row[9] <= 100
            )
            self.assertGreaterEqual(sensible_techs, 120)

            tech_tiers = _unpack_block(rom, "techTierList")
            tiered_ids = [tech_id for row in tech_tiers for tech_id in row]
            self.assertEqual(len(tech_tiers), 7)
            self.assertEqual(len(tiered_ids), 56)
            self.assertEqual(len(set(tiered_ids)), 56)
            self.assertEqual(set(tiered_ids), set(range(0x3A)) - {0x30, 0x39})
            self.assertEqual(tech_tiers[0][0], 0x02)  # Spit Fire
            self.assertEqual(tech_tiers[1][0], 0x2B)  # Sonic Jab
            self.assertEqual(tech_tiers[4][0], 0x17)  # Tear Drop
            for specialty, row in enumerate(tech_tiers):
                self.assertEqual({tech_data[tech_id][6] for tech_id in row}, {specialty})

            evo_reqs = _unpack_block(rom, "evoReqs")
            req_values = [value for row in evo_reqs for value in row[:11] + row[12:]]
            battles = [row[11] for row in evo_reqs]
            self.assertGreater(req_values.count(0xFFFF), 400)
            self.assertGreaterEqual(min(battles), -2)
            self.assertLessEqual(max(battles), 100)

            evo_stats = _unpack_block(rom, "evoStats")
            self.assertEqual([row[6] for row in evo_stats], list(range(len(evo_stats))))
            self.assertLessEqual(max(max(row[:6]) for row in evo_stats), 9000)

            evo_to_from = _unpack_block(rom, "evoToFrom")
            evo_values = [value for row in evo_to_from for value in row]
            self.assertGreater(evo_values.count(0xFF), 400)
            self.assertLessEqual(max(evo_values), 0xFF)

            item_data = _unpack_block(rom, "itemData")
            self.assertEqual(len(item_data), 0x80)
            self.assertEqual({row[2] for row in item_data}, {0, 1, 2, 3, 4, 5})
            self.assertEqual(item_data[0], (100, 0, 0, 2, True))
            self.assertEqual(item_data[0x47][2], 4)
            self.assertEqual(item_data[0x73][2], 5)
            self.assertFalse(item_data[0x73][4])

            digimon_data = _unpack_block(rom, "digimonData")
            self.assertEqual(len(digimon_data), 0xB4)
            self.assertEqual(digimon_data[1][4], 1)   # Botamon
            self.assertEqual(digimon_data[3][4], 3)   # Agumon
            self.assertEqual(digimon_data[5][4], 4)   # Greymon
            self.assertEqual(digimon_data[0x0C][4], 5)  # MetalGreymon
            sensible_rows = sum(
                1
                for row in digimon_data
                if 0 <= row[0] <= 1000
                and 0 <= row[1] <= 1000
                and 0 <= row[2] <= 1000
                and 0 <= row[3] <= 3
                and 0 <= row[4] <= 5
                and all(0 <= value <= 6 or value == 0xFF for value in row[5:8])
                and 0 <= row[8] <= 0x7F
                and 0 <= row[9] <= 100
                and all(0 <= value <= 0x78 or value == 0xFF for value in row[10:26])
            )
            self.assertGreaterEqual(sensible_rows, 160)

            track_names = _read_block(rom, "trackName")
            names = [name for name in track_names.split(b"\0\0") if name]
            self.assertEqual(len(track_names), 0x93A)
            self.assertEqual(len(names), 86)
            self.assertEqual(names[0], scrutil.encode("Heimatwald"))
            self.assertEqual(names[41], MUELLBERG_BEI_NACHT)
            self.assertEqual(names[-1], KAEFER_POKAL)
            self.assertGreater(max(len(name) for name in names), 24)
            for index in range(0, len(track_names), 2):
                pair = track_names[index:index + 2]
                self.assertTrue(
                    pair == b"\0\0" or pair[0] in (0x0D, 0x81, 0x82, 0x83),
                    f"Unexpected pair {pair.hex()} at logical offset {index:#x}",
                )

    def test_pal_de_script_layout_is_partial_and_explicit(self):
        scripts = PAL_DE_LAYOUT.require_scripts()
        expected_spec_evos = (
            (PAL_DE_MONZAEMON_SPEC_EVO_OFFSETS, 0x0E, 0x0B),
            (PAL_DE_GIROMON_SPEC_EVO_OFFSETS, 0x29, 0x0D),
            (PAL_DE_METALMAMEMON_SPEC_EVO_OFFSETS, 0x1B, 0x0D),
            *(
                ((offset,), target_id, from_id)
                for offset, target_id, from_id in PAL_DE_RESULT_TABLE_SPEC_EVO_OFFSETS
            ),
            (PAL_DE_SUKAMON_SPEC_EVO_OFFSETS, 0x27, 0x27),
        )

        self.assertEqual(scripts.starterSetDigimonOffset, PAL_DE_STARTER_SET_OFFSETS)
        self.assertEqual(scripts.starterChkDigimonOffset, PAL_DE_STARTER_CHECK_OFFSETS)
        self.assertEqual(scripts.starterLearnTechOffset, PAL_DE_STARTER_LEARN_TECH_OFFSETS)
        self.assertEqual(scripts.starterEquipAnimOffset, PAL_DE_STARTER_EQUIP_ANIM_OFFSETS)
        self.assertEqual(scripts.starterStatChkDigimonOffset, PAL_DE_STARTER_STAT_CHECK_OFFSET)
        self.assertEqual(scripts.tokoItemOffsets, PAL_DE_TOKOMON_ITEM_OFFSETS)
        self.assertEqual(scripts.learnMoveOffsets, PAL_DE_LEARN_MOVE_OFFSETS)
        self.assertEqual(scripts.checkMoveOffsets, PAL_DE_CHECK_MOVE_OFFSETS)
        self.assertEqual(scripts.chestItemOffsets, PAL_DE_CHEST_ITEM_OFFSETS)
        self.assertEqual(scripts.mapItemOffsets, PAL_DE_MAP_ITEM_OFFSETS)
        self.assertEqual(scripts.recruitOffsets, ())
        self.assertTrue(scripts.dynamicRecruitOffsets)
        self.assertEqual(scripts.specEvoOffsets, expected_spec_evos)
        self.assertNotIn("chestItemOffsets", PAL_DE_LAYOUT.unmapped)
        self.assertNotIn("mapItemOffsets", PAL_DE_LAYOUT.unmapped)
        self.assertNotIn("recruitOffsets", PAL_DE_LAYOUT.unmapped)

    def test_verified_pal_de_starter_learning_script_offsets(self):
        with PAL_DE_ROM.open("rb") as rom:
            starter_checks = []
            starter_techs = []
            starter_slots = []

            for offset in PAL_DE_STARTER_CHECK_OFFSETS:
                rom.seek(offset)
                starter_checks.append(rom.read(4))

            for offset in PAL_DE_STARTER_LEARN_TECH_OFFSETS:
                rom.seek(offset)
                starter_techs.append(rom.read(4))

            for offset in PAL_DE_STARTER_EQUIP_ANIM_OFFSETS:
                rom.seek(offset)
                anim_id = rom.read(4)
                starter_slots.append(animIDTechSlot(anim_id[0]))

        self.assertEqual(starter_checks, [bytes.fromhex("03 00 01 24"), bytes.fromhex("11 00 01 24")])
        self.assertEqual(starter_techs, [bytes.fromhex("02 00 04 24"), bytes.fromhex("2b 00 04 24")])
        self.assertEqual(starter_slots, [1, 3])

    def test_verified_pal_de_starter_set_script_offsets(self):
        with PAL_DE_ROM.open("rb") as rom:
            starter_ids = []
            for offset in PAL_DE_STARTER_SET_OFFSETS:
                rom.seek(offset)
                starter_ids.append(rom.read(4))

            rom.seek(0x15782620)
            branch_context = rom.read(0x60)

        self.assertEqual(
            starter_ids,
            [bytes.fromhex("03 00 10 24"), bytes.fromhex("11 00 10 24")],
        )
        self.assertIn(bytes.fromhex("fe 00 04 24"), branch_context)
        self.assertIn(bytes.fromhex("04 00 40 14"), branch_context)
        self.assertIn(bytes.fromhex("21 20 00 02"), branch_context)

    def test_verified_pal_de_starter_stat_check_script_offset(self):
        with PAL_DE_ROM.open("rb") as rom:
            rom.seek(PAL_DE_STARTER_STAT_CHECK_OFFSET)
            starter_id = rom.read(1)

            rom.seek(PAL_DE_STARTER_STAT_CHECK_OFFSET - 0x11)
            context = rom.read(0x40)

        self.assertEqual(starter_id, bytes([0x03]))
        self.assertEqual(context.count(bytes.fromhex("67 03 18 00")), 1)
        self.assertIn(bytes.fromhex("34 00 50 00 34 01 3c 00"), context)

    def test_verified_pal_de_tokomon_item_script_offsets(self):
        with PAL_DE_ROM.open("rb") as rom:
            rom.seek(0x14A1ECC4)
            context = rom.read(0x80)

            records = []
            for offset in PAL_DE_TOKOMON_ITEM_OFFSETS:
                rom.seek(offset)
                records.append(struct.unpack("<BxBB", rom.read(4)))

        self.assertIn(scrutil.encode("Gegenst"), context)
        self.assertEqual(
            records,
            [
                (0x28, 0x00, 3),
                (0x28, 0x26, 3),
                (0x28, 0x04, 3),
                (0x28, 0x0B, 1),
                (0x28, 0x0D, 2),
                (0x28, 0x0E, 1),
            ],
        )

    def test_verified_pal_de_tech_gift_script_offsets(self):
        with PAL_DE_ROM.open("rb") as rom:
            learn_records = []
            for offset in PAL_DE_LEARN_MOVE_OFFSETS:
                rom.seek(offset)
                learn_records.append(struct.unpack("<2B", rom.read(2)))

            check_techs = []
            for offset in PAL_DE_CHECK_MOVE_OFFSETS:
                rom.seek(offset)
                check_techs.append(rom.read(1)[0])

            rom.seek(0x149D4A1E)
            beetle_check_context = rom.read(0x10)
            rom.seek(0x149D4DDA)
            beetle_learn_context = rom.read(0x10)
            rom.seek(0x1498D04C)
            seadramon_context = rom.read(0xA0)

        expected_techs = [0x21, 0x15, 0x12, 0x10]
        self.assertEqual(
            learn_records,
            [(scrutil.learnMove, tech_id) for tech_id in expected_techs],
        )
        self.assertEqual(check_techs, expected_techs)
        self.assertIn(bytes.fromhex("19 00 22 00 21 00"), beetle_check_context)
        self.assertIn(bytes.fromhex("fe 00 2d 21 1b 07"), beetle_learn_context)
        self.assertIn(bytes.fromhex("22 00 15 01 18 00"), seadramon_context)
        self.assertIn(bytes.fromhex("22 00 12 01 18 00"), seadramon_context)
        self.assertIn(bytes.fromhex("22 00 10 01 18 00"), seadramon_context)

    def test_verified_pal_de_monzaemon_special_evolution_offsets(self):
        with PAL_DE_ROM.open("rb") as rom:
            target_ids = []
            for offset in PAL_DE_MONZAEMON_SPEC_EVO_OFFSETS:
                rom.seek(offset)
                target_ids.append(rom.read(1)[0])

            rom.seek(0x149F42D0)
            entry_context = rom.read(0x18)
            rom.seek(0x149F4344)
            setup_context = rom.read(0x18)
            rom.seek(0x149F43A6)
            check_context = rom.read(0x18)
            rom.seek(0x149F4438)
            result_context = rom.read(0x10)
            rom.seek(0x149F4CA8)
            post_lock_context = rom.read(0x18)

        self.assertEqual(target_ids, [0x0E] * 5)
        self.assertEqual(
            entry_context,
            bytes.fromhex("64 2a fe 00 19 00 00 00 0e 01 80 00 5e 01 a4 00 78 05 01 00 81 00 5e 01"),
        )
        self.assertEqual(
            setup_context,
            bytes.fromhex("fe 00 19 00 00 00 5d 01 81 00 0e 01 18 00 20 09 19 00 1b 05 1a 00 82 75"),
        )
        self.assertEqual(
            check_context,
            bytes.fromhex("fe 00 22 67 19 00 08 00 67 0e 81 00 5d 01 18 00 3a 09 19 00 16 00 d0 09"),
        )
        self.assertEqual(
            result_context,
            bytes.fromhex("1b fd 10 02 9a 01 32 0e 1a 00 82 69 82 81 0d 00"),
        )
        self.assertEqual(
            post_lock_context,
            bytes.fromhex("0d 00 00 00 fe 00 ff 00 0e 01 81 00 5e 01 a4 00 78 02 01 00 18 00 96 01"),
        )

    def test_verified_pal_de_toy_town_lock_check_offsets(self):
        with PAL_DE_ROM.open("rb") as rom:
            lock_checks = []
            for offset in PAL_DE_TOY_TOWN_LOCK_CHECK_OFFSETS:
                rom.seek(offset)
                lock_checks.append(rom.read(4))

            rom.seek(0x149F4BA8)
            first_lock_context = rom.read(0xC0)
            rom.seek(0x149F4C24)
            second_lock_context = rom.read(0xC0)

        self.assertEqual(lock_checks, [bytes.fromhex("00005d01")] * 2)
        lock_message = bytes.fromhex(
            "82 67 82 8d 82 8d 81 44 81 44 81 44 81 40"
            "82 87 82 85 82 88 82 94 81 40 82 8e 82 89"
            "82 83 82 88 82 94 81 40 82 81 82 95 82 86"
            "81 44"
        )
        self.assertIn(lock_message, first_lock_context)
        self.assertIn(lock_message, second_lock_context)
        self.assertIn(bytes.fromhex("fe00190000005d0118004400"), first_lock_context)
        self.assertIn(bytes.fromhex("fe00190000005d0118004400"), second_lock_context)

    def test_pal_de_toy_town_unlock_candidates_do_not_match_monzaemon_targets(self):
        with PAL_DE_ROM.open("rb") as rom:
            lock_checks = []
            unlock_ranges = []
            for offset in PAL_DE_TOY_TOWN_LOCK_CHECK_OFFSETS:
                rom.seek(offset)
                lock_checks.append(rom.read(len(PAL_DE_TOY_TOWN_UNLOCK_CANDIDATE_VALUE)))
                unlock_ranges.append(
                    range(offset, offset + len(PAL_DE_TOY_TOWN_UNLOCK_CANDIDATE_VALUE))
                )

        self.assertEqual(lock_checks, [bytes.fromhex("00 00 5d 01")] * 2)
        self.assertEqual(PAL_DE_TOY_TOWN_UNLOCK_CANDIDATE_VALUE, bytes.fromhex("01 00 5d 01"))

        verified_monzaemon_offsets = set(PAL_DE_MONZAEMON_SPEC_EVO_OFFSETS)
        for unlock_range in unlock_ranges:
            self.assertTrue(verified_monzaemon_offsets.isdisjoint(unlock_range))

    def test_pal_de_monzaemon_special_evolution_candidate_families(self):
        with PAL_DE_ROM.open("rb") as rom:
            box_contexts = []
            for offset in PAL_DE_MONZAEMON_BOX_CHOICE_CONTEXT_OFFSETS:
                rom.seek(offset)
                box_contexts.append(rom.read(0x40))

            reaction_contexts = []
            for offset in PAL_DE_MONZAEMON_REACTION_CONTEXT_OFFSETS:
                rom.seek(offset)
                reaction_contexts.append(rom.read(0x30))

        box_prefix = bytes.fromhex(
            "4e fd 0e 00 0e fd 00 00 4f 14 49 00 b5 00 4a c8"
            "4e fd 33 ff a0 fd 00 00 4e fc c3 00 a0 fd 00 00"
            "67 00 28 00 4d fd 00 08 4d fc 00 08 67 00 05 00"
            "1b ff 1a 00 01 07 81 48 81 48 81 48"
        )
        self.assertTrue(all(context.startswith(box_prefix) for context in box_contexts))
        reaction_prefixes = [
            bytes.fromhex(
                "67 00 0e 00 5a 00 08 0e 71 00 00 01 0c 00 a5 00"
                "b1 00 71 01 01 01 0c 00 a0 00 be 00 67 00 0d 00"
                "1b fd 1a 00 82 76 81 7c 82 97 82 81 82 93"
            ),
            bytes.fromhex(
                "67 00 0e 00 5a 00 08 0e 71 00 00 01 0c 00 a5 00"
                "b1 00 71 01 01 01 0c 00 a0 00 be 00 67 00 0d 00"
                "1b fd 1a 00 82 76 82 89 82 85 81 48 81 40"
            ),
            bytes.fromhex(
                "67 00 0e 00 5a 00 08 0e 71 00 00 01 0c 00 a5 00"
                "b1 00 71 01 01 01 0c 00 a0 00 be 00 67 00 0d 00"
                "1b fd 1a 00 82 76 81 7c 82 97 82 81 82 93"
            ),
            bytes.fromhex(
                "67 00 0e 00 5a 00 08 0e 71 00 00 01 0c 00 a5 00"
                "b1 00 71 01 01 01 0c 00 a0 00 be 00 67 00 0d 00"
                "1b fd 1a 00 82 76 81 7c 82 97 82 81 82 93"
            ),
        ]
        self.assertEqual(len(reaction_contexts), len(reaction_prefixes))
        for context, prefix in zip(reaction_contexts, reaction_prefixes):
            self.assertTrue(context.startswith(prefix))

    def test_pal_de_sukamon_special_evolution_candidate_offsets(self):
        with PAL_DE_ROM.open("rb") as rom:
            target_pairs = []
            for offsets in PAL_DE_SUKAMON_SPEC_EVO_CANDIDATE_OFFSETS:
                pair = []
                for offset in offsets:
                    rom.seek(offset)
                    pair.append(rom.read(1)[0])
                target_pairs.append(tuple(pair))

            rom.seek(0x14A2990A)
            first_context = rom.read(0x70)
            rom.seek(0x14A29F6A)
            second_context = rom.read(0x70)

        self.assertEqual(target_pairs, [(0x27, 0x27), (0x27, 0x27)])
        sukamon_prefix = bytes.fromhex(
            "6e 63 19 00 0b 00 6e 04 18 00 32 00 19 00"
            "74 2c 27 00 2f 00 74 2c 27 00 2d 00"
            "74 2c 27 00 31 00 24 00 6e 63 19 00"
            "0b 00 6e 0e 18 00 48 00 19 00"
            "74 2c 2c 00 42 00 24 00 6e 63 19 00"
        )
        self.assertTrue(first_context.startswith(sukamon_prefix))
        self.assertTrue(second_context.startswith(sukamon_prefix))
        self.assertEqual(first_context, second_context)

    def test_pal_de_mamemon_special_evolution_candidate_offsets(self):
        with PAL_DE_ROM.open("rb") as rom:
            target_pairs = []
            for offsets in PAL_DE_MAMEMON_SPEC_EVO_CANDIDATE_OFFSETS:
                pair = []
                for offset in offsets:
                    rom.seek(offset)
                    pair.append(rom.read(1)[0])
                target_pairs.append(tuple(pair))

            rom.seek(0x149C919C)
            first_context = rom.read(0xB0)
            rom.seek(0x149C93E4)
            second_context = rom.read(0xB0)

        self.assertEqual(target_pairs, [(0x29, 0x1B), (0x29, 0x1B)])
        mamemon_prefix = bytes.fromhex(
            "19 00 0b 00 6e 05 18 00 36 00 19 00"
            "74 2c 3f 00 29 00 24 00 6e 63 19 00"
            "0b 00 6e 0f 18 00 4c 00 19 00"
            "74 2c 2f 00 26 00 24 00 6e 63 19 00"
            "0b 00 6e 13 18 00 62 00 19 00"
            "74 2c 22 00 37 00"
        )
        self.assertTrue(first_context.startswith(mamemon_prefix))
        self.assertTrue(second_context.startswith(mamemon_prefix))
        self.assertEqual(first_context, second_context)

    def test_pal_de_mamemon_family_language_copy_candidate_offsets(self):
        with PAL_DE_ROM.open("rb") as rom:
            target_pairs = []
            giromon_contexts = []
            metal_contexts = []
            for giromon_offset, metal_mamemon_offset in (
                PAL_DE_MAMEMON_SPEC_EVO_LANGUAGE_COPY_CANDIDATE_OFFSETS
            ):
                rom.seek(giromon_offset)
                giromon_id = rom.read(1)[0]
                rom.seek(metal_mamemon_offset)
                metal_mamemon_id = rom.read(1)[0]
                target_pairs.append((giromon_id, metal_mamemon_id))

                rom.seek(giromon_offset - 0x10)
                giromon_contexts.append(rom.read(0x18))
                rom.seek(metal_mamemon_offset - 0x04)
                metal_contexts.append(rom.read(0x08))

        self.assertEqual(target_pairs, [(0x29, 0x1B)] * 10)
        all_offsets = {
            offset
            for pair in PAL_DE_MAMEMON_SPEC_EVO_LANGUAGE_COPY_CANDIDATE_OFFSETS
            for offset in pair
        }
        metal_signature = bytes.fromhex("2f 01 fe 00 1b 06 1a 00")
        self.assertEqual(
            len(all_offsets),
            20,
        )
        for context in giromon_contexts:
            self.assertEqual(context[0:4], bytes.fromhex("19 00 0b 00"))
            self.assertEqual(context[0x0C:0x12], bytes.fromhex("74 2c 3f 00 29 00"))
            self.assertEqual(context[0x12:0x16], bytes.fromhex("24 00 6e 63"))
        self.assertEqual(metal_contexts, [metal_signature] * 10)

    def test_pal_de_sukamon_language_copy_candidate_offsets(self):
        with PAL_DE_ROM.open("rb") as rom:
            target_pairs = []
            contexts = []
            for offsets in PAL_DE_SUKAMON_SPEC_EVO_LANGUAGE_COPY_CANDIDATE_OFFSETS:
                pair = []
                for offset in offsets:
                    rom.seek(offset)
                    pair.append(rom.read(1)[0])
                target_pairs.append(tuple(pair))

                rom.seek(offsets[0] - 0x0E)
                contexts.append(rom.read(0x28))

        self.assertEqual(target_pairs, [(0x27, 0x27)] * 10)
        all_offsets = {
            offset
            for pair in PAL_DE_SUKAMON_SPEC_EVO_LANGUAGE_COPY_CANDIDATE_OFFSETS
            for offset in pair
        }
        sukamon_signature = bytes.fromhex(
            "19 00 74 2c 27 00 2f 00 74 2c 27 00"
            "2d 00 74 2c 27 00 31 00 24 00"
        )
        self.assertEqual(
            len(all_offsets),
            20,
        )
        for context in contexts:
            self.assertEqual(context[0:4], bytes.fromhex("19 00 0b 00"))
            self.assertEqual(context[0x0A:0x20], sukamon_signature)

    def test_pal_de_result_table_special_evolution_candidate_offsets(self):
        with PAL_DE_ROM.open("rb") as rom:
            records = []
            for offset, expected_target in PAL_DE_RESULT_TABLE_SPEC_EVO_CANDIDATE_OFFSETS:
                rom.seek(offset - 0x0D)
                context = rom.read(0x20)
                records.append((context, context[0x0D], expected_target))

        for context, actual_target, expected_target in records:
            self.assertEqual(actual_target, expected_target)
            self.assertEqual(context[0:4], bytes.fromhex("19 00 0b 00"))
            self.assertEqual(context[0x0A:0x0D], bytes.fromhex("19 00 2f"))
            self.assertEqual(context[0x0E:0x12], bytes.fromhex("1b fd 1a 00"))
            self.assertTrue(context[0x12] in (0x81, 0x82, 0x83))

    def test_pal_de_result_table_language_copy_candidates(self):
        with PAL_DE_ROM.open("rb") as rom:
            records = []
            for evidence in PAL_DE_RESULT_TABLE_SPEC_EVO_LANGUAGE_COPY_CANDIDATES:
                for offset in evidence.offsets:
                    rom.seek(offset - 0x0D)
                    records.append((evidence, rom.read(0x20)))

        all_offsets = {
            offset
            for evidence in PAL_DE_RESULT_TABLE_SPEC_EVO_LANGUAGE_COPY_CANDIDATES
            for offset in evidence.offsets
        }
        counts_by_name = {
            evidence.name: len(evidence.offsets)
            for evidence in PAL_DE_RESULT_TABLE_SPEC_EVO_LANGUAGE_COPY_CANDIDATES
        }
        representative_offsets = {
            offset
            for offset, _target_id in PAL_DE_RESULT_TABLE_SPEC_EVO_CANDIDATE_OFFSETS
        }

        self.assertEqual(len(all_offsets), 65)
        self.assertEqual(counts_by_name["Devimon"], 10)
        self.assertEqual(counts_by_name["Airdramon"], 10)
        other_counts = {
            count
            for name, count in counts_by_name.items()
            if name not in {"Devimon", "Airdramon"}
        }
        self.assertEqual(
            other_counts,
            {5},
        )
        self.assertTrue(representative_offsets.issubset(all_offsets))

        for evidence, context in records:
            self.assertEqual(context[0:4], bytes.fromhex("19 00 0b 00"))
            self.assertEqual(context[0x0A:0x0D], bytes.fromhex("19 00 2f"))
            self.assertEqual(context[0x0D], evidence.target_id)
            self.assertEqual(context[0x0E:0x12], bytes.fromhex("1b fd 1a 00"))
            self.assertTrue(context[0x12] in (0x81, 0x82, 0x83))

    def test_pal_de_verified_special_evolution_layout_bytes(self):
        layout_records = PAL_DE_LAYOUT.require_scripts().specEvoOffsets
        evidence_records = tuple(
            (evidence.offsets, evidence.target_id, evidence.from_id)
            for evidence in PAL_DE_SPEC_EVO_EVIDENCE
        )

        self.assertEqual(layout_records, evidence_records)

        with PAL_DE_ROM.open("rb") as rom:
            for evidence in PAL_DE_SPEC_EVO_EVIDENCE:
                for offset in evidence.offsets:
                    rom.seek(offset)
                    self.assertEqual(
                        rom.read(1)[0],
                        evidence.target_id,
                        f"{evidence.name} target byte at {offset:#x}",
                    )

    def test_pal_de_special_evolution_evidence_is_classified(self):
        evidence_by_name = {evidence.name: evidence for evidence in PAL_DE_SPEC_EVO_EVIDENCE}

        self.assertIn("Monzaemon/Toy Town", evidence_by_name)
        self.assertIn("Giromon", evidence_by_name)
        self.assertIn("MetalMamemon", evidence_by_name)
        self.assertIn("Sukamon", evidence_by_name)
        self.assertEqual(len(PAL_DE_SPEC_EVO_EVIDENCE), 15)
        self.assertEqual(len(evidence_by_name["Monzaemon/Toy Town"].offsets), 5)
        self.assertEqual(len(evidence_by_name["Giromon"].offsets), 2)
        self.assertEqual(len(evidence_by_name["MetalMamemon"].offsets), 2)
        self.assertEqual(len(evidence_by_name["Sukamon"].offsets), 4)

        for evidence in PAL_DE_SPEC_EVO_EVIDENCE:
            self.assertTrue(evidence.offsets)
            self.assertEqual(evidence.confidence, "verified-layout")
            self.assertIn(evidence.target_id, range(0x100))
            self.assertIn(evidence.from_id, range(0x100))

    def test_pal_de_verified_script_evidence_is_classified(self):
        evidence_by_name = {evidence.name: evidence for evidence in PAL_DE_SCRIPT_EVIDENCE}
        expected_names = {
            "starter-set",
            "starter-learning-check",
            "starter-learning-tech",
            "starter-equip-animation",
            "starter-stat-check",
            "tokomon-items",
            "tech-gift-learn",
            "tech-gift-check",
        }
        expected_offsets = {
            *PAL_DE_STARTER_SET_OFFSETS,
            *PAL_DE_STARTER_CHECK_OFFSETS,
            *PAL_DE_STARTER_LEARN_TECH_OFFSETS,
            *PAL_DE_STARTER_EQUIP_ANIM_OFFSETS,
            PAL_DE_STARTER_STAT_CHECK_OFFSET,
            *PAL_DE_TOKOMON_ITEM_OFFSETS,
            *PAL_DE_LEARN_MOVE_OFFSETS,
            *PAL_DE_CHECK_MOVE_OFFSETS,
        }
        actual_offsets = {
            offset
            for evidence in PAL_DE_SCRIPT_EVIDENCE
            for offset in evidence.offsets
        }

        self.assertEqual(set(evidence_by_name), expected_names)
        self.assertEqual(actual_offsets, expected_offsets)
        for evidence in PAL_DE_SCRIPT_EVIDENCE:
            self.assertTrue(evidence.offsets)
            self.assertEqual(evidence.confidence, "verified-write")

    def test_pal_de_patch_evidence_is_classified(self):
        evidence_by_name = {evidence.name: evidence for evidence in PAL_DE_PATCH_EVIDENCE}

        self.assertEqual(set(evidence_by_name), {
            "fix-evo-items",
            "type-effectiveness",
            "ogremon-softlock",
            "pp-calculation",
            "unlock-areas",
            "intro-hash",
            "intro-skip",
            "spawn-rate",
            "training-slots",
            "movement-softlocks",
            "learn-move-and-command",
            "gabumon",
            "woah",
            "happy-vending",
            "intro-hash-relative-candidate",
            "dv-chip-descriptions",
            "always-on-executable-hooks",
        })
        self.assertEqual(
            evidence_by_name["fix-evo-items"].offsets,
            (PAL_DE_LAYOUT.patch_offsets["evoItemPatchOffset"],),
        )
        self.assertEqual(evidence_by_name["fix-evo-items"].confidence, "verified-write")
        self.assertEqual(
            evidence_by_name["type-effectiveness"].offsets,
            (PAL_DE_LAYOUT.patch_offsets["typeEffectivenessOffset"],),
        )
        self.assertEqual(evidence_by_name["type-effectiveness"].confidence, "verified-write")
        self.assertEqual(
            evidence_by_name["ogremon-softlock"].offsets,
            PAL_DE_LAYOUT.patch_offsets["ogremonSoftlockOffset"],
        )
        self.assertEqual(evidence_by_name["ogremon-softlock"].confidence, "verified-write")
        self.assertEqual(
            evidence_by_name["pp-calculation"].offsets,
            (PAL_DE_LAYOUT.patch_offsets["rewritePPOffset"],),
        )
        self.assertEqual(evidence_by_name["pp-calculation"].confidence, "verified-write")
        self.assertEqual(
            evidence_by_name["unlock-areas"].offsets,
            (
                *PAL_DE_LAYOUT.patch_offsets["unlockGreylordOffset"],
                *PAL_DE_LAYOUT.patch_offsets["unlockIceOffset"],
                *PAL_DE_LAYOUT.patch_offsets["unlockToyTownOffset"],
            ),
        )
        self.assertEqual(evidence_by_name["unlock-areas"].confidence, "verified-write")
        self.assertEqual(
            evidence_by_name["intro-hash"].offsets,
            (PAL_DE_LAYOUT.patch_offsets["introHashOffset"],),
        )
        self.assertEqual(evidence_by_name["intro-hash"].confidence, "verified-write")
        self.assertEqual(
            evidence_by_name["intro-skip"].offsets,
            (
                PAL_DE_LAYOUT.patch_offsets["introSkipOutsideOffset"],
                PAL_DE_LAYOUT.patch_offsets["introSkipInsideOffset"],
            ),
        )
        self.assertEqual(evidence_by_name["intro-skip"].confidence, "verified-write")
        self.assertEqual(
            evidence_by_name["spawn-rate"].offsets,
            (
                *PAL_DE_LAYOUT.patch_offsets["spawnRateMamemonOffset"],
                *PAL_DE_LAYOUT.patch_offsets["spawnRatePiximonOffset"],
                *PAL_DE_LAYOUT.patch_offsets["spawnRateMMamemonOffset"],
                *PAL_DE_LAYOUT.patch_offsets["spawnRateOtamamonOffset"],
            ),
        )
        self.assertEqual(evidence_by_name["spawn-rate"].confidence, "verified-write")
        self.assertEqual(
            evidence_by_name["training-slots"].offsets,
            PAL_DE_UNRIG_SLOTS_CANDIDATE_OFFSETS,
        )
        self.assertEqual(evidence_by_name["training-slots"].confidence, "verified-write")
        self.assertEqual(evidence_by_name["movement-softlocks"].confidence, "verified-write")
        self.assertEqual(
            evidence_by_name["movement-softlocks"].offsets,
            (
                *PAL_DE_SOFTLOCK_ROTATION_BRANCH_OFFSETS,
                *PAL_DE_SOFTLOCK_MOVE_TO_BRANCH_OFFSETS,
                *PAL_DE_SOFTLOCK_TOY_TOWN_COORDINATE_OFFSETS,
                *PAL_DE_SOFTLOCK_LEOMON_CAVE_OFFSETS,
            ),
        )
        self.assertEqual(
            evidence_by_name["learn-move-and-command"].offsets,
            (
                PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_OFFSET,
                PAL_DE_LEARN_MOVE_AND_COMMAND_REJECTED_CANDIDATE_OFFSET,
            ),
        )
        self.assertEqual(evidence_by_name["learn-move-and-command"].confidence, "verified-write")
        self.assertEqual(evidence_by_name["gabumon"].offsets, (PAL_DE_GABUMON_NTSC_RAW_CANDIDATE_OFFSET,))
        self.assertEqual(evidence_by_name["gabumon"].confidence, "verified-file-relative-write")
        self.assertEqual(
            evidence_by_name["woah"].offsets,
            PAL_DE_WOAH_TEXT_OFFSETS,
        )
        self.assertEqual(evidence_by_name["woah"].confidence, "verified-write")
        self.assertEqual(len(PAL_DE_WOAH_ENCODED_TEXT), 8)
        self.assertEqual(len(PAL_DE_WOAH_PAYLOAD), len(PAL_DE_WOAH_ENCODED_TEXT))
        self.assertGreater(len(PAL_DE_WOAH_NTSC_REPLACEMENT_AS_PAL_TEXT), len(PAL_DE_WOAH_ENCODED_TEXT))
        self.assertEqual(
            evidence_by_name["happy-vending"].offsets,
            (
                *PAL_DE_HAPPY_VENDING_MENU_OFFSETS,
                *PAL_DE_HAPPY_VENDING_RESULT_OFFSETS,
                *PAL_DE_HAPPY_VENDING_PRICE_OFFSETS,
                *PAL_DE_HAPPY_VENDING_ITEM_ID_OFFSETS,
            ),
        )
        self.assertEqual(evidence_by_name["happy-vending"].confidence, "verified-write")
        self.assertEqual(evidence_by_name["intro-hash-relative-candidate"].confidence, "deferred-scenario-padding")
        self.assertEqual(
            evidence_by_name["intro-hash-relative-candidate"].offsets,
            (PAL_DE_HASH_DG4_CANDIDATE_OFFSET,),
        )
        self.assertEqual(evidence_by_name["dv-chip-descriptions"].offsets, PAL_DE_DV_CHIP_DESCRIPTION_OFFSETS)
        self.assertEqual(evidence_by_name["dv-chip-descriptions"].confidence, "verified-write")
        self.assertEqual(evidence_by_name["always-on-executable-hooks"].confidence, "verified-write")
        self.assertEqual(
            evidence_by_name["always-on-executable-hooks"].offsets,
            (
                *PAL_DE_LAYOUT.patch_offsets["evoTargetUnifyHack"],
                PAL_DE_LAYOUT.patch_offsets["customTickFunctionOffset"],
                PAL_DE_LAYOUT.patch_offsets["customTickHookOffset"],
            ),
        )

    def test_verified_pal_de_fix_evo_items_patch_offset(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["evoItemPatchOffset"],
            PAL_DE_FIX_EVO_ITEMS_OFFSET,
        )

        with PAL_DE_ROM.open("rb") as rom:
            rom.seek(PAL_DE_FIX_EVO_ITEMS_OFFSET)
            context = rom.read(len(PAL_DE_FIX_EVO_ITEMS_CONTEXT))

        self.assertEqual(context, PAL_DE_FIX_EVO_ITEMS_CONTEXT)
        self.assertEqual(context[0], 0x21)

    def test_verified_pal_de_happy_vending_patch_offsets(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingOffset1"],
            PAL_DE_HAPPY_VENDING_MENU_OFFSETS,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingOffset2"],
            PAL_DE_HAPPY_VENDING_RESULT_OFFSETS,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingOffset3"],
            PAL_DE_HAPPY_VENDING_PRICE_OFFSETS[:2],
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingOffset4"],
            PAL_DE_HAPPY_VENDING_PRICE_OFFSETS[2:],
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingOffset5"],
            PAL_DE_HAPPY_VENDING_ITEM_ID_OFFSETS,
        )
        self.assertLessEqual(
            len(PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingPayload1"]),
            struct.calcsize(PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingFormat1"]),
        )
        self.assertEqual(
            len(PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingPayload2"]),
            struct.calcsize(PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingFormat2"]),
        )

        with PAL_DE_ROM.open("rb") as rom:
            menu_contexts = []
            for offset, expected_context in zip(
                PAL_DE_HAPPY_VENDING_MENU_OFFSETS,
                PAL_DE_HAPPY_VENDING_MENU_CONTEXTS,
            ):
                rom.seek(offset)
                menu_contexts.append(rom.read(len(expected_context)))

            result_contexts = []
            for offset, expected_context in zip(
                PAL_DE_HAPPY_VENDING_RESULT_OFFSETS,
                PAL_DE_HAPPY_VENDING_RESULT_CONTEXTS,
            ):
                rom.seek(offset)
                result_contexts.append(rom.read(len(expected_context)))

            price_values = []
            for offset in PAL_DE_HAPPY_VENDING_PRICE_OFFSETS:
                rom.seek(offset)
                price_values.append(struct.unpack("<H", rom.read(2))[0])

            item_ids = []
            for offset in PAL_DE_HAPPY_VENDING_ITEM_ID_OFFSETS:
                rom.seek(offset)
                item_ids.append(rom.read(1)[0])

        self.assertEqual(menu_contexts, list(PAL_DE_HAPPY_VENDING_MENU_CONTEXTS))
        self.assertEqual(result_contexts, list(PAL_DE_HAPPY_VENDING_RESULT_CONTEXTS))
        self.assertEqual(price_values, [300, 300, 300, 300])
        self.assertEqual(item_ids, [0x26, 0x26, 0x26, 0x26, 0x26, 0x26])

    def test_verified_pal_de_dv_chip_description_patch_offsets(self):
        self.assertEqual(PAL_DE_LAYOUT.patch_offsets["DVChipAOffset"], PAL_DE_DV_CHIP_DESCRIPTION_OFFSETS[0])
        self.assertEqual(PAL_DE_LAYOUT.patch_offsets["DVChipDOffset"], PAL_DE_DV_CHIP_DESCRIPTION_OFFSETS[1])
        self.assertEqual(PAL_DE_LAYOUT.patch_offsets["DVChipEOffset"], PAL_DE_DV_CHIP_DESCRIPTION_OFFSETS[2])
        self.assertLessEqual(
            len(PAL_DE_LAYOUT.patch_offsets["DVChipAPayload"]),
            struct.calcsize(PAL_DE_LAYOUT.patch_offsets["DVChipAFormat"]),
        )
        self.assertLessEqual(
            len(PAL_DE_LAYOUT.patch_offsets["DVChipDPayload"]),
            struct.calcsize(PAL_DE_LAYOUT.patch_offsets["DVChipDFormat"]),
        )
        self.assertLessEqual(
            len(PAL_DE_LAYOUT.patch_offsets["DVChipEPayload"]),
            struct.calcsize(PAL_DE_LAYOUT.patch_offsets["DVChipEFormat"]),
        )

        with PAL_DE_ROM.open("rb") as rom:
            contexts = []
            for offset, expected_context in zip(
                PAL_DE_DV_CHIP_DESCRIPTION_OFFSETS,
                PAL_DE_DV_CHIP_DESCRIPTION_CONTEXTS,
            ):
                rom.seek(offset)
                contexts.append(rom.read(len(expected_context)))

        self.assertEqual(contexts, list(PAL_DE_DV_CHIP_DESCRIPTION_CONTEXTS))

    def test_verified_pal_de_learn_move_and_command_patch_offset(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["learnMoveAndCommandOffset"],
            PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_OFFSET,
        )

        with PAL_DE_ROM.open("rb") as rom:
            rom.seek(PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_OFFSET - 0x10)
            branch_context = rom.read(len(PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_CONTEXT))
            rom.seek(PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_OFFSET)
            original_branch = rom.read(8)

        self.assertEqual(branch_context, PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_CONTEXT)
        self.assertEqual(original_branch, bytes.fromhex("68 00 40 14 00 00 00 00"))
        self.assertEqual(
            struct.pack(patch_data.learnMoveAndCommandFormat, *patch_data.learnMoveAndCommandValue),
            bytes.fromhex("65 00 00 10 21 10 00 00"),
        )

    def test_verified_pal_de_gabumon_patch_offset(self):
        from digimon.rom.scenario import RawCdImage

        gabu_writes = PAL_DE_LAYOUT.patch_offsets["gabuPatchWrites"]
        self.assertEqual(gabu_writes, patch_data.gabuPatchWrites)
        self.assertEqual(gabu_writes[0][0], PAL_DE_GABUMON_NTSC_RAW_CANDIDATE_OFFSET)

        entry = RawCdImage(PAL_DE_ROM).find(PAL_DE_GABUMON_TFS_PATH)
        self.assertEqual(entry.data_offset, PAL_DE_GABUMON_TFS_OFFSET)
        self.assertEqual(
            PAL_DE_GABUMON_NTSC_RAW_CANDIDATE_OFFSET - entry.data_offset,
            PAL_DE_GABUMON_TFS_RELATIVE_PATCH_OFFSET,
        )

        with PAL_DE_ROM.open("rb") as rom:
            rom.seek(PAL_DE_GABUMON_NTSC_RAW_CANDIDATE_OFFSET - 0x40)
            context = rom.read(len(PAL_DE_GABUMON_PATCH_ORIGINAL_CONTEXT))
            rom.seek(PAL_DE_GABUMON_NAIVE_DELTA_CANDIDATE_OFFSET)
            naive_delta_context = rom.read(16)

        self.assertEqual(context, PAL_DE_GABUMON_PATCH_ORIGINAL_CONTEXT)
        self.assertEqual(naive_delta_context, bytes.fromhex("8c a3 ce f8 dc 6d 02 21 96 07 a1 01 39 35 72 03"))

    def test_verified_pal_de_movement_softlock_executable_offsets(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["fixRotationSLOffset"],
            PAL_DE_SOFTLOCK_ROTATION_BRANCH_OFFSETS,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["fixMoveToSLOffset"],
            PAL_DE_SOFTLOCK_MOVE_TO_BRANCH_OFFSETS,
        )

        with PAL_DE_ROM.open("rb") as rom:
            rotation_contexts = []
            for offset, expected_context in zip(
                PAL_DE_SOFTLOCK_ROTATION_BRANCH_OFFSETS,
                PAL_DE_SOFTLOCK_ROTATION_BRANCH_CONTEXTS,
            ):
                rom.seek(offset - 0x30)
                rotation_contexts.append(rom.read(len(expected_context)))

            rom.seek(PAL_DE_SOFTLOCK_MOVE_TO_BRANCH_OFFSETS[0] - 0x24)
            move_to_context = rom.read(len(PAL_DE_SOFTLOCK_MOVE_TO_BRANCH_CONTEXT))

        self.assertEqual(rotation_contexts, list(PAL_DE_SOFTLOCK_ROTATION_BRANCH_CONTEXTS))
        self.assertEqual(move_to_context, PAL_DE_SOFTLOCK_MOVE_TO_BRANCH_CONTEXT)
        self.assertEqual(
            [context[0x30] for context in rotation_contexts],
            [0x58, 0x58],
        )
        self.assertEqual(
            struct.pack(patch_data.fixRotationSLFormat, patch_data.fixRotationSLValue),
            bytes.fromhex("0d"),
        )
        self.assertEqual(
            move_to_context[0x24:0x28],
            bytes.fromhex("03 00 40 10"),
        )
        self.assertEqual(
            struct.pack(patch_data.fixMoveToSLFormat, patch_data.fixMoveToSLValue),
            bytes.fromhex("06 00 40 10"),
        )

    def test_verified_pal_de_toy_town_softlock_coordinate_offsets(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["fixToyTownSLOffset"],
            PAL_DE_SOFTLOCK_TOY_TOWN_COORDINATE_OFFSETS,
        )

        with PAL_DE_ROM.open("rb") as rom:
            command_contexts = []
            for offset, expected_context in zip(
                PAL_DE_SOFTLOCK_TOY_TOWN_COORDINATE_OFFSETS,
                PAL_DE_SOFTLOCK_TOY_TOWN_COMMAND_CONTEXTS,
            ):
                rom.seek(offset - 2)
                command_contexts.append(rom.read(len(expected_context)))

        self.assertEqual(command_contexts, list(PAL_DE_SOFTLOCK_TOY_TOWN_COMMAND_CONTEXTS))
        self.assertEqual([context[:2] for context in command_contexts], [bytes.fromhex("4f 12")] * 2)
        self.assertEqual([context[2:6] for context in command_contexts], [bytes.fromhex("b0 ff 18 04")] * 2)
        self.assertEqual(
            struct.pack(patch_data.fixToyTownSLFormat, patch_data.fixToyTownSLValue),
            bytes.fromhex("31 fc a3 02"),
        )

    def test_verified_pal_de_leomon_cave_softlock_offsets(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["fixLeoCaveSLOffset"],
            PAL_DE_SOFTLOCK_LEOMON_CAVE_OFFSETS,
        )

        with PAL_DE_ROM.open("rb") as rom:
            contexts = []
            for offset, expected_context in zip(
                PAL_DE_SOFTLOCK_LEOMON_CAVE_OFFSETS,
                PAL_DE_SOFTLOCK_LEOMON_CAVE_CONTEXTS,
            ):
                rom.seek(offset - 12)
                contexts.append(rom.read(len(expected_context)))

        self.assertEqual(contexts, list(PAL_DE_SOFTLOCK_LEOMON_CAVE_CONTEXTS))
        self.assertEqual([context[8:12] for context in contexts], [bytes.fromhex("4e fd aa f8")] * 8)
        self.assertEqual([context[12:16] for context in contexts], [bytes.fromhex("54 0b 01 00")] * 8)
        self.assertEqual(
            struct.pack(patch_data.fixLeoCaveSLFormat, patch_data.fixLeoCaveSLValue),
            bytes.fromhex("3b"),
        )

    def test_verified_pal_de_unrig_slots_patch_offsets(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["unrigSlotsOffset"],
            PAL_DE_UNRIG_SLOTS_CANDIDATE_OFFSETS[0],
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["unrigSlots2Offset"],
            PAL_DE_UNRIG_SLOTS_CANDIDATE_OFFSETS[1],
        )

        with PAL_DE_ROM.open("rb") as rom:
            slots_contexts = []
            for offset in PAL_DE_UNRIG_SLOTS_CANDIDATE_OFFSETS:
                rom.seek(offset)
                slots_contexts.append(rom.read(0x38))

        self.assertEqual(slots_contexts, list(PAL_DE_UNRIG_SLOTS_CANDIDATE_CONTEXTS))
        self.assertEqual(
            struct.pack(patch_data.unrigSlotsFormat, patch_data.unrigSlotsValue),
            bytes.fromhex("1e 3a 02 08"),
        )
        self.assertEqual(
            struct.pack(patch_data.unrigSlots2Format, patch_data.unrigSlots2Value),
            bytes.fromhex("94 34 02 08"),
        )

    def test_pal_de_deferred_optional_patch_candidates_are_not_enabled(self):
        blocked_offset_keys = set()

        self.assertTrue(blocked_offset_keys.isdisjoint(PAL_DE_LAYOUT.patch_offsets))

        with PAL_DE_ROM.open("rb") as rom:
            slots_contexts = []
            for offset in PAL_DE_UNRIG_SLOTS_CANDIDATE_OFFSETS:
                rom.seek(offset)
                slots_contexts.append(rom.read(0x38))
            rom.seek(PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_OFFSET - 0x10)
            learn_branch_context = rom.read(len(PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_CONTEXT))
            rom.seek(PAL_DE_LEARN_MOVE_AND_COMMAND_REJECTED_CANDIDATE_OFFSET)
            learn_rejected_context = rom.read(len(PAL_DE_LEARN_MOVE_AND_COMMAND_REJECTED_CANDIDATE_CONTEXT))
            rom.seek(PAL_DE_WOAH_NAIVE_SLES_DELTA_CANDIDATE_OFFSET)
            woah_context = rom.read(16)
            woah_text_contexts = []
            for offset, expected_context in zip(PAL_DE_WOAH_TEXT_OFFSETS, PAL_DE_WOAH_TEXT_CONTEXTS):
                rom.seek(offset - 8)
                woah_text_contexts.append(rom.read(len(expected_context)))
            rom.seek(PAL_DE_GABUMON_NAIVE_DELTA_CANDIDATE_OFFSET)
            gabumon_delta_context = rom.read(16)
            softlock_contexts = []
            for offset in PAL_DE_SOFTLOCK_NAIVE_SLES_DELTA_CANDIDATE_OFFSETS:
                rom.seek(offset)
                softlock_contexts.append(rom.read(8))
            reset_contexts = []
            for offset in PAL_DE_RESET_BUTTON_NAIVE_SLES_DELTA_CANDIDATE_OFFSETS:
                rom.seek(offset)
                reset_contexts.append(rom.read(8))
            dv_contexts = []
            for offset, expected_context in zip(
                PAL_DE_DV_CHIP_DESCRIPTION_CANDIDATE_OFFSETS,
                PAL_DE_DV_CHIP_DESCRIPTION_CANDIDATE_CONTEXTS,
            ):
                rom.seek(offset)
                dv_contexts.append(rom.read(len(expected_context)))
            devi_chip_name_contexts = []
            for offset, expected_context in zip(
                PAL_DE_DEVI_CHIP_NAME_OFFSETS,
                PAL_DE_DEVI_CHIP_NAME_CONTEXTS,
            ):
                rom.seek(offset)
                devi_chip_name_contexts.append(rom.read(len(expected_context)))

        self.assertEqual(slots_contexts, list(PAL_DE_UNRIG_SLOTS_CANDIDATE_CONTEXTS))
        self.assertEqual(learn_branch_context, PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_CONTEXT)
        self.assertEqual(learn_rejected_context, PAL_DE_LEARN_MOVE_AND_COMMAND_REJECTED_CANDIDATE_CONTEXT)
        self.assertEqual(woah_context, b"\0" * 16)
        self.assertEqual(woah_text_contexts, list(PAL_DE_WOAH_TEXT_CONTEXTS))
        self.assertEqual(gabumon_delta_context, bytes.fromhex("8c a3 ce f8 dc 6d 02 21 96 07 a1 01 39 35 72 03"))
        self.assertEqual(
            softlock_contexts,
            [
                bytes.fromhex("40 10 03 00 20 18 43 00"),
                bytes.fromhex("00 00 00 00 14 00 a2 af"),
                bytes.fromhex("00 00 00 00 2a 18 62 00"),
                bytes.fromhex("00 00 43 8c 13 80 02 3c"),
            ],
        )
        self.assertEqual(
            reset_contexts,
            [
                bytes.fromhex("0c 00 02 a2 12 00 24 92"),
                bytes.fromhex("ca fe a1 28 1b 86 9f 9f"),
                bytes.fromhex("00 00 08 00 00 00 08 00"),
                bytes.fromhex("66 07 f6 b9 33 43 0e 8e"),
            ],
        )
        self.assertGreater(PAL_DE_SPAWN_RATE_ACTIVE_RANDOM_COMMAND_CANDIDATE_COUNT, 1000)
        self.assertEqual(dv_contexts, list(PAL_DE_DV_CHIP_DESCRIPTION_CANDIDATE_CONTEXTS))
        self.assertEqual(devi_chip_name_contexts, list(PAL_DE_DEVI_CHIP_NAME_CONTEXTS))

    def test_verified_pal_de_always_on_patch_offsets(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["evoTargetUnifyHack"],
            {
                PAL_DE_EVO_TARGET_UNIFY_OFFSETS[0]: 0x24050003,
                PAL_DE_EVO_TARGET_UNIFY_OFFSETS[1]: 0x8FB00018,
                PAL_DE_EVO_TARGET_UNIFY_OFFSETS[2]: 0x16050004,
            },
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["customTickFunctionOffset"],
            PAL_DE_RESET_BUTTON_CUSTOM_FUNCTION_OFFSET,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["customTickHookOffset"],
            PAL_DE_RESET_BUTTON_HOOK_OFFSET,
        )

        with PAL_DE_ROM.open("rb") as rom:
            rom.seek(PAL_DE_EVO_TARGET_UNIFY_CONTEXT_OFFSET)
            evo_context = rom.read(len(PAL_DE_EVO_TARGET_UNIFY_ORIGINAL_CONTEXT))
            rom.seek(PAL_DE_RESET_BUTTON_CUSTOM_FUNCTION_OFFSET)
            custom_function_original = rom.read(len(PAL_DE_RESET_BUTTON_CUSTOM_FUNCTION_ORIGINAL_BYTES))
            rom.seek(PAL_DE_RESET_BUTTON_HOOK_CONTEXT_OFFSET)
            hook_context = rom.read(len(PAL_DE_RESET_BUTTON_HOOK_ORIGINAL_CONTEXT))

        self.assertEqual(evo_context, PAL_DE_EVO_TARGET_UNIFY_ORIGINAL_CONTEXT)
        self.assertEqual(custom_function_original, PAL_DE_RESET_BUTTON_CUSTOM_FUNCTION_ORIGINAL_BYTES)
        self.assertEqual(hook_context, PAL_DE_RESET_BUTTON_HOOK_ORIGINAL_CONTEXT)
        self.assertEqual(
            struct.pack(patch_data.evoTargetUnifyHackFormat, 0x24050003),
            bytes.fromhex("03 00 05 24"),
        )
        self.assertEqual(
            struct.pack(patch_data.customTickHookFormat, patch_data.customTickHookValue),
            bytes.fromhex("08 2f e7 24"),
        )

    def test_verified_pal_de_woah_patch_offsets(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["woahPatchOffset"],
            PAL_DE_WOAH_TEXT_OFFSETS,
        )
        self.assertEqual(PAL_DE_LAYOUT.patch_offsets["woahPatchFormat"], "<8s")
        self.assertEqual(PAL_DE_LAYOUT.patch_offsets["woahPatchPayload"], PAL_DE_WOAH_PAYLOAD)

        with PAL_DE_ROM.open("rb") as rom:
            woah_text_contexts = []
            for offset, expected_context in zip(PAL_DE_WOAH_TEXT_OFFSETS, PAL_DE_WOAH_TEXT_CONTEXTS):
                rom.seek(offset - 8)
                woah_text_contexts.append(rom.read(len(expected_context)))

        self.assertEqual(woah_text_contexts, list(PAL_DE_WOAH_TEXT_CONTEXTS))
        self.assertEqual([context[8:16] for context in woah_text_contexts], [PAL_DE_WOAH_ENCODED_TEXT] * 5)
        self.assertEqual(struct.pack("<8s", PAL_DE_WOAH_PAYLOAD), PAL_DE_WOAH_PAYLOAD)

    def test_verified_pal_de_intro_hash_patch_offset_and_size(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["introHashOffset"],
            PAL_DE_INTRO_HASH_OFFSET,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["introHashSize"],
            PAL_DE_INTRO_HASH_SIZE,
        )

        with PAL_DE_ROM.open("rb") as rom:
            rom.seek(PAL_DE_INTRO_HASH_OFFSET)
            original_text = rom.read(PAL_DE_INTRO_HASH_SIZE)

        self.assertEqual(original_text, PAL_DE_INTRO_HASH_ORIGINAL_TEXT)

    def test_verified_pal_de_intro_skip_patch_offsets_and_targets(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["introSkipOutsideOffset"],
            PAL_DE_INTRO_SKIP_OUTSIDE_OFFSET,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["introSkipOutsideDest"],
            PAL_DE_INTRO_SKIP_OUTSIDE_DEST,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["introSkipInsideOffset"],
            PAL_DE_INTRO_SKIP_INSIDE_OFFSET,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["introSkipInsideDest"],
            PAL_DE_INTRO_SKIP_INSIDE_DEST,
        )

        with PAL_DE_ROM.open("rb") as rom:
            rom.seek(PAL_DE_INTRO_SKIP_OUTSIDE_OFFSET)
            outside_original = rom.read(4)
            rom.seek(PAL_DE_INTRO_SKIP_OUTSIDE_TARGET_OFFSET)
            outside_target = rom.read(4)
            rom.seek(PAL_DE_INTRO_SKIP_INSIDE_OFFSET)
            inside_original = rom.read(4)
            rom.seek(PAL_DE_INTRO_SKIP_INSIDE_TARGET_OFFSET)
            inside_target = rom.read(4)

        self.assertEqual(outside_original, PAL_DE_INTRO_SKIP_OUTSIDE_ORIGINAL_COMMAND)
        self.assertEqual(outside_target, PAL_DE_INTRO_SKIP_OUTSIDE_TARGET_COMMAND)
        self.assertEqual(inside_original, PAL_DE_INTRO_SKIP_INSIDE_ORIGINAL_COMMAND)
        self.assertEqual(inside_target, PAL_DE_INTRO_SKIP_INSIDE_TARGET_COMMAND)

    def test_verified_pal_de_pp_calculation_patch_offset_and_payload(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["rewritePPOffset"],
            PAL_DE_PP_CALCULATION_CANDIDATE_OFFSET,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["rewritePPValue"],
            (
                0x0F19040C,
                0xFFFF6432,
                0x1E004010,
                0x00000000,
                0x1480023C,
                0x144B4224,
                0x21105200,
                0x00004290,
                0x03004230,
                0x21885100,
                0x16000010,
            ),
        )

        with PAL_DE_ROM.open("rb") as rom:
            rom.seek(PAL_DE_PP_CALCULATION_CANDIDATE_OFFSET)
            original_context = rom.read(len(PAL_DE_PP_CALCULATION_ORIGINAL_CONTEXT))

        self.assertEqual(original_context, PAL_DE_PP_CALCULATION_ORIGINAL_CONTEXT)
        self.assertIn(bytes.fromhex("14 80 02 3c 14 4b 42 24"), PAL_DE_PP_CALCULATION_PATCH_VALUE)
        self.assertNotIn(bytes.fromhex("13 80 02 3c ce ce 42 24"), PAL_DE_PP_CALCULATION_PATCH_VALUE)

    def test_verified_pal_de_spawn_rate_patch_offsets_and_commands(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["spawnRateMamemonOffset"],
            PAL_DE_SPAWN_RATE_MAMEMON_OFFSETS,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["spawnRatePiximonOffset"],
            PAL_DE_SPAWN_RATE_PIXIMON_OFFSETS,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["spawnRateMMamemonOffset"],
            PAL_DE_SPAWN_RATE_METALMAMEMON_OFFSETS,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["spawnRateOtamamonOffset"],
            PAL_DE_SPAWN_RATE_OTAMAMON_OFFSETS,
        )

        with PAL_DE_ROM.open("rb") as rom:
            commands = []
            for offset, _expected_command in PAL_DE_SPAWN_RATE_COMMANDS:
                rom.seek(offset - 1)
                commands.append((offset, rom.read(2)))

        self.assertEqual(commands, list(PAL_DE_SPAWN_RATE_COMMANDS))

    def test_verified_pal_de_unlock_area_patch_offsets(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["unlockGreylordOffset"],
            PAL_DE_UNLOCK_GREYLORD_OFFSETS,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["unlockIceOffset"],
            PAL_DE_UNLOCK_ICE_OFFSETS,
        )
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["unlockToyTownOffset"],
            PAL_DE_TOY_TOWN_LOCK_CHECK_OFFSETS,
        )

        with PAL_DE_ROM.open("rb") as rom:
            rom.seek(PAL_DE_UNLOCK_GREYLORD_OFFSETS[0])
            greylord_context = rom.read(2)
            ice_contexts = []
            for offset in PAL_DE_UNLOCK_ICE_OFFSETS:
                rom.seek(offset)
                ice_contexts.append(rom.read(2))
            toy_town_contexts = []
            for offset in PAL_DE_TOY_TOWN_LOCK_CHECK_OFFSETS:
                rom.seek(offset)
                toy_town_contexts.append(rom.read(4))

        self.assertEqual(greylord_context, bytes.fromhex("3c 00"))
        self.assertEqual(PAL_DE_UNLOCK_GREYLORD_VALUE, bytes.fromhex("ca 04"))
        self.assertEqual(ice_contexts, [bytes.fromhex("5d 01")] * 2)
        self.assertEqual(PAL_DE_UNLOCK_ICE_VALUE, bytes.fromhex("3c 00"))
        self.assertEqual(toy_town_contexts, [bytes.fromhex("00 00 5d 01")] * 2)
        self.assertEqual(PAL_DE_TOY_TOWN_UNLOCK_CANDIDATE_VALUE, bytes.fromhex("01 00 5d 01"))

    def test_verified_pal_de_ogremon_softlock_patch_offsets(self):
        self.assertEqual(
            PAL_DE_LAYOUT.patch_offsets["ogremonSoftlockOffset"],
            PAL_DE_OGREMON_SOFTLOCK_OFFSETS,
        )

        with PAL_DE_ROM.open("rb") as rom:
            ogremon_values = []
            for offset in PAL_DE_OGREMON_SOFTLOCK_OFFSETS:
                rom.seek(offset)
                ogremon_values.append(struct.unpack("<H", rom.read(2))[0])

            rom.seek(PAL_DE_OGREMON_SOFTLOCK_OFFSETS[0] - 0x3C)
            recruitment_context = rom.read(0x70)
            rom.seek(PAL_DE_OGREMON_SOFTLOCK_OFFSETS[1])
            ogremon_status_context = rom.read(0x70)
            rom.seek(PAL_DE_SHELLMON_STATUS_CHECK_OFFSET)
            shellmon_status_context = rom.read(0x70)

        self.assertEqual(ogremon_values, [234, 234])
        self.assertIn(scrutil.encode("Ogremon zieht in die Stadt"), recruitment_context)
        self.assertTrue(ogremon_status_context.startswith(bytes.fromhex("ea 00 81 00 5c 02")))
        self.assertIn(scrutil.encode("Ogremon war da"), ogremon_status_context)
        self.assertTrue(shellmon_status_context.startswith(bytes.fromhex("eb 00 81 00 5d 02")))
        self.assertIn(scrutil.encode("Shellmon war da"), shellmon_status_context)

    def test_pal_de_patch_registry_readiness_is_explicit(self):
        classified_patch_names = (
            set(PAL_DE_STATE_SAFE_PATCH_NAMES)
            | set(PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES)
            | set(PAL_DE_UNMAPPED_ROM_PATCH_NAMES)
            | set(PAL_DE_INCOMPATIBLE_ROM_PATCH_NAMES)
            | set(GLOBAL_DISABLED_PATCH_NAMES)
        )
        always_on_names = {patch.name for patch in ALWAYS_ON_PATCHES}

        self.assertEqual(classified_patch_names, set(PATCHES))
        self.assertTrue(set(PAL_DE_STATE_SAFE_PATCH_NAMES).isdisjoint(PAL_DE_UNMAPPED_ROM_PATCH_NAMES))
        self.assertTrue(set(PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES).isdisjoint(PAL_DE_UNMAPPED_ROM_PATCH_NAMES))
        self.assertTrue(set(PAL_DE_INCOMPATIBLE_ROM_PATCH_NAMES).isdisjoint(PAL_DE_UNMAPPED_ROM_PATCH_NAMES))
        self.assertTrue(set(PAL_DE_INCOMPATIBLE_ROM_PATCH_NAMES).isdisjoint(PAL_DE_STATE_SAFE_PATCH_NAMES))
        self.assertTrue(set(PAL_DE_INCOMPATIBLE_ROM_PATCH_NAMES).isdisjoint(PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES))
        self.assertTrue(set(PAL_DE_STATE_SAFE_PATCH_NAMES).isdisjoint(GLOBAL_DISABLED_PATCH_NAMES))
        self.assertTrue(set(PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES).isdisjoint(GLOBAL_DISABLED_PATCH_NAMES))
        self.assertTrue(set(PAL_DE_UNMAPPED_ROM_PATCH_NAMES).isdisjoint(GLOBAL_DISABLED_PATCH_NAMES))
        self.assertTrue(set(PAL_DE_INCOMPATIBLE_ROM_PATCH_NAMES).isdisjoint(GLOBAL_DISABLED_PATCH_NAMES))
        self.assertEqual(set(PAL_DE_UNMAPPED_ALWAYS_ON_PATCH_NAMES), set())
        self.assertTrue(always_on_names.isdisjoint(PAL_DE_UNMAPPED_ALWAYS_ON_PATCH_NAMES))
        self.assertIn("typeEffectiveness", PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES)
        self.assertIn("ogremon", PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES)
        self.assertIn("hash", PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES)
        self.assertIn("intro", PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES)
        self.assertIn("unlock", PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES)
        self.assertIn("pp", PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES)
        self.assertIn("spawn", PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES)
        self.assertIn("ogremon", PAL_DE_RECRUITMENT_REQUIRED_PATCH_NAMES)

        for name in PAL_DE_STATE_SAFE_PATCH_NAMES + PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES:
            self.assertTrue(PATCHES[name].supports_layout(PAL_DE_LAYOUT), name)
        for name in PAL_DE_UNMAPPED_ROM_PATCH_NAMES:
            self.assertFalse(PATCHES[name].supports_layout(PAL_DE_LAYOUT), name)
        for name in PAL_DE_INCOMPATIBLE_ROM_PATCH_NAMES:
            self.assertFalse(PATCHES[name].supports_layout(PAL_DE_LAYOUT), name)
        for name in GLOBAL_DISABLED_PATCH_NAMES:
            self.assertFalse(PATCHES[name].supports_layout(PAL_DE_LAYOUT), name)
        for patch in ALWAYS_ON_PATCHES:
            self.assertTrue(patch.supports_layout(PAL_DE_LAYOUT), patch.name)


if __name__ == "__main__":
    unittest.main()
