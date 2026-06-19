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

import script.util as scrutil
from digimon.models import Item
from digimon.rom.layouts import NTSC_U_LAYOUT, PAL_DE_LAYOUT, RomLayout
from digimon.rom import patch_data
from digimon.rom.patches import PatchPipeline
from digimon.rom.patches.allow_drop import AllowDropPatch
from digimon.rom.patches.base import PatchContext
from digimon.rom.patches.fix_evo_items import FixEvoItemsPatch
from digimon.rom.patches.giromon import GiromonPatch
from digimon.rom.patches.happy_vending import HappyVendingPatch
from digimon.rom.patches.intro_hash import IntroHashPatch
from digimon.rom.patches.intro_skip import IntroSkipPatch
from digimon.rom.patches.learn_tier_one import LearnTierOnePatch
from digimon.rom.patches.movement_softlock import MovementSoftlockPatch
from digimon.rom.patches.ogremon_softlock import OgremonSoftlockPatch
from digimon.rom.patches.pp import PPCalculationPatch
from digimon.rom.patches.registry import ALWAYS_ON_PATCHES, PATCHES, get_patch
from digimon.rom.patches.spawn_rate import SpawnRatePatch
from digimon.rom.patches.type_effectiveness import (
    EFFECTIVENESS_VALUES,
    TypeEffectivenessPatch,
)
from digimon.rom.patches.unlock_areas import UnlockAreasPatch
from digimon.rom.state import RomState
from tests.pal_de_evidence import PAL_DE_PP_CALCULATION_PATCH_VALUE


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


def _pal_patch_test_layout() -> RomLayout:
    return RomLayout(
        key="pal-test",
        display_name="PAL Test",
        serials=("TEST",),
        complete=False,
        blocks={},
        patch_offsets={"typeEffectivenessOffset": 0x20},
    )


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


class _RecordingHandle:
    def __init__(self):
        self.offset = 0
        self.writes = []

    def seek(self, offset, whence=0):
        self.offset = offset

    def write(self, payload):
        self.writes.append((self.offset, payload))
        return len(payload)


def _item(id: int = 0, name: str = "Drop", dropable: bool = False) -> Item:
    encoded = name.encode("ascii") + b"\0" * (20 - len(name))
    return Item(_MinimalLookup(), id, (encoded, 100, 0, 0x02, 1, dropable))


