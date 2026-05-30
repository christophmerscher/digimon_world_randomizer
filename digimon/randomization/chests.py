"""Randomise the contents of every chest in the game."""

from __future__ import annotations

from digimon.randomization.base import Randomizer, RandomizationContext
from digimon.randomization.pickers import RandomItemPicker


class ChestItemsRandomizer(Randomizer):
    def __init__(self, allow_evo: bool = False) -> None:
        self.allow_evo = allow_evo

    def apply(self, ctx: RandomizationContext) -> None:
        ctx.logger.logChange(ctx.logger.getHeader("Randomize Chest Items"))

        picker = RandomItemPicker(ctx.state)
        items = ctx.state.itemData
        chests = ctx.state.chestItems

        for key in list(chests):
            rand_id = picker.pick(notQuest=True, notEvo=(not self.allow_evo))
            previous = chests[key]
            chests[key] = items[rand_id].id

            ctx.logger.logChange(
                "Changed chest item from " + items[previous].name
                + " to " + items[chests[key]].name
            )
