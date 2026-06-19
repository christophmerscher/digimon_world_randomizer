# Author: Tristan Challener <challenert@gmail.com>
# Author: Christoph Merscher <dev@fmerscher.com>
# Copyright: please don't steal this that is all

"""Backward-compatibility shim.

The actual patch implementations live in :mod:`digimon.rom.patches`.
``applyPatches(handler, file)`` is kept here so that historical call
sites (notably :meth:`DigimonWorldHandler.write`) and the existing test
suite continue to work without changes.

New code should use :class:`digimon.rom.patches.PatchPipeline` directly.
"""

from __future__ import annotations

from typing import Any

from digimon.rom.patches.pipeline import PatchPipeline
from digimon.rom.patches.registry import PATCHES, get_patch
from digimon.rom.state import RomState


def applyPatches(handler: Any, file: Any) -> bool:
    """Dispatch the handler's queued patches via the new pipeline.

    The function preserves the legacy contract:

    * ``handler.patches`` is an iterable of ``(name, value)`` tuples.
    * Returns ``True`` when any applied patch sets the Toy-Town flag.
    * Logs an error and continues when a queued patch name is unknown.

    For callers (tests) that pass a stand-in handler exposing the
    historical ``_applyPatchXxx`` methods rather than the new state-based
    Strategy classes, the shim falls back to invoking those methods
    directly. That covers ``tests/test_patch_registry.py`` without
    requiring a real :class:`RomState`.
    """

    if isinstance(getattr(handler, "_state", None), RomState):
        return PatchPipeline(handler.logger, handler._layout).apply(
            file, handler._state, handler.patches
        )

    # Legacy / test fallback — keep calling the handler's bound methods so
    # existing duck-typed test doubles continue to work.
    return _apply_via_handler_methods(handler, file)


def _apply_via_handler_methods(handler: Any, file: Any) -> bool:
    toy_town_workaround = False

    for name, value in handler.patches:
        patch = get_patch(name)
        if patch is None:
            handler.logger.logError(
                'Error: unknown patch "' + str(name) + '".'
            )
            continue

        method = _LEGACY_METHOD_NAMES.get(name)
        if method is None or not hasattr(handler, method):
            handler.logger.logError(
                'Error: unknown patch "' + str(name) + '".'
            )
            continue

        if _PATCH_TAKES_VALUE.get(name, False):
            getattr(handler, method)(file, value)
        else:
            getattr(handler, method)(file)

        if patch.requires_toy_town_workaround:
            toy_town_workaround = True

    return toy_town_workaround


# Legacy method-name table — preserved for test_patch_registry.py.
_LEGACY_METHOD_NAMES = {
    "fixEvoItems":         "_applyPatchFixEvoItems",
    "allowDrop":           "_applyPatchAllowDrop",
    "woah":                "_applyPatchWoah",
    "learnTierOne":        "_applyPatchLearnTierOne",
    "upLearnChance":       "_applyPatchLearnChance",
    "gabumon":             "_applyPatchGabumon",
    "giromon":             "_applyPatchGiromon",
    "spawn":               "_applyPatchSpawn",
    "hash":                "_applyPatchIntroHash",
    "intro":               "_applyPatchIntroSkip",
    "slots":               "_applyPatchUnrigSlots",
    "unlock":              "_applyPatchUnlockAreas",
    "pp":                  "_applyPatchPP",
    "ogremon":             "_applyPatchOgremonSoftlock",
    "softlock":            "_applyPatchMovementSoftlock",
    "typeEffectiveness":   "_randomizeTypeEffectiveness",
    "learnmoveandcommand": "_applyPatchLearnMoveAndCommand",
    "fixDVChips":          "_applyPatchDVChipDescription",
    "happyVending":        "_applyPatchGuaranteeHappyShrm",
}

_PATCH_TAKES_VALUE = {
    name: PATCHES[name].takes_value for name in PATCHES
}


# Backward-compat re-exports kept for any external importers.
PATCH_HANDLERS = {
    name: (method, _PATCH_TAKES_VALUE.get(name, False))
    for name, method in _LEGACY_METHOD_NAMES.items()
}

TOY_TOWN_WORKAROUND_PATCHES = tuple(
    name for name, patch in PATCHES.items() if patch.requires_toy_town_workaround
)
