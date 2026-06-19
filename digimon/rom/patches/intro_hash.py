# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: write the settings hash into the Jijimon intro dialogue.

Used during races so every participant can verify they generated the
same ROM by reading the hash in-game.
"""

from __future__ import annotations

import script.util as scrutil
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


# The dialogue box is two short lines; we split the hash in the middle.
LINE_LENGTH = 16
LINE_GAP = "\n"
TRAILING_PAD = "   "


class IntroHashPatch(Patch):
    name = "hash"
    takes_value = True
    supported_layouts = None
    required_patch_offsets = ("introHashOffset",)

    def apply(self, ctx: PatchContext) -> None:
        full_hash = "" if ctx.value is None else str(ctx.value)
        first_line = full_hash[:LINE_LENGTH]
        second_line = full_hash[LINE_LENGTH - 1:] + TRAILING_PAD

        payload = scrutil.encode(first_line + LINE_GAP + second_line)
        if ctx.layout is not None and "introHashSize" in ctx.layout.patch_offsets:
            field_size = ctx.layout.patch_offsets["introHashSize"]
            if len(payload) > field_size:
                raise ValueError("Encoded intro hash is larger than the mapped text field.")
            payload = payload + (b"\0" * (field_size - len(payload)))

        write_value(ctx.handle, require_patch_offset(ctx, "introHashOffset"), payload)
        ctx.logger.logChange("Inserted settings hash into intro dialogue.")
