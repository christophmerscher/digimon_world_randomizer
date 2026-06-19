# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: mark every item as dropable from the inventory menu."""

from __future__ import annotations

from digimon.rom.patches.base import Patch, PatchContext


class AllowDropPatch(Patch):
    name = "allowDrop"
    supported_layouts = None

    def apply(self, ctx: PatchContext) -> None:
        for item in ctx.state.itemData:
            item.dropable = True
        ctx.logger.logChange("Patched quest items to be dropable from the menu.")
