"""Open/read/write context for a single PSX ROM image."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, Iterator


class RomFile:
    """Thin wrapper around a binary file handle for the Digimon World ROM.

    Used as a context manager so the caller doesn't have to remember to
    close the file. Created via :meth:`open_for_read` or
    :meth:`open_for_update` to make the intent (and the file mode) obvious
    at the call site.
    """

    def __init__(self, path: Path, handle: BinaryIO) -> None:
        self.path = path
        self._handle = handle

    # ---- factory methods --------------------------------------------------

    @classmethod
    @contextmanager
    def open_for_read(cls, path: str | Path) -> Iterator["RomFile"]:
        """Open the ROM for read-only access."""

        path = Path(path)
        with path.open("rb") as handle:
            yield cls(path, handle)

    @classmethod
    @contextmanager
    def open_for_update(cls, path: str | Path) -> Iterator["RomFile"]:
        """Open the ROM for in-place read/write access."""

        path = Path(path)
        with path.open("r+b") as handle:
            yield cls(path, handle)

    # ---- pass-through accessors ------------------------------------------

    @property
    def handle(self) -> BinaryIO:
        """The underlying binary file handle (for codec helpers that need it)."""

        return self._handle

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._handle.seek(offset, whence)

    def read(self, size: int) -> bytes:
        return self._handle.read(size)

    def write(self, payload: bytes) -> int:
        return self._handle.write(payload)
