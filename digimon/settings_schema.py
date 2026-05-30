# Author: Christoph Merscher <dev@fmerscher.com>

"""Backward-compatibility shim — implementations now live in
:mod:`digimon.settings.schema` and :mod:`digimon.settings.errors`.
"""

from digimon.settings.errors import SettingsValidationError
from digimon.settings.schema import SETTINGS_SCHEMA, validateSettings

__all__ = ["SETTINGS_SCHEMA", "SettingsValidationError", "validateSettings"]
