"""Patch: write the settings hash into the Jijimon intro dialogue.

Used during races so every participant can verify they generated the
same ROM by reading the hash in-game.
"""

from __future__ import annotations

import script.util as scrutil
from digimon.rom.patch_data import introHashOffset
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


# The dialogue box is two short lines; we split the hash in the middle.
LINE_LENGTH = 16
LINE_GAP = "\n"
TRAILING_PAD = "   "


class IntroHashPatch(Patch):
    name = "hash"
    takes_value = True

    def apply(self, ctx: PatchContext) -> None:
        full_hash = "" if ctx.value is None else str(ctx.value)
        first_line = full_hash[:LINE_LENGTH]
        second_line = full_hash[LINE_LENGTH - 1:] + TRAILING_PAD

        payload = scrutil.encode(first_line + LINE_GAP + second_line)
        write_value(ctx.handle, introHashOffset, payload)
        ctx.logger.logChange("Inserted settings hash into intro dialogue.")
