# Author: Tristan Challener <challenert@gmail.com>
# Author: Christoph Merscher <dev@fmerscher.com>
# Copyright: please don't steal this that is all

"""CLI entry point for the Digimon World randomizer.

Parses the ``-settings`` argument, hands the parsed JSON to
:func:`digimon.app.run`, and translates user-facing exceptions into a
process exit code. All real work happens behind :func:`digimon.app.run`.
"""

from __future__ import annotations

import argparse
import sys

from digimon.app import run as run_randomizer
from digimon.settings import (
    SettingsError,
    SettingsJsonError,
    loadSettings,
    validateSettings,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point — returns the desired process exit code."""

    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Randomize Digimon World")
    parser.add_argument(
        "-settings", required=True,
        help="JSON settings string that configures the operation",
    )
    settings_json = parser.parse_args(argv).settings

    try:
        config = loadSettings(settings_json)
        validateSettings(config)
        run_randomizer(config)
    except SettingsJsonError as err:
        print("Failed to parse JSON")
        print(err.error)
        return 1
    except SettingsError as err:
        print(err)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
