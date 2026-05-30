"""Write a :class:`RomState` back into a Digimon World ROM image.

The writer is the inverse of :class:`~digimon.rom.reader.RomReader`. Each
``_write_*`` helper handles one block; their order matches the legacy
:meth:`DigimonWorldHandler.write` exactly so that any patches that depend
on data-block layout sequencing keep their original effect.
"""

from __future__ import annotations

import struct
from typing import BinaryIO

import digimon.data as data
from digimon.rom import blocks, script_offsets
from digimon.rom.file import RomFile
from digimon.rom.state import RomState
from digimon.rom.struct_codec import (
    pack_array,
    write_block_with_exclusions,
    write_value,
)
import script.util as scrutil


# Address of one of the Monzaemon/Toy Town spec-evo writes that has to be
# skipped when the "unlock areas" patch is applied.
_TOY_TOWN_SKIP_OFFSET = 0x140479ED


class RomWriter:
    """Serialise an in-memory :class:`RomState` back into the ROM image."""

    def __init__(self, logger) -> None:
        self._logger = logger

    # ------------------------------------------------------------------
    def write(self, rom: RomFile, state: RomState, toy_town_workaround: bool) -> None:
        handle = rom.handle

        self._write_tech_data(handle, state)
        self._write_tech_learn_chances(handle, state)
        self._write_digimon_data(handle, state)
        self._write_evolutions(handle, state)
        self._write_evolution_stats(handle, state)
        self._write_evolution_requirements(handle, state)
        self._write_item_data(handle, state)
        self._write_starters(handle, state)
        self._write_recruitments(handle, state)
        self._write_special_evolutions(handle, state, toy_town_workaround)
        self._write_chest_items(handle, state)
        self._write_map_items(handle, state)
        self._write_tokomon_items(handle, state)
        self._write_tech_gifts(handle, state)
        self._write_jukebox_track_names(handle, state)

    # ------------------------------------------------------------------
    # Tech data
    # ------------------------------------------------------------------
    def _write_tech_data(self, handle: BinaryIO, state: RomState) -> None:
        records = [tech.unpackedFormat() for tech in state.techData]
        packed = pack_array(records, blocks.techDataFormat)
        write_block_with_exclusions(
            handle, packed,
            blocks.techDataBlockOffset, blocks.techDataBlockSize,
            blocks.techDataExclusionOffsets, blocks.techDataExclusionSize,
        )

    def _write_tech_learn_chances(self, handle: BinaryIO, state: RomState) -> None:
        battle_records = [
            tech.unpackedLearnFormat()
            for tech in state.techData
            if tech.isLearnable
        ]
        packed = pack_array(battle_records, blocks.techLearnFormat)
        write_block_with_exclusions(
            handle, packed,
            blocks.techLearnBlockOffset, blocks.techLearnBlockSize,
            blocks.techLearnExclusionOffsets, blocks.techLearnExclusionSize,
        )

        brain_records = [tuple(chances) for chances in state.brainLearn]
        packed = pack_array(brain_records, blocks.techBrainFormat)
        write_block_with_exclusions(
            handle, packed,
            blocks.techBrainBlockOffset, blocks.techBrainBlockSize,
            blocks.techBrainExclusionOffsets, blocks.techBrainExclusionSize,
        )

    # ------------------------------------------------------------------
    # Digimon data
    # ------------------------------------------------------------------
    def _write_digimon_data(self, handle: BinaryIO, state: RomState) -> None:
        records = [digi.unpackedFormat() for digi in state.digimonData]
        packed = pack_array(records, blocks.digimonDataFormat)
        write_block_with_exclusions(
            handle, packed,
            blocks.digimonDataBlockOffset, blocks.digimonDataBlockSize,
            blocks.digimonDataExclusionOffsets, blocks.digimonDataExclusionSize,
        )

    # ------------------------------------------------------------------
    # Evolution tables
    # ------------------------------------------------------------------
    def _write_evolutions(self, handle: BinaryIO, state: RomState) -> None:
        partners = range(1, data.lastPartnerDigimon - 2)
        records = [
            digi.unpackedEvoFormat()
            for i, digi in enumerate(state.digimonData)
            if i in partners
        ]
        packed = pack_array(records, blocks.evoToFromFormat)
        write_block_with_exclusions(
            handle, packed,
            blocks.evoToFromBlockOffset, blocks.evoToFromBlockSize,
            blocks.evoToFromExclusionOffsets, blocks.evoToFromExclusionSize,
        )

    def _write_evolution_stats(self, handle: BinaryIO, state: RomState) -> None:
        partners = range(0, data.lastPartnerDigimon + 1)
        records = [
            digi.unpackedEvoStatsFormat()
            for i, digi in enumerate(state.digimonData)
            if i in partners
        ]
        packed = pack_array(records, blocks.evoStatsFormat)
        write_block_with_exclusions(
            handle, packed,
            blocks.evoStatsBlockOffset, blocks.evoStatsBlockSize,
            blocks.evoStatsExclusionOffsets, blocks.evoStatsExclusionSize,
        )

    def _write_evolution_requirements(self, handle: BinaryIO, state: RomState) -> None:
        partners = range(0, data.lastPartnerDigimon - 2)
        records = [
            digi.unpackedEvoReqFormat()
            for i, digi in enumerate(state.digimonData)
            if i in partners
        ]
        packed = pack_array(records, blocks.evoReqsFormat)
        write_block_with_exclusions(
            handle, packed,
            blocks.evoReqsBlockOffset, blocks.evoReqsBlockSize,
            blocks.evoReqsExclusionOffsets, blocks.evoReqsExclusionSize,
        )

    # ------------------------------------------------------------------
    # Items
    # ------------------------------------------------------------------
    def _write_item_data(self, handle: BinaryIO, state: RomState) -> None:
        records = [item.unpackedFormat() for item in state.itemData]
        packed = pack_array(records, blocks.itemDataFormat)
        write_block_with_exclusions(
            handle, packed,
            blocks.itemDataBlockOffset, blocks.itemDataBlockSize,
            blocks.itemDataExclusionOffsets, blocks.itemDataExclusionSize,
        )

    # ------------------------------------------------------------------
    # Starters
    # ------------------------------------------------------------------
    def _write_starters(self, handle: BinaryIO, state: RomState) -> None:
        from digimon.util import techSlotAnimID  # local import keeps phase boundary clear

        for i in (0, 1):
            # Starter digimon ID
            write_value(handle, script_offsets.starterSetDigimonOffset[i],
                        struct.pack(data.digimonIDFormat, state.starterID[i]))

            # The check that matches the starter when learning its first tech
            write_value(handle, script_offsets.starterChkDigimonOffset[i],
                        struct.pack(data.digimonIDFormat, state.starterID[i]))

            # Tech ID
            write_value(handle, script_offsets.starterLearnTechOffset[i],
                        struct.pack(data.techIDFormat, state.starterTech[i]))

            # Animation slot for the first tech
            write_value(handle, script_offsets.starterEquipAnimOffset[i],
                        struct.pack(data.animIDFormat, techSlotAnimID(state.starterTechSlot[i])))

        # The starting-stats check matches the first starter only.
        write_value(handle, script_offsets.starterStatChkDigimonOffset,
                    struct.pack(data.digimonIDFormat, state.starterID[0]))

    # ------------------------------------------------------------------
    # Recruitments
    # ------------------------------------------------------------------
    def _write_recruitments(self, handle: BinaryIO, state: RomState) -> None:
        for trigger in state.recruitData:
            verified_offsets, digimon_id, name_offsets = state.recruitData[trigger]

            for ofst in verified_offsets:
                write_value(handle, ofst, struct.pack(script_offsets.recruitFormat, trigger))

            current_name = state.digimonData[trigger - 200].name
            name_to_write = state.digimonData[digimon_id].name[:len(current_name)]

            for name_ofst in name_offsets:
                write_value(handle, name_ofst, scrutil.encode(name_to_write))

    # ------------------------------------------------------------------
    # Special evolutions
    # ------------------------------------------------------------------
    def _write_special_evolutions(self, handle: BinaryIO, state: RomState,
                                  toy_town_workaround: bool) -> None:
        for offsets in state.specEvos:
            target_id = state.specEvos[offsets][0]
            for ofst in offsets:
                if ofst == _TOY_TOWN_SKIP_OFFSET and toy_town_workaround:
                    continue
                write_value(handle, ofst,
                            struct.pack(script_offsets.specEvoFormat, target_id))

    # ------------------------------------------------------------------
    # Script-driven item placements
    # ------------------------------------------------------------------
    def _write_chest_items(self, handle: BinaryIO, state: RomState) -> None:
        for ofst, item_id in state.chestItems.items():
            write_value(handle, ofst,
                        struct.pack(script_offsets.chestItemFormat, scrutil.spawnChest, item_id))

    def _write_map_items(self, handle: BinaryIO, state: RomState) -> None:
        for ofst, item_id in state.mapItems.items():
            write_value(handle, ofst,
                        struct.pack(script_offsets.mapItemFormat, scrutil.spawnItem, item_id))

    def _write_tokomon_items(self, handle: BinaryIO, state: RomState) -> None:
        for ofst, (item_id, count) in state.tokoItems.items():
            write_value(handle, ofst,
                        struct.pack(script_offsets.tokoItemFormat, scrutil.giveItem, item_id, count))

    def _write_tech_gifts(self, handle: BinaryIO, state: RomState) -> None:
        for (learn_ofst, check_ofst), tech_id in state.techGifts.items():
            write_value(handle, learn_ofst,
                        struct.pack(script_offsets.learnMoveFormat, scrutil.learnMove, tech_id))
            write_value(handle, check_ofst,
                        struct.pack(script_offsets.checkMoveFormat, tech_id))

    # ------------------------------------------------------------------
    # Jukebox
    # ------------------------------------------------------------------
    def _write_jukebox_track_names(self, handle: BinaryIO, state: RomState) -> None:
        write_block_with_exclusions(
            handle, state.trackNames,
            blocks.trackNameBlockOffset, blocks.trackNameBlockSize,
            blocks.trackNameExclusionOffsets, blocks.trackNameExclusionSize,
        )
