"""Randomise the per-digimon evolution graph.

The legacy implementation handles each evo tier (Fresh→In-Training,
In-Training→Rookie, Rookie→Champion, Champion→Ultimate, refresh-
Ultimate-back-pointers) in a single long method. We split them into
private helpers but consume RNG in the same order — preserving byte-
identical output.
"""

from __future__ import annotations

import random

import digimon.data as data
from digimon.randomization.base import Randomizer, RandomizationContext


# Per-tier number of evo targets each source digimon should end up with.
ROOKIE_EVO_COUNT_RANGE    = (4, 6)
CHAMPION_EVO_COUNT_RANGE  = (1, 2)
IN_TRAINING_EVO_COUNT     = 2


class EvolutionsRandomizer(Randomizer):
    def __init__(self, obtain_all: bool = False) -> None:
        self.obtain_all = obtain_all

    def apply(self, ctx: RandomizationContext) -> None:
        ctx.logger.logChange(ctx.logger.getHeader("Randomize Evolutions"))

        # Reset everyone's evo lists.
        for digi in ctx.state.digimonData:
            digi.clearEvos()

        self._randomize_freshes(ctx)
        self._randomize_in_trainings(ctx)
        self._randomize_rookies(ctx)
        self._randomize_champions(ctx)
        self._refresh_ultimates(ctx)

        ctx.logger.logChange("Changed digimon evolutions to the following: ")
        for i in range(1, data.lastPartnerDigimon + 1):
            ctx.logger.logChange(
                "Changed evolutions for " + ctx.state.digimonData[i].evoData() + "\n"
            )

    # ------------------------------------------------------------------
    def _randomize_freshes(self, ctx: RandomizationContext) -> None:
        # Each fresh gets one in-training target.
        freshes = ctx.lookup.getPlayableDigimonByLevel(data.levelsByName["FRESH"])
        valid_evos = freshes[0].validEvosTo()
        for digi in freshes:
            chosen = random.randint(0, len(valid_evos) - 1)
            digi.addEvoTo(valid_evos[chosen].id)
            if self.obtain_all:
                del valid_evos[chosen]

    def _randomize_in_trainings(self, ctx: RandomizationContext) -> None:
        # Each in-training gets two rookie targets.
        in_trainings = ctx.lookup.getPlayableDigimonByLevel(data.levelsByName["IN-TRAINING"])
        valid_evos = in_trainings[0].validEvosTo()
        for digi in in_trainings:
            digi.updateEvosFrom()
            while digi.getEvoToCount() < IN_TRAINING_EVO_COUNT:
                chosen = random.randint(0, len(valid_evos) - 1)
                digi.addEvoTo(valid_evos[chosen].id)
                if self.obtain_all:
                    del valid_evos[chosen]

    def _randomize_rookies(self, ctx: RandomizationContext) -> None:
        rookies = ctx.lookup.getPlayableDigimonByLevel(data.levelsByName["ROOKIE"])

        # In obtain-all mode, give every champion at least one rookie evo.
        if self.obtain_all:
            valid_evos = rookies[0].validEvosTo()
            while valid_evos:
                digi = random.choice(rookies)
                count_before = digi.getEvoToCount()
                digi.addEvoTo(valid_evos[0].id)
                if count_before < digi.getEvoToCount():
                    del valid_evos[0]

        # Then fill each rookie up to 4-6 champion evos.
        valid_evos = rookies[0].validEvosTo()
        for digi in rookies:
            target_count = random.randint(*ROOKIE_EVO_COUNT_RANGE)
            digi.updateEvosFrom()
            while digi.getEvoToCount() < target_count:
                chosen = random.randint(0, len(valid_evos) - 1)
                digi.addEvoTo(valid_evos[chosen].id)

    def _randomize_champions(self, ctx: RandomizationContext) -> None:
        champions = ctx.lookup.getPlayableDigimonByLevel(
            data.levelsByName["CHAMPION"], excludeSpecials=True,
        )

        # In obtain-all mode, give every ultimate at least one champion evo.
        if self.obtain_all:
            valid_evos = champions[0].validEvosTo()
            while valid_evos:
                digi = random.choice(champions)
                count_before = digi.getEvoToCount()
                digi.addEvoTo(valid_evos[0].id)
                if count_before < digi.getEvoToCount():
                    del valid_evos[0]

        # Then fill each champion up to 1-2 ultimate evos.
        rookies = ctx.lookup.getPlayableDigimonByLevel(data.levelsByName["ROOKIE"])
        _ = rookies[0].validEvosTo()   # legacy RNG: intentionally evaluated, discarded
        for digi in champions:
            target_count = random.randint(*CHAMPION_EVO_COUNT_RANGE)
            digi.updateEvosFrom()
            valid_evos = digi.validEvosTo()
            while digi.getEvoToCount() < target_count:
                chosen = random.randint(0, len(valid_evos) - 1)
                digi.addEvoTo(valid_evos[chosen].id)

    def _refresh_ultimates(self, ctx: RandomizationContext) -> None:
        ultimates = ctx.lookup.getPlayableDigimonByLevel(
            data.levelsByName["ULTIMATE"], excludeSpecials=True,
        )
        for digi in ultimates:
            digi.updateEvosFrom()
