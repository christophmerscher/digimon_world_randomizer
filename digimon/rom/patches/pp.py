# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: rewrite the prosperity-point calculation function.

Reads the new PP value from the least-significant two bits of each
digimon's height (the recruitment randomiser stashes the value there).
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import rewritePPFormat
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


class PPCalculationPatch(Patch):
    name = "pp"
    supported_layouts = None
    required_patch_offsets = ("rewritePPOffset", "rewritePPValue")

    def apply(self, ctx: PatchContext) -> None:
        payload = require_patch_offset(ctx, "rewritePPValue")
        write_value(
            ctx.handle,
            require_patch_offset(ctx, "rewritePPOffset"),
            struct.pack(rewritePPFormat, *payload),
        )
        ctx.logger.logChange("Updated PP calculation function.")
