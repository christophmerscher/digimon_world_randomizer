# Author: Christoph Merscher <dev@fmerscher.com>

"""Region-specific ROM address layouts.

The randomizer works directly against raw PlayStation ``.bin`` images. Those
images include 304 bytes of sector metadata for every 2048 bytes of game data,
so a region layout must own both the data offsets and the sector-gap
exclusions. A plain "PAL offset = NTSC offset + delta" is not safe.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from digimon.rom import blocks, patch_data
from digimon.rom.region import RomRegion, RomRegionInfo
from digimon.rom.script_layouts import NTSC_U_SCRIPT_LAYOUT, ScriptLayout


@dataclass(frozen=True)
class DataBlockLayout:
    """Raw-image location and struct metadata for one readable/writable block."""

    name: str
    format: str
    offset: int
    size: int
    count: int | None = None
    exclusion_offsets: tuple[int, ...] = ()
    exclusion_size: int = 0x130
    verified: bool = True
    note: str = ""


@dataclass(frozen=True)
class RomLayout:
    """Strategy object for one concrete disc layout."""

    key: str
    display_name: str
    serials: tuple[str, ...]
    complete: bool
    blocks: Mapping[str, DataBlockLayout]
    scripts: ScriptLayout | None = None
    patch_offsets: Mapping[str, int] = field(default_factory=dict)
    unmapped: tuple[str, ...] = ()

    def require_block(self, name: str) -> DataBlockLayout:
        """Return a mapped block or raise a clear error for incomplete layouts."""

        try:
            return self.blocks[name]
        except KeyError as exc:
            raise IncompleteLayoutError(
                f"{self.display_name} does not have a verified mapping for {name!r} yet."
            ) from exc

    def require_scripts(self) -> ScriptLayout:
        """Return the mapped script layout or explain what is still missing."""

        if self.scripts is None:
            raise IncompleteLayoutError(
                f"{self.display_name} does not have verified script offsets yet."
            )

        return self.scripts


class IncompleteLayoutError(Exception):
    """Raised when a region layout is known but not fully mapped yet."""


def _block(
    name: str,
    fmt: str,
    offset: int,
    size: int,
    count: int | None,
    exclusion_offsets: tuple[int, ...] = (),
    exclusion_size: int = 0x130,
) -> DataBlockLayout:
    return DataBlockLayout(
        name=name,
        format=fmt,
        offset=offset,
        size=size,
        count=count,
        exclusion_offsets=exclusion_offsets,
        exclusion_size=exclusion_size,
    )


NTSC_U_LAYOUT = RomLayout(
    key="ntsc-u",
    display_name="NTSC-U",
    serials=("SLUS_010.32",),
    complete=True,
    blocks={
        "techData": _block(
            "techData", blocks.techDataFormat, blocks.techDataBlockOffset,
            blocks.techDataBlockSize, blocks.techDataBlockCount,
            blocks.techDataExclusionOffsets, blocks.techDataExclusionSize,
        ),
        "techLearn": _block(
            "techLearn", blocks.techLearnFormat, blocks.techLearnBlockOffset,
            blocks.techLearnBlockSize, blocks.techLearnBlockCount,
            blocks.techLearnExclusionOffsets, blocks.techLearnExclusionSize,
        ),
        "techBrain": _block(
            "techBrain", blocks.techBrainFormat, blocks.techBrainBlockOffset,
            blocks.techBrainBlockSize, blocks.techBrainBlockCount,
            blocks.techBrainExclusionOffsets, blocks.techBrainExclusionSize,
        ),
        "techTierList": _block(
            "techTierList", blocks.techTierListFormat, blocks.techTierListBlockOffset,
            blocks.techTierListBlockSize, blocks.techTierListBlockCount,
            blocks.techTierListExclusionOffsets, blocks.techTierListExclusionSize,
        ),
        "digimonData": _block(
            "digimonData", blocks.digimonDataFormat, blocks.digimonDataBlockOffset,
            blocks.digimonDataBlockSize, blocks.digimonDataBlockCount,
            blocks.digimonDataExclusionOffsets, blocks.digimonDataExclusionSize,
        ),
        "evoToFrom": _block(
            "evoToFrom", blocks.evoToFromFormat, blocks.evoToFromBlockOffset,
            blocks.evoToFromBlockSize, blocks.evoToFromBlockCount,
            blocks.evoToFromExclusionOffsets, blocks.evoToFromExclusionSize,
        ),
        "evoStats": _block(
            "evoStats", blocks.evoStatsFormat, blocks.evoStatsBlockOffset,
            blocks.evoStatsBlockSize, blocks.evoStatsBlockCount,
            blocks.evoStatsExclusionOffsets, blocks.evoStatsExclusionSize,
        ),
        "evoReqs": _block(
            "evoReqs", blocks.evoReqsFormat, blocks.evoReqsBlockOffset,
            blocks.evoReqsBlockSize, blocks.evoReqsBlockCount,
            blocks.evoReqsExclusionOffsets, blocks.evoReqsExclusionSize,
        ),
        "itemData": _block(
            "itemData", blocks.itemDataFormat, blocks.itemDataBlockOffset,
            blocks.itemDataBlockSize, blocks.itemDataBlockCount,
            blocks.itemDataExclusionOffsets, blocks.itemDataExclusionSize,
        ),
        "trackName": _block(
            "trackName", "raw", blocks.trackNameBlockOffset,
            blocks.trackNameBlockSize, None,
            blocks.trackNameExclusionOffsets, blocks.trackNameExclusionSize,
        ),
    },
    scripts=NTSC_U_SCRIPT_LAYOUT,
    patch_offsets={
        "typeEffectivenessOffset": patch_data.typeEffectivenessOffset,
    },
)


PAL_DE_LAYOUT = RomLayout(
    key="pal-de",
    display_name="PAL-DE",
    serials=("SLES_034.34",),
    complete=False,
    blocks={
        "techData": _block(
            "techData", blocks.techDataFormat, 0x157A15E4,
            0x8C0, blocks.techDataBlockCount,
            (0x157A1AB8,), blocks.techDataExclusionSize,
        ),
        "techLearn": _block(
            "techLearn", blocks.techLearnFormat, 0x157A134C,
            0xAE, blocks.techLearnBlockCount,
            (), blocks.techLearnExclusionSize,
        ),
        "techBrain": _block(
            "techBrain", blocks.techBrainFormat, 0x157AA704,
            blocks.techBrainBlockSize, blocks.techBrainBlockCount,
            (), blocks.techBrainExclusionSize,
        ),
        "techTierList": _block(
            "techTierList", blocks.techTierListFormat, 0x1784F4,
            blocks.techTierListBlockSize, blocks.techTierListBlockCount,
            (), blocks.techTierListExclusionSize,
        ),
        "evoReqs": _block(
            "evoReqs", blocks.evoReqsFormat, 0x157A70B8,
            0x814, blocks.evoReqsBlockCount,
            (0x157A7698,), blocks.evoReqsExclusionSize,
        ),
        "evoStats": _block(
            "evoStats", blocks.evoStatsFormat, 0x157A78CC,
            0x39C, blocks.evoStatsBlockCount,
            (), blocks.evoStatsExclusionSize,
        ),
        "evoToFrom": _block(
            "evoToFrom", blocks.evoToFromFormat, 0x157A7C68,
            0x2AA, blocks.evoToFromBlockCount,
            (), blocks.evoToFromExclusionSize,
        ),
        "digimonData": DataBlockLayout(
            name="digimonData",
            format="<ihh23Bx",
            offset=0x157ABD68,
            size=0x1A10,
            count=blocks.digimonDataBlockCount,
            exclusion_offsets=(0x157AC018, 0x157AC948, 0x157AD278),
            exclusion_size=blocks.digimonDataExclusionSize,
            note="PAL-DE stores Digimon names in a separate encoded text table.",
        ),
        "itemData": DataBlockLayout(
            name="itemData",
            format="<IHHb?2x",
            offset=0x157A1EB4,
            size=0x730,
            count=blocks.itemDataBlockCount,
            exclusion_offsets=(0x157A23E8,),
            exclusion_size=blocks.itemDataExclusionSize,
            note="PAL-DE stores item names in a separate encoded text table.",
        ),
        "trackName": DataBlockLayout(
            name="trackName",
            format="raw",
            offset=0x157A5FD4,
            size=0xA6A,
            count=None,
            exclusion_offsets=(0x157A6438,),
            exclusion_size=blocks.trackNameExclusionSize,
            note="German Giromon jukebox names; one name spans the exclusion hole.",
        ),
    },
    patch_offsets={
        "typeEffectivenessOffset": 0x157A1318,
    },
    unmapped=(
        "scriptOffsets",
        "optionalPatches",
    ),
)


def layout_for_region(info: RomRegionInfo) -> RomLayout:
    """Return the layout strategy matching detected ROM metadata."""

    if info.region is RomRegion.NTSC_U:
        return NTSC_U_LAYOUT

    if info.serial in PAL_DE_LAYOUT.serials:
        return PAL_DE_LAYOUT

    raise IncompleteLayoutError(
        f"No verified ROM layout exists for {info.serial or info.region.value}."
    )
