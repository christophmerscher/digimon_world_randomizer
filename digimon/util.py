# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""Backward-compatibility shim for the legacy ``digimon.util`` API.

The binary-codec helpers (``readDataWithExclusions`` &c.) now live in
:mod:`digimon.rom.struct_codec`; the name-lookup helpers wrap the
dictionaries in :mod:`digimon.rom.enums`. Both groups are re-exported
here under their original names so existing callers continue to work
while the refactor progresses.
"""

from __future__ import annotations

import digimon.data as data
from digimon.rom.struct_codec import (
    pack_array as _pack_array,
    read_block_with_exclusions as _read_block_with_exclusions,
    unpack_array as _unpack_array,
    write_block_with_exclusions as _write_block_with_exclusions,
    write_value as _write_value,
)


# ---------------------------------------------------------------------------
# Binary IO (legacy names)
# ---------------------------------------------------------------------------

def writeDataToFile(file, ofst, data, logger):
    """Write ``data`` bytes at the given offset; mirrors legacy signature."""

    return _write_value(file, ofst, data, logger)


def readDataWithExclusions(file, ofst, sz, excls, excl_sz):
    return _read_block_with_exclusions(file, ofst, sz, excls, excl_sz)


def writeDataWithExclusions(file, buf, ofst, sz, excls, excl_sz):
    return _write_block_with_exclusions(file, buf, ofst, sz, excls, excl_sz)


def unpackDataArray(buf, fmt, count):
    return _unpack_array(buf, fmt, count)


def packDataArray(records, fmt):
    return _pack_array(records, fmt)


# ---------------------------------------------------------------------------
# Name lookups (legacy names)
# ---------------------------------------------------------------------------

def typeIDToName(id: int) -> str:
    return data.types.get(id, "UNDEFINED")


def levelIDToName(id: int) -> str:
    return data.levels.get(id, "UNDEFINED")


def specIDToName(id: int) -> str:
    return data.specs.get(id, "-")


# ---------------------------------------------------------------------------
# Tech slot / animation ID conversion
# ---------------------------------------------------------------------------

# Move slots are 1-indexed; their animations are stored 0-indexed starting at
# this anim ID. So slot 1 maps to anim 0x2E, slot 2 to 0x2F, etc.
TECH_SLOT_ANIM_BASE = 0x2E
TECH_SLOT_COUNT = 16


def techSlotAnimID(slot: int) -> int:
    """Convert a 1..16 tech slot number into its animation ID."""

    if slot < 1 or slot > TECH_SLOT_COUNT:
        print(
            "Error: Tried to use an invalid tech slot: " + format(slot, "02x")
        )
        slot = 1

    return TECH_SLOT_ANIM_BASE + (slot - 1)


def animIDTechSlot(anim: int) -> int:
    """Convert an animation ID back into its 1..16 tech slot number."""

    slot = anim - TECH_SLOT_ANIM_BASE + 1

    if slot < 1 or slot > TECH_SLOT_COUNT:
        print(
            "Error: Tried to read an invalid animation ID as a tech slot: "
            + format(slot, "02x")
        )
        slot = 1

    return slot
