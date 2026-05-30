"""Randomise tech stat data (power, MP cost, accuracy, effect).

Has two modes:

* ``shuffle`` — swap vanilla values between random pairs of learnable techs.
* ``random``  — apply ``shuffle`` first, then jitter each value within a
  reasonable range around the vanilla average (kept verbatim from the
  legacy implementation so RNG order stays preserved).
"""

from __future__ import annotations

import random

from digimon.randomization.base import Randomizer, RandomizationContext
from digimon.randomization.pickers import RandomTechPicker


# Caps mirror what the engine accepts.
MAX_POWER     = 999
MAX_MP        = 255

# Probability (out of 100) that the effect roll yields a real effect.
EFFECT_NOEFFECT_THRESHOLD = 1   # random.randint(0, 1) > 0  → ~50%
MAX_EFFECT_CHANCE         = 70


class TechDataRandomizer(Randomizer):
    def __init__(
        self,
        mode: str = "shuffle",
        power: bool = False,
        cost: bool = False,
        accuracy: bool = False,
        effect: bool = False,
        effect_chance: bool = False,
    ) -> None:
        self.mode          = mode
        self.power         = power
        self.cost          = cost
        self.accuracy      = accuracy
        self.effect        = effect
        self.effect_chance = effect_chance

    def apply(self, ctx: RandomizationContext) -> None:
        ctx.logger.logChange(ctx.logger.getHeader("Randomize Tech Data"))
        picker = RandomTechPicker(ctx.state)

        for tech in ctx.state.techData:
            if not tech.isLearnable:
                continue
            self._shuffle_single(tech, ctx, picker)

        if self.mode != "shuffle":
            for tech in ctx.state.techData:
                self._jitter_single(tech)

        # This must run AFTER all swapping is done — power/mp/accuracy may
        # have been moved across techs above.
        for tech in ctx.state.techData:
            if not tech.isLearnable:
                continue
            ctx.logger.logChange(
                "{:<2d} Set '{:s}' to {:d} power {:d} MP with {:d} accuracy\n"
                "   {:s} {:d}% of the time.  Learn chance {:d}%-{:d}%-{:d}%".format(
                    tech.id, tech.name, tech.power, tech.mp3 * 3, tech.accuracy,
                    ctx.lookup.getEffectName(tech.effect), tech.effChance,
                    tech.learnChance[0], tech.learnChance[1], tech.learnChance[2],
                )
            )

    # ------------------------------------------------------------------
    def _shuffle_single(self, tech, ctx: RandomizationContext, picker: RandomTechPicker) -> None:
        if self.power and tech.power > 0:
            swap = ctx.state.techData[picker.pick(learnableOnly=True, damagingOnly=True)]
            tech.power, swap.power = swap.power, tech.power

        if self.cost:
            swap = ctx.state.techData[picker.pick(learnableOnly=True)]
            tech.mp3, swap.mp3 = swap.mp3, tech.mp3

        if self.accuracy:
            swap = ctx.state.techData[picker.pick(learnableOnly=True)]
            tech.accuracy, swap.accuracy = swap.accuracy, tech.accuracy

        if self.effect:
            if random.randint(0, 1) > 0 and self.power != 0:
                tech.effect = random.randint(1, 4)
            else:
                tech.effect    = 0
                tech.effChance = 0

        if self.effect_chance:
            if tech.effect == 0:
                tech.effChance = 0
            else:
                tech.effChance = random.randint(1, MAX_EFFECT_CHANCE)

    def _jitter_single(self, tech) -> None:
        if self.power:
            percent = random.randint(70, 130)
            tech.power = int(min((tech.power * percent) / 100, MAX_POWER))

        if self.cost and tech.power != 0:
            factor = random.randint(10, 140)
            tech.mp3 = int(min((factor * tech.power) / 300, MAX_MP))

        if self.accuracy:
            roll = random.randint(0, 99)
            if   roll < 10: tech.accuracy = random.randint(33, 60)
            elif roll < 50: tech.accuracy = random.randint(50, 80)
            elif roll < 90: tech.accuracy = random.randint(75, 100)
            else:           tech.accuracy = 100
