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
    ogremonSoftlockOffset,
    ogremonSoftlockValue,
)
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


class OgremonSoftlockPatch(Patch):
    name = "ogremon"

    def apply(self, ctx: PatchContext) -> None:
        for offset in ogremonSoftlockOffset:
            write_value(ctx.handle, offset,
                        struct.pack(ogremonSoftlockFormat, ogremonSoftlockValue))
        ctx.logger.logChange("Applied Ogremon softlock fix")
