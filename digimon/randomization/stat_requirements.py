"""Generate random per-level stat requirements for evolution.

Encapsulates the legacy ``_getRandomStatRequirements`` so its quirky
per-level rules (Rookies pick three stats at 1, Champions pick 1..4 at
100, Ultimates pick 4..6 with a 30% "hard" flag) live in one place.
"""

from __future__ import annotations

import random

import digimon.data as data


# Sentinel "no requirement" value for the per-stat slot.
NO_REQUIREMENT = 0xFFFF

# Indices into the six-element stat array.
NUM_STATS = 6

# Probability (out of 100) that the Ultimate requirements get the
# "hard" multiplier range.
HARD_ULTIMATE_THRESHOLD = 70


class StatRequirementGenerator:
    """Random per-level stat requirements (Rookie / Champion / Ultimate)."""

    def generate(self, level: int) -> list[int]:
        requirements = [NO_REQUIREMENT] * NUM_STATS
        choices      = list(range(NUM_STATS))

        if level == data.levelsByName["ROOKIE"]:
            for stat in self._sample(choices, count=3):
                requirements[stat] = 1
            return requirements

        if level == data.levelsByName["CHAMPION"]:
            count = random.randint(1, 4)
            for stat in self._sample(choices, count=count):
                requirements[stat] = 100
            return requirements

        if level == data.levelsByName["ULTIMATE"]:
            count = random.randint(4, 6)
            picked = self._sample(choices, count=count)

            # 30% chance for the stats to be "hard".
            hard = random.randint(0, 99) > HARD_ULTIMATE_THRESHOLD
            for stat in picked:
                requirements[stat] = (
                    random.randint(3, 7) * 100 if hard else random.randint(2, 5) * 100
                )
            return requirements

        return requirements

    # ------------------------------------------------------------------
    @staticmethod
    def _sample(choices: list[int], *, count: int) -> list[int]:
        """Pick ``count`` distinct values, consuming RNG identically to
        the legacy ``random.choice`` + ``list.remove`` loop."""

        picked: list[int] = []
        for _ in range(count):
            value = random.choice(choices)
            choices.remove(value)
            picked.append(value)
        return picked
