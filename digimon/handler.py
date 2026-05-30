# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""ROM-state facade.

``DigimonWorldHandler`` is the long-standing entry point used by the
legacy ``digimon.randomizer`` module. Historically it was a 2,000-line
god class that owned reading, writing, randomising, patching, and the
in-memory state.

The refactor splits those concerns into dedicated subsystems:

* Reading / writing → :class:`digimon.rom.reader.RomReader` and
  :class:`digimon.rom.writer.RomWriter`.
* Patches → :mod:`digimon.rom.patches` (Strategy + Factory).
* Randomisation → :mod:`digimon.randomization` (Strategy + Pipeline).
* Domain enums → :mod:`digimon.rom.enums` and :mod:`data`.

This class is now a **facade**: it constructs the right collaborators,
holds onto the loaded ``RomState``, and re-exports the same public API
(``randomizeXxx``, ``applyPatch``, ``getXName``, …) that the legacy
``digimon.randomizer`` module and the test suite reach for.

New code should compose the subsystems directly (see
:mod:`digimon.app` for the modern entry point added in Phase 7).
"""

from __future__ import annotations

from typing import Any

import digimon.data as data
import digimon.patch_registry as patch_registry
import digimon.util as util
from digimon.models import Digimon, Item, Tech
from digimon.seeding import SeedingPolicy
from digimon.randomization import (
    ChestItemsRandomizer,
    DevimonStatGainOverride,
    DigimonDataRandomizer,
    EvolutionRequirementsRandomizer,
    EvolutionsRandomizer,
    MapItemsRandomizer,
    RandomizationContext,
    RecruitmentsRandomizer,
    SpecialEvolutionsRandomizer,
    StartersRandomizer,
    TechDataRandomizer,
    TechGiftsRandomizer,
    TokomonItemsRandomizer,
)
from digimon.rom.file import RomFile
from digimon.rom.reader import RomReader
from digimon.rom.writer import RomWriter
from log.logger import Logger


# Re-export for tests / external consumers that imported these off the
# handler module historically.
__all__ = ["DigimonWorldHandler", "Digimon", "Item", "Tech"]


# Specialty / type / range / effect "no name found" fallbacks.
_UNDEFINED_RANGE  = "UNDEF"
_UNDEFINED_EFFECT = "NONE"


class DigimonWorldHandler:
    """Loaded-ROM facade — reads on construction, writes on demand."""

    def __init__(self, filename: str, logger: Logger, seed: int | None = None) -> None:
        """Open ``filename`` and load every supported data block into memory."""

        self.randomizedRequirements = False
        self.logger = logger
        self.patches: list[tuple[str, Any]] = []

        self.randomseed = SeedingPolicy(verbose=logger.verbose).seed(seed)
        self.inFilename = filename

        try:
            rom_cm = RomFile.open_for_read(filename)
        except IOError:
            self.logger.fatalError(
                "Error: input file could not be read (it probably doesn't exist)\n"
                "Make sure the filename and relative path in settings.ini 'Input' "
                "are correct."
            )
            raise  # pragma: no cover — fatalError exits

        with rom_cm as rom:
            self._state = RomReader(self, logger).read(rom)

        # Backward-compat attribute aliases — preserve every public name the
        # randomisers, patches, and tests historically reach for.
        self.techData        = self._state.techData
        self.brainLearn      = self._state.brainLearn
        self.itemData        = self._state.itemData
        self.digimonData     = self._state.digimonData
        self.starterID       = self._state.starterID
        self.starterTech     = self._state.starterTech
        self.starterTechSlot = self._state.starterTechSlot
        self.recruitData     = self._state.recruitData
        self.specEvos        = self._state.specEvos
        self.chestItems      = self._state.chestItems
        self.mapItems        = self._state.mapItems
        self.tokoItems       = self._state.tokoItems
        self.techGifts       = self._state.techGifts
        self.trackNames      = self._state.trackNames

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def write(self, filename: str) -> None:
        """Serialise the current in-memory state back to ``filename``."""

        from shutil import copyfile

        # When writing to a different file, start from a copy of the source
        # ROM so the writer only needs to overwrite the changed regions.
        if self.inFilename != filename:
            copyfile(self.inFilename, filename)

        try:
            rom_cm = RomFile.open_for_update(filename)
        except IOError:
            self.logger.fatalError(
                "Error: output file could not be read (it probably doesn't exist)\n"
                "Make sure the filename and relative path in settings.ini 'Output' "
                "are correct."
            )
            raise  # pragma: no cover — fatalError exits

        with rom_cm as rom:
            self.logger.logChange(self.logger.getHeader("Apply Patches"))

            # patch_registry delegates to the Strategy-based pipeline,
            # which prepends the always-on EvoTargetUnify / ResetButton
            # patches in the legacy order.
            toy_town_workaround = patch_registry.applyPatches(self, rom.handle)

            # Synchronise any potentially-reassigned attribute back into
            # the state container before serialising. ``trackNames`` is
            # bytes (immutable) and may have been replaced by Giromon.
            self._state.trackNames = self.trackNames

            RomWriter(self.logger).write(rom, self._state, toy_town_workaround)

    # ------------------------------------------------------------------
    # Patch queue
    # ------------------------------------------------------------------
    def applyPatch(self, patch: str, val: int | str = 0) -> None:
        """Queue a named patch to be applied during :meth:`write`."""

        self.patches.append((patch, val))

    # ------------------------------------------------------------------
    # Randomiser delegates — each one builds a Strategy from arguments and
    # runs it against the shared ``RandomizationContext``.
    # ------------------------------------------------------------------

    def _make_context(self) -> RandomizationContext:
        return RandomizationContext(
            state=self._state,
            logger=self.logger,
            lookup=self,
            queue_patch=self.applyPatch,
        )

    def randomizeDigimonData(self, dropItem: bool = False, dropRate: bool = False,
                             price: int = 1000) -> None:
        DigimonDataRandomizer(drop_item=dropItem, drop_rate=dropRate, price=price) \
            .apply(self._make_context())

    def randomizeTechData(self, mode: str = "shuffle", power: bool = False,
                          cost: bool = False, accuracy: bool = False,
                          effect: bool = False, effectChance: bool = False) -> None:
        TechDataRandomizer(
            mode=mode, power=power, cost=cost, accuracy=accuracy,
            effect=effect, effect_chance=effectChance,
        ).apply(self._make_context())

    def randomizeStarters(self, useWeakestTech: bool = True,
                          forceDigimon: str = "Random",
                          allowedLevels: list[int] | None = None) -> None:
        StartersRandomizer(
            use_weakest_tech=useWeakestTech,
            force_digimon=forceDigimon,
            allowed_levels=allowedLevels,
        ).apply(self._make_context())

    def randomizeChestItems(self, allowEvo: bool = False) -> None:
        ChestItemsRandomizer(allow_evo=allowEvo).apply(self._make_context())

    def randomizeTokomonItems(self, consumableOnly: bool = True) -> None:
        TokomonItemsRandomizer(consumable_only=consumableOnly).apply(self._make_context())

    def randomizeMapSpawnItems(self, foodOnly: bool = False, price: int = 1000) -> None:
        MapItemsRandomizer(food_only=foodOnly, price=price).apply(self._make_context())

    def randomizeTechGifts(self) -> None:
        TechGiftsRandomizer().apply(self._make_context())

    def randomizeRecruitments(self) -> None:
        RecruitmentsRandomizer().apply(self._make_context())

    def randomizeEvolutions(self, obtainAll: bool = False) -> None:
        EvolutionsRandomizer(obtain_all=obtainAll).apply(self._make_context())

    def randomizeEvolutionRequirements(self) -> None:
        EvolutionRequirementsRandomizer().apply(self._make_context())

    def randomizeSpecialEvolutions(self) -> None:
        SpecialEvolutionsRandomizer().apply(self._make_context())

    def updateEvolutionStats(self) -> None:
        DevimonStatGainOverride().apply(self._make_context())

    # ------------------------------------------------------------------
    # Name / roster lookups (used by models, randomisers, patches, tests)
    # ------------------------------------------------------------------

    def getPlayableDigimonByLevel(self, level: int, excludeSpecials: bool = False) -> list[Digimon]:
        excluded_specials = {"Panjyamon", "Gigadramon", "MetalEtemon"}
        result: list[Digimon] = []
        for digi in self.digimonData:
            if digi.level == level and digi.id in digi.playableDigimon:
                if excludeSpecials and digi.name in excluded_specials:
                    continue
                result.append(digi)
        return result

    def getDigimonName(self, id: int) -> str:
        if id < len(self.digimonData):
            return self.digimonData[id].name
        return "---"

    def getDigimonByName(self, name: str) -> Digimon | None:
        return next((digi for digi in self.digimonData if digi.name == name), None)

    def getItemName(self, id: int) -> str:
        if id < len(self.itemData):
            return self.itemData[id].name
        return "None"

    def getTechName(self, id: int) -> str:
        return data.techs[id] if id < len(data.techs) else "None"

    def getTypeName(self, id: int) -> str:
        return util.typeIDToName(id)

    def getSpecialtyName(self, id: int) -> str:
        return util.specIDToName(id)

    def getLevelName(self, id: int) -> str:
        return util.levelIDToName(id)

    def getRangeName(self, id: int) -> str:
        return data.ranges.get(id, _UNDEFINED_RANGE)

    def getEffectName(self, id: int) -> str:
        return data.effects.get(id, _UNDEFINED_EFFECT)
