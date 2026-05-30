"""Patch: double the chance of learning techs in battle + brain training.

Zero rates in brain training stay non-zero (the engine treats 0 as
"never"); they get replaced with a low fallback so every cell has at
least a small chance to fire.
"""

from __future__ import annotations

from digimon.rom.patches.base import Patch, PatchContext


# Replacement value for previously-zero brain-train cells.
ZERO_REPLACEMENT_RATE = 5


class IncreaseLearnChancePatch(Patch):
    name = "upLearnChance"

    def apply(self, ctx: PatchContext) -> None:
        for tech in ctx.state.techData:
            for i, val in enumerate(tech.learnChance):
                tech.learnChance[i] = val * 2

        for chances in ctx.state.brainLearn:
            for i, val in enumerate(chances):
                chances[i] = (val * 2) if val != 0 else ZERO_REPLACEMENT_RATE

        ctx.logger.logChange("Patched learn chance (battle and brain) to be twice as high.")
