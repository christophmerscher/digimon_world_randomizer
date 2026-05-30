from enum import Enum

from data.digimon.digimon_level import DigimonLevel


class DigimonID(Enum):
    """Common Enum base for the per-level digimon enums.

    Each member's value is a :class:`DigimonInfo` instance, so derived
    enums (``RookieDigimon``, ``ChampionDigimon``, …) inherit a uniform
    name / id / level interface without repeating accessors.
    """

    @property
    def hex(self) -> str:
        """Original two-digit hexadecimal string from the ROM tables."""
        return self.value.hex_code

    @property
    def id(self) -> int:
        """Numeric ROM ID."""
        return int(self.value.hex_code, 16)

    @property
    def display_name(self) -> str:
        """Capitalised name as shown in-game and in the GUI."""
        return self.value.display_name

    @property
    def playable(self) -> bool:
        return self.value.playable

    @property
    def level(self) -> DigimonLevel | None:
        return self.value.level

    @property
    def is_perfect(self) -> bool:
        """True when this digimon is at the Ultimate (Perfect) stage."""
        return self.value.level is DigimonLevel.ULTIMATE
