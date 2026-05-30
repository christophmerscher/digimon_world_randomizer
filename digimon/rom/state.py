"""Container for all mutable state loaded from a ROM image.

A single ``RomState`` corresponds to one open ROM in memory. The reader
populates it, the randomizers mutate it, and the writer serialises it
back out.

Field names mirror the long-standing attributes on
:class:`~digimon.handler.DigimonWorldHandler` so that the facade can
continue to expose them under the same names while the refactor
progresses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover — avoid runtime import cycle
    from digimon.models import Digimon, Item, Tech


@dataclass
class RomState:
    """Everything we know about a loaded ROM."""

    techData:        list["Tech"]           = field(default_factory=list)
    brainLearn:      list[list[int]]        = field(default_factory=list)
    itemData:        list["Item"]           = field(default_factory=list)
    digimonData:     list["Digimon"]        = field(default_factory=list)

    starterID:       list[int]              = field(default_factory=list)
    starterTech:     list[int]              = field(default_factory=list)
    starterTechSlot: list[int]              = field(default_factory=list)

    # Each entry: trigger -> (verified-offsets, digimon-id, name-offsets)
    recruitData:     dict[int, tuple[tuple[int, ...], int, tuple[int, ...]]] = field(default_factory=dict)

    # Each entry: (offsets-tuple) -> (target-digimon-id, from-digimon-id)
    specEvos:        dict[tuple[int, ...], tuple[int, int]] = field(default_factory=dict)

    chestItems:      dict[int, int]                              = field(default_factory=dict)
    mapItems:        dict[int, int]                              = field(default_factory=dict)
    tokoItems:       dict[int, tuple[int, int]]                  = field(default_factory=dict)
    techGifts:       dict[tuple[int, int], int]                  = field(default_factory=dict)

    trackNames:      bytes                                       = b""
