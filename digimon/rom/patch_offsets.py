# Author: Christoph Merscher <dev@fmerscher.com>

"""Region-owned raw offsets for optional ROM patches.

Patch Strategy classes know *what* they write; layouts own *where* those
writes are safe for a concrete disc build. Keeping these maps here keeps the
large block/layout descriptors focused on data tables and makes PAL offset
promotion an explicit, reviewable step.
"""

from __future__ import annotations

from typing import Any

import script.util as scrutil
from digimon.rom import patch_data


NTSC_U_PATCH_OFFSETS: dict[str, Any] = {
    "evoItemPatchOffset": patch_data.evoItemPatchOffset,
    "woahPatchOffset": patch_data.woahPatchOffset,
    "gabuPatchWrites": patch_data.gabuPatchWrites,
    "introHashOffset": patch_data.introHashOffset,
    "introSkipOutsideOffset": patch_data.introSkipOutsideOffset,
    "introSkipOutsideDest": patch_data.introSkipOutsideDest,
    "introSkipInsideOffset": patch_data.introSkipInsideOffset,
    "introSkipInsideDest": patch_data.introSkipInsideDest,
    "unrigSlotsOffset": patch_data.unrigSlotsOffset,
    "unrigSlots2Offset": patch_data.unrigSlots2Offset,
    "rewritePPOffset": patch_data.rewritePPOffset,
    "rewritePPValue": patch_data.rewritePPValue,
    "fixRotationSLOffset": patch_data.fixRotationSLOffset,
    "fixMoveToSLOffset": patch_data.fixMoveToSLOffset,
    "fixToyTownSLOffset": patch_data.fixToyTownSLOffset,
    "fixLeoCaveSLOffset": patch_data.fixLeoCaveSLOffset,
    "evoTargetUnifyHack": patch_data.evoTargetUnifyHack,
    "customTickFunctionOffset": patch_data.customTickFunctionOffset,
    "customTickHookOffset": patch_data.customTickHookOffset,
    "unlockGreylordOffset": patch_data.unlockGreylordOffset,
    "unlockIceOffset": patch_data.unlockIceOffset,
    "unlockToyTownOffset": patch_data.unlockToyTownOffset,
    "ogremonSoftlockOffset": patch_data.ogremonSoftlockOffset,
    "spawnRateMamemonOffset": patch_data.spawnRateMamemonOffset,
    "spawnRatePiximonOffset": patch_data.spawnRatePiximonOffset,
    "spawnRateMMamemonOffset": patch_data.spawnRateMMamemonOffset,
    "spawnRateOtamamonOffset": patch_data.spawnRateOtamamonOffset,
    "typeEffectivenessOffset": patch_data.typeEffectivenessOffset,
    "learnMoveAndCommandOffset": patch_data.learnMoveAndCommandOffset,
    "DVChipAOffset": patch_data.DVChipAOffset,
    "DVChipDOffset": patch_data.DVChipDOffset,
    "DVChipEOffset": patch_data.DVChipEOffset,
    "happyMushroomVendingOffset1": patch_data.happyMushroomVendingOffset1,
    "happyMushroomVendingOffset2": patch_data.happyMushroomVendingOffset2,
    "happyMushroomVendingOffset3": patch_data.happyMushroomVendingOffset3,
    "happyMushroomVendingOffset4": patch_data.happyMushroomVendingOffset4,
    "happyMushroomVendingOffset5": patch_data.happyMushroomVendingOffset5,
}


