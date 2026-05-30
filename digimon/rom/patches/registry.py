"""Factory map of registry-key → :class:`Patch` Strategy instance.

The registry decouples the *name* used by callers (settings JSON, queued
patches on the handler) from the *implementation* — adding a new patch
means dropping in a new module and one line here, with no edits to a
switch statement.
"""

from __future__ import annotations

from typing import Mapping

from digimon.rom.patches.allow_drop import AllowDropPatch
from digimon.rom.patches.base import Patch
from digimon.rom.patches.dv_chip_descriptions import DVChipDescriptionsPatch
from digimon.rom.patches.evo_target_unify import EvoTargetUnifyPatch
from digimon.rom.patches.fix_evo_items import FixEvoItemsPatch
from digimon.rom.patches.gabumon import GabumonPatch
from digimon.rom.patches.giromon import GiromonPatch
from digimon.rom.patches.happy_vending import HappyVendingPatch
from digimon.rom.patches.intro_hash import IntroHashPatch
from digimon.rom.patches.intro_skip import IntroSkipPatch
from digimon.rom.patches.learn_chance import IncreaseLearnChancePatch
from digimon.rom.patches.learn_move_and_command import LearnMoveAndCommandPatch
from digimon.rom.patches.learn_tier_one import LearnTierOnePatch
from digimon.rom.patches.movement_softlock import MovementSoftlockPatch
from digimon.rom.patches.ogremon_softlock import OgremonSoftlockPatch
from digimon.rom.patches.pp import PPCalculationPatch
from digimon.rom.patches.reset_button import ResetButtonPatch
from digimon.rom.patches.spawn_rate import SpawnRatePatch
from digimon.rom.patches.type_effectiveness import TypeEffectivenessPatch
from digimon.rom.patches.unlock_areas import UnlockAreasPatch
from digimon.rom.patches.unrig_slots import UnrigSlotsPatch
from digimon.rom.patches.woah import WoahPatch


# Single source of truth: every opt-in patch the randomiser knows about.
PATCHES: Mapping[str, Patch] = {
    patch.name: patch
    for patch in (
        FixEvoItemsPatch(),
        AllowDropPatch(),
        WoahPatch(),
        LearnTierOnePatch(),
        IncreaseLearnChancePatch(),
        GabumonPatch(),
        GiromonPatch(),
        SpawnRatePatch(),
        IntroHashPatch(),
        IntroSkipPatch(),
        UnrigSlotsPatch(),
        PPCalculationPatch(),
        UnlockAreasPatch(),
        OgremonSoftlockPatch(),
        MovementSoftlockPatch(),
        TypeEffectivenessPatch(),
        LearnMoveAndCommandPatch(),
        DVChipDescriptionsPatch(),
        HappyVendingPatch(),
    )
}


# Patches that run on every write, regardless of settings. Order matters:
# the reset-button function lives inside the memory freed by the unify hack.
ALWAYS_ON_PATCHES: tuple[Patch, ...] = (
    EvoTargetUnifyPatch(),
    ResetButtonPatch(),
)


def get_patch(name: str) -> Patch | None:
    """Look up a registered patch by name, or ``None`` if unknown."""

    return PATCHES.get(name)
