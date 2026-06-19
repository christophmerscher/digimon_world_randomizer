# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: allow learning a move and a command in the same brain-training session.

The game gates the second learn opportunity behind the "command learned"
textbox; removing it lets both fire.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    learnMoveAndCommandFormat,
    learnMoveAndCommandValue,
)
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


class LearnMoveAndCommandPatch(Patch):
    name = "learnmoveandcommand"
    supported_layouts = None
    required_patch_offsets = ("learnMoveAndCommandOffset",)

    def apply(self, ctx: PatchContext) -> None:
        write_value(
            ctx.handle,
            require_patch_offset(ctx, "learnMoveAndCommandOffset"),
            struct.pack(learnMoveAndCommandFormat, *learnMoveAndCommandValue),
        )
        ctx.logger.logChange("Fixing move learning at brains training.")
