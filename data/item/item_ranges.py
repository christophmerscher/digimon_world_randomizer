"""Item ID range tables and membership predicates.

The legacy randomizer scattered raw ID ranges through model and
randomizer code (``range(0x00, 0x21) + range(0x26, 0x73) + [0x79 ...]``).
Centralising them here means a future ROM revision needs an edit in
exactly one file.
"""

from __future__ import annotations

# ----- raw membership tables (extracted from digimon/models/item.py) ------

CONSUMABLE_ITEM_IDS: frozenset[int] = frozenset(
    list(range(0x00, 0x21)) + list(range(0x26, 0x73)) + [0x79, 0x7A, 0x7D, 0x7E, 0x7F]
)

QUEST_ITEM_IDS: frozenset[int] = frozenset(
    list(range(0x73, 0x79)) + list(range(0x7B, 0x7D))
)

BANNED_ITEM_IDS: frozenset[int] = frozenset((0x53, 0x72))

# Two items use the FOOD category indirectly because of how the engine
# treats them ("Rain Plant" and "Steak").
SPECIAL_FOOD_ITEM_IDS: frozenset[int] = frozenset((0x79, 0x7A))

# Items at or after this ID with ``sort == STATEVO`` are real evo items;
# below this they are stat boosters that share the sort byte.
EVO_ITEM_FIRST_ID: int = 0x47


def is_consumable(item_id: int) -> bool:
    return item_id in CONSUMABLE_ITEM_IDS


def is_quest(item_id: int) -> bool:
    return item_id in QUEST_ITEM_IDS


def is_banned(item_id: int) -> bool:
    return item_id in BANNED_ITEM_IDS


def is_special_food(item_id: int) -> bool:
    return item_id in SPECIAL_FOOD_ITEM_IDS


def is_evo_item(item_id: int, sort_byte: int) -> bool:
    """An item is a true Evo item iff its sort is STATEVO *and* its ID is at
    or above :data:`EVO_ITEM_FIRST_ID` (which separates evo items from the
    stat-boost items that share the sort byte)."""

    from data.item.item_category import ItemCategory  # local import to avoid cycle

    return ItemCategory.from_byte(sort_byte) is ItemCategory.STATEVO and item_id >= EVO_ITEM_FIRST_ID
