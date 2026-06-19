# Author: Christoph Merscher <dev@fmerscher.com>

"""High-level orchestrator for one randomisation run.

``run(config)`` is the modern equivalent of the legacy
``digimon.randomizer.runRandomizer`` — it composes the loader, handler,
randomisation pipeline, patch queue, and writer into a single, top-to-
bottom function. Each step delegates to a focused subsystem, so the
function reads as a high-level checklist of what happens during a run.

This module is invoked from two entry points:

* ``digimon_randomize.py`` — the CLI shim packaged with the GUI.
* ``digimon.randomizer.runRandomizer`` — the legacy public entry point
  (now a one-line shim around :func:`run`).
"""

from __future__ import annotations

import sys
from typing import Any

from digimon.handler import DigimonWorldHandler
from digimon.randomization import RandomizationContext, RandomizationPipeline
from digimon.rom.feature_support import (
    RECRUITMENT_REQUIRED_PATCHES,
    patch_requests_from_settings,
    unsupported_features_for_layout as _unsupported_features_for_layout,
    validate_layout_feature_support as _validate_layout_feature_support,
)
from digimon.settings import (
    getRequiredGeneralSetting,
)
from log.logger import Logger


LOG_FILENAME = "randomize.log"
PRICE_CUTOFF_ERROR = "Item price cutoff must be an integer. {0} is not a valid value."


def run(config: dict) -> None:
    """Execute a complete randomisation run from a validated config dict.

    Raises :class:`~digimon.settings.SettingsError` for any user-fixable
    misconfiguration; otherwise writes the output ROM and a companion
    log file alongside it.
    """

    input_file  = getRequiredGeneralSetting(config, "InputFile",  "ROM file section is required")
    output_file = getRequiredGeneralSetting(config, "OutputFile", "Destination file section is required")

    print("Reading data from " + input_file + "...")
    sys.stdout.flush()

    logger, handler = _create_handler(config, input_file)
    _validate_layout_feature_support(config, handler)

    print("Modifying data...")
    sys.stdout.flush()

    _run_randomisation(config, handler, logger)
    _queue_patches(config, handler)

    _write_output(handler, logger, output_file)
    _finalise_log(handler, logger)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _create_handler(config: dict, input_file: str) -> tuple[Logger, DigimonWorldHandler]:
    """Open the input ROM with the right logger + seed."""

    verbose = config["general"]["LogLevel"]
    seedcfg = config["general"].get("Seed")

    try:
        logger = Logger(verbose, filename=LOG_FILENAME)
        handler = DigimonWorldHandler(input_file, logger, seed=int(seedcfg))
        return logger, handler
    except ValueError:
        print("Seed must be an integer. " + str(seedcfg) + " is not a valid value.")
        raise SystemExit(1)
    except Exception as exc:   # noqa: BLE001 — mirrors legacy fallback
        # Legacy behaviour: any non-seed exception falls back to a random
        # seed and re-tries. The original code printed the exception
        # message and continued.
        print(exc)
        logger = Logger(verbose, filename=LOG_FILENAME)
        handler = DigimonWorldHandler(input_file, logger)
        return logger, handler


def _run_randomisation(config: dict, handler: DigimonWorldHandler, logger: Logger) -> None:
    """Build and run the per-section randomiser pipeline."""

    ctx = RandomizationContext(
        state=handler._state,
        logger=logger,
        lookup=handler,
        queue_patch=handler.applyPatch,
        layout=handler._layout,
    )

    def parse_price(value: Any) -> int:
        try:
            return int(value)
        except ValueError:
            logger.fatalError(PRICE_CUTOFF_ERROR.format(str(value)))
            raise   # pragma: no cover — fatalError exits

    pipeline = RandomizationPipeline.build_from_config(
        config, ctx, price_parser=parse_price,
    )
    pipeline.run()


def _queue_patches(config: dict, handler: DigimonWorldHandler) -> None:
    """Forward the patches section into the handler's patch queue."""

    for request in patch_requests_from_settings(config):
        handler.applyPatch(request.name, request.value)


def _write_output(handler: DigimonWorldHandler, logger: Logger, output_file: str) -> None:
    print("Writing to " + output_file + "...")
    sys.stdout.flush()

    try:
        handler.write(output_file)
    except Exception as exc:   # noqa: BLE001 — mirrors legacy fallback
        logger.logError("System error: {0}".format(exc))
        print("An irrecoverable error occured")

    if not logger.error:
        print("Modifications completed successfully.  See log file for details (Warning: spoilers!).")
        print("Seed was " + str(handler.randomseed))
        print("Enter this seed in settings file to produce the same ROM again.")
    else:
        print("Program ended with errors.  See log file for details.")

    sys.stdout.flush()


def _finalise_log(handler: DigimonWorldHandler, logger: Logger) -> None:
    logger.logAlways(logger.getHeader("Seed"))
    logger.logAlways("Seed was " + str(handler.randomseed) + ".")
    logger.close()
    logger.rename("randomize-" + str(handler.randomseed) + ".log")
