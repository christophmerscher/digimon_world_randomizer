# Author: Christoph Merscher <dev@fmerscher.com>

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
from digimon.rom.patches.registry import get_patch


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

        # Queue patches the new recruitment plan depends on when they are
        # mapped for the active layout.
        pp_patch_enabled = self._queue_patch_if_supported(ctx, "pp")
        self._queue_patch_if_supported(ctx, "ogremon")

        # Stash each recruit's new PP value into the low 2 bits of the
        # *old* recruit's height so the new PP patch can read it at runtime.
        digimon = ctx.state.digimonData
        if pp_patch_enabled:
            for trigger in recruit_data:
                old_digi = digimon[trigger - 200]
                new_digi = digimon[recruit_data[trigger][1]]
                old_digi.height = (old_digi.height & PP_CLEAR_MASK) | new_digi.pp
        else:
            ctx.logger.logChange(
                "Skipped PP calculation patch; recruitment shuffling stays enabled, "
                "but PP awards remain the original runtime values."
            )

        for trigger in recruit_data:
            old_digi = digimon[trigger - 200]
            new_digi = digimon[recruit_data[trigger][1]]
            if pp_patch_enabled:
                ctx.logger.logChange(
                    old_digi.name + " now recruits " + new_digi.name
                    + " and gives " + str(old_digi.height & PP_MASK) + " pp"
                )
            else:
                ctx.logger.logChange(
                    old_digi.name + " now recruits " + new_digi.name
                )
            ctx.logger.logChange(
                old_digi.name + " now has height: " + str(old_digi.height)
            )

    def _queue_patch_if_supported(self, ctx: RandomizationContext, name: str) -> bool:
        patch = get_patch(name)
        if patch is None:
            return False

        if ctx.layout is not None and not patch.supports_layout(ctx.layout):
            return False

        ctx.queue_patch(name, 0)
        return True
