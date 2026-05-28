from enum import Enum


class DigimonID(Enum):

    @property
    def hex(self) -> str:
        return self.value.hex_code

    @property
    def id(self) -> int:
        return int(self.value.hex_code, 16)

    @property
    def display_name(self) -> str:
        return self.value.display_name

    @property
    def playable(self) -> bool:
        return self.value.playable

    @property
    def level(self) -> str | None:
        return self.value.level

    @property
    def is_perfect(self) -> bool:
        return self.value.level == "ULTIMATE"