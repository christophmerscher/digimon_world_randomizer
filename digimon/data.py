# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""Backward-compatibility re-export of the ROM descriptor tables.

The original 800-line ``digimon.data`` god module has been split into
focused submodules under :mod:`digimon.rom`:

* :mod:`digimon.rom.enums`           — domain enums (types, levels, techs, …)
* :mod:`digimon.rom.blocks`          — variable-length data block descriptors
* :mod:`digimon.rom.script_offsets`  — chest/map/recruit/spec-evo offsets
* :mod:`digimon.rom.patch_data`      — byte payloads for the optional patches

This module re-exports every public name from those submodules so that
existing callers (``import digimon.data as data; data.techDataBlockOffset``)
continue to work unchanged while the refactor progresses.

New code should import directly from the focused submodules.
"""

from digimon.rom.blocks import *  # noqa: F401,F403
from digimon.rom.enums import *  # noqa: F401,F403
from digimon.rom.patch_data import *  # noqa: F401,F403
from digimon.rom.script_offsets import *  # noqa: F401,F403
