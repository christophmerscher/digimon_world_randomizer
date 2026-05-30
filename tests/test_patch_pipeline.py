# Author: Christoph Merscher <dev@fmerscher.com>

"""Tests for the Strategy-pattern :class:`PatchPipeline`.

These tests drive the new framework directly (rather than through the
legacy ``patch_registry`` shim) to make sure the always-on prelude runs,
unknown patches log an error and skip, and the Toy-Town workaround flag
is reported correctly.
"""

from __future__ import annotations

import io
import struct
import unittest

from digimon.models import Item
from digimon.rom.patches import PatchPipeline
from digimon.rom.patches.allow_drop import AllowDropPatch
from digimon.rom.patches.base import PatchContext
from digimon.rom.patches.giromon import GiromonPatch
from digimon.rom.patches.learn_tier_one import LearnTierOnePatch
from digimon.rom.patches.registry import ALWAYS_ON_PATCHES, get_patch
from digimon.rom.state import RomState


class _RecordingLogger:
    def __init__(self) -> None:
        self.changes: list[str] = []
        self.errors:  list[str] = []

    def log(self, message: str) -> None:
        pass

    def logChange(self, message: str) -> None:
        self.changes.append(message)

    def logError(self, message: str) -> None:
        self.errors.append(message)

    def getHeader(self, name: str) -> str:
        return name


def _empty_rom() -> io.BytesIO:
    # 256 MB is overkill, but cheap with BytesIO since unused regions stay
    # un-allocated.
    return io.BytesIO(b"\x00" * 0x14E00000)


class _MinimalLookup:
    """Just enough of ``ModelContext`` to construct an ``Item``."""

    digimonData: list = []
    randomizedRequirements: bool = False
    logger = None

    def getTypeName(self, id):      return ""
    def getLevelName(self, id):     return ""
    def getItemName(self, id):      return ""
    def getSpecialtyName(self, id): return ""
    def getDigimonName(self, id):   return ""
    def getTechName(self, id):      return ""
    def getRangeName(self, id):     return ""
    def getEffectName(self, id):    return ""
    def getPlayableDigimonByLevel(self, level): return []


def _item(id: int = 0, name: str = "Drop", dropable: bool = False) -> Item:
    encoded = name.encode("ascii") + b"\0" * (20 - len(name))
    return Item(_MinimalLookup(), id, (encoded, 100, 0, 0x02, 1, dropable))


class PipelineDispatchTests(unittest.TestCase):
    def test_pipeline_always_runs_the_two_always_on_patches_first(self):
        logger = _RecordingLogger()
        state = RomState()

        rom = _empty_rom()
        PatchPipeline(logger).apply(rom, state, queued=())

        # Both always-on patches log; expect their messages in order.
        always_on_names = {p.name for p in ALWAYS_ON_PATCHES}
        self.assertGreaterEqual(len(always_on_names), 2)
        self.assertIn("Unified evoTarget functions.", logger.changes)
        self.assertIn("Added custom function and hook for it", logger.changes)

    def test_pipeline_logs_error_for_unknown_patch_and_continues(self):
        logger = _RecordingLogger()
        state = RomState()

        rom = _empty_rom()
        PatchPipeline(logger).apply(
            rom, state,
            queued=(("not-a-real-patch", None),),
        )

        self.assertEqual(len(logger.errors), 1)
        self.assertIn("not-a-real-patch", logger.errors[0])

    def test_pipeline_reports_toy_town_workaround_for_unlock_patch(self):
        logger = _RecordingLogger()
        state = RomState()

        rom = _empty_rom()
        toy_town = PatchPipeline(logger).apply(
            rom, state, queued=(("unlock", None),),
        )
        self.assertTrue(toy_town)

        # Sanity: another patch leaves the flag false.
        rom2 = _empty_rom()
        state2 = RomState()
        toy_town2 = PatchPipeline(_RecordingLogger()).apply(
            rom2, state2, queued=(("fixEvoItems", None),),
        )
        self.assertFalse(toy_town2)


class IndividualPatchTests(unittest.TestCase):
    def test_learn_tier_one_writes_to_state_not_to_file(self):
        state = RomState()
        # Reader normally populates 8 rows × 3 columns; mimic that here.
        state.brainLearn = [[0, 0, 0] for _ in range(8)]
        rom = _empty_rom()

        LearnTierOnePatch().apply(
            PatchContext(handle=rom, state=state, logger=_RecordingLogger())
        )

        self.assertEqual(state.brainLearn[0][0], 30)
        # File must not be touched by a state-only patch.
        rom.seek(0)
        self.assertEqual(rom.read(16), b"\x00" * 16)

    def test_allow_drop_marks_every_item_as_dropable(self):
        state = RomState()
        state.itemData = [_item(id=i, name=f"X{i}", dropable=False) for i in range(3)]

        AllowDropPatch().apply(
            PatchContext(handle=_empty_rom(), state=state, logger=_RecordingLogger())
        )

        self.assertTrue(all(item.dropable for item in state.itemData))

    def test_giromon_truncates_long_track_names(self):
        state = RomState()
        # Two tracks separated by a null: 30 'A' bytes (too long), then 'B'.
        state.trackNames = b"A" * 30 + b"\0" + b"B" * 5 + b"\0"

        GiromonPatch().apply(
            PatchContext(handle=_empty_rom(), state=state, logger=_RecordingLogger())
        )

        # Bytes 25+ in the first run should now be nulls; the short second
        # track is left alone.
        self.assertEqual(state.trackNames[:24], b"A" * 24)
        self.assertEqual(state.trackNames[24:30], b"\0" * 6)
        self.assertTrue(state.trackNames.endswith(b"B" * 5 + b"\0"))

    def test_registry_returns_none_for_unknown_patch(self):
        self.assertIsNone(get_patch("not-a-real-patch"))
        self.assertIsNotNone(get_patch("fixEvoItems"))


if __name__ == "__main__":
    unittest.main()
