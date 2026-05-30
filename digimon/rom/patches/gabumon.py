"""Patch: bump enemy Gabumon's stats to mountain-clearing levels."""

from __future__ import annotations

import struct

from digimon.rom.patch_data import gabuPatchFormat, gabuPatchWrites
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


class GabumonPatch(Patch):
    name = "gabumon"

    def apply(self, ctx: PatchContext) -> None:
        for offset, value in gabuPatchWrites:
            write_value(ctx.handle, offset, struct.pack(gabuPatchFormat, value))
        ctx.logger.logChange("Patched enemy Gabumon to be unreasonably strong.")
