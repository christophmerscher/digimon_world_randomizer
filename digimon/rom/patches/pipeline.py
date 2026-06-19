# Author: Christoph Merscher <dev@fmerscher.com>

"""Apply a queue of patches against an open ROM image."""

from __future__ import annotations

from typing import Iterable, Tuple

from digimon.rom.layouts import NTSC_U_LAYOUT, RomLayout
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

    def __init__(self, logger, layout: RomLayout = NTSC_U_LAYOUT) -> None:
        self._logger = logger
        self._layout = layout

    # ------------------------------------------------------------------
    def apply(self, handle, state: RomState, queued: Iterable[QueuedPatch]) -> bool:
        toy_town_workaround = False

        # 1) Always-on prelude.
        for patch in ALWAYS_ON_PATCHES:
            self._run(patch, handle, state, None, unsupported_is_error=False)

        # 2) Opt-in queue, in registration order from the caller.
        for name, value in queued:
            patch = get_patch(name)
            if patch is None:
                self._logger.logError(
                    'Error: unknown patch "' + str(name) + '".'
                )
                continue

            applied = self._run(patch, handle, state, value)

            if applied and patch.requires_writer_workaround(self._layout):
                toy_town_workaround = True

        return toy_town_workaround

    # ------------------------------------------------------------------
    def _run(
        self,
        patch: Patch,
        handle,
        state: RomState,
        value,
        *,
        unsupported_is_error: bool = True,
    ) -> bool:
        if not patch.supports_layout(self._layout):
            message = (
                'Patch "' + patch.name + '" is not mapped for '
                + self._layout.display_name + "."
            )
            if unsupported_is_error:
                self._logger.logError("Error: " + message)
            else:
                self._logger.log("Skipped " + message)
            return False

        ctx = PatchContext(
            handle=handle,
            state=state,
            logger=self._logger,
            value=value,
            layout=self._layout,
        )
        patch.apply(ctx)
        return True
