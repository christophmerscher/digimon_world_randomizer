"""Patch: rewrite the in-game DV-chip descriptions to match real behaviour."""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    DVChipAFormat, DVChipAOffset, DVChipAValue,
    DVChipDFormat, DVChipDOffset, DVChipDValue,
    DVChipEFormat, DVChipEOffset, DVChipEValue,
)
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


# The text field accepts 28 bytes; the visible portion is 26 — the rest
# is the box's null-terminator + padding (preserved by the format spec).
MAX_VISIBLE = 26


class DVChipDescriptionsPatch(Patch):
    name = "fixDVChips"

    def apply(self, ctx: PatchContext) -> None:
        self._write_one(ctx, DVChipAOffset, DVChipAFormat, DVChipAValue)
        self._write_one(ctx, DVChipDOffset, DVChipDFormat, DVChipDValue)
        self._write_one(ctx, DVChipEOffset, DVChipEFormat, DVChipEValue)

    @staticmethod
    def _write_one(ctx: PatchContext, offset: int, fmt: str, text: str) -> None:
        write_value(ctx.handle, offset, struct.pack(fmt, text[:MAX_VISIBLE].encode("ascii")))
