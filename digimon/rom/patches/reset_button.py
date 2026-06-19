# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch (always-on): add a button combination that reboots the game.

Writes a small custom tick function plus a hook that calls it every
frame. Depends on the memory freed by
:class:`~digimon.rom.patches.evo_target_unify.EvoTargetUnifyPatch`, so
the two must be applied in that order.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    customTickFunctionFormat,
    customTickFunctionValue,
    customTickHookFormat,
    customTickHookValue,
)
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


class ResetButtonPatch(Patch):
    """Always applied — does not depend on any settings toggle."""

    name = "_resetButton"   # leading underscore: private registry key
    supported_layouts = None
    required_patch_offsets = ("customTickFunctionOffset", "customTickHookOffset")

    def apply(self, ctx: PatchContext) -> None:
        write_value(
            ctx.handle, require_patch_offset(ctx, "customTickFunctionOffset"),
            struct.pack(customTickFunctionFormat, *customTickFunctionValue),
        )
        write_value(
            ctx.handle, require_patch_offset(ctx, "customTickHookOffset"),
            struct.pack(customTickHookFormat, customTickHookValue),
        )
        ctx.logger.logChange("Added custom function and hook for it")
