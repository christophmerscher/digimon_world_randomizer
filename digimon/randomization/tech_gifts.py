"""Randomise the techs gifted by Seadramon and the Beetle Land NPC."""

from __future__ import annotations

from digimon.randomization.base import Randomizer, RandomizationContext
from digimon.randomization.pickers import RandomTechPicker


class TechGiftsRandomizer(Randomizer):
    def apply(self, ctx: RandomizationContext) -> None:
        ctx.logger.logChange(ctx.logger.getHeader("Randomize Tech Gifts"))

        picker = RandomTechPicker(ctx.state)
        gifts = ctx.state.techGifts
        techs = ctx.state.techData

        for key in list(gifts):
            rand_id = picker.pick(learnableOnly=True)
            previous = gifts[key]
            gifts[key] = techs[rand_id].id

            ctx.logger.logChange(
                "Changed tech gift from " + ctx.lookup.getTechName(previous)
                + " to " + ctx.lookup.getTechName(gifts[key])
            )
