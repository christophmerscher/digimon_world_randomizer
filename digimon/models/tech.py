# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""Technique ROM data model."""

from __future__ import annotations

from typing import Sequence

from digimon.models.lookups import ModelContext


# Finisher techs (cannot be learned by player digimon).
FINISHER_TECH_IDS = list(range(0x3A, 0x71))

# Bubble animation techs.
BUBBLE_TECH_IDS = list(range(0x71, 0x79))

# Duplicate animations of regular techs.
ALT_TECH_IDS = [0x30, 0x39]


class Tech:
    """In-memory representation of one entry in the technique stat block."""

    # Backward-compatible class-level aliases.
    finishers = FINISHER_TECH_IDS
    bubbles   = BUBBLE_TECH_IDS
    altTechs  = ALT_TECH_IDS

    def __init__(self, handler: ModelContext, id: int, data: Sequence) -> None:
        """Unpack one row of the tech stat block into an object."""

        self.handler = handler
        self.id      = id

        # Tier / name / learn chance are filled in later by the reader.
        self.name        = "None"
        self.tier        = 0xFF
        self.learnChance = [0, 0, 0]

        self.unkn1     = data[0]
        self.aiDist    = data[1]
        self.power     = data[2]
        self.mp3       = data[3]
        self.itime     = data[4]
        self.range     = data[5]
        self.spec      = data[6]
        self.effect    = data[7]
        self.accuracy  = data[8]
        self.effChance = data[9]
        self.unkn2     = data[10]

        self.isDamaging  = self.power > 0
        self.isFinisher  = self.id in FINISHER_TECH_IDS
        self.isLearnable = (not self.isFinisher) and (self.id not in BUBBLE_TECH_IDS)

    def __str__(self) -> str:
        return (
            "{:>3d} {:<20s} (Tier: {:<2d}) {:<2d}% {:<2d}% {:<2d}%\n"
            "   {:>3d} {:>3d} {:>2d} {:>5s} {:>6s} {:>7s} {:>3d} {:>3d}% {:>2d}"
        ).format(
            self.id,
            self.name,
            self.tier,
            self.learnChance[0], self.learnChance[1], self.learnChance[2],
            self.power,
            self.mp3 * 3,
            self.itime,
            self.handler.getRangeName(self.range),
            self.handler.getSpecialtyName(self.spec),
            self.handler.getEffectName(self.effect),
            self.accuracy,
            self.effChance,
            self.aiDist,
        )

    def unpackedFormat(self) -> tuple:
        """Tuple shape consumed by ``struct.pack`` for this record."""

        return (
            self.unkn1, self.aiDist, self.power, self.mp3, self.itime,
            self.range, self.spec, self.effect, self.accuracy, self.effChance,
            self.unkn2,
        )

    def unpackedLearnFormat(self) -> tuple[int, int, int]:
        """The (tier-1, tier-2, tier-3) learn-chance triple for this tech."""

        return tuple(self.learnChance)  # type: ignore[return-value]

    def setName(self, name: str) -> None:
        self.name = name
