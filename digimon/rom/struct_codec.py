"""Low-level helpers for reading/writing the PSX ROM blocks.

A "block" in this codebase is a contiguous run of fixed-size records that
may contain "holes" — short runs of bytes belonging to unrelated systems
that the game engine doesn't touch. The exclusion-aware helpers below
honour those holes so the reader/writer can treat each block as a flat
array of records.

These are the *bytes-level* primitives. Higher-level orchestration lives
in :mod:`digimon.rom.reader` / :mod:`digimon.rom.writer`.
"""

from __future__ import annotations

import struct
from typing import BinaryIO, Iterable


def read_block_with_exclusions(
    file: BinaryIO,
    offset: int,
    size: int,
    exclusion_offsets: Iterable[int],
    exclusion_size: int,
) -> bytes:
    """Read a block, skipping over fixed-size "holes" inside it.

    ``size`` is the total size including the exclusions; the returned
    buffer omits them, so its length is ``size - len(exclusions) * exclusion_size``.
    """

    file.seek(offset, 0)
    out = b""

    bytes_read = 0
    for next_exclusion in exclusion_offsets:
        pos = offset + bytes_read
        bytes_to_read = next_exclusion - pos
        out += file.read(bytes_to_read)
        file.seek(exclusion_size, 1)
        bytes_read += bytes_to_read + exclusion_size

    out += file.read(size - bytes_read)
    return out


def write_block_with_exclusions(
    file: BinaryIO,
    buf: bytes,
    offset: int,
    size: int,
    exclusion_offsets: Iterable[int],
    exclusion_size: int,
) -> None:
    """Write a block back, skipping past the same holes the reader skipped."""

    exclusions = tuple(exclusion_offsets)
    expected_size = len(buf) + len(exclusions) * exclusion_size

    if size != expected_size:
        # Match legacy behaviour: emit a console error and return silently.
        # Callers rely on the previous block content already being on disk.
        print(
            "Error: trying to write data with size not matching expected size."
        )
        print(f"{size} {expected_size}")
        return

    file.seek(offset, 0)

    bytes_written = 0
    excluded_bytes = 0
    for next_exclusion in exclusions:
        pos = offset + bytes_written + excluded_bytes
        bytes_to_write = next_exclusion - pos
        file.write(buf[bytes_written : bytes_written + bytes_to_write])
        file.seek(exclusion_size, 1)
        bytes_written += bytes_to_write
        excluded_bytes += exclusion_size

    file.write(buf[bytes_written:])


def unpack_array(buf: bytes, fmt: str, count: int) -> list[tuple]:
    """Parse a flat byte buffer as a homogeneous array of structs."""

    fmt_size = struct.calcsize(fmt)

    if count * fmt_size != len(buf):
        print(
            "Error: trying to parse data array with size "
            "not matching expected size."
            + str(len(buf))
            + " "
            + str(count * fmt_size)
        )
        return []

    return [struct.unpack_from(fmt, buf, i * fmt_size) for i in range(count)]


def pack_array(records: Iterable[tuple], fmt: str) -> bytes:
    """Pack an iterable of struct-tuples into a single contiguous buffer."""

    buf = b""
    for record in records:
        buf += struct.pack(fmt, *record)
    return buf


def write_value(file: BinaryIO, offset: int, payload: bytes, _logger=None) -> int:
    """Seek + write a single packed payload at an absolute offset.

    The optional ``_logger`` parameter is kept for backward compatibility
    with the legacy ``digimon.util.writeDataToFile`` signature; it is not
    used here.
    """

    file.seek(offset, 0)
    return file.write(payload)
