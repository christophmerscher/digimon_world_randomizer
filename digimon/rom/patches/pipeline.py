"""Apply a queue of patches against an open ROM image."""

from __future__ import annotations

from typing import Iterable, Tuple

from digimon.rom.patches.base import Patch, PatchContext
from digimon.rom.patches.registry import ALWAYS_ON_PATCHES, get_patch
from digimon.rom.state import RomState


# A queued patch entry: (registry-key, value passed to the patch).
QueuedPatch = Tuple[str, object]


class PatchPipeline:
    """Apply the always-on patches plus a queued sequence of opt-in patches.

    Returns ``True`` from :meth:`apply` if any applied patch flagged the
    Toy-Town workaround (the writer uses that signal to skip one of the
    Monzaemon special-evolution writes).
    """

    def __init__(self, logger) -> None:
        self._logger = logger

    # ------------------------------------------------------------------
    def apply(self, handle, state: RomState, queued: Iterable[QueuedPatch]) -> bool:
        toy_town_workaround = False

        # 1) Always-on prelude.
        for patch in ALWAYS_ON_PATCHES:
            self._run(patch, handle, state, None)

        # 2) Opt-in queue, in registration order from the caller.
        for name, value in queued:
            patch = get_patch(name)
            if patch is None:
                self._logger.logError(
                    'Error: unknown patch "' + str(name) + '".'
                )
                continue

            self._run(patch, handle, state, value)

            if patch.requires_toy_town_workaround:
                toy_town_workaround = True

        return toy_town_workaround

    # ------------------------------------------------------------------
    def _run(self, patch: Patch, handle, state: RomState, value) -> None:
        ctx = PatchContext(handle=handle, state=state, logger=self._logger, value=value)
        patch.apply(ctx)
