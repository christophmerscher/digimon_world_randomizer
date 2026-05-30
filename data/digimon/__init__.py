"""Partner-cast digimon enums and lookups (single source of truth).

This package replaces the ad-hoc name dictionaries in :mod:`digimon.data`
for the **player-controllable** digimon (IDs ``0x01``–``0x41``). Non-partner
NPC digimon names are still read from the ROM at runtime.

Each level has its own enum class:

* :class:`FreshDigimon`        — Fresh stage (baby form)
* :class:`InTrainingDigimon`   — In-Training stage
* :class:`RookieDigimon`       — Rookie stage (eight starter candidates)
* :class:`ChampionDigimon`     — Champion stage
* :class:`PerfectDigimon`      — Ultimate (Perfect) stage

The module-level helpers below combine those enums for cross-cutting
queries: by ID, by display name, or filtered by level/starter/recruitable.
"""

from __future__ import annotations

from data.digimon.adult_digimon import ChampionDigimon
from data.digimon.digimon_id import DigimonID
from data.digimon.digimon_info import DigimonInfo
from data.digimon.digimon_level import DigimonLevel
from data.digimon.digimon_specialty import DigimonSpecialty
from data.digimon.digimon_type import DigimonType
from data.digimon.fresh_digimon import FreshDigimon
from data.digimon.in_training_digimon import InTrainingDigimon
from data.digimon.perfect_digimon import PerfectDigimon
from data.digimon.rookie_digimon import RookieDigimon

__all__ = [
    "ChampionDigimon",
    "DigimonID",
    "DigimonInfo",
    "DigimonLevel",
    "DigimonSpecialty",
    "DigimonType",
    "FreshDigimon",
    "InTrainingDigimon",
    "PerfectDigimon",
    "RookieDigimon",
    "ALL_DIGIMON_ENUMS",
    "all_partner_digimon",
    "find_by_id",
    "find_by_display_name",
    "partner_digimon_by_level",
]


ALL_DIGIMON_ENUMS: tuple[type[DigimonID], ...] = (
    FreshDigimon,
    InTrainingDigimon,
    RookieDigimon,
    ChampionDigimon,
    PerfectDigimon,
)


def all_partner_digimon() -> tuple[DigimonID, ...]:
    """Every partner-cast digimon, in level order (fresh → ultimate)."""

    return tuple(member for enum in ALL_DIGIMON_ENUMS for member in enum)


def find_by_id(digimon_id: int) -> DigimonID | None:
    """Look up a partner digimon by ROM byte id; returns ``None`` if unknown."""

    for member in all_partner_digimon():
        if member.id == digimon_id:
            return member
    return None


def find_by_display_name(name: str) -> DigimonID | None:
    """Look up a partner digimon by case-sensitive display name."""

    for member in all_partner_digimon():
        if member.display_name == name:
            return member
    return None


def partner_digimon_by_level(level: DigimonLevel) -> tuple[DigimonID, ...]:
    """Return every partner digimon at the given level."""

    return tuple(member for member in all_partner_digimon() if member.level is level)
