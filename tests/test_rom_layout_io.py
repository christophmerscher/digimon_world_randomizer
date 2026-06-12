# Author: Christoph Merscher <dev@fmerscher.com>

import io
import struct
import unittest

from digimon.rom.layouts import DataBlockLayout, RomLayout
from digimon.rom.reader import RomReader
from digimon.rom.writer import RomWriter


def _layout() -> RomLayout:
    return RomLayout(
        key="test",
        display_name="Test Layout",
        serials=("TEST_000.00",),
        complete=True,
        blocks={
            "numbers": DataBlockLayout(
                name="numbers",
                format="<H",
                offset=4,
                size=8,
                count=3,
                exclusion_offsets=(8,),
                exclusion_size=2,
            ),
        },
    )


class RomLayoutIoTests(unittest.TestCase):
    def test_reader_uses_supplied_layout_block_metadata(self):
        rom = io.BytesIO(
            b"\x00" * 4
            + struct.pack("<HH", 0x1111, 0x2222)
            + b"XY"
            + struct.pack("<H", 0x3333)
        )

        records = RomReader(object(), object(), _layout())._unpack_block(rom, "numbers")

        self.assertEqual(records, [(0x1111,), (0x2222,), (0x3333,)])

    def test_writer_uses_supplied_layout_block_metadata(self):
        rom = io.BytesIO(bytearray(b"." * 14))
        rom.seek(8)
        rom.write(b"XY")

        RomWriter(object(), _layout())._write_records(rom, "numbers", [(1,), (2,), (3,)])

        self.assertEqual(rom.getvalue()[4:8], struct.pack("<HH", 1, 2))
        self.assertEqual(rom.getvalue()[8:10], b"XY")
        self.assertEqual(rom.getvalue()[10:12], struct.pack("<H", 3))


if __name__ == "__main__":
    unittest.main()