PAL_DE_FIX_EVO_ITEMS_OFFSET = 0x1573041C
PAL_DE_OGREMON_SOFTLOCK_OFFSETS = (0x1499BF6A, 0x14A61626)
PAL_DE_TYPE_EFFECTIVENESS_OFFSET = 0x157A1318
PAL_DE_UNRIG_SLOTS_OFFSET = 0x177004
PAL_DE_UNRIG_SLOTS2_OFFSET = 0x16D9D4
PAL_DE_ROTATION_SOFTLOCK_OFFSETS = (0x15721F70, 0x15722148)
PAL_DE_MOVE_TO_SOFTLOCK_OFFSETS = (0x15715B20,)
PAL_DE_TOY_TOWN_SOFTLOCK_OFFSETS = (0x149F4A74, 0x149F4D78)
PAL_DE_LEOMON_CAVE_SOFTLOCK_OFFSETS = (
    0x149DC436,
    0x149DC4D8,
    0x149DCDE0,
    0x149DCE82,
    0x149DD8D4,
    0x149DD976,
    0x149DE268,
    0x149DE30A,
)
PAL_DE_INTRO_HASH_OFFSET = 0x14A2C080
PAL_DE_INTRO_HASH_SIZE = 0x60
PAL_DE_INTRO_SKIP_OUTSIDE_OFFSET = 0x14A2CE1A
PAL_DE_INTRO_SKIP_OUTSIDE_DEST = 0x03FE
PAL_DE_INTRO_SKIP_INSIDE_OFFSET = 0x14A2C0E2
PAL_DE_INTRO_SKIP_INSIDE_DEST = 0x0FF8
PAL_DE_SPAWN_RATE_MAMEMON_OFFSETS = (0x149815AF,)
PAL_DE_SPAWN_RATE_PIXIMON_OFFSETS = (
    0x149812FB,
    0x149841B1,
    0x149841BB,
    0x1498AF41,
)
PAL_DE_SPAWN_RATE_METALMAMEMON_OFFSETS = (0x1498313F, 0x1498479D)
PAL_DE_SPAWN_RATE_OTAMAMON_OFFSETS = (0x14982D67,)
PAL_DE_REWRITE_PP_OFFSET = 0x15762DAC
PAL_DE_REWRITE_PP_VALUE = (
    0x0F19040C,
    0xFFFF6432,
    0x1E004010,
    0x00000000,
    0x1480023C,
    0x144B4224,
    0x21105200,
    0x00004290,
    0x03004230,
    0x21885100,
    0x16000010,
)
PAL_DE_UNLOCK_GREYLORD_OFFSET = (0x149A2DE4,)
PAL_DE_UNLOCK_ICE_OFFSETS = (0x149C7FC8, 0x149C8164)
PAL_DE_UNLOCK_TOY_TOWN_OFFSETS = (0x149F4BC8, 0x149F4C44)
PAL_DE_HAPPY_VENDING_OFFSET1 = (0x147C7368, 0x147C7CEC)
PAL_DE_HAPPY_VENDING_OFFSET2 = (0x147C74A0, 0x147C7E24)
PAL_DE_HAPPY_VENDING_OFFSET3 = (0x147C73F2, 0x147C7D76)
PAL_DE_HAPPY_VENDING_OFFSET4 = (0x147C7498, 0x147C7E1C)
PAL_DE_HAPPY_VENDING_OFFSET5 = (
    0x147C74C6,
    0x147C74D8,
    0x147C7522,
    0x147C7E4A,
    0x147C7E5C,
    0x147C7EA6,
)
PAL_DE_HAPPY_VENDING_PAYLOAD1 = (
    scrutil.encode("HappyMushroom 2000 bits\n")
    + scrutil.encode("DigiMushrooms six hund bits\n")
    + scrutil.encode("Dont buy\n")
)
PAL_DE_HAPPY_VENDING_FORMAT1 = "<124s"
PAL_DE_HAPPY_VENDING_PAYLOAD2 = (
    b"\x01\x06"
    + scrutil.encode("Happy")
    + b"\x01\x01"
    + scrutil.encode(" came out")
    + bytes.fromhex("81 49")
    + scrutil.encode("\n")
)
PAL_DE_HAPPY_VENDING_FORMAT2 = "<36s"
PAL_DE_DV_CHIP_A_OFFSET = 0x157A03D4
PAL_DE_DV_CHIP_D_OFFSET = 0x157A0414
PAL_DE_DV_CHIP_E_OFFSET = 0x157A0448
PAL_DE_GABU_PATCH_WRITES = patch_data.gabuPatchWrites
PAL_DE_LEARN_MOVE_AND_COMMAND_OFFSET = 0x1717B4
PAL_DE_EVO_TARGET_UNIFY_HACK = {
    0x1575CE94: 0x24050003,
    0x1575CEA0: 0x8FB00018,
    0x1575CEAC: 0x16050004,
}
PAL_DE_CUSTOM_TICK_FUNCTION_OFFSET = 0x1575CEF0
PAL_DE_CUSTOM_TICK_HOOK_OFFSET = 0x1576E244
PAL_DE_WOAH_OFFSETS = (
    0x14845392,
    0x14846882,
    0x14854BBA,
    0x1485714E,
    0x14857ACA,
)
PAL_DE_WOAH_FORMAT = "<8s"
PAL_DE_WOAH_PAYLOAD = scrutil.encode("Oha") + bytes.fromhex("81 49")
PAL_DE_DV_CHIP_A_FORMAT = "<60s"
PAL_DE_DV_CHIP_D_FORMAT = "<48s"
PAL_DE_DV_CHIP_E_FORMAT = "<60s"
PAL_DE_PLUS = bytes.fromhex("81 7b")
PAL_DE_EXCLAMATION = bytes.fromhex("81 49")
PAL_DE_DV_CHIP_A_PAYLOAD = (
    scrutil.encode("Angriff")
    + PAL_DE_PLUS
    + scrutil.encode("IQ ")
    + PAL_DE_PLUS
    + scrutil.encode("100")
    + PAL_DE_EXCLAMATION
)
PAL_DE_DV_CHIP_D_PAYLOAD = (
    scrutil.encode("Abwehr")
    + PAL_DE_PLUS
    + scrutil.encode("Tempo ")
    + PAL_DE_PLUS
    + scrutil.encode("100")
    + PAL_DE_EXCLAMATION
)
PAL_DE_DV_CHIP_E_PAYLOAD = (
    scrutil.encode("LE")
    + PAL_DE_PLUS
    + scrutil.encode("MP ")
    + PAL_DE_PLUS
    + scrutil.encode("1000")
    + PAL_DE_EXCLAMATION
)

