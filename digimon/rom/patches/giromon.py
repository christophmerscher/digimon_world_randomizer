"""Patch: prevent the jukebox crash caused by overlong track names.

The Giromon jukebox glitch happens when the engine reads a track name
that exceeds the display buffer. Truncating every name to 24 bytes (the
buffer width) by overwriting the next byte with a null terminator fixes
it without disturbing earlier entries.
"""

from __future__ import annotations

from digimon.rom.patches.base import Patch, PatchContext


MAX_TRACK_NAME_LENGTH = 24


class GiromonPatch(Patch):
    name = "giromon"

    def apply(self, ctx: PatchContext) -> None:
        track_names = ctx.state.trackNames
        track_len = 0

        for i in range(len(track_names)):
            if track_names[i] == 0x00:
                track_len = 0
                continue

            track_len += 1
            if track_len > MAX_TRACK_NAME_LENGTH:
                track_names = track_names[:i] + b"\0" + track_names[i + 1:]

        ctx.state.trackNames = track_names
        ctx.logger.logChange("Patched out Giromon/jukebox glitch.")
