from enum import Enum


class ItemCategory(Enum):
    """The high-level kind of an item, mirroring the ROM ``sort`` byte.

    The Digimon World engine uses a single byte to discriminate items into
    six broad categories. ``STATEVO`` overloads both stat-boost items and
    evolution items; use :func:`data.item.is_evo_item` to disambiguate by ID.
    """

    HEAL         = 0x00
    STATUS       = 0x01
    FOOD         = 0x02
    BATTLE       = 0x03
    STATEVO      = 0x04
    PASSIVEQUEST = 0x05

    @classmethod
    def from_byte(cls, value: int) -> "ItemCategory":
        return cls(value)
