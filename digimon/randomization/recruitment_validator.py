"""Validate that a randomised recruitment plan is actually beatable.

The Factorial Town digimon (Numemon, MetalMamemon, Andromon, Giromon —
but not Nanimon) can only be reached after the Whamon recruit. If the
randomiser swaps the Whamon trigger to one of them, the player can
softlock with no way to progress.

This service exposes one boolean check; it knows nothing about how the
randomisation happened.
"""

from __future__ import annotations

from typing import Any

from data.digimon import ChampionDigimon, PerfectDigimon
from digimon.rom.state import RomState


# Champions / Ultimates in Factorial Town that require Whamon to be
# recruited first. Names are pulled from the data/ enums so a typo in
# either place fails at import time rather than silently letting an
# invalid recruit configuration through.
FACTORIAL_TOWN_DIGIS = frozenset((
    ChampionDigimon.NUMEMON.display_name,
    PerfectDigimon.METALMAMEMON.display_name,
    PerfectDigimon.ANDROMON.display_name,
    PerfectDigimon.GIROMON.display_name,
))

# Nanimon is in Factorial Town too, but recruiting it does NOT need
# Whamon (it shares a path via Ogremon's cave); the validator keeps an
# explicit override for it.
NANIMON_NAME = ChampionDigimon.NANIMON.display_name


class RecruitmentValidator:
    """Detect recruitment shuffles that would softlock progression."""

    def __init__(self, lookup: Any) -> None:
        self._lookup = lookup

    def is_valid(self, state: RomState) -> bool:
        whamon_name = ChampionDigimon.WHAMON.display_name

        for trigger in state.recruitData:
            recruited = self._lookup.getDigimonName(trigger - 200)
            showed_up = self._lookup.getDigimonName(state.recruitData[trigger][1])

            if (showed_up == whamon_name
                    and recruited in FACTORIAL_TOWN_DIGIS
                    and recruited != NANIMON_NAME):
                return False

        return True
