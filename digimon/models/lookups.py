# Author: Christoph Merscher <dev@fmerscher.com>

"""Narrow Protocols that the ROM data models depend on.

Before this refactor, every :class:`~digimon.models.Digimon`,
:class:`~digimon.models.Item`, and :class:`~digimon.models.Tech` instance
held a back-reference to the whole :class:`~digimon.handler.DigimonWorldHandler`.
That meant unit-testing a model required reproducing the entire handler
surface area.

The two Protocols here express precisely what the models need:

* :class:`NameLookup`  — eight ``get*Name(id)`` methods used by ``__str__``
  and the various log helpers.
* :class:`RosterLookup` — read access to the digimon roster + the
  randomisation-state flags used by ``Digimon.updateEvosFrom`` and
  ``Digimon.validEvosTo``.

:class:`ModelContext` aggregates both (plus a ``logger``) so the model
constructors can keep a single positional argument and the existing
``FakeHandler`` test double continues to satisfy the contract by
structural typing.
"""

from __future__ import annotations

from typing import Any, Protocol, Sequence, runtime_checkable


@runtime_checkable
class NameLookup(Protocol):
    """Look up display names for the various ID-keyed enums."""

    def getTypeName(self,      id: int) -> str: ...
    def getLevelName(self,     id: int) -> str: ...
    def getItemName(self,      id: int) -> str: ...
    def getSpecialtyName(self, id: int) -> str: ...
    def getDigimonName(self,   id: int) -> str: ...
    def getTechName(self,      id: int) -> str: ...
    def getRangeName(self,     id: int) -> str: ...
    def getEffectName(self,    id: int) -> str: ...


@runtime_checkable
class RosterLookup(Protocol):
    """Read-side access to the loaded digimon roster + randomiser state."""

    digimonData: Sequence[Any]
    randomizedRequirements: bool

    def getPlayableDigimonByLevel(self, level: int) -> list[Any]: ...


@runtime_checkable
class ErrorReporter(Protocol):
    """Just enough of the Logger interface for the models to report errors."""

    def logError(self, message: str) -> None: ...


@runtime_checkable
class ModelContext(NameLookup, RosterLookup, Protocol):
    """Aggregate Protocol passed to the model constructors.

    The legacy handler satisfies this Protocol naturally — it already
    exposes ``logger`` plus the name lookups and roster accessors. New
    callers can build a smaller stand-in object instead of carrying the
    full handler when they only need model behaviour.
    """

    logger: ErrorReporter
