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

from digimon.rom.state import RomState


# Champions in Factorial Town that require Whamon to be recruited first.
FACTORIAL_TOWN_DIGIS = frozenset(
    ("Numemon", "MetalMamemon", "Andromon", "Giromon")
)


class RecruitmentValidator:
    """Detect recruitment shuffles that would softlock progression."""

    def __init__(self, lookup: Any) -> None:
        self._lookup = lookup

    def is_valid(self, state: RomState) -> bool:
        for trigger in state.recruitData:
            recruited = self._lookup.getDigimonName(trigger - 200)
            showed_up = self._lookup.getDigimonName(state.recruitData[trigger][1])

            if showed_up == "Whamon" \
               and recruited in FACTORIAL_TOWN_DIGIS \
               and recruited != "Nanimon":
                return False

        return True
