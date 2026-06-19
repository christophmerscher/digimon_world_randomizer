# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch (always-on): unify two near-duplicate evo-target functions.

Frees up ~one function's worth of memory at a fixed address so the
:class:`~digimon.rom.patches.reset_button.ResetButtonPatch` has somewhere
to write its custom tick function.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import evoTargetUnifyHackFormat
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


class EvoTargetUnifyPatch(Patch):
    """Always applied — does not depend on any settings toggle."""

    name = "_evoTargetUnify"   # leading underscore: private registry key
    supported_layouts = None
    required_patch_offsets = ("evoTargetUnifyHack",)

    def apply(self, ctx: PatchContext) -> None:
        for offset, value in require_patch_offset(ctx, "evoTargetUnifyHack").items():
            write_value(ctx.handle, offset,
                        struct.pack(evoTargetUnifyHackFormat, value))
        ctx.logger.logChange("Unified evoTarget functions.")
