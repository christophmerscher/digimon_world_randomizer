from data.digimon.digimon_id import DigimonID
from data.digimon.digimon_info import DigimonInfo
from data.digimon.digimon_level import DigimonLevel


class PerfectDigimon(DigimonID):
    """Ultimate (Perfect) stage partner digimon."""

    MAMEMON      = DigimonInfo("0x0D", "Mamemon",      True, DigimonLevel.ULTIMATE, recruitable=True)
    MONZAEMON    = DigimonInfo("0x0E", "Monzaemon",    True, DigimonLevel.ULTIMATE, special=True)
    SKULLGREYMON = DigimonInfo("0x1A", "SkullGreymon", True, DigimonLevel.ULTIMATE, recruitable=True)
    METALMAMEMON = DigimonInfo("0x1B", "MetalMamemon", True, DigimonLevel.ULTIMATE, recruitable=True)
    VADEMON      = DigimonInfo("0x1C", "Vademon",      True, DigimonLevel.ULTIMATE, special=True, recruitable=True)
    ANDROMON     = DigimonInfo("0x28", "Andromon",     True, DigimonLevel.ULTIMATE, recruitable=True)
    GIROMON      = DigimonInfo("0x29", "Giromon",      True, DigimonLevel.ULTIMATE, recruitable=True)
    ETEMON       = DigimonInfo("0x2A", "Etemon",       True, DigimonLevel.ULTIMATE, recruitable=True)
    MEGADRAMON   = DigimonInfo("0x36", "Megadramon",   True, DigimonLevel.ULTIMATE, recruitable=True)
    PIXIMON      = DigimonInfo("0x37", "Piximon",      True, DigimonLevel.ULTIMATE, recruitable=True)
    DIGITAMAMON  = DigimonInfo("0x38", "Digitamamon",  True, DigimonLevel.ULTIMATE, recruitable=True)
    PHOENIXMON   = DigimonInfo("0x3B", "Phoenixmon",   True, DigimonLevel.ULTIMATE, special=True)
    PANJYAMON    = DigimonInfo("0x3F", "Panjyamon",    True, DigimonLevel.ULTIMATE, special=True)
    GIGADRAMON   = DigimonInfo("0x40", "Gigadramon",   True, DigimonLevel.ULTIMATE, special=True)
    METALETEMON  = DigimonInfo("0x41", "MetalEtemon",  True, DigimonLevel.ULTIMATE, special=True)
