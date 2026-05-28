from data.digimon.digimon_id import DigimonID
from data.digimon.digimon_info import DigimonInfo
from data.digimon.digimon_level import DigimonLevel


class RookieDigimon(DigimonID):
    AGUMON = DigimonInfo("0x03", "Agumon", True, DigimonLevel.ROOKIE, starter=True)
    BETAMON = DigimonInfo("0x04", "Betamon", True, DigimonLevel.ROOKIE, recruitable=True)
    GABUMON = DigimonInfo("0x11", "Gabumon", True, DigimonLevel.ROOKIE, recruitable=True, starter=True)
    ELECMON = DigimonInfo("0x12", "Elecmon", True, DigimonLevel.ROOKIE, recruitable=True)
    PATAMON = DigimonInfo("0x1F", "Patamon", True, DigimonLevel.ROOKIE, recruitable=True)
    KUNEMON = DigimonInfo("0x20", "Kunemon", True, DigimonLevel.ROOKIE, recruitable=True)
    BIYOMON = DigimonInfo("0x2D", "Biyomon", True, DigimonLevel.ROOKIE, recruitable=True)
    PALMON = DigimonInfo("0x2E", "Palmon", True, DigimonLevel.ROOKIE)
