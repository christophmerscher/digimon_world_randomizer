"""Patch: change the Dragon Eye Lake vending machine output to HappyMushroom.

.. warning::

   This patch is **broken** in the legacy code — it references constants
   (``happyMushroomVendingFormat5`` / ``happyMushroomVendingValue5``)
   that have never been defined anywhere in the repository. Calling
   ``apply`` will raise :class:`NameError` at the final write.

   The Strategy class preserves the legacy crash so the byte-identical
   output guarantee holds for runs that don't enable this patch. The
   missing constants belong with the in-ROM text payloads that were
   never published; fixing the patch is tracked separately.
"""

from __future__ import annotations

import struct

from digimon.rom.patch_data import (
    happyMushroomVendingFormat1,
    happyMushroomVendingFormat2,
    happyMushroomVendingOffset1,
    happyMushroomVendingOffset2,
    happyMushroomVendingOffset3,
    happyMushroomVendingOffset4,
    happyMushroomVendingOffset5,
    happyMushroomVendingPriceFormat,
    happyMushroomVendingPriceValue,
    happyMushroomVendingValue1,
    happyMushroomVendingValue2,
)
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


class HappyVendingPatch(Patch):
    name = "happyVending"

    def apply(self, ctx: PatchContext) -> None:
        write_value(
            ctx.handle, happyMushroomVendingOffset1,
            struct.pack(happyMushroomVendingFormat1,
                        happyMushroomVendingValue1.encode("shift_jis")),
        )
        write_value(
            ctx.handle, happyMushroomVendingOffset2,
            struct.pack(happyMushroomVendingFormat2,
                        happyMushroomVendingValue2.encode("ascii")),
        )
        write_value(
            ctx.handle, happyMushroomVendingOffset3,
            struct.pack(happyMushroomVendingPriceFormat, happyMushroomVendingPriceValue),
        )
        write_value(
            ctx.handle, happyMushroomVendingOffset4,
            struct.pack(happyMushroomVendingPriceFormat, happyMushroomVendingPriceValue),
        )

        # The legacy code references ``happyMushroomVendingFormat5`` and
        # ``happyMushroomVendingValue5`` here, but neither exists in
        # ``digimon.rom.patch_data``. Preserve the legacy NameError.
        from digimon.rom import patch_data  # local import — preserves error site

        for offset in happyMushroomVendingOffset5:
            write_value(
                ctx.handle, offset,
                struct.pack(
                    patch_data.happyMushroomVendingFormat5,  # noqa: F821 — see docstring
                    patch_data.happyMushroomVendingValue5,   # noqa: F821 — see docstring
                ),
            )
