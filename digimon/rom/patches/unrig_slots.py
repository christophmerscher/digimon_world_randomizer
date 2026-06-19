# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: short-circuit the rigging logic on the bonus-training slot machines.

Overwrites one instruction inside both training-slot functions (one per
station REL) so the result is purely skill-based instead of weighted.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    unrigSlots2Format,
    unrigSlots2Value,
    unrigSlotsFormat,
    unrigSlotsValue,
)
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


class UnrigSlotsPatch(Patch):
    name = "slots"
    supported_layouts = None
    required_patch_offsets = ("unrigSlotsOffset", "unrigSlots2Offset")

    def apply(self, ctx: PatchContext) -> None:
        write_value(ctx.handle, require_patch_offset(ctx, "unrigSlotsOffset"),
                    struct.pack(unrigSlotsFormat, unrigSlotsValue))
        write_value(ctx.handle, require_patch_offset(ctx, "unrigSlots2Offset"),
                    struct.pack(unrigSlots2Format, unrigSlots2Value))
        ctx.logger.logChange("Un-rigged slots.")
