"""Patch: remove the digimon-type locks on Greylord's Mansion, Ice
Sanctuary, and Toy Town.

Also flags the writer to skip one of the Monzaemon/Toy Town special-
evolution writes so unlocking Toy Town doesn't double-write the same
byte from two patches.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    unlockGreylordOffset,
    unlockGreylordValue,
    unlockIceOffset,
    unlockIceValue,
    unlockToyTownFormat,
    unlockToyTownOffset,
    unlockToyTownValue,
    unlockTypeLockFormat,
)
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


class UnlockAreasPatch(Patch):
    name = "unlock"
    requires_toy_town_workaround = True

    def apply(self, ctx: PatchContext) -> None:
        for offset in unlockGreylordOffset:
            write_value(ctx.handle, offset,
                        struct.pack(unlockTypeLockFormat, unlockGreylordValue))
        for offset in unlockIceOffset:
            write_value(ctx.handle, offset,
                        struct.pack(unlockTypeLockFormat, unlockIceValue))
        for offset in unlockToyTownOffset:
            write_value(ctx.handle, offset,
                        struct.pack(unlockToyTownFormat, unlockToyTownValue))

        ctx.logger.logChange(
            "Removed digimon type locks on Greylord's Mansion, Ice Sanctuary and Toy Town."
        )
