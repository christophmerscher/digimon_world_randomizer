# Author: Christoph Merscher <dev@fmerscher.com>

import io
import unittest

from digimon.rom.region import (
    RomRegion,
    UnsupportedRomRegionError,
    detect_rom_region,
    ensure_supported_region,
)


class RomRegionTests(unittest.TestCase):
    def test_detects_ntsc_u_serial_without_moving_handle_position(self):
        rom = io.BytesIO(b"\0" * 32 + b"cdrom:\\SLUS_010.32;1" + b"\0" * 32)
        rom.seek(5)

        info = detect_rom_region(rom)

        self.assertEqual(info.region, RomRegion.NTSC_U)
        self.assertEqual(info.serial, "SLUS_010.32")
        self.assertEqual(rom.tell(), 5)
        ensure_supported_region(info)

    def test_detects_pal_serial_and_rejects_until_layout_is_mapped(self):
        rom = io.BytesIO(b"\0" * 32 + b"cdrom:\\SLES_029.14;1" + b"\0" * 32)

        info = detect_rom_region(rom)

        self.assertEqual(info.region, RomRegion.PAL)
        self.assertEqual(info.serial, "SLES_029.14")
        with self.assertRaises(UnsupportedRomRegionError):
            ensure_supported_region(info)

    def test_detects_german_pal_serial(self):
        rom = io.BytesIO(b"\0" * 32 + b"cdrom:\\SLES_034.34;1" + b"\0" * 32)

        info = detect_rom_region(rom)

        self.assertEqual(info.region, RomRegion.PAL)
        self.assertEqual(info.serial, "SLES_034.34")

    def test_unknown_region_is_rejected(self):
        info = detect_rom_region(io.BytesIO(b"not a known digimon world image"))

        self.assertEqual(info.region, RomRegion.UNKNOWN)
        with self.assertRaises(UnsupportedRomRegionError):
            ensure_supported_region(info)


if __name__ == "__main__":
    unittest.main()
