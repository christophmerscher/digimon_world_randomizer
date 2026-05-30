"""Patch: randomise the 7x7 type effectiveness chart."""

from __future__ import annotations

import random
import struct

from digimon.rom.patch_data import typeEffectivenessFormat, typeEffectivenessOffset
from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.struct_codec import write_value


# Each cell becomes one of these five multipliers (×0.02, ×0.05, ×0.10, ×0.15, ×0.20).
EFFECTIVENESS_VALUES = (2, 5, 10, 15, 20)
TYPE_COUNT = 7


class TypeEffectivenessPatch(Patch):
    """Note: kept under the legacy name ``typeEffectiveness`` even though
    it's a randomiser rather than a fixed patch. It happens at write-time
    against the ROM file, which is why it lives with the patches."""

    name = "typeEffectiveness"

    def apply(self, ctx: PatchContext) -> None:
        ctx.logger.logChange("Changing type effectivness chart")

        for type1 in range(TYPE_COUNT):
            row = ""
            for type2 in range(TYPE_COUNT):
                new_value = random.choice(EFFECTIVENESS_VALUES)
                offset = type1 * TYPE_COUNT + type2
                write_value(
                    ctx.handle,
                    typeEffectivenessOffset + offset,
                    struct.pack(typeEffectivenessFormat, new_value),
                )
                row += str(new_value) + " "
            ctx.logger.logChange(row)

        ctx.logger.logChange("Randomized type effectiveness")
