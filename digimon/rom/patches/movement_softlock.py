"""Patch: fix four movement-related softlocks.

Each fix overwrites a single instruction (or branch target) at every
copy of the buggy code path so the engine continues movement instead of
spinning on an aborted entityMoveTo / entityWalkTo / rotation update.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    fixLeoCaveSLFormat,
    fixLeoCaveSLOffset,
    fixLeoCaveSLValue,
    fixMoveToSLFormat,
    fixMoveToSLOffset,
    fixMoveToSLValue,
    fixRotationSLFormat,
    fixRotationSLOffset,
    fixRotationSLValue,
    fixToyTownSLFormat,
    fixToyTownSLOffset,
    fixToyTownSLValue,
)
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


class MovementSoftlockPatch(Patch):
    name = "softlock"

    def apply(self, ctx: PatchContext) -> None:
        self._apply_group(ctx, fixRotationSLOffset,  fixRotationSLFormat,  fixRotationSLValue)
        self._apply_group(ctx, fixMoveToSLOffset,    fixMoveToSLFormat,    fixMoveToSLValue)
        self._apply_group(ctx, fixToyTownSLOffset,   fixToyTownSLFormat,   fixToyTownSLValue)
        self._apply_group(ctx, fixLeoCaveSLOffset,   fixLeoCaveSLFormat,   fixLeoCaveSLValue)

        ctx.logger.logChange("Applied 4 movement softlock patches.")

    @staticmethod
    def _apply_group(ctx: PatchContext, offsets, fmt, value) -> None:
        for offset in offsets:
            write_value(ctx.handle, offset, struct.pack(fmt, value))
