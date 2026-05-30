"""Patch: short-circuit the rigging logic on the bonus-training slot machines.

Overwrites one instruction inside both training-slot functions (one per
station REL) so the result is purely skill-based instead of weighted.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    unrigSlots2Format,
    unrigSlots2Offset,
    unrigSlots2Value,
    unrigSlotsFormat,
    unrigSlotsOffset,
    unrigSlotsValue,
)
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


class UnrigSlotsPatch(Patch):
    name = "slots"

    def apply(self, ctx: PatchContext) -> None:
        write_value(ctx.handle, unrigSlotsOffset,
                    struct.pack(unrigSlotsFormat, unrigSlotsValue))
        write_value(ctx.handle, unrigSlots2Offset,
                    struct.pack(unrigSlots2Format, unrigSlots2Value))
        ctx.logger.logChange("Un-rigged slots.")
