# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: fix four movement-related softlocks.

Each fix overwrites a single instruction (or branch target) at every
copy of the buggy code path so the engine continues movement instead of
spinning on an aborted entityMoveTo / entityWalkTo / rotation update.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    fixLeoCaveSLFormat,
    fixLeoCaveSLValue,
    fixMoveToSLFormat,
    fixMoveToSLValue,
    fixRotationSLFormat,
    fixRotationSLValue,
    fixToyTownSLFormat,
    fixToyTownSLValue,
)
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


class MovementSoftlockPatch(Patch):
    name = "softlock"
    supported_layouts = None
    required_patch_offsets = (
        "fixRotationSLOffset",
        "fixMoveToSLOffset",
        "fixToyTownSLOffset",
        "fixLeoCaveSLOffset",
    )

    def apply(self, ctx: PatchContext) -> None:
        self._apply_group(
            ctx, require_patch_offset(ctx, "fixRotationSLOffset"),
            fixRotationSLFormat, fixRotationSLValue,
        )
        self._apply_group(
            ctx, require_patch_offset(ctx, "fixMoveToSLOffset"),
            fixMoveToSLFormat, fixMoveToSLValue,
        )
        self._apply_group(
            ctx, require_patch_offset(ctx, "fixToyTownSLOffset"),
            fixToyTownSLFormat, fixToyTownSLValue,
        )
        self._apply_group(
            ctx, require_patch_offset(ctx, "fixLeoCaveSLOffset"),
            fixLeoCaveSLFormat, fixLeoCaveSLValue,
        )

        ctx.logger.logChange("Applied 4 movement softlock patches.")

    @staticmethod
    def _apply_group(ctx: PatchContext, offsets, fmt, value) -> None:
        for offset in offsets:
            write_value(ctx.handle, offset, struct.pack(fmt, value))
