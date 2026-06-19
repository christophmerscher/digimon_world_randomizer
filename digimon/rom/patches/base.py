# Author: Christoph Merscher <dev@fmerscher.com>

"""Abstract base for every ROM patch implemented as a Strategy class.

A patch is a self-contained transformation applied at write-time. It can
either:

* mutate a single byte range of the ROM image (most common — write a
  hard-coded payload at a known offset), or
* mutate an entry in the :class:`~digimon.rom.state.RomState` so that the
  ordinary writer serialises the new value during its normal pass.

Each subclass declares its registry key (``name``) and a couple of
metadata fields used by :class:`~digimon.rom.patches.pipeline.PatchPipeline`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, BinaryIO, ClassVar

from digimon.rom.state import RomState


@dataclass
class PatchContext:
    """Everything a patch needs to do its work."""

    handle: BinaryIO
    """Open binary file handle for the ROM image (positioned freely)."""

    state: RomState
    """Mutable in-memory state — patches that change track names, brain
    learn rates, or item ``dropable`` flags write into this container."""

    logger: Any
    """Anything implementing the small Logger interface (``log``,
    ``logChange``, ``logError``)."""

    value: Any = None
    """Per-patch parameter — e.g. the integer spawn rate for ``spawn`` or
    the settings hash string for ``hash``. Patches without a parameter
    leave this as ``None``."""

    layout: Any = None
    """Region-specific ROM layout for patches that write raw offsets."""


class Patch(ABC):
    """Base Strategy class for a single, opt-in ROM transformation."""

    name: ClassVar[str]
    """The string key under which this patch is registered. Matches the
    settings JSON / legacy ``handler.patches`` queue entries."""

    requires_toy_town_workaround: ClassVar[bool] = False
    """Patches that need the writer to skip one of the Monzaemon/Toy Town
    special-evolution writes set this to ``True`` (currently only the
    ``unlock`` patch)."""

    takes_value: ClassVar[bool] = False
    """Whether this patch reads :attr:`PatchContext.value`. Pure metadata —
    the pipeline always passes the queued value regardless."""

    supported_layouts: ClassVar[tuple[str, ...] | None] = ("ntsc-u",)
    """Layout keys this patch can safely run against.

    ``None`` means the patch is layout-independent, usually because it only
    mutates :class:`RomState` and lets the normal writer handle addresses.
    """

    required_patch_offsets: ClassVar[tuple[str, ...]] = ()
    """Named layout ``patch_offsets`` entries required by this patch."""

    def supports_layout(self, layout: Any) -> bool:
        """Return whether this patch can safely run for ``layout``."""

        if self.supported_layouts is not None and layout.key not in self.supported_layouts:
            return False

        return all(name in layout.patch_offsets for name in self.required_patch_offsets)

    def requires_writer_workaround(self, layout: Any) -> bool:
        """Return whether applying this patch needs a writer-side workaround."""

        return self.requires_toy_town_workaround

    @abstractmethod
    def apply(self, ctx: PatchContext) -> None:
        """Run the patch against ``ctx`` (file handle + state)."""


def require_patch_offset(ctx: PatchContext, name: str) -> Any:
    """Return a layout-owned patch offset group.

    Direct unit tests may construct a :class:`PatchContext` without a
    layout; keep that path NTSC-compatible while production calls continue
    to use the detected ROM layout supplied by :class:`PatchPipeline`.
    """

    layout = ctx.layout
    if layout is None:
        from digimon.rom.layouts import NTSC_U_LAYOUT

        layout = NTSC_U_LAYOUT

    return layout.require_patch_offset(name)
