# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: skip most of the opening Jijimon dialogue."""

from __future__ import annotations

import script.util as scrutil
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


class IntroSkipPatch(Patch):
    name = "intro"
    supported_layouts = None
    required_patch_offsets = (
        "introSkipOutsideOffset",
        "introSkipOutsideDest",
        "introSkipInsideOffset",
        "introSkipInsideDest",
    )

    def apply(self, ctx: PatchContext) -> None:
        write_value(
            ctx.handle,
            require_patch_offset(ctx, "introSkipOutsideOffset"),
            scrutil.compile(
                "jumpTo",
                require_patch_offset(ctx, "introSkipOutsideDest"),
            ),
        )
        write_value(
            ctx.handle,
            require_patch_offset(ctx, "introSkipInsideOffset"),
            scrutil.compile(
                "jumpTo",
                require_patch_offset(ctx, "introSkipInsideDest"),
            ),
        )
        ctx.logger.logChange("Modified intro scenes to remove most of the dialogue.")
