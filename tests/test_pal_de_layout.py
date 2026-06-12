# Author: Christoph Merscher <dev@fmerscher.com>

import struct
import unittest
from pathlib import Path

from digimon.rom.layouts import (
    IncompleteLayoutError,
    PAL_DE_LAYOUT,
    layout_for_region,
)
from digimon.rom.region import RomRegion, detect_rom_region
from digimon.rom.struct_codec import read_block_with_exclusions


PAL_DE_ROM = Path(__file__).resolve().parents[1] / "roms" / "Digimon World (Germany).bin"
TYPE_EFFECTIVENESS_VALUES = {2, 5, 10, 15, 20}


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

    def test_unmapped_pal_de_blocks_fail_explicitly(self):
        with self.assertRaises(IncompleteLayoutError):
            PAL_DE_LAYOUT.require_block("itemData")

        with self.assertRaises(IncompleteLayoutError):
            PAL_DE_LAYOUT.require_block("digimonData")


if __name__ == "__main__":
    unittest.main()
