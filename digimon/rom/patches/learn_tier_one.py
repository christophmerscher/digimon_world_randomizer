"""Patch: let brain training teach tier-1 techs with a 30% success rate."""

from __future__ import annotations

from digimon.rom.patches.base import Patch, PatchContext


# Tier-1 specialty 0 is the lowest learnable rate; bumping it makes the
# whole first row of the brain-training matrix non-zero.
TIER_ONE_LEARN_RATE = 30


class LearnTierOnePatch(Patch):
    name = "learnTierOne"

    def apply(self, ctx: PatchContext) -> None:
        ctx.state.brainLearn[0][0] = TIER_ONE_LEARN_RATE
        ctx.logger.logChange(
            "Patched brain training to make tier 1 moves learnable with a 30% success rate."
        )
