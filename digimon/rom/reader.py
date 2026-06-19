# Author: Christoph Merscher <dev@fmerscher.com>

"""Read every supported data block out of a Digimon World ROM image.

The reader is the only place that turns raw PSX bytes into the typed
in-memory ``RomState`` used elsewhere. Each ``_read_*`` helper handles
one section of the ROM so the top-level :meth:`RomReader.read` reads
top-to-bottom as a high-level checklist.
"""

from __future__ import annotations

import struct
from typing import BinaryIO

import digimon.data as data
from data.digimon import find_by_id
from digimon.models import Digimon, Item, ModelContext, Tech
from digimon.rom.file import RomFile
from digimon.rom.layouts import DataBlockLayout, NTSC_U_LAYOUT, RomLayout
from digimon.rom.script_layouts import ScriptLayout
from digimon.rom.state import RomState
from digimon.rom.struct_codec import (
    read_block_with_exclusions,
    unpack_array,
)
import script.util as scrutil


NAME_FIELD_SIZE = 20


def _name_bytes(name: str) -> bytes:
    return name.encode("ascii")[:NAME_FIELD_SIZE].ljust(NAME_FIELD_SIZE, b"\0")


class RomReader:
    """Populate a fresh :class:`RomState` from a ROM file image."""

    def __init__(
        self,
        lookup: ModelContext,
        logger,
        layout: RomLayout = NTSC_U_LAYOUT,
    ) -> None:
        self._lookup = lookup
        self._logger = logger
        self._layout = layout

    @property
    def _scripts(self) -> ScriptLayout:
        return self._layout.require_scripts()

    def _block(self, name: str) -> DataBlockLayout:
        return self._layout.require_block(name)

    def _read_block(self, handle: BinaryIO, name: str) -> bytes:
        block = self._block(name)
        return read_block_with_exclusions(
            handle,
            block.offset,
            block.size,
            block.exclusion_offsets,
            block.exclusion_size,
        )

    def _unpack_block(self, handle: BinaryIO, name: str) -> list[tuple]:
        block = self._block(name)
        if block.count is None:
            raise ValueError(f"{name!r} is a raw block and cannot be unpacked.")

        return unpack_array(self._read_block(handle, name), block.format, block.count)

    # ------------------------------------------------------------------
    def read(self, rom: RomFile) -> RomState:
        state = RomState()
        setattr(self._lookup, "_state", state)
        handle = rom.handle

        self._read_techs(handle, state)
        self._read_tech_tier_list(handle, state)
        self._read_tech_battle_learn(handle, state)
        self._read_tech_brain_learn(handle, state)
        self._read_items(handle, state)
        self._read_digimon(handle, state)
        self._read_evolutions(handle, state)
        self._read_evolution_stats(handle, state)
        self._read_evolution_requirements(handle, state)
        self._read_starters(handle, state)
        self._read_recruitments(rom, state)
        self._read_special_evolutions(handle, state)
        self._read_chest_items(handle, state)
        self._read_map_items(handle, state)
        self._read_tokomon_items(handle, state)
        self._read_tech_gifts(handle, state)
        self._read_jukebox_track_names(handle, state)

        return state

    # ------------------------------------------------------------------
    # Tech data
    # ------------------------------------------------------------------
    def _read_techs(self, handle: BinaryIO, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Tech Data"))

        records = self._unpack_block(handle, "techData")

        for i, record in enumerate(records):
            tech = Tech(self._lookup, i, record)
            tech.setName(data.techs[i])
            state.techData.append(tech)

    def _read_tech_tier_list(self, handle: BinaryIO, state: RomState) -> None:
        records = self._unpack_block(handle, "techTierList")

        # Each tier-list row is (id_at_slot_1, id_at_slot_2, …); the slot
        # index plus one is the tier value assigned to that tech.
        for record in records:
            for slot_index, tech_id in enumerate(record):
                state.techData[tech_id].tier = slot_index + 1

    def _read_tech_battle_learn(self, handle: BinaryIO, state: RomState) -> None:
        records = self._unpack_block(handle, "techLearn")

        for tech_id, record in enumerate(records):
            state.techData[tech_id].learnChance = list(record)

        for tech in state.techData:
            self._logger.log(str(tech))

    def _read_tech_brain_learn(self, handle: BinaryIO, state: RomState) -> None:
        records = self._unpack_block(handle, "techBrain")

        # Index = tier, value = per-specialty learn chance tuple.
        state.brainLearn = [list(record) for record in records]

        self._logger.log("Brain training learn chances:")
        for tier_index, learn_rate in enumerate(state.brainLearn):
            self._logger.log("Tier " + str(tier_index + 1) + ": " + str(learn_rate))

    # ------------------------------------------------------------------
    # Items
    # ------------------------------------------------------------------
    def _read_items(self, handle: BinaryIO, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Item Data"))

        records = self._unpack_block(handle, "itemData")

        for i, record in enumerate(records):
            item = Item(self._lookup, i, self._with_item_name(i, record))
            state.itemData.append(item)
            self._logger.log(str(item))

        # Override prices for the three high-tier evo items (matches legacy).
        state.itemData[125].price = 9999
        state.itemData[126].price = 5000
        state.itemData[127].price = 9999

    # ------------------------------------------------------------------
    # Digimon
    # ------------------------------------------------------------------
    def _read_digimon(self, handle: BinaryIO, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Digimon Data"))

        records = self._unpack_block(handle, "digimonData")

        for i, record in enumerate(records):
            digi = Digimon(self._lookup, i, self._with_digimon_name(i, record))
            state.digimonData.append(digi)
            self._logger.log(str(digi) + "\n")

    def _with_item_name(self, item_id: int, record: tuple) -> tuple:
        if isinstance(record[0], (bytes, bytearray)):
            return record

        return (_name_bytes("Item " + format(item_id, "02X")), *record)

    def _with_digimon_name(self, digimon_id: int, record: tuple) -> tuple:
        if isinstance(record[0], (bytes, bytearray)):
            return record

        known = find_by_id(digimon_id)
        name = known.display_name if known is not None else "Digimon " + format(digimon_id, "02X")
        return (_name_bytes(name), *record)

    # ------------------------------------------------------------------
    # Evolution tables
    # ------------------------------------------------------------------
    def _read_evolutions(self, handle: BinaryIO, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Evolution Data"))

        records = self._unpack_block(handle, "evoToFrom")

        # Player (ID 0) has no evo entries, so this block starts at id 1.
        for i, record in enumerate(records):
            state.digimonData[1 + i].setEvoData(record)
            self._logger.log(state.digimonData[1 + i].evoData() + "\n")

    def _read_evolution_stats(self, handle: BinaryIO, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Evolution Stat Gain Data"))

        records = self._unpack_block(handle, "evoStats")

        for i, record in enumerate(records):
            state.digimonData[i].setEvoStats(record)
            self._logger.log(state.digimonData[i].evoStatsToString() + "\n")

    def _read_evolution_requirements(self, handle: BinaryIO, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Evolution Requirements Data"))

        records = self._unpack_block(handle, "evoReqs")

        for i, record in enumerate(records):
            state.digimonData[i].setEvoReqs(record)
            self._logger.log(state.digimonData[i].evoReqsToString() + "\n")

    # ------------------------------------------------------------------
    # Starters
    # ------------------------------------------------------------------
    def _read_starters(self, handle: BinaryIO, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Starter Data"))

        from digimon.util import animIDTechSlot  # local import keeps phase boundary clear

        for i in (0, 1):
            handle.seek(self._scripts.starterSetDigimonOffset[i], 0)
            digimon_id = struct.unpack(data.digimonIDFormat, handle.read(1))[0]
            state.starterID.append(digimon_id)
            self._logger.log(state.digimonData[digimon_id].name)

            handle.seek(self._scripts.starterLearnTechOffset[i], 0)
            tech_id = struct.unpack(data.techIDFormat, handle.read(1))[0]
            state.starterTech.append(tech_id)
            self._logger.log("0x" + format(tech_id, "02x") + " = tech ID")

            handle.seek(self._scripts.starterEquipAnimOffset[i], 0)
            anim_id = struct.unpack(data.animIDFormat, handle.read(1))[0]
            slot = animIDTechSlot(anim_id)
            state.starterTechSlot.append(slot)
            self._logger.log("0x" + format(slot, "02x") + " = tech slot")

    # ------------------------------------------------------------------
    # Recruitments
    # ------------------------------------------------------------------
    def _read_recruitments(self, rom: RomFile, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Recruitment Data"))

        handle = rom.handle
        err = False
        for (
            trigger_offsets,
            name_offsets,
            trigger_byte,
            digimon_id,
        ) in self._recruitment_offsets(rom):
            verified_offsets = []
            for ofst in trigger_offsets:
                handle.seek(ofst, 0)
                value = struct.unpack(
                    self._scripts.recruitFormat,
                    handle.read(struct.calcsize(self._scripts.recruitFormat)),
                )[0]
                if value != trigger_byte:
                    self._logger.logError(
                        "Error: Looking for recruit trigger check, found incorrect value: "
                        + str(value) + " @ " + format(ofst, "08x")
                    )
                    err = True
                else:
                    verified_offsets.append(ofst)

            for name_ofst in name_offsets:
                handle.seek(name_ofst, 0)
                expected_name = scrutil.encode(state.digimonData[digimon_id].name)
                actual_name = handle.read(len(expected_name))

                if expected_name != actual_name:
                    self._logger.logError(
                        "Error: Looking for recruit" + state.digimonData[digimon_id].name
                        + ", found incorrect value: " + scrutil.decode(actual_name)
                        + " @ " + format(name_ofst, "08x")
                    )
                    err = True

            state.recruitData[trigger_byte] = (tuple(verified_offsets), digimon_id, name_offsets)

        if not err:
            self._logger.log("All recruitment check values verified.")

    def _recruitment_offsets(
        self,
        rom: RomFile,
    ) -> tuple[tuple[tuple[int, ...], tuple[int, ...], int, int], ...]:
        if not self._scripts.dynamicRecruitOffsets:
            return self._scripts.recruitOffsets

        if self._layout.key == "pal-de":
            from digimon.rom.recruitment_offsets import pal_de_recruit_offsets_from_rom

            return pal_de_recruit_offsets_from_rom(rom.path)

        return self._scripts.recruitOffsets

    # ------------------------------------------------------------------
    # Special evolutions
    # ------------------------------------------------------------------
    def _read_special_evolutions(self, handle: BinaryIO, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Special Evolution Data"))

        err = False
        for offsets, check_val, from_val in self._scripts.specEvoOffsets:
            for ofst in offsets:
                handle.seek(ofst, 0)
                actual = struct.unpack(
                    self._scripts.specEvoFormat,
                    handle.read(struct.calcsize(self._scripts.specEvoFormat)),
                )[0]
                if actual != check_val:
                    self._logger.logError(
                        "Error: Looking for spec evo, found incorrect value: "
                        + str(actual) + " @ " + format(ofst, "08x")
                    )
                    err = True

            state.specEvos[offsets] = (check_val, from_val)

        if not err:
            self._logger.log("All special evolutions verified.")

    # ------------------------------------------------------------------
    # Script-driven item placements
    # ------------------------------------------------------------------
    def _read_chest_items(self, handle: BinaryIO, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Chest Item Data"))

        for ofst in self._scripts.chestItemOffsets:
            handle.seek(ofst, 0)
            cmd, item_id = struct.unpack(
                self._scripts.chestItemFormat,
                handle.read(struct.calcsize(self._scripts.chestItemFormat)),
            )
            if cmd != scrutil.spawnChest:
                self._logger.logError(
                    "Error: Looking for chest item, found incorrect command: "
                    + str(cmd) + " @ " + format(ofst, "08x")
                )
            else:
                state.chestItems[ofst] = item_id

        for item_id in state.chestItems.values():
            self._logger.log("Chest contains: '" + state.itemData[item_id].name + "'")

    def _read_map_items(self, handle: BinaryIO, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Map Item Data"))

        for ofst in self._scripts.mapItemOffsets:
            handle.seek(ofst, 0)
            cmd, item_id = struct.unpack(
                self._scripts.mapItemFormat,
                handle.read(struct.calcsize(self._scripts.mapItemFormat)),
            )
            if cmd != scrutil.spawnItem:
                self._logger.logError(
                    "Error: Looking for map item, found incorrect command: "
                    + str(cmd) + " @ " + format(ofst, "08x")
                )
            else:
                self._logger.log(" '" + state.itemData[item_id].name + "' spawns on the map.")
                state.mapItems[ofst] = item_id

    def _read_tokomon_items(self, handle: BinaryIO, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Tokomon Item Data"))

        for ofst in self._scripts.tokoItemOffsets:
            handle.seek(ofst, 0)
            cmd, item_id, count = struct.unpack(
                self._scripts.tokoItemFormat,
                handle.read(struct.calcsize(self._scripts.tokoItemFormat)),
            )
            if cmd != scrutil.giveItem:
                self._logger.logError(
                    "Error: Looking for Tokomon item, found incorrect command: "
                    + str(cmd) + " @ " + format(ofst, "08x")
                )
            else:
                state.tokoItems[ofst] = (item_id, count)

        for item_id, count in state.tokoItems.values():
            self._logger.log(
                "Tokomon gives: " + str(count) + "x '"
                + state.itemData[item_id].name + "'"
            )

    def _read_tech_gifts(self, handle: BinaryIO, state: RomState) -> None:
        self._logger.log(self._logger.getHeader("Read Tech Gift Data"))

        for i, ofst in enumerate(self._scripts.learnMoveOffsets):
            handle.seek(ofst, 0)
            cmd, tech_id = struct.unpack(
                self._scripts.learnMoveFormat,
                handle.read(struct.calcsize(self._scripts.learnMoveFormat)),
            )
            if cmd != scrutil.learnMove:
                self._logger.logError(
                    "Error: Looking for tech learning gift, found incorrect command: "
                    + str(cmd) + " @ " + format(ofst, "08x")
                )
            else:
                state.techGifts[(ofst, self._scripts.checkMoveOffsets[i])] = tech_id

        for tech_id in state.techGifts.values():
            tech_name = state.techData[tech_id].name if tech_id < len(state.techData) else "None"
            self._logger.log("Tech gift: '" + tech_name + "'")

    # ------------------------------------------------------------------
    # Jukebox
    # ------------------------------------------------------------------
    def _read_jukebox_track_names(self, handle: BinaryIO, state: RomState) -> None:
        state.trackNames = self._read_block(handle, "trackName")
