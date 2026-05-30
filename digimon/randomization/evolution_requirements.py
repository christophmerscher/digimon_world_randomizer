"""Randomise the per-digimon evolution requirements.

The legacy method body was a 130-line ``if level == X`` ladder. Each
branch is now a private helper.  The order of every ``random.*`` call
inside each branch is preserved byte-for-byte to keep seed-stability.
"""

from __future__ import annotations

import random

import digimon.data as data
from digimon.randomization.base import Randomizer, RandomizationContext
from digimon.randomization.stat_requirements import StatRequirementGenerator


# Digimon whose evolution requirements stay vanilla regardless of mode.
ROOKIE_PASSTHROUGH    = frozenset(("Kunemon",))
CHAMPION_PASSTHROUGH  = frozenset(("Numemon", "Sukamon", "Nanimon"))
ULTIMATE_PASSTHROUGH  = frozenset(("Vademon", "WereGarurumon"))


class EvolutionRequirementsRandomizer(Randomizer):
    def apply(self, ctx: RandomizationContext) -> None:
        ctx.logger.logChange(ctx.logger.getHeader("Randomize Evolution Requirements"))

        ctx.lookup.randomizedRequirements = True
        generator = StatRequirementGenerator()

        for digi in ctx.state.digimonData:
            if digi.id > data.lastPartnerDigimon - 3:
                continue

            if digi.level in (data.levelsByName["FRESH"], data.levelsByName["IN-TRAINING"]):
                digi.clearEvoReqs()
                continue

            if digi.level == data.levelsByName["ROOKIE"]:
                self._randomize_rookie(digi, generator)
            elif digi.level == data.levelsByName["CHAMPION"]:
                self._randomize_champion(digi, generator)
            elif digi.level == data.levelsByName["ULTIMATE"]:
                self._randomize_ultimate(digi, generator)

        for i in range(1, data.lastPartnerDigimon + 1):
            ctx.logger.logChange(
                "Changed requirements for " + ctx.state.digimonData[i].evoReqsToString() + "\n"
            )

    # ------------------------------------------------------------------
    @staticmethod
    def _randomize_rookie(digi, generator: StatRequirementGenerator) -> None:
        if digi.name in ROOKIE_PASSTHROUGH:
            digi.clearEvoReqs()
            return

        digi.clearEvoReqs()
        digi.evoBonusDigi       = digi.fromEvo[2]
        digi.evoStatReqs        = generator.generate(digi.level)
        digi.evoCareMistakes    = 0
        digi.evoMaxCareMistakes = False
        digi.evoWeight          = 15
        digi.evoTechs           = 0
        digi.evoBattles         = -2
        digi.evoMaxBattles      = False

    @staticmethod
    def _randomize_champion(digi, generator: StatRequirementGenerator) -> None:
        if digi.name in CHAMPION_PASSTHROUGH:
            digi.clearEvoReqs()
            return

        digi.clearEvoReqs()
        digi.evoStatReqs = generator.generate(digi.level)

        digi.evoMaxCareMistakes = random.choice([True, False])
        digi.evoCareMistakes = (
            random.randint(0, 6) if digi.evoMaxCareMistakes else random.randint(2, 6)
        )

        digi.evoWeight = random.randint(1, 10) * 5
        digi.evoTechs  = random.randint(10, 35)
        bonus_count    = 1

        if random.randint(0, 99) < 10:
            digi.evoDiscipline = random.randint(50, 95)
            bonus_count += 1

        if random.randint(0, 99) < 10:
            digi.evoDiscipline = random.randint(45, 85)
            bonus_count += 1

        if random.randint(0, 99) < 30:
            digi.evoMaxBattles = random.choice([True, False])
            digi.evoBattles = (
                random.randint(2, 15) if digi.evoMaxBattles else random.randint(2, 15)
            )
            bonus_count += 1

        if random.randint(0, 99) < 10 or bonus_count < 2:
            digi.evoBonusDigi = digi.fromEvo[2]
            bonus_count += 1

    @staticmethod
    def _randomize_ultimate(digi, generator: StatRequirementGenerator) -> None:
        if digi.name in ULTIMATE_PASSTHROUGH:
            digi.clearEvoReqs()
            return

        digi.clearEvoReqs()
        digi.evoStatReqs = generator.generate(digi.level)

        digi.evoMaxCareMistakes = random.choice([True, False])
        digi.evoCareMistakes = (
            random.randint(0, 15) if digi.evoMaxCareMistakes else random.randint(5, 15)
        )

        digi.evoWeight = random.randint(1, 14) * 5
        digi.evoTechs  = random.randint(21, 50)
        bonus_count    = 1

        if random.randint(0, 99) < 10:
            digi.evoDiscipline = random.randint(90, 100)
            bonus_count += 1

        if random.randint(0, 99) < 10:
            digi.evoDiscipline = random.randint(90, 100)
            bonus_count += 1

        if random.randint(0, 99) < 30:
            digi.evoMaxBattles = random.choice([True, False])
            digi.evoBattles = (
                random.randint(0, 15) if digi.evoMaxBattles else random.randint(5, 20) * 5
            )
            bonus_count += 1

        if random.randint(0, 99) < 10 or bonus_count < 2:
            digi.evoBonusDigi = digi.fromEvo[2]
            bonus_count += 1
