# Author: Christoph Merscher <dev@fmerscher.com>

"""Centralised RNG-seeding policy.

Encapsulates the two seed-related behaviours that used to be inlined in
``DigimonWorldHandler.__init__``:

1. If no seed was supplied, pick a random one.
2. In *race mode*, advance the RNG by one step right after seeding so
   that running the randomiser with race verbosity produces a different
   ROM than running it with casual verbosity (preventing racers from
   peeking at the casual output ahead of time).
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass


@dataclass
class SeedingPolicy:
    """Apply the project's seeding rules to the global :mod:`random`."""

    #: Verbosity mode passed by the user. Only ``"race"`` advances the RNG.
    verbose: str

    def seed(self, seed: int | None) -> int:
        """Seed the RNG and return the effective seed value."""

        effective_seed = seed if seed is not None else random.randrange(sys.maxsize)
        random.seed(a=effective_seed)

        # Race-mode RNG advance — burn one RNG step so the race-mode ROM
        # diverges from the casual-mode ROM for the same seed.
        if self.verbose == "race":
            random.randint(0, 1)

        return effective_seed
