# Author: Christoph Merscher <dev@fmerscher.com>

"""Patch: change the random spawn rate of Mamemon/Piximon/MMamemon/Otamamon.

Mamemon-family spawns use a 0..99 RNG, Otamamon uses a 0..2 RNG. The
patch translates the requested percentage into the appropriate
representation for each enemy group.
"""

from __future__ import annotations

import math
import struct

from digimon.rom.patch_data import (
    spawnRateFormat,
)
from digimon.rom.patches.base import Patch, PatchContext, require_patch_offset
from digimon.rom.struct_codec import write_value


# Percentage range the engine actually understands.
MIN_PCT, MAX_PCT = 1, 100

# Otamamon spawns are gated by a 0..2 random, so its rate uses a coarse
# 3-bucket conversion (every 33% bumps it by one bucket).
OTAMAMON_BUCKET_SIZE = 33


class SpawnRatePatch(Patch):
    name = "spawn"
    takes_value = True
    supported_layouts = None
    required_patch_offsets = (
        "spawnRateMamemonOffset",
        "spawnRatePiximonOffset",
        "spawnRateMMamemonOffset",
        "spawnRateOtamamonOffset",
    )

    def apply(self, ctx: PatchContext) -> None:
        # ctx.value comes from the settings as ``patches['SpawnRate']`` (1–100).
        requested = max(MIN_PCT, min(MAX_PCT, int(ctx.value)))

        large_percent = requested - 1
        small_percent = math.floor(requested / OTAMAMON_BUCKET_SIZE)

        for offset in require_patch_offset(ctx, "spawnRateMamemonOffset"):
            write_value(ctx.handle, offset, struct.pack(spawnRateFormat, large_percent))
        for offset in require_patch_offset(ctx, "spawnRatePiximonOffset"):
            write_value(ctx.handle, offset, struct.pack(spawnRateFormat, large_percent))
        for offset in require_patch_offset(ctx, "spawnRateMMamemonOffset"):
            write_value(ctx.handle, offset, struct.pack(spawnRateFormat, large_percent))
        for offset in require_patch_offset(ctx, "spawnRateOtamamonOffset"):
            write_value(ctx.handle, offset, struct.pack(spawnRateFormat, small_percent))

        ctx.logger.logChange(
            "Updated Piximon, Mamemon, MetalMamemon, and Otamamon spawn rates."
        )
