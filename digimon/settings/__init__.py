"""Randomiser settings — load, validate, adapt.

The legacy ``digimon.settings`` and ``digimon.settings_schema`` modules
have been split into focused submodules:

* :mod:`digimon.settings.loader`   — JSON string → dict
* :mod:`digimon.settings.schema`   — schema definition + validator
* :mod:`digimon.settings.adapters` — config-dict → typed values
* :mod:`digimon.settings.errors`   — exception hierarchy

Every public name from the old flat modules is re-exported here so
``from digimon.settings import getPriceCutoff`` still works.
"""

from digimon.settings.adapters import (
    DEFAULT_ITEM_VALUE_CUTOFF,
    getAllowedStarterLevels,
    getPriceCutoff,
    getRequiredGeneralSetting,
)
from digimon.settings.errors import (
    SettingsError,
    SettingsJsonError,
    SettingsValidationError,
)
from digimon.settings.loader import loadSettings
from digimon.settings.schema import SETTINGS_SCHEMA, validateSettings

__all__ = [
    "DEFAULT_ITEM_VALUE_CUTOFF",
    "SETTINGS_SCHEMA",
    "SettingsError",
    "SettingsJsonError",
    "SettingsValidationError",
    "getAllowedStarterLevels",
    "getPriceCutoff",
    "getRequiredGeneralSetting",
    "loadSettings",
    "validateSettings",
]