PAL_DE_PATCH_OFFSETS: dict[str, Any] = {
    "evoItemPatchOffset": PAL_DE_FIX_EVO_ITEMS_OFFSET,
    "introHashOffset": PAL_DE_INTRO_HASH_OFFSET,
    "introHashSize": PAL_DE_INTRO_HASH_SIZE,
    "introSkipOutsideOffset": PAL_DE_INTRO_SKIP_OUTSIDE_OFFSET,
    "introSkipOutsideDest": PAL_DE_INTRO_SKIP_OUTSIDE_DEST,
    "introSkipInsideOffset": PAL_DE_INTRO_SKIP_INSIDE_OFFSET,
    "introSkipInsideDest": PAL_DE_INTRO_SKIP_INSIDE_DEST,
    "spawnRateMamemonOffset": PAL_DE_SPAWN_RATE_MAMEMON_OFFSETS,
    "spawnRatePiximonOffset": PAL_DE_SPAWN_RATE_PIXIMON_OFFSETS,
    "spawnRateMMamemonOffset": PAL_DE_SPAWN_RATE_METALMAMEMON_OFFSETS,
    "spawnRateOtamamonOffset": PAL_DE_SPAWN_RATE_OTAMAMON_OFFSETS,
    "ogremonSoftlockOffset": PAL_DE_OGREMON_SOFTLOCK_OFFSETS,
    "typeEffectivenessOffset": PAL_DE_TYPE_EFFECTIVENESS_OFFSET,
    "unrigSlotsOffset": PAL_DE_UNRIG_SLOTS_OFFSET,
    "unrigSlots2Offset": PAL_DE_UNRIG_SLOTS2_OFFSET,
    "fixRotationSLOffset": PAL_DE_ROTATION_SOFTLOCK_OFFSETS,
    "fixMoveToSLOffset": PAL_DE_MOVE_TO_SOFTLOCK_OFFSETS,
    "fixToyTownSLOffset": PAL_DE_TOY_TOWN_SOFTLOCK_OFFSETS,
    "fixLeoCaveSLOffset": PAL_DE_LEOMON_CAVE_SOFTLOCK_OFFSETS,
    "rewritePPOffset": PAL_DE_REWRITE_PP_OFFSET,
    "rewritePPValue": PAL_DE_REWRITE_PP_VALUE,
    "unlockGreylordOffset": PAL_DE_UNLOCK_GREYLORD_OFFSET,
    "unlockIceOffset": PAL_DE_UNLOCK_ICE_OFFSETS,
    "unlockToyTownOffset": PAL_DE_UNLOCK_TOY_TOWN_OFFSETS,
    "happyMushroomVendingOffset1": PAL_DE_HAPPY_VENDING_OFFSET1,
    "happyMushroomVendingOffset2": PAL_DE_HAPPY_VENDING_OFFSET2,
    "happyMushroomVendingOffset3": PAL_DE_HAPPY_VENDING_OFFSET3,
    "happyMushroomVendingOffset4": PAL_DE_HAPPY_VENDING_OFFSET4,
    "happyMushroomVendingOffset5": PAL_DE_HAPPY_VENDING_OFFSET5,
    "happyMushroomVendingFormat1": PAL_DE_HAPPY_VENDING_FORMAT1,
    "happyMushroomVendingFormat2": PAL_DE_HAPPY_VENDING_FORMAT2,
    "happyMushroomVendingPayload1": PAL_DE_HAPPY_VENDING_PAYLOAD1,
    "happyMushroomVendingPayload2": PAL_DE_HAPPY_VENDING_PAYLOAD2,
    "DVChipAOffset": PAL_DE_DV_CHIP_A_OFFSET,
    "DVChipDOffset": PAL_DE_DV_CHIP_D_OFFSET,
    "DVChipEOffset": PAL_DE_DV_CHIP_E_OFFSET,
    "DVChipAFormat": PAL_DE_DV_CHIP_A_FORMAT,
    "DVChipDFormat": PAL_DE_DV_CHIP_D_FORMAT,
    "DVChipEFormat": PAL_DE_DV_CHIP_E_FORMAT,
    "DVChipAPayload": PAL_DE_DV_CHIP_A_PAYLOAD,
    "DVChipDPayload": PAL_DE_DV_CHIP_D_PAYLOAD,
    "DVChipEPayload": PAL_DE_DV_CHIP_E_PAYLOAD,
    "gabuPatchWrites": PAL_DE_GABU_PATCH_WRITES,
    "learnMoveAndCommandOffset": PAL_DE_LEARN_MOVE_AND_COMMAND_OFFSET,
    "evoTargetUnifyHack": PAL_DE_EVO_TARGET_UNIFY_HACK,
    "customTickFunctionOffset": PAL_DE_CUSTOM_TICK_FUNCTION_OFFSET,
    "customTickHookOffset": PAL_DE_CUSTOM_TICK_HOOK_OFFSET,
    "woahPatchOffset": PAL_DE_WOAH_OFFSETS,
    "woahPatchFormat": PAL_DE_WOAH_FORMAT,
    "woahPatchPayload": PAL_DE_WOAH_PAYLOAD,
}
