# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""Digimon ROM data model.

A ``Digimon`` instance is the in-memory mirror of one record in the
digimon stat block. It owns its own evolution tables (``fromEvo``,
``toEvo``, ``evoStats``, ``evoStatReqs``) plus convenience helpers for
manipulating them during randomisation.

The model has *no* dependency on the full handler — only on the narrow
:class:`~digimon.models.lookups.ModelContext` Protocol — so it can be
unit-tested in isolation.
"""

from __future__ import annotations

from typing import Sequence

import digimon.data as data
from data.digimon import (
    ChampionDigimon,
    PerfectDigimon,
    RookieDigimon,
    all_partner_digimon,
)
from digimon.models.lookups import ModelContext


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Sentinel byte for "no evolution in this slot".
NO_EVO_SLOT = 0xFF

# Sentinel value for "no requirement / unset stat req".
NO_REQUIREMENT = 0xFFFF

# Order in which the ``fromEvo`` slots get filled when computing evolutions.
FROM_EVO_FILL_ORDER = (2, 1, 3, 0, 4)

# Order in which the ``toEvo`` slots get filled when assigning a new evo.
TO_EVO_FILL_ORDER = (2, 3, 1, 4, 0, 5)

# Evolution requirement flags packed into the trailing 16-bit ``evoFlags``.
EVO_FLAG_MAX_BATTLES        = 0x0001
EVO_FLAG_MAX_CARE_MISTAKES  = 0x0010


# Names whose Champion entries form Factorial Town's recruit chain; used
# in the PP rule below to clamp those three digimon to 1 PP regardless
# of level.
NUMEMON_FAMILY_NAMES = frozenset((
    ChampionDigimon.NUMEMON.display_name,
    ChampionDigimon.SUKAMON.display_name,
    ChampionDigimon.NANIMON.display_name,
))

# Names that the evolution randomiser must never pick as an evo target
# because they have no standard digivolution requirements.
_ALWAYS_INVALID_EVO_TARGETS = frozenset((
    RookieDigimon.KUNEMON.display_name,
    ChampionDigimon.NUMEMON.display_name,
    ChampionDigimon.SUKAMON.display_name,
    ChampionDigimon.NANIMON.display_name,
    PerfectDigimon.VADEMON.display_name,
    PerfectDigimon.PANJYAMON.display_name,
    PerfectDigimon.GIGADRAMON.display_name,
    PerfectDigimon.METALETEMON.display_name,
))

# Devimon is the one extra exclusion that only applies when the
# evolution-requirements randomiser hasn't run yet.
_DEVIMON_NAME = ChampionDigimon.DEVIMON.display_name


class Digimon:
    """In-memory representation of a single digimon stat-block record."""

    # Partner IDs that correspond to actual playable digimon. Derived from
    # the data/ enums so adding a new partner needs only one edit (the
    # enum) instead of a magic range here as well. IDs not present in the
    # enums belong to enemy / NPC digimon read from the same stat block.
    playableDigimon: list[int] = sorted({member.id for member in all_partner_digimon()})

    def __init__(self, handler: ModelContext, id: int, readData: Sequence) -> None:
        """Unpack one row of the digimon stat block into an object.

        ``readData`` is the tuple produced by ``struct.unpack`` against the
        block's record format; the per-index meaning is documented inline
        below.
        """

        self.handler = handler
        self.id      = id

        # decode binary data as ascii and trim trailing nulls
        self.name   = readData[0].decode("ascii").rstrip("\0")
        self.models = readData[1]
        self.radius = readData[2]
        self.height = readData[3]
        self.type   = readData[4]
        self.level  = readData[5]

        self.pp = self._compute_prosperity_points()

        # Pack the PP value into the least significant two bits of height so
        # that the updated PP calculation patch can read it without needing
        # a new ROM field.
        self.height = (self.height & 0xFFFC) | self.pp

        self.spec      = [readData[6 + i] for i in range(3)]
        self.item      = readData[9]
        self.drop_rate = readData[10]
        self.tech      = [readData[11 + i] for i in range(16)]

        # Evolution tables — initialised empty; populated by setEvoData/setEvoStats/setEvoReqs.
        self.fromEvo     = [NO_EVO_SLOT      for _ in range(5)]
        self.toEvo       = [NO_EVO_SLOT      for _ in range(6)]
        self.evoStats    = [NO_REQUIREMENT   for _ in range(6)]
        self.evoStatReqs = [NO_REQUIREMENT   for _ in range(6)]

        self.evoBonusDigi       = NO_REQUIREMENT
        self.evoCareMistakes    = NO_REQUIREMENT
        self.evoWeight          = NO_REQUIREMENT
        self.evoDiscipline      = NO_REQUIREMENT
        self.evoHappiness       = NO_REQUIREMENT
        self.evoBattles         = -1
        self.evoTechs           = NO_REQUIREMENT
        self.evoFlags           = NO_REQUIREMENT

        self.evoMaxBattles      = True
        self.evoMaxCareMistakes = True

    # ----- private helpers --------------------------------------------------

    def _compute_prosperity_points(self) -> int:
        """Apply the legacy per-name / per-level PP table."""

        if self.name in NUMEMON_FAMILY_NAMES:
            return 1
        if self.level == data.levelsByName["ROOKIE"]:
            return 1
        if self.level == data.levelsByName["CHAMPION"]:
            return 2
        if self.level == data.levelsByName["ULTIMATE"]:
            return 3
        return 0

    # ----- string representations ------------------------------------------

    def __str__(self) -> str:
        """Detailed log-friendly representation of the digimon record."""

        type_name  = self.handler.getTypeName(self.type)
        level_name = self.handler.getLevelName(self.level)
        item_name  = self.handler.getItemName(self.item)
        spec_names = [self.handler.getSpecialtyName(self.spec[i]) for i in range(3)]

        out = (
            "{:>3d}{:>20s} {:>5d}{:>5d}{:>5d} {:>9s} {:>11s} {:>6s} {:>6s} {:>6s} "
            "{:>12s} {:>3d}% {:>1d}\n{:>23s} "
        ).format(
            self.id,
            self.name.rstrip(" \t\r\n\0"),
            self.models,
            self.radius,
            self.height,
            type_name,
            level_name,
            spec_names[0], spec_names[1], spec_names[2],
            item_name,
            self.drop_rate,
            self.pp,
            "",
        )

        for i in range(16):
            if self.tech[i] != "None":
                out += self.handler.getTechName(self.tech[i])
            if i == 15 or self.handler.getTechName(self.tech[i + 1]) == "None":
                break
            out += ", "

        return out

    # ----- evo data round-trip ---------------------------------------------

    def setEvoData(self, data: Sequence[int]) -> None:
        """Populate the ``fromEvo`` and ``toEvo`` slots from an unpacked tuple."""

        for i in range(5):
            self.fromEvo[i] = data[i]

        for i in range(6):
            self.toEvo[i] = data[5 + i]

    def evoData(self) -> str:
        """Log-friendly summary of this digimon's evo to/from tables."""

        out = self.name + "\nNow evolves from "
        for i in range(5):
            out += self.handler.getDigimonName(self.fromEvo[i]) + " "

        out += "\nNow evolves to "
        for i in range(6):
            out += self.handler.getDigimonName(self.toEvo[i]) + " "

        return out

    def setEvoStats(self, data: Sequence[int]) -> None:
        """Populate the per-level stat-gain table. ``data[6]`` is the owning ID."""

        if data[6] != self.id:
            self.handler.logger.logError(
                "Error: trying to attach evo stats for "
                + str(data[6]) + " to " + str(self.id)
            )
            return

        for i in range(6):
            self.evoStats[i] = data[i]

    def evoStatsToString(self) -> str:
        out = self.name + "\nNow gains stats: "
        for i in range(6):
            out += str(self.evoStats[i]) + " "
        return out

    def setEvoReqs(self, data: Sequence[int]) -> None:
        """Populate the evolution-requirement fields from an unpacked tuple."""

        self.evoBonusDigi = data[0]

        for i in range(6):
            self.evoStatReqs[i] = data[1 + i]

        self.evoCareMistakes = data[7]
        self.evoWeight       = data[8]
        self.evoDiscipline   = data[9]
        self.evoHappiness    = data[10]
        self.evoBattles      = data[11]
        self.evoTechs        = data[12]
        self.evoFlags        = data[13]

        self.evoMaxBattles      = (self.evoFlags & EVO_FLAG_MAX_BATTLES)       == EVO_FLAG_MAX_BATTLES
        self.evoMaxCareMistakes = (self.evoFlags & EVO_FLAG_MAX_CARE_MISTAKES) == EVO_FLAG_MAX_CARE_MISTAKES

    def evoReqsToString(self) -> str:  # noqa: C901 — mirrors legacy output exactly
        """Detailed prose summary of every active evolution requirement."""

        out = self.name + "'s evo requirements are: \n"

        out += "Stats: {:s}{:s}{:s}{:s}{:s}{:s}".format(
            "HP >= " + str(self.evoStatReqs[0] * 10) + "   " if self.evoStatReqs[0] != NO_REQUIREMENT else "",
            "MP >= " + str(self.evoStatReqs[1] * 10) + "   " if self.evoStatReqs[1] != NO_REQUIREMENT else "",
            "OFF >= " + str(self.evoStatReqs[2])     + "   " if self.evoStatReqs[2] != NO_REQUIREMENT else "",
            "DEF >= " + str(self.evoStatReqs[3])     + "   " if self.evoStatReqs[3] != NO_REQUIREMENT else "",
            "SPD >= " + str(self.evoStatReqs[4])     + "   " if self.evoStatReqs[4] != NO_REQUIREMENT else "",
            "BRN >= " + str(self.evoStatReqs[5])     + "   " if self.evoStatReqs[5] != NO_REQUIREMENT else "",
        )

        out += "\n"

        if self.evoCareMistakes != NO_REQUIREMENT:
            limit = "most" if self.evoMaxCareMistakes else "least"
            out += "Had at " + limit + " " + str(self.evoCareMistakes) + " care mistake(s) at current level\n"

        if self.evoWeight != NO_REQUIREMENT:
            out += "Weight is in range " + str(self.evoWeight - 5) + "-" + str(self.evoWeight + 5) + "\n"

        out += "One of the following bonus requirements: \n"

        if self.evoBonusDigi != NO_REQUIREMENT:
            out += "Current digimon is " + self.handler.getDigimonName(self.evoBonusDigi) + "\n"

        if self.evoDiscipline != NO_REQUIREMENT:
            out += "Discipline is at least " + str(self.evoDiscipline) + "\n"

        if self.evoHappiness != NO_REQUIREMENT:
            out += "Happiness is at least " + str(self.evoHappiness) + "\n"

        if self.evoBattles != -1:
            limit = "most" if self.evoMaxBattles else "least"
            out += "Particpated in at " + limit + " " + str(self.evoBattles) + " battle(s) at current level\n"

        if self.evoTechs != NO_REQUIREMENT:
            out += "Learned at least " + str(self.evoTechs) + " techs\n"

        return out

    # ----- pack helpers (used by RomWriter) --------------------------------

    def unpackedFormat(self) -> tuple:
        """Return the tuple shape consumed by ``struct.pack`` for this record."""

        repr_ = [
            self.name.encode("ascii"),  # 0
            self.models,                # 1
            self.radius,                # 2
            self.height,                # 3
            self.type,                  # 4
            self.level,                 # 5
        ]
        repr_.extend(self.spec)         # 6 7 8
        repr_.append(self.item)         # 9
        repr_.append(self.drop_rate)    # 10
        repr_.extend(self.tech)         # 11+

        return tuple(repr_)

    def unpackedEvoFormat(self) -> tuple:
        return tuple(list(self.fromEvo) + list(self.toEvo))

    def unpackedEvoStatsFormat(self) -> tuple:
        return tuple(list(self.evoStats) + [self.id])

    def unpackedEvoReqFormat(self) -> tuple:
        repr_ = [self.evoBonusDigi]
        repr_.extend(self.evoStatReqs[i] for i in range(6))
        repr_.extend([
            self.evoCareMistakes,
            self.evoWeight,
            self.evoDiscipline,
            self.evoHappiness,
            self.evoBattles,
            self.evoTechs,
        ])
        flags = (EVO_FLAG_MAX_BATTLES if self.evoMaxBattles else 0) \
              + (EVO_FLAG_MAX_CARE_MISTAKES if self.evoMaxCareMistakes else 0)
        repr_.append(flags)

        return tuple(repr_)

    # ----- evolution-graph helpers -----------------------------------------

    def getEvoToCount(self) -> int:
        return sum(1 for e in self.toEvo if e != NO_EVO_SLOT)

    def getEvoFromCount(self) -> int:
        return sum(1 for e in self.fromEvo if e != NO_EVO_SLOT)

    def clearEvos(self) -> None:
        for i in range(5):
            self.fromEvo[i] = NO_EVO_SLOT
        for i in range(6):
            self.toEvo[i] = NO_EVO_SLOT

    def clearEvoReqs(self) -> None:
        for i in range(6):
            self.evoStatReqs[i] = NO_REQUIREMENT

        self.evoBonusDigi    = NO_REQUIREMENT
        self.evoCareMistakes = NO_REQUIREMENT
        self.evoWeight       = NO_REQUIREMENT
        self.evoDiscipline   = NO_REQUIREMENT
        self.evoHappiness    = NO_REQUIREMENT
        self.evoBattles      = -1
        self.evoTechs        = NO_REQUIREMENT
        self.evoFlags        = NO_REQUIREMENT

        self.evoMaxBattles      = True
        self.evoMaxCareMistakes = True

    def updateEvosFrom(self) -> None:
        """Refresh ``fromEvo`` by scanning every digimon's ``toEvo`` list."""

        evos = [digi.id for digi in self.handler.digimonData if self.id in digi.toEvo]

        # Slot order matches the in-game UI: middle slot first, then outward.
        for i, j in enumerate(FROM_EVO_FILL_ORDER):
            self.fromEvo[j] = evos[i] if i < len(evos) else NO_EVO_SLOT

    def validEvosTo(self) -> list["Digimon"]:
        """Return every digimon this one could legally evolve to."""

        validEvos = self.handler.getPlayableDigimonByLevel(self.level + 1)

        invalid_names = set(_ALWAYS_INVALID_EVO_TARGETS)
        if not self.handler.randomizedRequirements:
            invalid_names.add(_DEVIMON_NAME)

        return [evo for evo in validEvos if evo.name not in invalid_names]

    def addEvoTo(self, id: int) -> None:
        """Insert an evolution target into the next free ``toEvo`` slot."""

        # Search in the order that evos are filled.
        for i in TO_EVO_FILL_ORDER:
            if self.toEvo[i] == id:
                return                 # already present — nothing to do
            if self.toEvo[i] == NO_EVO_SLOT:
                self.toEvo[i] = id
                return
