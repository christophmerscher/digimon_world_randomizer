# Author: Christoph Merscher <dev@fmerscher.com>

"""Helpers for inspecting PlayStation scenario files inside a raw BIN image.

The randomizer writes absolute offsets into a raw 2352-byte/sector PlayStation
image. PAL support needs stronger evidence than byte-pattern scans, so this
module provides the small amount of ISO9660 and scenario-table parsing needed
by the PAL layout tests.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
import struct
from typing import Iterable


RAW_SECTOR_SIZE = 2352
USER_DATA_OFFSET = 24
USER_DATA_SIZE = 2048
PRIMARY_VOLUME_DESCRIPTOR_LBA = 16
PRIMARY_VOLUME_DESCRIPTOR_ID = b"CD001"
ROOT_DIRECTORY_RECORD_OFFSET = 156


@dataclass(frozen=True)
class CdFileEntry:
    """One ISO9660 file or directory entry in a raw PlayStation image."""

    path: str
    lba: int
    size: int
    is_directory: bool
    allocated_size: int | None = None

    @property
    def data_offset(self) -> int:
        """Absolute raw-image offset where the entry's user data begins."""

        return self.lba * RAW_SECTOR_SIZE + USER_DATA_OFFSET

    @property
    def allocation_size(self) -> int:
        """Bytes allocated to this entry before the next file begins."""

        return self.allocated_size if self.allocated_size is not None else self.size


@dataclass(frozen=True)
class ScenarioFile:
    """Loaded ``SCN/*.SCN`` file plus its internal pointer table."""

    entry: CdFileEntry
    data: bytes
    pointers: tuple[int, ...]

    @property
    def data_offset(self) -> int:
        return self.entry.data_offset

    @property
    def size(self) -> int:
        return len(self.data)

    @property
    def reported_size(self) -> int:
        """Bytes reported by the ISO directory record for this scenario."""

        return self.entry.size

    @property
    def allocation_size(self) -> int:
        """Bytes available before the next ISO entry begins."""

        return self.entry.allocation_size

    def contains_reported_relative(self, relative_offset: int) -> bool:
        """Return whether ``relative_offset`` is inside the reported SCN file."""

        return 0 <= relative_offset < self.reported_size

    def absolute_offset(self, relative_offset: int) -> int:
        """Convert a scenario-relative offset to a raw-image offset."""

        if relative_offset < 0 or relative_offset >= self.size:
            raise ValueError(f"relative offset {relative_offset:#x} is outside {self.entry.path}")

        return self.data_offset + relative_offset

    def relative_offset(self, absolute_offset: int) -> int:
        """Convert a raw-image offset to a scenario-relative offset."""

        relative = absolute_offset - self.data_offset
        if relative < 0 or relative >= self.size:
            raise ValueError(f"absolute offset {absolute_offset:#x} is outside {self.entry.path}")

        return relative

    def pointer_index_for_relative(self, relative_offset: int) -> int:
        """Return the script pointer-table slice containing ``relative_offset``."""

        index = bisect_right(self.pointers, relative_offset) - 1
        if index < 0:
            raise ValueError(f"relative offset {relative_offset:#x} is before the pointer table")

        return index


@dataclass(frozen=True)
class ScriptCommandCandidate:
    """A command-shaped byte sequence inside a scenario file."""

    absolute_offset: int
    relative_offset: int
    pointer_index: int
    opcode: int
    item_id: int
    payload: bytes


@dataclass(frozen=True)
class ScenarioValueCandidate:
    """A little-endian value occurrence inside a scenario file."""

    absolute_offset: int
    relative_offset: int
    pointer_index: int
    value: int
    payload: bytes


@dataclass(frozen=True)
class EncodedTextHit:
    """An encoded text payload occurrence inside a scenario file."""

    absolute_offset: int
    relative_offset: int
    pointer_index: int
    payload: bytes


