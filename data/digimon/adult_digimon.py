from data.digimon.digimon_id import DigimonID
from data.digimon.digimon_info import DigimonInfo
from data.digimon.digimon_level import DigimonLevel


class ChampionDigimon(DigimonID):
    """Champion stage partner digimon (the middle evolution tier)."""

    GREYMON     = DigimonInfo("0x05", "Greymon",     True, DigimonLevel.CHAMPION)
    DEVIMON     = DigimonInfo("0x06", "Devimon",     True, DigimonLevel.CHAMPION, recruitable=True)
    AIRDRAMON   = DigimonInfo("0x07", "Airdramon",   True, DigimonLevel.CHAMPION, special=True)
    TYRANNOMON  = DigimonInfo("0x08", "Tyrannomon",  True, DigimonLevel.CHAMPION, recruitable=True)
    MERAMON     = DigimonInfo("0x09", "Meramon",     True, DigimonLevel.CHAMPION, recruitable=True)
    SEADRAMON   = DigimonInfo("0x0A", "Seadramon",   True, DigimonLevel.CHAMPION, recruitable=True)
    NUMEMON     = DigimonInfo("0x0B", "Numemon",     True, DigimonLevel.CHAMPION, recruitable=True)
    KABUTERIMON = DigimonInfo("0x13", "Kabuterimon", True, DigimonLevel.CHAMPION, recruitable=True)
    ANGEMON     = DigimonInfo("0x14", "Angemon",     True, DigimonLevel.CHAMPION)
    BIRDRAMON   = DigimonInfo("0x15", "Birdramon",   True, DigimonLevel.CHAMPION)
    GARURUMON   = DigimonInfo("0x16", "Garurumon",   True, DigimonLevel.CHAMPION, recruitable=True)
    FRIGIMON    = DigimonInfo("0x17", "Frigimon",    True, DigimonLevel.CHAMPION, recruitable=True)
    WHAMON      = DigimonInfo("0x18", "Whamon",      True, DigimonLevel.CHAMPION, recruitable=True)
    VEGIEMON    = DigimonInfo("0x19", "Vegiemon",    True, DigimonLevel.CHAMPION)
    UNIMON      = DigimonInfo("0x21", "Unimon",      True, DigimonLevel.CHAMPION, recruitable=True)
    OGREMON     = DigimonInfo("0x22", "Ogremon",     True, DigimonLevel.CHAMPION, recruitable=True)
    SHELLMON    = DigimonInfo("0x23", "Shellmon",    True, DigimonLevel.CHAMPION, recruitable=True)
    CENTARUMON  = DigimonInfo("0x24", "Centarumon",  True, DigimonLevel.CHAMPION)
    BAKEMON     = DigimonInfo("0x25", "Bakemon",     True, DigimonLevel.CHAMPION, recruitable=True)
    DRIMOGEMON  = DigimonInfo("0x26", "Drimogemon",  True, DigimonLevel.CHAMPION, recruitable=True)
    SUKAMON     = DigimonInfo("0x27", "Sukamon",     True, DigimonLevel.CHAMPION, recruitable=True)
    MONOCHROMON = DigimonInfo("0x2F", "Monochromon", True, DigimonLevel.CHAMPION, recruitable=True)
    LEOMON      = DigimonInfo("0x30", "Leomon",      True, DigimonLevel.CHAMPION, recruitable=True)
    COELAMON    = DigimonInfo("0x31", "Coelamon",    True, DigimonLevel.CHAMPION, recruitable=True)
    KOKATORIMON = DigimonInfo("0x32", "Kokatorimon", True, DigimonLevel.CHAMPION, recruitable=True)
    KUWAGAMON   = DigimonInfo("0x33", "Kuwagamon",   True, DigimonLevel.CHAMPION, recruitable=True)
    MOJYAMON    = DigimonInfo("0x34", "Mojyamon",    True, DigimonLevel.CHAMPION, recruitable=True)
    NANIMON     = DigimonInfo("0x35", "Nanimon",     True, DigimonLevel.CHAMPION, recruitable=True)
    PENGUINMON  = DigimonInfo("0x39", "Penguinmon",  True, DigimonLevel.CHAMPION, recruitable=True)
    NINJAMON    = DigimonInfo("0x3A", "Ninjamon",    True, DigimonLevel.CHAMPION, recruitable=True)
