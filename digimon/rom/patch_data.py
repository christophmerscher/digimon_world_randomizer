"""Byte-payload tables for every optional ROM patch.

These constants are consumed by the patch Strategy classes added in Phase 5
of the refactor. They are split out of the legacy `digimon.data` god module
so that the patch implementations can `from digimon.rom.patch_data import …`
when they land in `digimon/rom/patches/`.

Each block names the offset(s), struct format, and replacement value(s) of
a single patch. Patches that share a topic (e.g. softlock fixes) live in
the same section for readability.
"""


# ---------------------------------------------------------------------------
# Evo items — give stats and lifetime
# ---------------------------------------------------------------------------

evoItemPatchOffset = 0x14CF5AFC
evoItemPatchValue  = 0x00
evoitemPatchFormat = "<B"


# ---------------------------------------------------------------------------
# "Woah!" pickup text override
# ---------------------------------------------------------------------------

woahPatchOffset = 0x14D76EF4
woahPatchFormat = "<10s"


# ---------------------------------------------------------------------------
# Gabumon enemy stat boost
# ---------------------------------------------------------------------------

gabuPatchFormat = "<h"
gabuPatchWrites = (
    (0x0A7EEA8C, 0x7530),   # CurrentHP  30,000
    (0x0A7EEA8E, 0x7530),   # CurrentMP  30,000
    (0x0A7EEA90, 0x7530),   # MaxHP      30,000
    (0x0A7EEA92, 0x7530),   # MaxMP      30,000
    (0x0A7EEA94, 0x7D0 ),   # Offense    2,000
    (0x0A7EEA96, 0x7D0 ),   # Defense    2,000
    (0x0A7EEA98, 0x7D0 ),   # Speed      2,000
    (0x0A7EEA9A, 0x7D0 ),   # Brains     2,000
    (0x0A7EEA9C, 0x1   ),   # Bits       1
)


# ---------------------------------------------------------------------------
# Tier-1 tech learn chance from brain training
# ---------------------------------------------------------------------------

tierOneTechLearnOffset = 0x14C8E58C
tierOneTechLearnValue  = 0x28
tierOneTechLearnFormat = "<B"


# ---------------------------------------------------------------------------
# Intro hash injection (race verification)
# ---------------------------------------------------------------------------

introHashOffset = 0x140BD212


# ---------------------------------------------------------------------------
# Intro scene skip
# ---------------------------------------------------------------------------

introSkipOutsideDest   = 2306
introSkipOutsideOffset = 0x1407DA20   # just after "Welcome to Digimon World"

introSkipInsideDest    = 5108
introSkipInsideOffset  = 0x1407E44C   # just after "I invited you here\nto save us"


# ---------------------------------------------------------------------------
# Unrigged training slots
# ---------------------------------------------------------------------------

unrigSlotsFormat = "<I"
unrigSlotsValue  = 0x08023A1E   # little-endian instruction (reverse byte order)
unrigSlotsOffset = 0x14C8DB10   # TRN_REL.BIN

unrigSlots2Format = "<I"
unrigSlots2Value  = 0x08023494
unrigSlots2Offset = 0x14C941F8  # TRN_REL2.BIN


# ---------------------------------------------------------------------------
# PP calculation rewrite
# ---------------------------------------------------------------------------

rewritePPFormat = ">IIIIIIIIIII"   # big-endian — instructions are forwards
rewritePPValue  = (
    0x0F19040C, 0xFFFF6432, 0x1E004010, 0x00000000, 0x1380023C, 0xCECE4224,
    0x21105200, 0x00004290, 0x03004230, 0x21885100, 0x16000010,
)
rewritePPOffset = 0x14D2848C


# ---------------------------------------------------------------------------
# Movement / rotation softlock fixes
# ---------------------------------------------------------------------------

fixRotationSLFormat = "B"
fixRotationSLValue  = 0x0D
fixRotationSLOffset = (0x14CE72C0, 0x14CE7464)

fixMoveToSLFormat = "<I"
fixMoveToSLValue  = 0x10400006
fixMoveToSLOffset = (0x14CDB140, 0x14CDB19C)

fixToyTownSLFormat = ">I"
fixToyTownSLValue  = 0x31FCA302
fixToyTownSLOffset = (0x14049DD8, 0x1404A2EA)

fixLeoCaveSLFormat = "B"
fixLeoCaveSLValue  = 0x3B
fixLeoCaveSLOffset = (
    0x14030380, 0x14030444, 0x14030D36, 0x14030DFA,
    0x140317F6, 0x140318BA, 0x140321C8, 0x1403228C,
)


