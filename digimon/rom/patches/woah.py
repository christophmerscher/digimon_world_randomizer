"""Patch: replace the "Woah!" item pickup text with custom text."""

from __future__ import annotations

import struct

from digimon.rom.patch_data import woahPatchFormat, woahPatchOffset
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


PICKUP_TEXT = "Oh shit!"
MAX_TEXT_LENGTH = 8


class WoahPatch(Patch):
    name = "woah"

    def apply(self, ctx: PatchContext) -> None:
        write_value(
            ctx.handle,
            woahPatchOffset,
            struct.pack(woahPatchFormat, PICKUP_TEXT[:MAX_TEXT_LENGTH].encode("ascii")),
        )
        ctx.logger.logChange('Patched "Woah!" to be "' + PICKUP_TEXT + '".')
