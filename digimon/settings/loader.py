"""Parse the JSON settings string fed in from the CLI or GUI."""

from __future__ import annotations

import json
from json import JSONDecodeError

from digimon.settings.errors import SettingsError, SettingsJsonError


def loadSettings(settings: str) -> dict:
    """Parse the settings string into a dict.

    Raises :class:`SettingsError` if the string is empty (the user forgot
    the ``-settings`` argument) and :class:`SettingsJsonError` if the
    string is not valid JSON.
    """

    if settings == "":
        raise SettingsError(
            "Settings file must be provided at command line.  Use [-h] for help."
        )

    try:
        return json.loads(settings)
    except JSONDecodeError as err:
        raise SettingsJsonError(err)
