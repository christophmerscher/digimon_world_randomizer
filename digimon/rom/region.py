# Author: Christoph Merscher <dev@fmerscher.com>

"""PlayStation disc-region detection for Digimon World ROM images.

The randomizer currently has only the NTSC-U address layout mapped. PAL
images must be detected before any offset table is used, otherwise the
reader/writer can seek into unrelated PAL data and produce a broken ROM.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import BinaryIO


class RomRegion(Enum):
    """Known Digimon World disc regions."""

    NTSC_U = "NTSC-U"
    PAL = "PAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RomRegionInfo:
    """Detected region metadata."""

    region: RomRegion
    serial: str | None = None


DETECTION_SCAN_BYTES = 4 * 1024 * 1024

_NTSC_U_SERIALS = (
    b"SLUS_010.32",
    b"SLUS-01032",
    b"SLUS01032",
)

_PAL_SERIALS = (
    b"SLES_029.14",
    b"SLES-02914",
    b"SLES02914",
    b"SLES_034.34",
    b"SLES-03434",
    b"SLES03434",
)


def detect_rom_region(handle: BinaryIO) -> RomRegionInfo:
    """Detect a ROM region by scanning the disc header area for serials."""

    original_position = handle.tell()
    try:
        handle.seek(0, 0)
        header = handle.read(DETECTION_SCAN_BYTES)
    finally:
        handle.seek(original_position, 0)

    serial = _find_serial(header)
    if serial is None:
        return RomRegionInfo(RomRegion.UNKNOWN)

    if serial.startswith("SLUS"):
        return RomRegionInfo(RomRegion.NTSC_U, serial)
    if serial.startswith("SLES"):
        return RomRegionInfo(RomRegion.PAL, serial)

    return RomRegionInfo(RomRegion.UNKNOWN, serial)


def _find_serial(data: bytes) -> str | None:
    for serial in _NTSC_U_SERIALS + _PAL_SERIALS:
        if serial in data:
            return serial.decode("ascii").replace("-", "_")

    return None


def ensure_supported_region(info: RomRegionInfo) -> None:
    """Raise if the detected region does not have a mapped layout yet."""

    if info.region is RomRegion.NTSC_U:
        return

    if info.region is RomRegion.PAL:
        suffix = " (" + info.serial + ")" if info.serial else ""
        raise UnsupportedRomRegionError(
            "PAL Digimon World ROM detected" + suffix
            + ", but PAL offset tables are not mapped yet. "
            + "Please provide the PAL .bin so the layout can be mapped safely."
        )

    suffix = " (" + info.serial + ")" if info.serial else ""
    raise UnsupportedRomRegionError(
        "Could not detect a supported Digimon World ROM region" + suffix + "."
    )


class UnsupportedRomRegionError(Exception):
    """Raised when the ROM region cannot be handled safely."""