class PipelineDispatchTests(unittest.TestCase):
    def test_every_layout_aware_patch_has_ntsc_offsets_registered(self):
        for patch in (*ALWAYS_ON_PATCHES, *PATCHES.values()):
            for offset_name in patch.required_patch_offsets:
                self.assertIn(offset_name, NTSC_U_LAYOUT.patch_offsets, patch.name)

    def test_pal_patch_support_is_driven_by_registered_offset_keys(self):
        for patch in (*ALWAYS_ON_PATCHES, *PATCHES.values()):
            expected = (
                patch.supported_layouts is None
                or PAL_DE_LAYOUT.key in patch.supported_layouts
            ) and all(
                offset_name in PAL_DE_LAYOUT.patch_offsets
                for offset_name in patch.required_patch_offsets
            )

            self.assertEqual(patch.supports_layout(PAL_DE_LAYOUT), expected, patch.name)

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

        pal_toy_town = PatchPipeline(_RecordingLogger(), PAL_DE_LAYOUT).apply(
            _RecordingHandle(), RomState(), queued=(("unlock", None),),
        )
        self.assertFalse(pal_toy_town)

        # Sanity: another patch leaves the flag false.
        rom2 = _empty_rom()
        state2 = RomState()
        toy_town2 = PatchPipeline(_RecordingLogger()).apply(
            rom2, state2, queued=(("fixEvoItems", None),),
        )
        self.assertFalse(toy_town2)

    def test_pipeline_skips_unmapped_patches_for_non_ntsc_layout(self):
        logger = _RecordingLogger()
        state = RomState()
        rom = io.BytesIO(b"\x00" * 0x80)

        toy_town = PatchPipeline(logger, _pal_patch_test_layout()).apply(
            rom,
            state,
            queued=(
                ("unlock", None),
                ("typeEffectiveness", None),
                ("allowDrop", None),
            ),
        )

        payload = rom.getvalue()
        chart = payload[0x20:0x20 + 49]
        self.assertFalse(toy_town)
        self.assertTrue(set(chart).issubset(EFFECTIVENESS_VALUES))
        self.assertNotEqual(chart, b"\x00" * 49)
        self.assertEqual(payload[:0x20], b"\x00" * 0x20)
        self.assertFalse(any('"_evoTargetUnify"' in error for error in logger.errors))
        self.assertFalse(any('"_resetButton"' in error for error in logger.errors))
        self.assertTrue(any('"unlock"' in error for error in logger.errors))
        self.assertFalse(any('"typeEffectiveness"' in error for error in logger.errors))
        self.assertFalse(any('"allowDrop"' in error for error in logger.errors))

    def test_pipeline_applies_happy_vending_patch_for_ntsc(self):
        logger = _RecordingLogger()
        rom = _empty_rom()

        PatchPipeline(logger).apply(
            rom,
            RomState(),
            queued=(("happyVending", None),),
        )

        rom.seek(patch_data.happyMushroomVendingOffset1)
        self.assertEqual(
            rom.read(struct.calcsize(patch_data.happyMushroomVendingFormat1)),
            struct.pack(
                patch_data.happyMushroomVendingFormat1,
                patch_data.happyMushroomVendingValue1.encode("shift_jis"),
            ),
        )
        rom.seek(patch_data.happyMushroomVendingOffset2)
        self.assertEqual(
            rom.read(struct.calcsize(patch_data.happyMushroomVendingFormat2)),
            struct.pack(
                patch_data.happyMushroomVendingFormat2,
                patch_data.happyMushroomVendingValue2.encode("ascii"),
            ),
        )
        for offset in (
            patch_data.happyMushroomVendingOffset3,
            patch_data.happyMushroomVendingOffset4,
        ):
            rom.seek(offset)
            self.assertEqual(
                rom.read(struct.calcsize(patch_data.happyMushroomVendingPriceFormat)),
                struct.pack(
                    patch_data.happyMushroomVendingPriceFormat,
                    patch_data.happyMushroomVendingPriceValue,
                ),
            )
        for offset in patch_data.happyMushroomVendingOffset5:
            rom.seek(offset)
            self.assertEqual(
                rom.read(struct.calcsize(patch_data.happyMushroomVendingFormat5)),
                struct.pack(
                    patch_data.happyMushroomVendingFormat5,
                    patch_data.happyMushroomVendingValue5,
                ),
            )
        self.assertTrue(HappyVendingPatch().supports_layout(NTSC_U_LAYOUT))
        self.assertFalse(logger.errors)

    def test_pipeline_applies_happy_vending_patch_for_pal_de(self):
        logger = _RecordingLogger()
        rom = _empty_rom()

        PatchPipeline(logger, PAL_DE_LAYOUT).apply(
            rom,
            RomState(),
            queued=(("happyVending", None),),
        )

        menu_payload = struct.pack(
            PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingFormat1"],
            PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingPayload1"],
        )
        for offset in PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingOffset1"]:
            rom.seek(offset)
            self.assertEqual(rom.read(len(menu_payload)), menu_payload)

        result_payload = struct.pack(
            PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingFormat2"],
            PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingPayload2"],
        )
        for offset in PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingOffset2"]:
            rom.seek(offset)
            self.assertEqual(rom.read(len(result_payload)), result_payload)

        for offset_group in (
            PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingOffset3"],
            PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingOffset4"],
        ):
            for offset in offset_group:
                rom.seek(offset)
                self.assertEqual(
                    rom.read(struct.calcsize(patch_data.happyMushroomVendingPriceFormat)),
                    struct.pack(
                        patch_data.happyMushroomVendingPriceFormat,
                        patch_data.happyMushroomVendingPriceValue,
                    ),
                )

        for offset in PAL_DE_LAYOUT.patch_offsets["happyMushroomVendingOffset5"]:
            rom.seek(offset)
            self.assertEqual(
                rom.read(struct.calcsize(patch_data.happyMushroomVendingFormat5)),
                struct.pack(
                    patch_data.happyMushroomVendingFormat5,
                    patch_data.happyMushroomVendingValue5,
                ),
            )

        self.assertTrue(HappyVendingPatch().supports_layout(PAL_DE_LAYOUT))
        self.assertFalse(logger.errors)

    def test_pipeline_applies_dv_chip_description_patch_for_pal_de(self):
        logger = _RecordingLogger()
        rom = _empty_rom()

        PatchPipeline(logger, PAL_DE_LAYOUT).apply(
            rom,
            RomState(),
            queued=(("fixDVChips", None),),
        )

        for prefix in ("DVChipA", "DVChipD", "DVChipE"):
            payload = struct.pack(
                PAL_DE_LAYOUT.patch_offsets[prefix + "Format"],
                PAL_DE_LAYOUT.patch_offsets[prefix + "Payload"],
            )
            rom.seek(PAL_DE_LAYOUT.patch_offsets[prefix + "Offset"])
            self.assertEqual(rom.read(len(payload)), payload)

        self.assertFalse(logger.errors)

    def test_pipeline_applies_learn_move_and_command_patch_for_pal_de(self):
        logger = _RecordingLogger()
        rom = _empty_rom()

        PatchPipeline(logger, PAL_DE_LAYOUT).apply(
            rom,
            RomState(),
            queued=(("learnmoveandcommand", None),),
        )

        payload = struct.pack(
            patch_data.learnMoveAndCommandFormat,
            *patch_data.learnMoveAndCommandValue,
        )
        rom.seek(PAL_DE_LAYOUT.patch_offsets["learnMoveAndCommandOffset"])
        self.assertEqual(rom.read(len(payload)), payload)
        self.assertFalse(logger.errors)

    def test_pipeline_applies_gabumon_patch_for_pal_de(self):
        logger = _RecordingLogger()
        rom = _empty_rom()

        PatchPipeline(logger, PAL_DE_LAYOUT).apply(
            rom,
            RomState(),
            queued=(("gabumon", None),),
        )

        for offset, value in PAL_DE_LAYOUT.patch_offsets["gabuPatchWrites"]:
            rom.seek(offset)
            self.assertEqual(
                rom.read(struct.calcsize(patch_data.gabuPatchFormat)),
                struct.pack(patch_data.gabuPatchFormat, value),
            )

        self.assertFalse(logger.errors)

    def test_pipeline_applies_unrig_slots_patch_for_pal_de(self):
        logger = _RecordingLogger()
        rom = _empty_rom()

        PatchPipeline(logger, PAL_DE_LAYOUT).apply(
            rom,
            RomState(),
            queued=(("slots", None),),
        )

        rom.seek(PAL_DE_LAYOUT.patch_offsets["unrigSlotsOffset"])
        self.assertEqual(
            rom.read(struct.calcsize(patch_data.unrigSlotsFormat)),
            struct.pack(patch_data.unrigSlotsFormat, patch_data.unrigSlotsValue),
        )
        rom.seek(PAL_DE_LAYOUT.patch_offsets["unrigSlots2Offset"])
        self.assertEqual(
            rom.read(struct.calcsize(patch_data.unrigSlots2Format)),
            struct.pack(patch_data.unrigSlots2Format, patch_data.unrigSlots2Value),
        )
        self.assertFalse(logger.errors)

    def test_pipeline_applies_woah_patch_for_pal_de(self):
        logger = _RecordingLogger()
        rom = _empty_rom()

        PatchPipeline(logger, PAL_DE_LAYOUT).apply(
            rom,
            RomState(),
            queued=(("woah", None),),
        )

        payload = struct.pack(
            PAL_DE_LAYOUT.patch_offsets["woahPatchFormat"],
            PAL_DE_LAYOUT.patch_offsets["woahPatchPayload"],
        )
        for offset in PAL_DE_LAYOUT.patch_offsets["woahPatchOffset"]:
            rom.seek(offset)
            self.assertEqual(rom.read(len(payload)), payload)

        self.assertFalse(logger.errors)

    def test_pipeline_applies_always_on_patches_for_pal_de(self):
        logger = _RecordingLogger()
        rom = _empty_rom()

        PatchPipeline(logger, PAL_DE_LAYOUT).apply(
            rom,
            RomState(),
            queued=(),
        )

        for offset, value in PAL_DE_LAYOUT.patch_offsets["evoTargetUnifyHack"].items():
            rom.seek(offset)
            self.assertEqual(
                rom.read(struct.calcsize(patch_data.evoTargetUnifyHackFormat)),
                struct.pack(patch_data.evoTargetUnifyHackFormat, value),
            )

        rom.seek(PAL_DE_LAYOUT.patch_offsets["customTickFunctionOffset"])
        self.assertEqual(
            rom.read(struct.calcsize(patch_data.customTickFunctionFormat)),
            struct.pack(
                patch_data.customTickFunctionFormat,
                *patch_data.customTickFunctionValue,
            ),
        )
        rom.seek(PAL_DE_LAYOUT.patch_offsets["customTickHookOffset"])
        self.assertEqual(
            rom.read(struct.calcsize(patch_data.customTickHookFormat)),
            struct.pack(patch_data.customTickHookFormat, patch_data.customTickHookValue),
        )

        self.assertIn("Unified evoTarget functions.", logger.changes)
        self.assertIn("Added custom function and hook for it", logger.changes)
        self.assertFalse(logger.errors)


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

    def test_type_effectiveness_uses_layout_patch_offset(self):
        layout = RomLayout(
            key="tiny-test",
            display_name="Tiny Test",
            serials=("TEST",),
            complete=True,
            blocks={},
            patch_offsets={"typeEffectivenessOffset": 0x20},
        )
        rom = io.BytesIO(b"\x00" * 0x80)

        TypeEffectivenessPatch().apply(
            PatchContext(
                handle=rom,
                state=RomState(),
                logger=_RecordingLogger(),
                layout=layout,
            )
        )

        payload = rom.getvalue()
        chart = payload[0x20:0x20 + 49]
        self.assertEqual(payload[:0x20], b"\x00" * 0x20)
        self.assertEqual(payload[0x20 + 49:], b"\x00" * (0x80 - 0x20 - 49))
        self.assertEqual(len(chart), 49)
        self.assertTrue(set(chart).issubset(EFFECTIVENESS_VALUES))
        self.assertNotEqual(chart, b"\x00" * 49)

    def test_raw_offset_patch_uses_layout_patch_offset(self):
        layout = RomLayout(
            key="tiny-test",
            display_name="Tiny Test",
            serials=("TEST",),
            complete=True,
            blocks={},
            patch_offsets={"evoItemPatchOffset": 0x10},
        )
        rom = io.BytesIO(b"\xff" * 0x20)

        FixEvoItemsPatch().apply(
            PatchContext(
                handle=rom,
                state=RomState(),
                logger=_RecordingLogger(),
                layout=layout,
            )
        )

        payload = rom.getvalue()
        self.assertEqual(payload[:0x10], b"\xff" * 0x10)
        self.assertEqual(payload[0x10], 0)
        self.assertEqual(payload[0x11:], b"\xff" * 0x0F)

    def test_fix_evo_items_patch_uses_pal_layout_offset(self):
        handle = _RecordingHandle()

        FixEvoItemsPatch().apply(
            PatchContext(
                handle=handle,
                state=RomState(),
                logger=_RecordingLogger(),
                layout=PAL_DE_LAYOUT,
            )
        )

        self.assertEqual(
            handle.writes,
            [(PAL_DE_LAYOUT.patch_offsets["evoItemPatchOffset"], b"\x00")],
        )

    def test_ogremon_patch_uses_pal_layout_offsets(self):
        handle = _RecordingHandle()

        OgremonSoftlockPatch().apply(
            PatchContext(
                handle=handle,
                state=RomState(),
                logger=_RecordingLogger(),
                layout=PAL_DE_LAYOUT,
            )
        )

        self.assertEqual(
            handle.writes,
            [
                (0x1499BF6A, b"\xeb\x00"),
                (0x14A61626, b"\xeb\x00"),
            ],
        )

    def test_pp_patch_uses_pal_layout_offset_and_payload(self):
        handle = _RecordingHandle()

        PPCalculationPatch().apply(
            PatchContext(
                handle=handle,
                state=RomState(),
                logger=_RecordingLogger(),
                layout=PAL_DE_LAYOUT,
            )
        )

        self.assertEqual(
            handle.writes,
            [
                (
                    PAL_DE_LAYOUT.patch_offsets["rewritePPOffset"],
                    PAL_DE_PP_CALCULATION_PATCH_VALUE,
                ),
            ],
        )

    def test_spawn_rate_patch_uses_pal_layout_offsets_and_bucket_conversion(self):
        handle = _RecordingHandle()

        SpawnRatePatch().apply(
            PatchContext(
                handle=handle,
                state=RomState(),
                logger=_RecordingLogger(),
                value=42,
                layout=PAL_DE_LAYOUT,
            )
        )

        expected = []
        for offset in PAL_DE_LAYOUT.patch_offsets["spawnRateMamemonOffset"]:
            expected.append((offset, b"\x29"))
        for offset in PAL_DE_LAYOUT.patch_offsets["spawnRatePiximonOffset"]:
            expected.append((offset, b"\x29"))
        for offset in PAL_DE_LAYOUT.patch_offsets["spawnRateMMamemonOffset"]:
            expected.append((offset, b"\x29"))
        for offset in PAL_DE_LAYOUT.patch_offsets["spawnRateOtamamonOffset"]:
            expected.append((offset, b"\x01"))

        self.assertEqual(handle.writes, expected)

    def test_unlock_patch_uses_pal_layout_offsets(self):
        handle = _RecordingHandle()

        UnlockAreasPatch().apply(
            PatchContext(
                handle=handle,
                state=RomState(),
                logger=_RecordingLogger(),
                layout=PAL_DE_LAYOUT,
            )
        )

        self.assertEqual(
            handle.writes,
            [
                (0x149A2DE4, b"\xca\x04"),
                (0x149C7FC8, b"\x3c\x00"),
                (0x149C8164, b"\x3c\x00"),
                (0x149F4BC8, b"\x01\x00\x5d\x01"),
                (0x149F4C44, b"\x01\x00\x5d\x01"),
            ],
        )

    def test_movement_softlock_patch_uses_pal_layout_offsets(self):
        handle = _RecordingHandle()

        MovementSoftlockPatch().apply(
            PatchContext(
                handle=handle,
                state=RomState(),
                logger=_RecordingLogger(),
                layout=PAL_DE_LAYOUT,
            )
        )

        expected = []
        expected.extend(
            (offset, b"\x0d")
            for offset in PAL_DE_LAYOUT.patch_offsets["fixRotationSLOffset"]
        )
        expected.extend(
            (offset, bytes.fromhex("06 00 40 10"))
            for offset in PAL_DE_LAYOUT.patch_offsets["fixMoveToSLOffset"]
        )
        expected.extend(
            (offset, bytes.fromhex("31 fc a3 02"))
            for offset in PAL_DE_LAYOUT.patch_offsets["fixToyTownSLOffset"]
        )
        expected.extend(
            (offset, b"\x3b")
            for offset in PAL_DE_LAYOUT.patch_offsets["fixLeoCaveSLOffset"]
        )

        self.assertEqual(handle.writes, expected)

    def test_intro_hash_patch_uses_pal_layout_offset_and_pads_field(self):
        handle = _RecordingHandle()
        hash_value = "abcdef1234567890abcdef1234567890"

        IntroHashPatch().apply(
            PatchContext(
                handle=handle,
                state=RomState(),
                logger=_RecordingLogger(),
                value=hash_value,
                layout=PAL_DE_LAYOUT,
            )
        )

        expected_text = (
            hash_value[:16]
            + "\n"
            + hash_value[15:]
            + "   "
        )
        expected_payload = scrutil.encode(expected_text)
        field_size = PAL_DE_LAYOUT.patch_offsets["introHashSize"]

        self.assertEqual(
            handle.writes,
            [
                (
                    PAL_DE_LAYOUT.patch_offsets["introHashOffset"],
                    expected_payload + (b"\0" * (field_size - len(expected_payload))),
                ),
            ],
        )

    def test_intro_skip_patch_uses_pal_layout_offsets_and_destinations(self):
        handle = _RecordingHandle()

        IntroSkipPatch().apply(
            PatchContext(
                handle=handle,
                state=RomState(),
                logger=_RecordingLogger(),
                layout=PAL_DE_LAYOUT,
            )
        )

        self.assertEqual(
            handle.writes,
            [
                (
                    PAL_DE_LAYOUT.patch_offsets["introSkipOutsideOffset"],
                    scrutil.compile(
                        "jumpTo",
                        PAL_DE_LAYOUT.patch_offsets["introSkipOutsideDest"],
                    ),
                ),
                (
                    PAL_DE_LAYOUT.patch_offsets["introSkipInsideOffset"],
                    scrutil.compile(
                        "jumpTo",
                        PAL_DE_LAYOUT.patch_offsets["introSkipInsideDest"],
                    ),
                ),
            ],
        )

    def test_registry_returns_none_for_unknown_patch(self):
        self.assertIsNone(get_patch("not-a-real-patch"))
        self.assertIsNotNone(get_patch("fixEvoItems"))


if __name__ == "__main__":
    unittest.main()
