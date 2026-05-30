"""Item-category enums and ID range helpers.

The Digimon World ROM uses byte-level IDs for items. Rather than scattering
ID-range checks across the codebase (consumable vs quest vs banned vs evo)
this package collects them in one place.

Categories are derived from the legacy constants in
:mod:`digimon.models.item` (``consumableItems``, ``questItems``,
``bannedItems``, ``itemSort``) so the migration is a like-for-like move
of authority into a structured form.
"""

from data.item.item_category import ItemCategory
from data.item.item_ranges import (
    BANNED_ITEM_IDS,
    CONSUMABLE_ITEM_IDS,
    EVO_ITEM_FIRST_ID,
    QUEST_ITEM_IDS,
    SPECIAL_FOOD_ITEM_IDS,
    is_banned,
    is_consumable,
    is_evo_item,
    is_quest,
    is_special_food,
)

__all__ = [
    "BANNED_ITEM_IDS",
    "CONSUMABLE_ITEM_IDS",
    "EVO_ITEM_FIRST_ID",
    "ItemCategory",
    "QUEST_ITEM_IDS",
    "SPECIAL_FOOD_ITEM_IDS",
    "is_banned",
    "is_consumable",
    "is_evo_item",
    "is_quest",
    "is_special_food",
]
