# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: rewrite the in-game DV-chip descriptions to match real behaviour."""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    DVChipAFormat, DVChipAValue,
    DVChipDFormat, DVChipDValue,
    DVChipEFormat, DVChipEValue,
)
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


# The text field accepts 28 bytes; the visible portion is 26 — the rest
# is the box's null-terminator + padding (preserved by the format spec).
MAX_VISIBLE = 26


class DVChipDescriptionsPatch(Patch):
    name = "fixDVChips"
    supported_layouts = ("ntsc-u", "pal-de")
    required_patch_offsets = ("DVChipAOffset", "DVChipDOffset", "DVChipEOffset")

    def apply(self, ctx: PatchContext) -> None:
        self._write_one(ctx, "DVChipA", DVChipAFormat, DVChipAValue.encode("ascii"))
        self._write_one(ctx, "DVChipD", DVChipDFormat, DVChipDValue.encode("ascii"))
        self._write_one(ctx, "DVChipE", DVChipEFormat, DVChipEValue.encode("ascii"))

    @staticmethod
    def _write_one(ctx: PatchContext, prefix: str, default_format: str, default_payload: bytes) -> None:
        layout = ctx.layout
        fmt = default_format
        payload = default_payload[:MAX_VISIBLE]
        if layout is not None:
            fmt = layout.patch_offsets.get(prefix + "Format", fmt)
            payload = layout.patch_offsets.get(prefix + "Payload", payload)

        write_value(
            ctx.handle,
            require_patch_offset(ctx, prefix + "Offset"),
            struct.pack(fmt, payload),
        )
