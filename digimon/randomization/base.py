# Author: Christoph Merscher <dev@fmerscher.com>

"""Strategy base class for every randomiser.

A randomiser mutates an in-memory :class:`~digimon.rom.state.RomState`
according to a section of the parsed settings JSON. They are designed to
be tiny — each one owns the rules for a single feature (chest items,
tech gifts, starters, …).

Sharing state between randomisers happens through three vehicles:

* :class:`RandomizationContext`  — the parameters every randomiser needs
  (state, logger, lookup, queued-patch sink).
* :mod:`digimon.randomization.pickers` — DRY helpers for picking random
  items / techs.
* :class:`~digimon.randomization.pipeline.RandomizationPipeline` — owns
  the order of execution and exposes a single ``run()`` entry point.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable

from digimon.rom.state import RomState


@dataclass
class RandomizationContext:
    """Everything a :class:`Randomizer` needs at apply time."""

    state: RomState
    """Mutable in-memory ROM state — the randomiser mutates it directly."""

    logger: Any
    """Anything implementing ``log`` / ``logChange`` / ``logError`` /
    ``getHeader``."""

    lookup: Any
    """Anything implementing the ``getXName`` methods (see
    :class:`digimon.models.NameLookup`). Today this is the
    :class:`DigimonWorldHandler` facade."""

    queue_patch: Callable[[str, Any], None]
    """Callback used by randomisers that need to also queue a follow-up
    ROM patch (e.g. the recruitment randomiser queues ``pp`` and
    ``ogremon``). Bound to :meth:`DigimonWorldHandler.applyPatch`."""

    layout: Any = None
    """Detected ROM layout; randomisers use this only to avoid queueing
    layout-specific patches that are not mapped for the current disc."""


class Randomizer(ABC):
    """Base Strategy class — one ``apply(ctx)`` per feature."""

    @abstractmethod
    def apply(self, ctx: RandomizationContext) -> None:
        """Mutate ``ctx.state`` to randomise this feature."""
