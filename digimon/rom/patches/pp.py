"""Patch: rewrite the prosperity-point calculation function.

Reads the new PP value from the least-significant two bits of each
digimon's height (the recruitment randomiser stashes the value there).
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import rewritePPFormat, rewritePPOffset, rewritePPValue
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


class PPCalculationPatch(Patch):
    name = "pp"

    def apply(self, ctx: PatchContext) -> None:
        write_value(
            ctx.handle,
            rewritePPOffset,
            struct.pack(rewritePPFormat, *rewritePPValue),
        )
        ctx.logger.logChange("Updated PP calculation function.")
