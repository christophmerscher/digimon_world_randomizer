# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: remove the digimon-type locks on Greylord's Mansion, Ice
Sanctuary, and Toy Town.

Also flags the writer to skip one of the Monzaemon/Toy Town special-
evolution writes so unlocking Toy Town doesn't double-write the same
byte from two patches.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    unlockGreylordValue,
    unlockIceValue,
    unlockToyTownFormat,
    unlockToyTownValue,
    unlockTypeLockFormat,
)
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


class UnlockAreasPatch(Patch):
    name = "unlock"
    requires_toy_town_workaround = True
    supported_layouts = None
    required_patch_offsets = (
        "unlockGreylordOffset",
        "unlockIceOffset",
        "unlockToyTownOffset",
    )

    def requires_writer_workaround(self, layout) -> bool:
        scripts = layout.require_scripts()
        return scripts.toyTownSpecEvoSkipOffset >= 0

    def apply(self, ctx: PatchContext) -> None:
        for offset in require_patch_offset(ctx, "unlockGreylordOffset"):
            write_value(ctx.handle, offset,
                        struct.pack(unlockTypeLockFormat, unlockGreylordValue))
        for offset in require_patch_offset(ctx, "unlockIceOffset"):
            write_value(ctx.handle, offset,
                        struct.pack(unlockTypeLockFormat, unlockIceValue))
        for offset in require_patch_offset(ctx, "unlockToyTownOffset"):
            write_value(ctx.handle, offset,
                        struct.pack(unlockToyTownFormat, unlockToyTownValue))

        ctx.logger.logChange(
            "Removed digimon type locks on Greylord's Mansion, Ice Sanctuary and Toy Town."
        )
