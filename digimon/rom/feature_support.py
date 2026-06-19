# Author: Christoph Merscher <dev@fmerscher.com>

"""Layout capability checks for user-selected randomizer features.

Incomplete layouts can still support a broad, safe subset of the randomizer.
This module keeps that policy close to the ROM layout/patch metadata instead
of embedding region-specific decisions in the application entry point.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from digimon.rom.patches.registry import get_patch
from digimon.settings import SettingsError


RECRUITMENT_REQUIRED_PATCHES = ("ogremon",)


@dataclass(frozen=True)
class PatchRequest:
    """One optional patch requested by the settings file."""

    name: str
    path: str
    value: Any = 0


def validate_layout_feature_support(config: dict, handler) -> None:
    """Reject selected features that are not mapped for the detected layout."""

    layout = handler._layout
    if layout.complete:
        return

    unsupported = unsupported_features_for_layout(config, layout)
    if unsupported:
        details = "\n - ".join(unsupported)
        raise SettingsError(
            layout.display_name + " support is incomplete for these enabled settings:\n - "
            + details
        )


def unsupported_features_for_layout(config: dict, layout) -> list[str]:
    """Return settings paths that the layout cannot safely randomize yet."""

    unsupported: list[str] = []

    if config["recruitment"]["Enabled"]:
        if not _layout_has_script_offsets(layout, "recruitOffsets"):
            unsupported.append("$.recruitment.Enabled")
        for patch_name in RECRUITMENT_REQUIRED_PATCHES:
            _append_unsupported_patch(
                unsupported,
                layout,
                patch_name,
                "$.recruitment.Enabled",
            )

    if (
        config["chests"]["Enabled"]
        and not _layout_has_script_offsets(layout, "chestItemOffsets")
    ):
        unsupported.append("$.chests.Enabled")

    if (
        config["mapItems"]["Enabled"]
        and not _layout_has_script_offsets(layout, "mapItemOffsets")
    ):
        unsupported.append("$.mapItems.Enabled")

    evolution_cfg = config["evolution"]
    if (
        evolution_cfg["Enabled"]
        and evolution_cfg["SpecialEvolutions"]
        and not _layout_has_script_offsets(layout, "specEvoOffsets")
    ):
        unsupported.append("$.evolution.SpecialEvolutions")

    techs_cfg = config["techs"]
    if techs_cfg["Enabled"] and techs_cfg["TypeEffectiveness"]:
        _append_unsupported_patch(
            unsupported,
            layout,
            "typeEffectiveness",
            "$.techs.TypeEffectiveness",
        )

    for request in patch_requests_from_settings(config):
        _append_unsupported_patch(unsupported, layout, request.name, request.path)

    return unsupported


def patch_requests_from_settings(config: dict) -> list[PatchRequest]:
    """Return optional patches that should be queued for this full config."""

    if not config["patches"]["Enabled"]:
        return []

    return _patch_requests(config["patches"], config.get("general", {}))


def requested_patch_names(patches: dict) -> list[tuple[str, str]]:
    """Return queued patch names implied by the settings ``patches`` section."""

    return [(request.name, request.path) for request in _patch_requests(patches, {})]


def _patch_requests(patches: dict, general: dict) -> list[PatchRequest]:
    requested: list[PatchRequest] = []

    def add(enabled, name: str, path: str, value: Any = 0) -> None:
        if _enabled(enabled):
            requested.append(PatchRequest(name=name, path=path, value=value))

    add(patches["EvoItemStatGain"], "fixEvoItems", "$.patches.EvoItemStatGain")
    add(patches["QuestItemsDroppable"], "allowDrop", "$.patches.QuestItemsDroppable")
    add(patches["Woah"], "woah", "$.patches.Woah")
    add(patches["BrainTrainTierOne"], "learnTierOne", "$.patches.BrainTrainTierOne")
    add(patches["JukeboxGlitch"], "giromon", "$.patches.JukeboxGlitch")
    add(patches["IncreaseLearnChance"], "upLearnChance", "$.patches.IncreaseLearnChance")
    add(patches["Gabu"], "gabumon", "$.patches.Gabu")

    add(
        patches["SpawnRateEnabled"],
        "spawn",
        "$.patches.SpawnRateEnabled",
        int(patches["SpawnRate"]),
    )

    add(
        patches["ShowHashIntro"],
        "hash",
        "$.patches.ShowHashIntro",
        general.get("Hash", ""),
    )
    add(patches["SkipIntro"], "intro", "$.patches.SkipIntro")
    add(patches["UnlockAreas"], "unlock", "$.patches.UnlockAreas")
    add(patches["UnrigSlots"], "slots", "$.patches.UnrigSlots")
    add(patches["Softlock"], "softlock", "$.patches.Softlock")
    add(
        patches["LearnMoveAndCommand"],
        "learnmoveandcommand",
        "$.patches.LearnMoveAndCommand",
    )
    add(patches["FixDVChips"], "fixDVChips", "$.patches.FixDVChips")
    add(patches["HappyVending"], "happyVending", "$.patches.HappyVending")

    return requested


def _enabled(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no", "off"}

    return bool(value)


def _layout_has_script_offsets(layout, name: str) -> bool:
    scripts = layout.require_scripts()
    if name == "recruitOffsets" and scripts.dynamicRecruitOffsets:
        return True

    return bool(getattr(scripts, name))


def _append_unsupported_patch(
    unsupported: list[str],
    layout,
    patch_name: str,
    path: str,
) -> None:
    patch = get_patch(patch_name)
    if patch is None or not patch.supports_layout(layout):
        unsupported.append(path + " (" + patch_name + ")")
