# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: prevent the Ogremon-2 room softlock.

If Ogremon 3 is completed before Ogremon 2, the engine loses track of
which fight is current and the player can become stuck in the room. We
replace the Ogremon-3 trigger check with the (always-true) Shellmon-
recruited check.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    ogremonSoftlockFormat,
    ogremonSoftlockValue,
)
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


class OgremonSoftlockPatch(Patch):
    name = "ogremon"
    supported_layouts = None
    required_patch_offsets = ("ogremonSoftlockOffset",)

    def apply(self, ctx: PatchContext) -> None:
        for offset in require_patch_offset(ctx, "ogremonSoftlockOffset"):
            write_value(ctx.handle, offset,
                        struct.pack(ogremonSoftlockFormat, ogremonSoftlockValue))
        ctx.logger.logChange("Applied Ogremon softlock fix")
