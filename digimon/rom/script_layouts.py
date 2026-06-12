# Author: Christoph Merscher <dev@fmerscher.com>

"""Region-specific script offset tables.

Script offsets are scattered one-off command locations rather than compact
record arrays. Keeping them behind a layout object lets the reader/writer use
the same orchestration for every region while each disc version owns its own
verified addresses.
"""

from __future__ import annotations

from dataclasses import dataclass

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
