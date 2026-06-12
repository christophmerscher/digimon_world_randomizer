# Author: Christoph Merscher <dev@fmerscher.com>

import struct
import unittest
from pathlib import Path

import script.util as scrutil
from digimon.util import animIDTechSlot
from digimon.rom.layouts import (
    IncompleteLayoutError,
    PAL_DE_LAYOUT,
    layout_for_region,
)
from digimon.rom.region import RomRegion, detect_rom_region
from digimon.rom.struct_codec import read_block_with_exclusions


PAL_DE_ROM = Path(__file__).resolve().parents[1] / "roms" / "Digimon World (Germany).bin"
TYPE_EFFECTIVENESS_VALUES = {2, 5, 10, 15, 20}
MUELLBERG_BEI_NACHT = bytes.fromhex(
    "82 6c 83 58 82 8c 82 8c 82 82 82 85 82 92 82 87"
    " 81 40 82 82 82 85 82 89 81 40 82 6d 82 81 82 83 82 88 82 94"
)
KAEFER_POKAL = bytes.fromhex(
    "82 6a 83 56 82 86 82 85 82 92 81 40 82 6f 82 8f 82 8b 82 81 82 8c"
)
PAL_DE_STARTER_CHECK_OFFSETS = (0x157023BC, 0x157023E0)
PAL_DE_STARTER_LEARN_TECH_OFFSETS = (0x157023D4, 0x157023F8)
PAL_DE_STARTER_EQUIP_ANIM_OFFSETS = (0x157023C8, 0x157023EC)
PAL_DE_STARTER_SET_OFFSETS = (0x15782634, 0x15782640)
PAL_DE_TOKOMON_ITEM_OFFSETS = (
    0x14A1ECE0,
    0x14A1ECE4,
    0x14A1ECE8,
    0x14A1ECEC,
    0x14A1ECF0,
    0x14A1ECF4,
)


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

    def test_unmapped_pal_de_blocks_fail_explicitly(self):
        with self.assertRaises(IncompleteLayoutError):
            PAL_DE_LAYOUT.require_scripts()

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


if __name__ == "__main__":
    unittest.main()
