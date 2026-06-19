# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: change the Dragon Eye Lake vending machine output to HappyMushroom."""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    happyMushroomVendingFormat1,
    happyMushroomVendingFormat2,
    happyMushroomVendingFormat5,
    happyMushroomVendingPriceFormat,
    happyMushroomVendingPriceValue,
    happyMushroomVendingValue1,
    happyMushroomVendingValue2,
    happyMushroomVendingValue5,
)
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


def _offsets(value):
    if isinstance(value, tuple):
        return value
    return (value,)


def _patch_value(ctx: PatchContext, name: str, default):
    layout = ctx.layout
    if layout is not None and name in layout.patch_offsets:
        return layout.patch_offsets[name]
    return default


class HappyVendingPatch(Patch):
    name = "happyVending"
    supported_layouts = ("ntsc-u", "pal-de")
    required_patch_offsets = (
        "happyMushroomVendingOffset1",
        "happyMushroomVendingOffset2",
        "happyMushroomVendingOffset3",
        "happyMushroomVendingOffset4",
        "happyMushroomVendingOffset5",
    )

    def apply(self, ctx: PatchContext) -> None:
        menu_format = _patch_value(ctx, "happyMushroomVendingFormat1", happyMushroomVendingFormat1)
        menu_payload = _patch_value(
            ctx,
            "happyMushroomVendingPayload1",
            happyMushroomVendingValue1.encode("shift_jis"),
        )
        result_format = _patch_value(ctx, "happyMushroomVendingFormat2", happyMushroomVendingFormat2)
        result_payload = _patch_value(
            ctx,
            "happyMushroomVendingPayload2",
            happyMushroomVendingValue2.encode("ascii"),
        )
        price_value = _patch_value(ctx, "happyMushroomVendingPriceValue", happyMushroomVendingPriceValue)
        item_value = _patch_value(ctx, "happyMushroomVendingValue5", happyMushroomVendingValue5)

        for offset in _offsets(require_patch_offset(ctx, "happyMushroomVendingOffset1")):
            write_value(ctx.handle, offset, struct.pack(menu_format, menu_payload))

        for offset in _offsets(require_patch_offset(ctx, "happyMushroomVendingOffset2")):
            write_value(ctx.handle, offset, struct.pack(result_format, result_payload))

        for offset in _offsets(require_patch_offset(ctx, "happyMushroomVendingOffset3")):
            write_value(
                ctx.handle,
                offset,
                struct.pack(happyMushroomVendingPriceFormat, price_value),
            )

        for offset in _offsets(require_patch_offset(ctx, "happyMushroomVendingOffset4")):
            write_value(
                ctx.handle,
                offset,
                struct.pack(happyMushroomVendingPriceFormat, price_value),
            )

        for offset in require_patch_offset(ctx, "happyMushroomVendingOffset5"):
            write_value(
                ctx.handle,
                offset,
                struct.pack(happyMushroomVendingFormat5, item_value),
            )
