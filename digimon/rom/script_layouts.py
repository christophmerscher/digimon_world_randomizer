# Author: Christoph Merscher <dev@fmerscher.com>

"""Region-specific script offset tables.

Script offsets are scattered one-off command locations rather than compact
record arrays. Keeping them behind a layout object lets the reader/writer use
the same orchestration for every region while each disc version owns its own
verified addresses.
"""

from __future__ import annotations

from dataclasses import dataclass

from digimon.rom.pal_de_script_offsets import PAL_DE_CHEST_ITEM_OFFSETS, PAL_DE_MAP_ITEM_OFFSETS
from digimon.rom import script_offsets


@dataclass(frozen=True)
class ScriptLayout:
    """All script-command offsets needed by the randomizer for one region."""

    scriptOffsetInBinary: int

    starterSetDigimonOffset: tuple[int, int]
    starterChkDigimonOffset: tuple[int, int]
    starterLearnTechOffset: tuple[int, int]
    starterEquipAnimOffset: tuple[int, int]
    starterStatChkDigimonOffset: int

    chestItemFormat: str
    chestItemOffsets: tuple[int, ...]

    mapItemFormat: str
    mapItemOffsets: tuple[int, ...]

    tokoItemFormat: str
    tokoItemOffsets: tuple[int, ...]

    learnMoveFormat: str
    learnMoveOffsets: tuple[int, ...]
    checkMoveFormat: str
    checkMoveOffsets: tuple[int, ...]

    recruitFormat: str
    recruitOffsets: tuple[tuple[tuple[int, ...], tuple[int, ...], int, int], ...]

    specEvoFormat: str
    specEvoOffsets: tuple[tuple[tuple[int, ...], int, int], ...]
    toyTownSpecEvoSkipOffset: int

    dynamicRecruitOffsets: bool = False
    """Whether the reader derives recruitment offsets from the input ROM."""


NTSC_U_SCRIPT_LAYOUT = ScriptLayout(
    scriptOffsetInBinary=script_offsets.scriptOffsetInBinary,
    starterSetDigimonOffset=script_offsets.starterSetDigimonOffset,
    starterChkDigimonOffset=script_offsets.starterChkDigimonOffset,
    starterLearnTechOffset=script_offsets.starterLearnTechOffset,
    starterEquipAnimOffset=script_offsets.starterEquipAnimOffset,
    starterStatChkDigimonOffset=script_offsets.starterStatChkDigimonOffset,
    chestItemFormat=script_offsets.chestItemFormat,
    chestItemOffsets=script_offsets.chestItemOffsets,
    mapItemFormat=script_offsets.mapItemFormat,
    mapItemOffsets=script_offsets.mapItemOffsets,
    tokoItemFormat=script_offsets.tokoItemFormat,
    tokoItemOffsets=script_offsets.tokoItemOffsets,
    learnMoveFormat=script_offsets.learnMoveFormat,
    learnMoveOffsets=script_offsets.learnMoveOffsets,
    checkMoveFormat=script_offsets.checkMoveFormat,
    checkMoveOffsets=script_offsets.checkMoveOffsets,
    recruitFormat=script_offsets.recruitFormat,
    recruitOffsets=script_offsets.recruitOffsets,
    specEvoFormat=script_offsets.specEvoFormat,
    specEvoOffsets=script_offsets.specEvoOffsets,
    toyTownSpecEvoSkipOffset=0x140479ED,
)


_PAL_DE_MONZAEMON_SPEC_EVO_OFFSETS = (
    0x149F42D8,
    0x149F434E,
    0x149F43AF,
    0x149F443F,
    0x149F4CB0,
)
_PAL_DE_GIROMON_SPEC_EVO_OFFSETS = (
    0x149C91AC,
    0x149C93F4,
)
_PAL_DE_METALMAMEMON_SPEC_EVO_OFFSETS = (
    0x149C9232,
    0x149C947A,
)
_PAL_DE_SUKAMON_SPEC_EVO_OFFSETS = (
    0x14A2991A,
    0x14A29926,
    0x14A29F7A,
    0x14A29F86,
)

_PAL_DE_SPEC_EVO_OFFSETS = (
    (_PAL_DE_MONZAEMON_SPEC_EVO_OFFSETS, 0x0E, 0x0B),
    (_PAL_DE_GIROMON_SPEC_EVO_OFFSETS, 0x29, 0x0D),
    (_PAL_DE_METALMAMEMON_SPEC_EVO_OFFSETS, 0x1B, 0x0D),
    ((0x14A5D741,), 0x25, 0x03),  # Bakemon
    ((0x14A5D465,), 0x1A, 0x0C),  # SkullGreymon
    ((0x14A5DE3B,), 0x3B, 0x32),  # Phoenixmon
    ((0x14A5CDD3,), 0x06, 0x14),  # Devimon
    ((0x14A5CE1D,), 0x07, 0x0A),  # Airdramon
    ((0x14A5DDF3,), 0x3A, 0x19),  # Ninjamon
    ((0x14A5D9D3,), 0x2F, 0x26),  # Monochromon
    ((0x14A5D5EF,), 0x20, 0x02),  # Kunemon
    ((0x14A5DA5F,), 0x31, 0x18),  # Coelamon
    ((0x14A5DB6F,), 0x35, 0x35),  # Nanimon
    ((0x14A5D4E5,), 0x1C, 0x1C),  # Vademon
    (_PAL_DE_SUKAMON_SPEC_EVO_OFFSETS, 0x27, 0x27),
)


PAL_DE_SCRIPT_LAYOUT = ScriptLayout(
    scriptOffsetInBinary=0,
    starterSetDigimonOffset=(0x15782634, 0x15782640),
    starterChkDigimonOffset=(0x157023BC, 0x157023E0),
    starterLearnTechOffset=(0x157023D4, 0x157023F8),
    starterEquipAnimOffset=(0x157023C8, 0x157023EC),
    starterStatChkDigimonOffset=0x14A2BF39,
    chestItemFormat=script_offsets.chestItemFormat,
    chestItemOffsets=PAL_DE_CHEST_ITEM_OFFSETS,
    mapItemFormat=script_offsets.mapItemFormat,
    mapItemOffsets=PAL_DE_MAP_ITEM_OFFSETS,
    tokoItemFormat=script_offsets.tokoItemFormat,
    tokoItemOffsets=(
        0x14A1ECE0,
        0x14A1ECE4,
        0x14A1ECE8,
        0x14A1ECEC,
        0x14A1ECF0,
        0x14A1ECF4,
    ),
    learnMoveFormat=script_offsets.learnMoveFormat,
    learnMoveOffsets=(
        0x149D4DDE,
        0x1498D058,
        0x1498D0A0,
        0x1498D0E4,
    ),
    checkMoveFormat=script_offsets.checkMoveFormat,
    checkMoveOffsets=(
        0x149D4A22,
        0x1498D050,
        0x1498D098,
        0x1498D0DC,
    ),
    recruitFormat=script_offsets.recruitFormat,
    recruitOffsets=(),
    specEvoFormat=script_offsets.specEvoFormat,
    specEvoOffsets=_PAL_DE_SPEC_EVO_OFFSETS,
    toyTownSpecEvoSkipOffset=-1,
    dynamicRecruitOffsets=True,
)
