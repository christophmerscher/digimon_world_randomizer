"""Randomise the two starter digimon (and their first taught tech)."""

from __future__ import annotations

import random

import digimon.data as data
from data.technique import Techniques, tech_id
from digimon.randomization.base import Randomizer, RandomizationContext


# Sentinel returned by ``getTechName`` for an empty tech slot. Lives
# in :meth:`DigimonWorldHandler.getTechName` so we duplicate it
# verbatim here rather than importing from the handler (which would
# pull in PyQt-free / GUI-free model code).
_NO_TECH_SENTINEL = "None"

# A "weakest tech" picker that ignores these names entirely. Counter
# is reactive, not a starting tech; the sentinel is for unfilled slots.
WEAKEST_TECH_BANNED_NAMES = frozenset((
    _NO_TECH_SENTINEL,
    data.techs[tech_id(Techniques.COUNTER)],
))


class StartersRandomizer(Randomizer):
    def __init__(
        self,
        use_weakest_tech: bool = True,
        force_digimon: str = "Random",
        allowed_levels: list[int] | None = None,
    ) -> None:
        self.use_weakest_tech = use_weakest_tech
        self.force_digimon    = force_digimon
        self.allowed_levels   = (
            allowed_levels if allowed_levels is not None
            else [data.levelsByName["ROOKIE"]]
        )

    def apply(self, ctx: RandomizationContext) -> None:
        ctx.logger.logChange(ctx.logger.getHeader("Randomize Starters"))
        state = ctx.state

        # Build the pool of starter candidates by walking the requested levels.
        candidates = []
        for level in self.allowed_levels:
            candidates += ctx.lookup.getPlayableDigimonByLevel(level)

        # Pick first starter (different from the existing one).
        previous_first = state.starterID[0]
        first = candidates[random.randint(0, len(candidates) - 1)]
        while first == previous_first:
            first = candidates[random.randint(0, len(candidates) - 1)]

        # Pick second starter (different from first AND from existing second).
        previous_second = state.starterID[1]
        second = first
        while second == first or second == previous_second:
            second = candidates[random.randint(0, len(candidates) - 1)]

        # Apply forced first-starter override AFTER the picks so the
        # override doesn't perturb the rest of the RNG stream.
        forced = ctx.lookup.getDigimonByName(self.force_digimon)
        if forced is not None:
            first = forced

        state.starterID[0] = first.id
        ctx.logger.logChange("First starter set to " + first.name)

        state.starterID[1] = second.id
        ctx.logger.logChange("Second starter set to " + second.name)

        self._assign_starter_techs(ctx)

    # ------------------------------------------------------------------
    def _assign_starter_techs(self, ctx: RandomizationContext) -> None:
        state = ctx.state

        for i in (0, 1):
            if self.use_weakest_tech:
                tech_id, slot = self._pick_weakest_tech(ctx, state.starterID[i])
            else:
                tech_id, slot = self._pick_random_tech(ctx, state.starterID[i])

            state.starterTech[i]     = tech_id
            state.starterTechSlot[i] = slot

            ctx.logger.logChange(
                "Starter tech set to " + ctx.lookup.getTechName(state.starterTech[i])
                + " (" + state.digimonData[state.starterID[i]].name
                + "'s slot " + str(state.starterTechSlot[i]) + ")"
            )

    @staticmethod
    def _pick_weakest_tech(ctx: RandomizationContext, digimon_id: int) -> tuple[int, int]:
        lowest_tier, lowest_id, lowest_slot = 0xFF, 0, 1
        for slot, tech_id in enumerate(ctx.state.digimonData[digimon_id].tech):
            name = ctx.lookup.getTechName(tech_id)
            if name in WEAKEST_TECH_BANNED_NAMES:
                continue
            tech = ctx.state.techData[tech_id]
            if tech.isDamaging and not tech.isFinisher and tech.tier < lowest_tier:
                lowest_tier = tech.tier
                lowest_id   = tech_id
                lowest_slot = slot + 1
        return lowest_id, lowest_slot

    @staticmethod
    def _pick_random_tech(ctx: RandomizationContext, digimon_id: int) -> tuple[int, int]:
        while True:
            rand_slot = random.randint(0, 15)
            tech_id   = ctx.state.digimonData[digimon_id].tech[rand_slot]
            name      = ctx.lookup.getTechName(tech_id)

            if name in WEAKEST_TECH_BANNED_NAMES:
                ctx.logger.log(name)
                continue

            tech = ctx.state.techData[tech_id]
            if not tech.isDamaging or tech.isFinisher:
                ctx.logger.log(name)
                continue

            return tech_id, rand_slot + 1
