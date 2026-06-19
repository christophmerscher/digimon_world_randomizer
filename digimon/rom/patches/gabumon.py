# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: bump enemy Gabumon's stats to mountain-clearing levels."""

from __future__ import annotations

import struct

from digimon.rom.patch_data import gabuPatchFormat
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


class GabumonPatch(Patch):
    name = "gabumon"
    supported_layouts = None
    required_patch_offsets = ("gabuPatchWrites",)

    def apply(self, ctx: PatchContext) -> None:
        for offset, value in require_patch_offset(ctx, "gabuPatchWrites"):
            write_value(ctx.handle, offset, struct.pack(gabuPatchFormat, value))
        ctx.logger.logChange("Patched enemy Gabumon to be unreasonably strong.")
