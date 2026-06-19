# Author: Christoph Merscher <dev@fmerscher.com>

"""Recruitment offset sources for layouts that cannot use a static table.

NTSC-U keeps a hand-verified table in :mod:`digimon.rom.script_offsets`.
German PAL has a translated scenario allocation where raw trigger values are
too noisy to promote wholesale, so the PAL source derives writable trigger
checks from the loaded ``SCN/DG2.SCN`` file and then lets the normal
reader/writer verify those offsets before randomisation.
"""

from __future__ import annotations

from pathlib import Path

from digimon.rom import script_offsets
from digimon.rom.pal_de_scenarios import PAL_DE_RECRUITMENT_SCENARIO_PATH
from digimon.rom.scenario import RawCdImage, ScenarioFile


def pal_de_recruit_offsets_from_rom(
    rom_path: str | Path,
) -> tuple[tuple[tuple[int, ...], tuple[int, ...], int, int], ...]:
    """Build the PAL-DE recruitment table from the active scenario file."""

    scenario = RawCdImage(rom_path).read_scenario(PAL_DE_RECRUITMENT_SCENARIO_PATH)
    return pal_de_recruit_offsets_from_scenario(scenario)


def pal_de_recruit_offsets_from_scenario(
    scenario: ScenarioFile,
) -> tuple[tuple[tuple[int, ...], tuple[int, ...], int, int], ...]:
    """Return PAL-DE recruitment trigger offsets using the verified scan rule.

    The writable PAL trigger checks are the third 16-bit operand of script
    command ``0x19``. We promote that canonical slot only for triggers whose
    NTSC record has writable trigger offsets; NTSC records with intentionally
    empty trigger tables stay empty on PAL too.

    PAL name anchors remain intentionally empty. The German script contains
    translated duplicate dialogue and status/list text, so gameplay shuffling
    is enabled without rewriting localized names until those anchors are
    separately classified.
    """

    records: list[tuple[tuple[int, ...], tuple[int, ...], int, int]] = []

    for ntsc_trigger_offsets, _ntsc_name_offsets, trigger, digimon_id in (
        script_offsets.recruitOffsets
    ):
        trigger_offsets: tuple[int, ...] = ()
        if ntsc_trigger_offsets:
            trigger_offsets = _pal_de_status_check_offsets(scenario, trigger)

        records.append((trigger_offsets, (), trigger, digimon_id))

    return tuple(records)


def _pal_de_status_check_offsets(scenario: ScenarioFile, trigger: int) -> tuple[int, ...]:
    data = scenario.data
    encoded_trigger = trigger.to_bytes(2, "little")
    offsets: list[int] = []

    for relative in range(4, len(data) - 1, 2):
        if data[relative:relative + 2] != encoded_trigger:
            continue
        if data[relative - 4:relative - 2] != b"\x19\x00":
            continue

        offsets.append(scenario.absolute_offset(relative))

    return tuple(offsets)
