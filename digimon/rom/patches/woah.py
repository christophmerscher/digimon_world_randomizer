# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: replace the "Woah!" item pickup text with custom text."""

from __future__ import annotations

import struct

from digimon.rom.patch_data import woahPatchFormat
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


PICKUP_TEXT = "Oh shit!"
MAX_TEXT_LENGTH = 8


class WoahPatch(Patch):
    name = "woah"
    supported_layouts = None
    required_patch_offsets = ("woahPatchOffset",)

    def apply(self, ctx: PatchContext) -> None:
        payload = _payload_for_layout(ctx)
        for offset in _offsets_for_layout(ctx):
            write_value(ctx.handle, offset, payload)

        ctx.logger.logChange('Patched "Woah!" text.')


def _payload_for_layout(ctx: PatchContext) -> bytes:
    layout_payload = ctx.layout.patch_offsets.get("woahPatchPayload")
    if layout_payload is not None:
        return struct.pack(
            ctx.layout.patch_offsets.get("woahPatchFormat", str(len(layout_payload)) + "s"),
            layout_payload,
        )

    return struct.pack(woahPatchFormat, PICKUP_TEXT[:MAX_TEXT_LENGTH].encode("ascii"))


def _offsets_for_layout(ctx: PatchContext):
    offsets = require_patch_offset(ctx, "woahPatchOffset")
    if isinstance(offsets, tuple):
        return offsets

    return (offsets,)