# ---------------------------------------------------------------------------
# Evo-target function unify hack (frees memory for the reset-button patch)
# ---------------------------------------------------------------------------

evoTargetUnifyHackFormat = "<I"
evoTargetUnifyHack = {
    0x14CD7520: 0x0C038AED,
    0x14D19A14: 0x24050003,
    0x14D19A20: 0x8FB00018,
    0x14D19A2C: 0x16050004,
}


# ---------------------------------------------------------------------------
# Reset-button combination / custom tick function
# ---------------------------------------------------------------------------

customTickFunctionFormat = "<9I"
customTickFunctionValue  = (
    0x8F8293B8, 0x200301F0, 0x00430824, 0x14230003,
    0x240A00A0, 0x01400008, 0x240900A0, 0x03E00008,
    0x00000000,
)
customTickFunctionOffset = 0x14D19A70

customTickHookFormat = "<I"
customTickHookValue  = 0x24E72F08
customTickHookOffset = 0x14D1A388


# ---------------------------------------------------------------------------
# Unlock type-locked areas (Greylord, Ice, Toy Town)
# ---------------------------------------------------------------------------

unlockTypeLockFormat = "<H"

unlockGreylordValue  = 1226
unlockGreylordOffset = (0x13FF808E,)

unlockIceValue  = 60
unlockIceOffset = (0x1401D130, 0x1401D2A8)

unlockToyTownFormat = "<I"
unlockToyTownValue  = 0x015D0001
unlockToyTownOffset = (0x140479EA,)


# ---------------------------------------------------------------------------
# Ogremon 2 / Nanimon softlock fix
# ---------------------------------------------------------------------------

ogremonSoftlockFormat = "<H"
ogremonSoftlockValue  = 235
ogremonSoftlockOffset = (0x13FD689A, 0x140B7A1A)


# ---------------------------------------------------------------------------
# Spawn rate overrides
# ---------------------------------------------------------------------------

spawnRateFormat         = "<B"
spawnRateMamemonOffset  = (0x13FD678F, 0x140B790F)
spawnRatePiximonOffset  = (0x13FD64DB, 0x13FDD389, 0x13FE0121, 0x140B765B)
spawnRateMMamemonOffset = (0x13FD831F, 0x140B949F)
spawnRateOtamamonOffset = (0x13FD7F47, 0x140B90C7)


# ---------------------------------------------------------------------------
# Type effectiveness
# ---------------------------------------------------------------------------

typeEffectivenessFormat = "B"
typeEffectivenessOffset = 0x14D669F8


# ---------------------------------------------------------------------------
# Learn move + command in same brain training session
# ---------------------------------------------------------------------------

learnMoveAndCommandFormat = "<II"
learnMoveAndCommandValue  = (0x10000065, 0x00001021)
learnMoveAndCommandOffset = 0x14C8821C


# ---------------------------------------------------------------------------
# DV Chip description text fixes
# ---------------------------------------------------------------------------

DVChipAValue  = "Boosts Off+Brains by 100"
DVChipAOffset = 0x14D65F10
DVChipAFormat = "<28s"

DVChipDValue  = "Boosts Def+Speed by 100"
DVChipDOffset = 0x14D65F2C
DVChipDFormat = "<28s"

DVChipEValue  = "Boosts HP+MP by 1000"
DVChipEOffset = 0x14D65F48
DVChipEFormat = "<28s"


# ---------------------------------------------------------------------------
# Dragon Eye Lake vending machine → HappyMushroom
# ---------------------------------------------------------------------------

happyMushroomVendingOffset1 = 0x13FE31C8
happyMushroomVendingFormat1 = "<124s"
happyMushroomVendingValue1  = "HappyMushroom: 2000 bits\r\0DigiMushroom: 600 bits\r\0Don「t buy\r\0"

happyMushroomVendingOffset2 = 0x13FE3300
happyMushroomVendingFormat2 = "<36s"
happyMushroomVendingValue2  = "\1\6HappyMushroom \1\1came out!\0\r\0\r\0\r"

happyMushroomVendingOffset3       = 0x13FE3252
happyMushroomVendingOffset4       = 0x13FE32F8
happyMushroomVendingPriceFormat   = "<H"
happyMushroomVendingPriceValue    = 2000

happyMushroomVendingOffset5 = (0x13FE3326, 0x13FE3338, 0x13FE3382)
happyMushroomVendingFormat5 = "B"
happyMushroomVendingValue5  = 69
