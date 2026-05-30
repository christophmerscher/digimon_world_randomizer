# Author: Christoph Merscher <dev@fmerscher.com>

"""Verifies that the model classes only require the narrow Protocol surface.

If anything in `Digimon` / `Item` / `Tech` accidentally reaches for a handler
attribute that isn't part of `ModelContext`, these tests will throw an
`AttributeError` from the stand-in object.
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass, field
from typing import Any, Sequence

import digimon.data as data
from digimon.models import Digimon, Item, ModelContext, Tech


@dataclass
class MinimalLookup:
    """The smallest object that satisfies ``ModelContext`` structurally."""

    digimonData:            list[Any] = field(default_factory=list)
    randomizedRequirements: bool      = False
    logger:                 Any       = None

    # ---- NameLookup --------------------------------------------------------
    def getTypeName(self,      id: int) -> str: return f"T{id}"
    def getLevelName(self,     id: int) -> str: return f"L{id}"
    def getItemName(self,      id: int) -> str: return f"I{id}"
    def getSpecialtyName(self, id: int) -> str: return f"S{id}"
    def getDigimonName(self,   id: int) -> str: return f"D{id}"
    def getTechName(self,      id: int) -> str: return "None" if id == 0xFF else f"X{id}"
    def getRangeName(self,     id: int) -> str: return f"R{id}"
    def getEffectName(self,    id: int) -> str: return f"E{id}"

    # ---- RosterLookup ------------------------------------------------------
    def getPlayableDigimonByLevel(self, level: int) -> list[Any]:
        return [digi for digi in self.digimonData if digi.level == level]


def _encodedName(name: str) -> bytes:
    return name.encode("ascii") + b"\0" * (20 - len(name))


def _makeDigimon(lookup: MinimalLookup, id: int = 3, name: str = "Agumon",
                 level: int = data.levelsByName["ROOKIE"]) -> Digimon:
    readData: Sequence = (
        _encodedName(name),
        100, 4, 0x1200, 1, level,
        0, 1, 2,
        5, 30,
        *range(16),
    )
    return Digimon(lookup, id, readData)


class ProtocolSatisfactionTests(unittest.TestCase):
    def test_minimal_lookup_satisfies_model_context(self):
        # `runtime_checkable` Protocol uses structural matching.
        self.assertIsInstance(MinimalLookup(), ModelContext)

    def test_digimon_str_uses_only_protocol_methods(self):
        lookup = MinimalLookup()
        digi = _makeDigimon(lookup)
        result = str(digi)
        # Tech IDs 0..15 should be substituted via the stand-in's getTechName,
        # and type/level/item should be substituted too.
        self.assertIn("L3", result)         # rookie level id 3 → "L3"
        self.assertIn("T1",  result)        # type 1 → "T1"
        self.assertIn("Agumon", result)
        self.assertIn("X0", result)         # first tech

    def test_digimon_update_evos_from_uses_only_roster_lookup(self):
        lookup = MinimalLookup()
        source = _makeDigimon(lookup, id=1, level=data.levelsByName["ROOKIE"])
        target = _makeDigimon(lookup, id=2, level=data.levelsByName["CHAMPION"])
        other  = _makeDigimon(lookup, id=3, level=data.levelsByName["ROOKIE"])

        source.toEvo[2] = target.id
        other.toEvo[3]  = target.id
        lookup.digimonData = [source, target, other]

        target.updateEvosFrom()
        self.assertEqual(target.fromEvo, [0xFF, 3, 1, 0xFF, 0xFF])

    def test_tech_str_uses_only_protocol_methods(self):
        lookup = MinimalLookup()
        tech = Tech(lookup, 0x10, (1, 2, 100, 4, 5, 1, 0, 2, 95, 50, 11))
        tech.setName("Giga Freeze")
        result = str(tech)
        self.assertIn("Giga Freeze", result)
        self.assertIn("R1", result)         # range id 1
        self.assertIn("S0", result)         # specialty id 0
        self.assertIn("E2", result)         # effect id 2

    def test_item_categorisation_uses_only_local_data(self):
        lookup = MinimalLookup()
        evo  = Item(lookup, 0x47, (_encodedName("EvoItem"), 1000, 2, 0x04, 3, True))
        food = Item(lookup, 0x10, (_encodedName("Berry"),   100,  1, 0x02, 1, True))

        self.assertTrue(evo.isEvo)
        self.assertTrue(food.isFood)
        # Item does not touch handler at all — confirm str() still works.
        self.assertIn("EvoItem", str(evo))


if __name__ == "__main__":
    unittest.main()
