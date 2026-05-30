"""Patch: skip most of the opening Jijimon dialogue."""

from __future__ import annotations

import script.util as scrutil
from digimon.rom.patch_data import (
    introSkipInsideDest,
    introSkipInsideOffset,
    introSkipOutsideDest,
    introSkipOutsideOffset,
)
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


class IntroSkipPatch(Patch):
    name = "intro"

    def apply(self, ctx: PatchContext) -> None:
        write_value(
            ctx.handle,
            introSkipOutsideOffset,
            scrutil.compile("jumpTo", introSkipOutsideDest),
        )
        write_value(
            ctx.handle,
            introSkipInsideOffset,
            scrutil.compile("jumpTo", introSkipInsideDest),
        )
        ctx.logger.logChange("Modified intro scenes to remove most of the dialogue.")
