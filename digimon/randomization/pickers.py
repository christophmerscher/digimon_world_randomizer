"""Shared random-pick services for the randomiser Strategy classes.

The legacy handler had two near-identical ``_getRandomItem`` and
``_getRandomTech`` rejection-sampling loops. Centralising them here
satisfies DRY and makes the per-feature randomisers smaller and clearer.

Both pickers use Python's module-level :mod:`random` (just like the
legacy code) so that RNG order — and therefore the ROM output for a
given seed — stays byte-identical with the pre-refactor behaviour.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from digimon.rom.state import RomState


@dataclass
class RandomItemPicker:
    """Pick a random item ID matching the predicates."""

    state: RomState

    def pick(
        self,
        *,
        foodOnly: bool = False,
        consumableOnly: bool = False,
        notEvo: bool = False,
        notQuest: bool = False,
        matchValueOf: int | None = None,
        matchValue: int = 1000,
    ) -> int:
        """Return a random item ID satisfying every active predicate.

        ``matchValueOf`` and ``matchValue`` together keep "cheap" item
        replacements cheap and "expensive" replacements expensive: the
        chosen item must sit on the same side of ``matchValue`` as the
        reference item.
        """

        while True:
            rand_id = random.randint(0, len(self.state.itemData) - 1)
            item = self.state.itemData[rand_id]

            if item.isBanned:                              continue
            if foodOnly       and not item.isFood:         continue
            if consumableOnly and not item.isConsumable:   continue
            if notEvo         and item.isEvo:              continue
            if notQuest       and not item.dropable:       continue

            if matchValueOf is not None:
                reference = self.state.itemData[matchValueOf]
                if (item.price < matchValue) != (reference.price < matchValue):
                    continue

            return rand_id


@dataclass
class RandomTechPicker:
    """Pick a random tech ID matching the predicates."""

    state: RomState

    def pick(
        self,
        *,
        learnableOnly: bool = False,
        notFinisher: bool = False,
        damagingOnly: bool = False,
    ) -> int:
        while True:
            rand_id = random.randint(0, len(self.state.techData) - 1)
            tech = self.state.techData[rand_id]

            if notFinisher   and tech.isFinisher:      continue
            if damagingOnly  and not tech.isDamaging:  continue
            if learnableOnly and not tech.isLearnable: continue

            return rand_id
