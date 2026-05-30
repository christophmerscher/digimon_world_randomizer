# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""Item ROM data model.

Pure data object — the only collaborator is the
:class:`~digimon.models.lookups.NameLookup` Protocol via the bundled
:class:`~digimon.models.lookups.ModelContext` (kept under the name
``handler`` for backward compatibility with existing callers).
"""

from __future__ import annotations

from typing import Sequence

from data.item import (
    BANNED_ITEM_IDS,
    CONSUMABLE_ITEM_IDS,
    QUEST_ITEM_IDS,
    SPECIAL_FOOD_ITEM_IDS,
    is_evo_item,
)
from data.item.item_category import ItemCategory
from digimon.models.lookups import ModelContext


class Item:
    """In-memory representation of one row of the item data block."""

    # Backward-compatible aliases for old call sites that read these
    # attributes off the class directly (e.g. tests, scripts).
    itemSort = {member.value: member.name for member in ItemCategory}
    consumableItems = sorted(CONSUMABLE_ITEM_IDS)
    questItems      = sorted(QUEST_ITEM_IDS)
    bannedItems     = sorted(BANNED_ITEM_IDS)

    def __init__(self, handler: ModelContext, id: int, data: Sequence) -> None:
        """Unpack one row of the item block into an object.

        ``data`` is the tuple returned by ``struct.unpack`` against the item
        block's record format (name / price / merit / sort / color / dropable).
        """

        self.handler = handler
        self.id      = id

        # decode binary data as ascii and trim trailing nulls
        self.name     = data[0].decode("ascii").rstrip("\0")
        self.price    = data[1]
        self.merit    = data[2]
        self.sort     = data[3]
        self.color    = data[4]
        self.dropable = data[5]

        # Category-derived flags (see data.item for authoritative ranges).
        self.isEvo        = is_evo_item(id, self.sort)
        self.isConsumable = id in CONSUMABLE_ITEM_IDS
        self.isFood       = (ItemCategory.from_byte(self.sort) is ItemCategory.FOOD) or (id in SPECIAL_FOOD_ITEM_IDS)
        self.isQuest      = id in QUEST_ITEM_IDS
        self.isBanned     = id in BANNED_ITEM_IDS

    def __str__(self) -> str:
        return "{:>3d}{:>20s} {:>4d} {:>4d} {:>2d} {:>2d} {!r:>5}".format(
            self.id,
            self.name,
            self.price,
            self.merit,
            self.sort,
            self.color,
            self.dropable,
        )

    def unpackedFormat(self) -> tuple:
        """Tuple shape consumed by ``struct.pack`` for this record."""

        return (
            self.name.encode("ascii"),  # 0
            self.price,                 # 1
            self.merit,                 # 2
            self.sort,                  # 3
            self.color,                 # 4
            self.dropable,              # 5
        )
