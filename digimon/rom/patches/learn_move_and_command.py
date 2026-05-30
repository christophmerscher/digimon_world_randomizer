"""Patch: allow learning a move and a command in the same brain-training session.

The game gates the second learn opportunity behind the "command learned"
textbox; removing it lets both fire.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    learnMoveAndCommandFormat,
    learnMoveAndCommandOffset,
    learnMoveAndCommandValue,
)
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


class LearnMoveAndCommandPatch(Patch):
    name = "learnmoveandcommand"

    def apply(self, ctx: PatchContext) -> None:
        write_value(
            ctx.handle,
            learnMoveAndCommandOffset,
            struct.pack(learnMoveAndCommandFormat, *learnMoveAndCommandValue),
        )
        ctx.logger.logChange("Fixing move learning at brains training.")
