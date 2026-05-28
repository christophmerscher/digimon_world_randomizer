from dataclasses import dataclass
from data.digimon.digimon_level import DigimonLevel

@dataclass(frozen=True)
class DigimonInfo:
    hex_code: str
    display_name: str
    playable: bool
    level: DigimonLevel | None = None
    special: bool = False
    recruitable: bool = False
    starter: bool = False
