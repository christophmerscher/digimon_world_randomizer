"""Strategy-pattern ROM patches.

Adding a new patch is a four-step process:

1. Create a new module under ``digimon/rom/patches/`` that defines a
   :class:`Patch` subclass with a unique ``name`` registry key.
2. Add an instance of it to :data:`registry.PATCHES`.
3. Wire the settings JSON / GUI to queue ``handler.applyPatch("<name>")``.
4. (optional) Add a unit test exercising the new ``apply``.

The :class:`PatchPipeline` then takes care of dispatch + always-on
prelude (`EvoTargetUnifyPatch`, `ResetButtonPatch`).
"""

from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.patches.pipeline import PatchPipeline
from digimon.rom.patches.registry import (
    ALWAYS_ON_PATCHES,
    PATCHES,
    get_patch,
)

__all__ = [
    "ALWAYS_ON_PATCHES",
    "PATCHES",
    "Patch",
    "PatchContext",
    "PatchPipeline",
    "get_patch",
]
