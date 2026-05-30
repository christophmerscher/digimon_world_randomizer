# Author: Tristan Challener <challenert@gmail.com>
# Author: Christoph Merscher <dev@fmerscher.com>
# Copyright: please don't steal this that is all

"""Backward-compatibility wrapper around :mod:`digimon.app`.

The high-level orchestration moved to :func:`digimon.app.run` as part of
the refactor. This module keeps the original :func:`runRandomizer`
entry point so any external automation that imports it keeps working.
"""

from __future__ import annotations

from digimon.app import LOG_FILENAME, PRICE_CUTOFF_ERROR, run as _run

__all__ = ["runRandomizer", "LOG_FILENAME", "PRICE_CUTOFF_ERROR"]


def runRandomizer(config: dict) -> None:
    """Run the complete randomization process for a validated config dict.

    Thin shim that delegates to :func:`digimon.app.run`.
    """

    _run(config)
