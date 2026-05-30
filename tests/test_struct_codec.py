# Author: Christoph Merscher <dev@fmerscher.com>

"""Round-trip tests for the binary IO primitives.

The reader and writer share these helpers, so verifying them with a
synthetic in-memory ROM gives us confidence the per-block extraction
in :mod:`digimon.rom.reader` / :mod:`digimon.rom.writer` is correct
without needing the actual PSX image.
"""

from __future__ import annotations

import io
import struct
import unittest

from digimon.rom.struct_codec import (
    pack_array,
    read_block_with_exclusions,
    unpack_array,
    write_block_with_exclusions,
    write_value,
)


class StructCodecTests(unittest.TestCase):
    def test_pack_and_unpack_array_are_inverses(self):
        records = [(i, i * 2, i * 3) for i in range(4)]
        fmt = "<BHI"

        packed = pack_array(records, fmt)
        self.assertEqual(len(packed), 4 * struct.calcsize(fmt))

        self.assertEqual(unpack_array(packed, fmt, 4), records)

    def test_read_block_skips_exclusion_holes(self):
        # Build a synthetic ROM:
        #   0x00..0x09  → "AAAAA" + "BBBBB"            (10 bytes of payload)
        #   0x0A..0x0F  → 6 bytes of hole (excluded)
        #   0x10..0x14  → "CCCCC"                       (5 more payload bytes)
        rom_bytes = (b"A" * 5 + b"B" * 5 + b"X" * 6 + b"C" * 5)
        rom = io.BytesIO(rom_bytes)

        result = read_block_with_exclusions(
            rom,
            offset=0,
            size=len(rom_bytes),
            exclusion_offsets=(0x0A,),
            exclusion_size=6,
        )

        self.assertEqual(result, b"A" * 5 + b"B" * 5 + b"C" * 5)

    def test_write_block_round_trips_through_excluded_region(self):
        # Build a synthetic ROM with the same layout, then overwrite the
        # payload via the writer and confirm the hole bytes survive.
        rom_bytes = bytearray(b"A" * 5 + b"B" * 5 + b"X" * 6 + b"C" * 5)
        rom = io.BytesIO(rom_bytes)

        new_payload = b"D" * 5 + b"E" * 5 + b"F" * 5
        write_block_with_exclusions(
            rom, new_payload,
            offset=0,
            size=len(rom_bytes),
            exclusion_offsets=(0x0A,),
            exclusion_size=6,
        )

        rom.seek(0)
        written = rom.read()
        self.assertEqual(written, b"D" * 5 + b"E" * 5 + b"X" * 6 + b"F" * 5)

    def test_write_block_rejects_size_mismatch_without_writing(self):
        rom = io.BytesIO(b"\x00" * 16)

        # Total size declares 16 bytes minus a 6-byte hole = 10 payload bytes
        # expected; we pass only 5 → mismatch.
        write_block_with_exclusions(
            rom, b"D" * 5,
            offset=0,
            size=16,
            exclusion_offsets=(0x0A,),
            exclusion_size=6,
        )

        rom.seek(0)
        self.assertEqual(rom.read(), b"\x00" * 16)

    def test_write_value_seeks_then_writes(self):
        rom = io.BytesIO(b"\x00" * 8)
        wrote = write_value(rom, 4, b"\xab\xcd")

        self.assertEqual(wrote, 2)
        rom.seek(0)
        self.assertEqual(rom.read(), b"\x00\x00\x00\x00\xab\xcd\x00\x00")


if __name__ == "__main__":
    unittest.main()
