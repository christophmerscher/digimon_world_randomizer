"""Randomise the digimon produced by each special-evolution trigger."""

from __future__ import annotations

import random

from data.digimon import ChampionDigimon
from digimon.randomization.base import Randomizer, RandomizationContext


class SpecialEvolutionsRandomizer(Randomizer):
    def apply(self, ctx: RandomizationContext) -> None:
        ctx.logger.logChange(ctx.logger.getHeader("Randomize Special Evolutions"))

        spec_evos = ctx.state.specEvos
        digimon_data = ctx.state.digimonData

        for offsets in spec_evos:
            current_id, from_id = spec_evos[offsets]
            candidates = ctx.lookup.getPlayableDigimonByLevel(
                digimon_data[current_id].level
            )

            new_id = random.choice(candidates).id
            while new_id == current_id or new_id == from_id:
                new_id = random.choice(candidates).id

            spec_evos[offsets] = (new_id, from_id)

            ctx.logger.logChange(
                "Changed special evolution for " + ctx.lookup.getDigimonName(current_id)
                + " to " + ctx.lookup.getDigimonName(new_id)
            )


class DevimonStatGainOverride(Randomizer):
    """Overrides Devimon's evo stat gains to canonical values.

    Not strictly a randomiser — but the legacy code ran it as part of the
    special-evolution flow whenever special evos were randomised, so it
    lives next to its caller. Idempotent.
    """

    DEVIMON_STATS = (1500, 2000, 250, 100, 150, 200)
    _DEVIMON_NAME = ChampionDigimon.DEVIMON.display_name

    def apply(self, ctx: RandomizationContext) -> None:
        devimon = next(
            (d for d in ctx.state.digimonData if d.name == self._DEVIMON_NAME),
            None,
        )
        if devimon is None:
            return

        for i, value in enumerate(self.DEVIMON_STATS):
            devimon.evoStats[i] = value

        ctx.logger.logChange(
            "Set Devimon stat gains to: 1500  2000  250  100  150  200"
        )
