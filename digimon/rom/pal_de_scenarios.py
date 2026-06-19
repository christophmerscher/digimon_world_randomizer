# Author: Christoph Merscher <dev@fmerscher.com>

"""German PAL scenario-bank metadata and loaders.

The German disc carries five ``SCN/DG*.SCN`` allocations. Earlier PAL work
proved recruitment, chest, and map-item writes in ``DG2`` only; optional raw
patches need a wider bank model because several NTSC-relative script leads
land in other banks or in scenario allocation padding.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from digimon.rom.scenario import RawCdImage, ScenarioFile


@dataclass(frozen=True)
class PalDeScenarioBank:
    """Expected ISO and scenario-table metadata for one PAL-DE DG bank."""

    path: str
    lba: int
    raw_offset: int
    reported_size: int
    allocation_size: int
    pointer_count: int
    first_pointer: int
    last_pointer: int
    note: str = ""

    @property
    def reported_end(self) -> int:
        """Absolute raw offset immediately after the reported SCN payload."""

        return self.raw_offset + self.reported_size

    @property
    def allocation_end(self) -> int:
        """Absolute raw offset immediately after the allocated SCN bytes."""

        return self.raw_offset + self.allocation_size

    def contains_reported_offset(self, absolute_offset: int) -> bool:
        """Return whether ``absolute_offset`` is inside the reported SCN file."""

        return self.raw_offset <= absolute_offset < self.reported_end

    def contains_allocated_offset(self, absolute_offset: int) -> bool:
        """Return whether ``absolute_offset`` is inside this bank allocation."""

        return self.raw_offset <= absolute_offset < self.allocation_end


PAL_DE_SCENARIO_BANKS = (
    PalDeScenarioBank(
        path="SCN/DG0.SCN",
        lba=146107,
        raw_offset=0x147B9628,
        reported_size=0xC4000,
        allocation_size=0xE1180,
        pointer_count=223,
        first_pointer=0x800,
        last_pointer=0xC4000,
    ),
    PalDeScenarioBank(
        path="SCN/DG1.SCN",
        lba=146499,
        raw_offset=0x1489A7A8,
        reported_size=0xC8000,
        allocation_size=0xE5B00,
        pointer_count=223,
        first_pointer=0x800,
        last_pointer=0xC8000,
    ),
    PalDeScenarioBank(
        path="SCN/DG2.SCN",
        lba=146899,
        raw_offset=0x149802A8,
        reported_size=0xC5000,
        allocation_size=0xE23E0,
        pointer_count=223,
        first_pointer=0x800,
        last_pointer=0xC5000,
        note="Verified PAL-DE gameplay script bank for recruitment/chest/map writes.",
    ),
    PalDeScenarioBank(
        path="SCN/DG3.SCN",
        lba=147293,
        raw_offset=0x14A62688,
        reported_size=0xC8000,
        allocation_size=0xE5B00,
        pointer_count=223,
        first_pointer=0x800,
        last_pointer=0xC8000,
    ),
    PalDeScenarioBank(
        path="SCN/DG4.SCN",
        lba=147693,
        raw_offset=0x14B48188,
        reported_size=0xCF000,
        allocation_size=0xEDBA0,
        pointer_count=223,
        first_pointer=0x800,
        last_pointer=0xCF000,
    ),
)
PAL_DE_SCENARIO_PATHS = tuple(bank.path for bank in PAL_DE_SCENARIO_BANKS)
PAL_DE_ACTIVE_SCENARIO_PATH = "SCN/DG2.SCN"
PAL_DE_RECRUITMENT_SCENARIO_PATH = PAL_DE_ACTIVE_SCENARIO_PATH


def pal_de_scenario_bank(path: str) -> PalDeScenarioBank:
    """Return expected metadata for one PAL-DE scenario path."""

    normalized_path = path.replace("\\", "/").upper()
    for bank in PAL_DE_SCENARIO_BANKS:
        if bank.path.upper() == normalized_path:
            return bank

    raise KeyError(f"{path!r} is not a known PAL-DE scenario bank")


def pal_de_scenario_bank_containing(absolute_offset: int) -> PalDeScenarioBank | None:
    """Return the PAL-DE DG bank whose allocation contains ``absolute_offset``."""

    for bank in PAL_DE_SCENARIO_BANKS:
        if bank.contains_allocated_offset(absolute_offset):
            return bank

    return None


def load_pal_de_scenarios(rom_path: str | Path) -> tuple[ScenarioFile, ...]:
    """Load every known PAL-DE DG scenario bank in disc order."""

    image = RawCdImage(rom_path)
    return tuple(image.read_scenario(path) for path in PAL_DE_SCENARIO_PATHS)


def load_pal_de_active_scenario(rom_path: str | Path) -> ScenarioFile:
    """Load the verified PAL-DE gameplay script bank."""

    return RawCdImage(rom_path).read_scenario(PAL_DE_ACTIVE_SCENARIO_PATH)
