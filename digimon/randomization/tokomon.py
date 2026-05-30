"""Randomise the items (and quantities) Tokomon hands out."""

from __future__ import annotations

import random

from digimon.randomization.base import Randomizer, RandomizationContext
from digimon.randomization.pickers import RandomItemPicker


# Items priced at or above this threshold get fewer copies per gift.
EXPENSIVE_PRICE_THRESHOLD = 1000


class TokomonItemsRandomizer(Randomizer):
    def __init__(self, consumable_only: bool = True) -> None:
        self.consumable_only = consumable_only

    def apply(self, ctx: RandomizationContext) -> None:
        ctx.logger.logChange(ctx.logger.getHeader("Randomize Tokomon Items"))

        picker = RandomItemPicker(ctx.state)
        items = ctx.state.itemData
        toko = ctx.state.tokoItems

        for key in list(toko):
            rand_id = picker.pick(
                notQuest=True, notEvo=True, consumableOnly=self.consumable_only,
            )

            count = self._sample_count(items[rand_id].price)

            previous_item, previous_count = toko[key]
            toko[key] = (items[rand_id].id, count)

            ctx.logger.logChange(
                "Changed Tokomon item from " + str(previous_count) + "x '"
                + items[previous_item].name
                + " to " + str(count) + "x '"
                + items[toko[key][0]].name + "'"
            )

    @staticmethod
    def _sample_count(price: int) -> int:
        """Reproduce the legacy two-roll bias toward small stacks of
        expensive items / non-singleton stacks of cheap items."""

        count = random.randint(1, 3)
        if price >= EXPENSIVE_PRICE_THRESHOLD and count > 1:
            count = random.randint(1, 3)
        elif price < EXPENSIVE_PRICE_THRESHOLD and count == 1:
            count = random.randint(1, 3)
        return count
