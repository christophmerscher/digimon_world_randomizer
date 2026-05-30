from data.digimon.digimon_id import DigimonID
from data.digimon.digimon_info import DigimonInfo
from data.digimon.digimon_level import DigimonLevel


class FreshDigimon(DigimonID):
    """Fresh stage partner digimon (the egg-hatching baby form)."""

    BOTAMON = DigimonInfo("0x01", "Botamon", True, DigimonLevel.FRESH)
