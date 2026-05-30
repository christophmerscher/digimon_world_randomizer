"""Randomise per-digimon drop item and drop rate."""

from __future__ import annotations

import random

from digimon.randomization.base import Randomizer, RandomizationContext
from digimon.randomization.pickers import RandomItemPicker


# Drop-rate buckets the legacy randomiser samples from. Sliding the index
# inside ``CHOOSE_FROM_RATES`` keeps the new rate "close" to the old one.
DEFAULT_RATES     = [1, 5, 10, 20, 25, 30, 40, 50]
CHOOSE_FROM_RATES = [1, 1, 1, 5, 10, 20, 25, 30, 40, 50, 50, 50]


class DigimonDataRandomizer(Randomizer):
    def __init__(
        self,
        drop_item: bool = False,
        drop_rate: bool = False,
        price: int = 1000,
    ) -> None:
        self.drop_item = drop_item
        self.drop_rate = drop_rate
        self.price = price

    def apply(self, ctx: RandomizationContext) -> None:
        ctx.logger.logChange(ctx.logger.getHeader("Randomize Digimon Data"))

        picker = RandomItemPicker(ctx.state)

        for digi in ctx.state.digimonData:
            if self.drop_item:
                digi.item = picker.pick(
                    consumableOnly=True, notQuest=True, notEvo=True,
                    matchValueOf=digi.item, matchValue=self.price,
                )

            if self.drop_rate:
                self._reroll_drop_rate(digi)

            ctx.logger.logChange(
                "Set {:s} to drop {:s} {:d}% of the time".format(
                    digi.name,
                    ctx.lookup.getItemName(digi.item),
                    digi.drop_rate,
                )
            )

    @staticmethod
    def _reroll_drop_rate(digi) -> None:
        rate = digi.drop_rate

        # Never demote a 100% drop or randomise a brand-new 100% drop.
        if rate == 0:
            digi.drop_rate = random.choice(DEFAULT_RATES)
        elif rate != 100:
            i = DEFAULT_RATES.index(rate) + 2
            digi.drop_rate = random.choice(CHOOSE_FROM_RATES[i - 2 : i + 3])
