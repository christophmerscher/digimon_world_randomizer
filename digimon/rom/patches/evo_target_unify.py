"""Patch (always-on): unify two near-duplicate evo-target functions.

Frees up ~one function's worth of memory at a fixed address so the
:class:`~digimon.rom.patches.reset_button.ResetButtonPatch` has somewhere
to write its custom tick function.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    evoTargetUnifyHack,
    evoTargetUnifyHackFormat,
)
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


class EvoTargetUnifyPatch(Patch):
    """Always applied — does not depend on any settings toggle."""

    name = "_evoTargetUnify"   # leading underscore: private registry key

    def apply(self, ctx: PatchContext) -> None:
        for offset, value in evoTargetUnifyHack.items():
            write_value(ctx.handle, offset,
                        struct.pack(evoTargetUnifyHackFormat, value))
        ctx.logger.logChange("Unified evoTarget functions.")
