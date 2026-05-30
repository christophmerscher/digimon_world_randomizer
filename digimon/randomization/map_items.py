"""Randomise the items spawned on every map.

When ``food_only`` is set, food items are only swapped with other food
items (the rest of the spawns are left alone).
"""

from __future__ import annotations

from digimon.randomization.base import Randomizer, RandomizationContext
from digimon.randomization.pickers import RandomItemPicker


class MapItemsRandomizer(Randomizer):
    def __init__(self, food_only: bool = False, price: int = 1000) -> None:
        self.food_only = food_only
        self.price = price

    def apply(self, ctx: RandomizationContext) -> None:
        ctx.logger.logChange(ctx.logger.getHeader("Randomize Map Items"))

        picker = RandomItemPicker(ctx.state)
        items = ctx.state.itemData
        spawns = ctx.state.mapItems

        for key in list(spawns):
            previous_id = spawns[key]
            food_only_here = self.food_only and items[previous_id].isFood

            rand_id = picker.pick(
                foodOnly=food_only_here,
                consumableOnly=True,
                notQuest=True,
                notEvo=True,
                matchValueOf=previous_id,
                matchValue=self.price,
            )

            spawns[key] = items[rand_id].id
            ctx.logger.logChange(
                "Changed map item from " + items[previous_id].name
                + " to " + items[spawns[key]].name
            )
