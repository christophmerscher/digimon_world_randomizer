from enum import Enum
from data.digimon.digimon_info import DigimonInfo
from data.digimon.digimon_level import DigimonLevel

class FreshDigimon(Enum):
    BOTAMON = DigimonInfo("0x01", "Botamon", True, DigimonLevel.FRESH)

