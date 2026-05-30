"""Translate raw config-dict entries into typed values the rest of the
codebase expects.

These helpers are pure functions — they don't touch the filesystem and
don't do their own logging, so they're cheap to unit-test.
"""

from __future__ import annotations

from digimon.rom.enums import levels
from digimon.settings.errors import SettingsError


# Default cutoff used when ``MatchValue`` is disabled. Kept as a string
# to mirror the legacy GUI behaviour (the GUI passes strings even for
# numeric settings).
DEFAULT_ITEM_VALUE_CUTOFF = "10000"


def getRequiredGeneralSetting(config: dict, key: str, missing_message: str) -> str:
    """Return ``config['general'][key]`` or raise ``SettingsError``."""

    value = config["general"][key]
    if value != "":
        return value
    raise SettingsError(missing_message)


def getPriceCutoff(section_config: dict) -> str | int:
    """Return the configured value-matching cutoff, or a fallback.

    Returns the user's ``ValuableItemCutoff`` if ``MatchValue`` is true;
    otherwise the default sentinel which is high enough that every item
    sits in the same bucket.
    """

    if section_config["MatchValue"]:
        return section_config["ValuableItemCutoff"]
    return DEFAULT_ITEM_VALUE_CUTOFF


def getAllowedStarterLevels(starter_config: dict) -> list[int]:
    """Convert the per-level toggles into the list of allowed level IDs."""

    toggles = [
        starter_config["Fresh"],
        starter_config["InTraining"],
        starter_config["Rookie"],
        starter_config["Champion"],
        starter_config["Ultimate"],
    ]
    return [level for enabled, level in zip(toggles, list(levels.keys())) if enabled]