class RawCdImage:
    """Read ISO9660 entries from a raw 2352-byte/sector PlayStation BIN."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._data = self.path.read_bytes()
        self._entries: dict[str, CdFileEntry] | None = None

    def read_user_data(self, lba: int, size: int = USER_DATA_SIZE) -> bytes:
        """Read user data from one or more raw sectors."""

        chunks = bytearray()
        sectors = (size + USER_DATA_SIZE - 1) // USER_DATA_SIZE
        for sector_index in range(sectors):
            offset = (lba + sector_index) * RAW_SECTOR_SIZE + USER_DATA_OFFSET
            chunks.extend(self._data[offset:offset + USER_DATA_SIZE])

        return bytes(chunks[:size])

    def find(self, path: str) -> CdFileEntry:
        """Return a file entry by slash-separated ISO path."""

        key = _normalize_path(path)
        entries = self._load_entries()
        try:
            return entries[key]
        except KeyError as exc:
            raise FileNotFoundError(f"{path!r} was not found in {self.path}") from exc

    def read_scenario(self, path: str) -> ScenarioFile:
        """Load one scenario allocation and parse its raw pointer table."""

        entry = self.find(path)
        data = self._data[entry.data_offset:entry.data_offset + entry.allocation_size]
        return ScenarioFile(entry, data, parse_scenario_pointers(data))

    def _load_entries(self) -> dict[str, CdFileEntry]:
        if self._entries is None:
            self._entries = self._read_entries()

        return self._entries

    def _read_entries(self) -> dict[str, CdFileEntry]:
        pvd = self.read_user_data(PRIMARY_VOLUME_DESCRIPTOR_LBA)
        if pvd[1:6] != PRIMARY_VOLUME_DESCRIPTOR_ID:
            raise ValueError(f"{self.path} does not contain an ISO9660 primary volume descriptor")

        root = _parse_directory_record(pvd, ROOT_DIRECTORY_RECORD_OFFSET, "")
        entries: dict[str, CdFileEntry] = {}
        self._walk_directory(root, entries)
        return _with_allocated_sizes(entries)

    def _walk_directory(self, directory: CdFileEntry, entries: dict[str, CdFileEntry]) -> None:
        data = self.read_user_data(directory.lba, directory.size)
        for entry in _iter_directory_records(data, directory.path):
            entries[_normalize_path(entry.path)] = entry
            if entry.is_directory:
                self._walk_directory(entry, entries)


class ScenarioCommandScanner:
    """Find command-shaped offsets in one scenario file."""

    def __init__(self, scenario: ScenarioFile) -> None:
        self.scenario = scenario

    def chest_object_candidates(self) -> tuple[ScriptCommandCandidate, ...]:
        """Find ``spawnChest``-shaped records that look like chest objects.

        The PAL layout owns the promoted offset table; tests regenerate these
        candidates from the local ROM to prove that table still matches the
        scenario allocation.
        """

        return tuple(
            self._iter_command_candidates(
                opcode=0x75,
                record_size=12,
                predicate=lambda data, offset: data[offset + 11] == 0x02,
            )
        )

    def map_item_candidates(self) -> tuple[ScriptCommandCandidate, ...]:
        """Find positive-coordinate ``spawnItem``-shaped records.

        The PAL layout owns the promoted offset table; tests regenerate these
        candidates from the local ROM to prove that table still matches the
        scenario allocation.
        """

        return tuple(
            self._iter_command_candidates(
                opcode=0x74,
                record_size=6,
                predicate=lambda data, offset: data[offset + 3] == 0 and data[offset + 5] == 0,
            )
        )

    def recruitment_trigger_candidates(self, trigger: int) -> tuple[ScenarioValueCandidate, ...]:
        """Find raw ``<H`` trigger-value candidates.

        Recruitment checks are not a single opcode-shaped command in the
        compiled scenario stream. This deliberately returns *candidates*:
        callers still need higher-level evidence before promoting offsets
        into a writable layout.
        """

        return self.value_candidates(trigger, size=2, alignment=2)

    def random_command_candidates(self, max_value: int = 99) -> tuple[ScriptCommandCandidate, ...]:
        """Find ``random`` command-shaped records with a small threshold.

        Spawn-rate patch offsets need more evidence than this broad command
        shape because translated scenario banks contain many unrelated random
        checks with the same two-byte structure.
        """

        return tuple(
            self._iter_command_candidates(
                opcode=0x6E,
                record_size=2,
                predicate=lambda data, offset: data[offset + 1] <= max_value,
            )
        )

    def value_candidates(
        self,
        value: int,
        *,
        size: int,
        alignment: int = 1,
    ) -> tuple[ScenarioValueCandidate, ...]:
        """Find little-endian integer occurrences in aligned scenario bytes."""

        if size not in (1, 2, 4):
            raise ValueError("size must be 1, 2, or 4 bytes")
        if value < 0 or value >= (1 << (size * 8)):
            raise ValueError(f"value {value:#x} does not fit in {size} bytes")
        if alignment < 1:
            raise ValueError("alignment must be at least 1")

        raw_value = value.to_bytes(size, "little")
        return tuple(
            self._value_candidate(relative, value, size)
            for relative in range(0, len(self.scenario.data) - size + 1, alignment)
            if self.scenario.data[relative:relative + size] == raw_value
        )

    def encoded_text_hits(self, payload: bytes) -> tuple[EncodedTextHit, ...]:
        """Find every occurrence of an already encoded text payload."""

        hits: list[EncodedTextHit] = []
        start = 0
        while True:
            relative = self.scenario.data.find(payload, start)
            if relative == -1:
                return tuple(hits)

            hits.append(
                EncodedTextHit(
                    absolute_offset=self.scenario.absolute_offset(relative),
                    relative_offset=relative,
                    pointer_index=self.scenario.pointer_index_for_relative(relative),
                    payload=payload,
                )
            )
            start = relative + 1

    def _iter_command_candidates(
        self,
        *,
        opcode: int,
        record_size: int,
        predicate,
    ) -> Iterable[ScriptCommandCandidate]:
        data = self.scenario.data
        for relative in range(0, len(data) - record_size + 1, 2):
            if data[relative] != opcode or data[relative + 1] >= 0x80:
                continue
            if _looks_like_encoded_text(data, relative):
                continue
            if not predicate(data, relative):
                continue

            yield ScriptCommandCandidate(
                absolute_offset=self.scenario.absolute_offset(relative),
                relative_offset=relative,
                pointer_index=self.scenario.pointer_index_for_relative(relative),
                opcode=opcode,
                item_id=data[relative + 1],
                payload=data[relative:relative + record_size],
            )

    def _value_candidate(
        self,
        relative: int,
        value: int,
        size: int,
    ) -> ScenarioValueCandidate:
        context_start = max(0, relative - 8)
        context_end = min(len(self.scenario.data), relative + size + 8)
        return ScenarioValueCandidate(
            absolute_offset=self.scenario.absolute_offset(relative),
            relative_offset=relative,
            pointer_index=self.scenario.pointer_index_for_relative(relative),
            value=value,
            payload=self.scenario.data[context_start:context_end],
        )


def parse_scenario_pointers(data: bytes) -> tuple[int, ...]:
    """Parse the sorted little-endian pointer prefix of an ``SCN`` file."""

    pointers: list[int] = []
    previous = -1
    for offset in range(0, len(data) - 3, 4):
        value = struct.unpack_from("<I", data, offset)[0]
        if value < previous or value > len(data):
            break

        pointers.append(value)
        previous = value

    return tuple(pointers)


def group_adjacent_candidates(
    candidates: Iterable[ScriptCommandCandidate],
    *,
    record_size: int,
) -> tuple[tuple[ScriptCommandCandidate, ...], ...]:
    """Group command candidates that are contiguous records of one run."""

    ordered = sorted(candidates, key=lambda candidate: candidate.relative_offset)
    if not ordered:
        return ()

    groups: list[list[ScriptCommandCandidate]] = [[ordered[0]]]
    for previous, candidate in zip(ordered, ordered[1:]):
        if candidate.relative_offset - previous.relative_offset == record_size:
            groups[-1].append(candidate)
        else:
            groups.append([candidate])

    return tuple(tuple(group) for group in groups)


def equivalent_run_count(
    runs: Iterable[tuple[ScriptCommandCandidate, ...]],
    *,
    max_gap: int,
) -> int:
    """Count duplicate command runs by item sequence and proximity.

    PAL scenario files can contain translated or alternate copies of the same
    run. This helper collapses only adjacent runs with the same item sequence
    within ``max_gap`` bytes, producing a conservative "logical run" count.
    """

    run_list = list(runs)
    if not run_list:
        return 0

    count = 0
    index = 0
    while index < len(run_list):
        current = run_list[index]
        current_key = tuple(candidate.item_id for candidate in current)
        count += len(current)
        index += 1
        while index < len(run_list):
            next_run = run_list[index]
            next_key = tuple(candidate.item_id for candidate in next_run)
            if (
                next_key != current_key
                or next_run[0].relative_offset - run_list[index - 1][0].relative_offset >= max_gap
            ):
                break
            index += 1

    return count


def _with_allocated_sizes(entries: dict[str, CdFileEntry]) -> dict[str, CdFileEntry]:
    ordered = sorted(entries.values(), key=lambda entry: (entry.lba, entry.path))
    allocated: dict[str, CdFileEntry] = {}
    for index, entry in enumerate(ordered):
        next_entries = (
            next_entry for next_entry in ordered[index + 1:]
            if next_entry.lba > entry.lba
        )
        next_entry = next(next_entries, None)
        allocated_size = entry.size
        if next_entry is not None:
            allocated_size = max(entry.size, next_entry.data_offset - entry.data_offset)

        allocated[_normalize_path(entry.path)] = CdFileEntry(
            path=entry.path,
            lba=entry.lba,
            size=entry.size,
            is_directory=entry.is_directory,
            allocated_size=allocated_size,
        )

    return allocated


def _parse_directory_record(data: bytes, offset: int, parent_path: str) -> CdFileEntry:
    length = data[offset]
    if length == 0:
        raise ValueError("empty ISO9660 directory record")

    lba = struct.unpack_from("<I", data, offset + 2)[0]
    size = struct.unpack_from("<I", data, offset + 10)[0]
    flags = data[offset + 25]
    name_length = data[offset + 32]
    raw_name = data[offset + 33:offset + 33 + name_length]
    name = _normalize_record_name(raw_name)
    base_path = "" if parent_path in {"", "."} else parent_path
    path = name if not base_path else f"{base_path}/{name}"
    return CdFileEntry(path=path, lba=lba, size=size, is_directory=bool(flags & 0x02))


def _iter_directory_records(data: bytes, parent_path: str) -> Iterable[CdFileEntry]:
    offset = 0
    while offset < len(data):
        length = data[offset]
        if length == 0:
            offset = ((offset // USER_DATA_SIZE) + 1) * USER_DATA_SIZE
            continue

        entry = _parse_directory_record(data, offset, parent_path)
        offset += length
        if entry.path.endswith("/.") or entry.path.endswith("/..") or entry.path in {".", ".."}:
            continue

        yield entry


def _normalize_record_name(raw_name: bytes) -> str:
    if raw_name == b"\x00":
        return "."
    if raw_name == b"\x01":
        return ".."

    name = raw_name.decode("ascii").split(";", 1)[0]
    return name.rstrip(".")


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip("/").upper()


def _looks_like_encoded_text(data: bytes, offset: int) -> bool:
    return offset > 0 and data[offset - 1] in (0x81, 0x82, 0x83)
