# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: make evo items grant stats and lifetime when consumed."""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    evoItemPatchValue,
    evoitemPatchFormat,
)
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


class FixEvoItemsPatch(Patch):
    name = "fixEvoItems"
    supported_layouts = None
    required_patch_offsets = ("evoItemPatchOffset",)

    def apply(self, ctx: PatchContext) -> None:
        write_value(
            ctx.handle,
            require_patch_offset(ctx, "evoItemPatchOffset"),
            struct.pack(evoitemPatchFormat, evoItemPatchValue),
        )
        ctx.logger.logChange("Patched evo items to increase stats and lifetime.")
