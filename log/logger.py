# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""Three-tier verbosity logger used throughout the randomizer.

Levels (passed at construction time as ``verbose``):

* ``"full"``    — every message goes to the log file.
* ``"casual"``  — only changes ("logChange") + errors go through.
* ``"race"``    — only changes + errors go through, plus the SeedingPolicy
  advances the RNG by one step so identical settings produce a different
  ROM between casual and race runs (so racers can't peek with a casual
  run first).

The class is unchanged in *behaviour* — only modernised with type hints,
``pathlib`` for the filename, and a context-manager protocol.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal


# Display labels for log section dividers.
SECTION_BANNER = "============================================================"


VerbosityLevel = Literal["full", "casual", "race"]


class Logger:
    """Randomization and ROM handler logging interface."""

    def __init__(self, verbose: VerbosityLevel, filename: str | os.PathLike | None = None) -> None:
        """Initialise verbosity and the optional log file path."""

        self.error: bool = False
        self.verbose: VerbosityLevel = verbose

        self.filename: str | None = str(filename) if filename is not None else None
        self.file = None

        if self.filename is not None:
            # Truncate any previous log and write the header.
            with open(self.filename, "w"):
                pass
            self.logAlways(self.getHeader("Digimon World Randomization Log"))
            self.logAlways("Logging mode is set to '" + verbose + "'")

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------
    def __enter__(self) -> "Logger":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Verbosity-gated log methods
    # ------------------------------------------------------------------
    def log(self, message: str) -> None:
        """Write only when verbosity is ``full``."""

        if self.verbose == "full":
            self.logAlways(message)

    def logChange(self, message: str) -> None:
        """Write when verbosity is ``full`` or ``casual`` (also ``race``)."""

        if self.verbose in ("full", "casual"):
            self.logAlways(message)

    def logError(self, message: str) -> None:
        """Always log + mark the error flag."""

        self.error = True
        self.logAlways(message)

    def fatalError(self, message: str) -> None:
        """Log the message and exit — used for unrecoverable failures."""

        self.logError(message)
        print("Program ended with errors.  See log file for errors.")
        self.close()
        exit()

    def logAlways(self, message: str) -> None:
        """Write unconditionally; appends to the log file or prints."""

        if self.filename is not None:
            if self.file is None:
                self.file = open(self.filename, "a")
            self.file.write(message + "\n")
        else:
            print(message)

    # ------------------------------------------------------------------
    # Bookkeeping
    # ------------------------------------------------------------------
    def close(self) -> None:
        """Close the file handle (if any)."""

        self.logAlways(self.getHeader("End of Log"))
        if self.file is not None:
            self.file.close()
            self.file = None

    def rename(self, new_name: str | os.PathLike) -> None:
        """Rename the on-disk log file."""

        if self.filename is None:
            return
        os.rename(self.filename, str(new_name))
        self.filename = str(new_name)

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------
    def getHeader(self, name: str) -> str:
        """Return a banner-style header for the section ``name``."""

        return f"\n{SECTION_BANNER}\n   {name}\n{SECTION_BANNER}\n"
