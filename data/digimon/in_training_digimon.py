from data.digimon.digimon_info import DigimonInfo
from data.digimon.digimon_id import DigimonID
from data.digimon.digimon_level import DigimonLevel


class InTrainingDigimon(DigimonID):
    KOROMON = DigimonInfo("0x02", "Koromon", True, DigimonLevel.FRESH)
