"""Randomly shuffle which digimon shows up for each recruitment trigger.

Side-effects beyond the state mutation:

* If the shuffled plan would softlock the run, re-rolls in place.
* Queues the ``pp`` patch so PP values can be looked up at runtime out of
  the digimon's height bits.
* Queues the ``ogremon`` softlock-fix patch.
* Rewrites the low 2 bits of each old recruit's ``height`` to encode the
  new recruit's PP value.
"""

from __future__ import annotations

import random

from digimon.randomization.base import Randomizer, RandomizationContext
from digimon.randomization.recruitment_validator import RecruitmentValidator


# Bit mask for the PP value packed into the low 2 bits of ``height``.
PP_MASK = 0x0003
PP_CLEAR_MASK = 0xFFFC


class RecruitmentsRandomizer(Randomizer):
    def apply(self, ctx: RandomizationContext) -> None:
        ctx.logger.logChange(ctx.logger.getHeader("Randomize Recruitments"))
        recruit_data = ctx.state.recruitData

        # Swap every entry with a random other entry. Re-roll on softlock.
        for trigger_a in recruit_data:
            trigger_b = random.choice(list(recruit_data))
            recruit_data[trigger_a], recruit_data[trigger_b] = \
                recruit_data[trigger_b], recruit_data[trigger_a]

        if not RecruitmentValidator(ctx.lookup).is_valid(ctx.state):
            self.apply(ctx)
            return

        # Queue patches the new recruitment plan depends on.
        ctx.queue_patch("pp", 0)
        ctx.queue_patch("ogremon", 0)

        # Stash each recruit's new PP value into the low 2 bits of the
        # *old* recruit's height so the new PP patch can read it at runtime.
        digimon = ctx.state.digimonData
        for trigger in recruit_data:
            old_digi = digimon[trigger - 200]
            new_digi = digimon[recruit_data[trigger][1]]
            old_digi.height = (old_digi.height & PP_CLEAR_MASK) | new_digi.pp

        for trigger in recruit_data:
            old_digi = digimon[trigger - 200]
            new_digi = digimon[recruit_data[trigger][1]]
            ctx.logger.logChange(
                old_digi.name + " now recruits " + new_digi.name
                + " and gives " + str(old_digi.height & PP_MASK) + " pp"
            )
            ctx.logger.logChange(
                old_digi.name + " now has height: " + str(old_digi.height)
            )
