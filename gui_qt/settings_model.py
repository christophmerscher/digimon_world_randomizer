# Author: Christoph Merscher <dev@fmerscher.com>

"""Typed settings model backing the PyQt6 GUI.

Mirrors the historical Electron ``MainModel.ts`` exactly:

* Same section names, same field names, same defaults.
* Same ``to_json`` post-processing rules — join the output filename to
  the input ROM directory, append ``.bin`` if missing, force
  ``starter.Rookie = True`` when every level toggle is off.
* MD5 hash of the settings, computed over a canonical representation
  that excludes ``InputFile``, ``OutputFile``, and the ``Hash`` field
  itself.  This is the value the ``hash`` patch embeds into Jijimon's
  intro screen for race verification.

Pure Python, no Qt dependencies — the same model is reused by tests and
by the Qt widget layer.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal


# ---------------------------------------------------------------------------
# Public constants — mirror MainModel.ts
# ---------------------------------------------------------------------------

ITEM_VALUE_MIN = 0
ITEM_VALUE_MAX = 10_000

SPAWN_RATE_MIN = 1
SPAWN_RATE_MAX = 100
SPAWN_RATE_DEFAULT = 3


LogLevel = Literal["full", "casual", "race"]
RandomizationMode = Literal["shuffle", "random"]


# Settings keys that must not influence the hash. Hashing input/output
# paths would make racers with different filesystems disagree on the
# hash; hashing the hash itself is self-referential.
_HASH_EXCLUDED_KEYS = frozenset(("InputFile", "OutputFile", "Hash"))


# ---------------------------------------------------------------------------
# Section dataclasses
# ---------------------------------------------------------------------------

@dataclass
class GeneralSettings:
    InputFile:  str  = ""
    OutputFile: str  = ""
    LogLevel:   str  = "casual"
    Seed:       str  = ""
    Hash:       str  = ""


@dataclass
class DigimonSettings:
    Enabled:            bool = False
    DroppedItem:        bool = False
    DropRate:           bool = False
    MatchValue:         bool = False
    ValuableItemCutoff: int  = 1000


@dataclass
class TechSettings:
    Enabled:           bool = False
    RandomizationMode: str  = "random"
    Power:             bool = False
    Cost:              bool = False
    Accuracy:          bool = False
    Effect:            bool = False
    EffectChance:      bool = False
    TypeEffectiveness: bool = False


@dataclass
class StarterSettings:
    Enabled:        bool = False
    UseWeakestTech: bool = False
    Digimon:        str  = "Random"
    Fresh:          bool = False
    InTraining:     bool = False
    Rookie:         bool = True
    Champion:       bool = False
    Ultimate:       bool = False


@dataclass
class RecruitmentSettings:
    Enabled: bool = False


@dataclass
class ChestSettings:
    Enabled:             bool = False
    AllowEvolutionItems: bool = False


@dataclass
class TokomonSettings:
    Enabled:        bool = False
    ConsumableOnly: bool = False


@dataclass
class TechGiftSettings:
    Enabled: bool = False


@dataclass
class MapItemSettings:
    Enabled:            bool = False
    FoodOnly:           bool = False
    MatchValue:         bool = False
    ValuableItemCutoff: int  = 1000


@dataclass
class EvolutionSettings:
    Enabled:           bool = False
    Requirements:      bool = False
    SpecialEvolutions: bool = False
    ObtainAllMode:     bool = False


@dataclass
class PatchSettings:
    Enabled:             bool = False
    EvoItemStatGain:     bool = False
    QuestItemsDroppable: bool = False
    BrainTrainTierOne:   bool = False
    JukeboxGlitch:       bool = False
    IncreaseLearnChance: bool = False
    SpawnRateEnabled:    bool = False
    SpawnRate:           int  = SPAWN_RATE_DEFAULT
    ShowHashIntro:       bool = False
    SkipIntro:           bool = False
    Woah:                bool = False
    Gabu:                bool = False
    Softlock:            bool = False
    UnlockAreas:         bool = False
    UnrigSlots:          bool = False
    LearnMoveAndCommand: bool = False
    FixDVChips:          bool = False
    HappyVending:        bool = False


# ---------------------------------------------------------------------------
# Top-level model
# ---------------------------------------------------------------------------

@dataclass
class SettingsModel:
    """All randomiser settings, one section per attribute."""

    General:     GeneralSettings     = field(default_factory=GeneralSettings)
    Digimon:     DigimonSettings     = field(default_factory=DigimonSettings)
    Techs:       TechSettings        = field(default_factory=TechSettings)
    Starter:     StarterSettings     = field(default_factory=StarterSettings)
    Recruitment: RecruitmentSettings = field(default_factory=RecruitmentSettings)
    Chests:      ChestSettings       = field(default_factory=ChestSettings)
    Tokomon:     TokomonSettings     = field(default_factory=TokomonSettings)
    TechGifts:   TechGiftSettings    = field(default_factory=TechGiftSettings)
    MapItems:    MapItemSettings     = field(default_factory=MapItemSettings)
    Evolution:   EvolutionSettings   = field(default_factory=EvolutionSettings)
    Patches:     PatchSettings       = field(default_factory=PatchSettings)

    # ------------------------------------------------------------------
    # JSON round-trip
    # ------------------------------------------------------------------

    @classmethod
    def from_json(cls, raw: str) -> "SettingsModel":
        """Parse a settings string produced by :meth:`to_json` (or the
        legacy Electron app) back into a model."""

        data = json.loads(raw)
        model = cls()
        _populate(model.General,     data.get("general",     {}))
        _populate(model.Digimon,     data.get("digimon",     {}))
        _populate(model.Techs,       data.get("techs",       {}))
        _populate(model.Starter,     data.get("starter",     {}))
        _populate(model.Recruitment, data.get("recruitment", {}))
        _populate(model.Chests,      data.get("chests",      {}))
        _populate(model.Tokomon,     data.get("tokomon",     {}))
        _populate(model.TechGifts,   data.get("techGifts",   {}))
        _populate(model.MapItems,    data.get("mapItems",    {}))
        _populate(model.Evolution,   data.get("evolution",   {}))
        _populate(model.Patches,     data.get("patches",     {}))

        # Match the Electron behaviour: when loaded, OutputFile shrinks
        # to a basename so the user-visible output field stays editable
        # independently of the input path.
        if model.General.OutputFile:
            model.General.OutputFile = os.path.basename(model.General.OutputFile)

        if not model.Starter.Digimon:
            model.Starter.Digimon = "Random"

        return model

    def to_json(self, *, indent: int | str = "\t") -> str:
        """Serialise to the JSON format consumed by ``digimon_randomize``.

        Side-effects (matching the legacy GUI):

        * Joins ``OutputFile`` to the directory of ``InputFile`` and
          appends ``.bin`` when missing.
        * Forces ``starter.Rookie = True`` when every starter level is
          unchecked, so the randomiser always has at least one pool.
        * Computes ``general.Hash`` and updates ``self.General.Hash`` in
          place.
        """

        raw = self._build_raw_dict()
        raw["general"]["Hash"] = compute_settings_hash(raw)
        self.General.Hash = raw["general"]["Hash"]
        return json.dumps(raw, indent=indent)

    # ------------------------------------------------------------------
    def _build_raw_dict(self) -> dict[str, Any]:
        """Snapshot the model as a plain dict with the JSON key shape."""

        out_path = self._resolve_output_path()

        raw = {
            "general":     {**asdict(self.General), "OutputFile": out_path},
            "digimon":     asdict(self.Digimon),
            "techs":       asdict(self.Techs),
            "starter":     asdict(self.Starter),
            "recruitment": asdict(self.Recruitment),
            "chests":      asdict(self.Chests),
            "tokomon":     asdict(self.Tokomon),
            "techGifts":   asdict(self.TechGifts),
            "mapItems":    asdict(self.MapItems),
            "evolution":   asdict(self.Evolution),
            "patches":     asdict(self.Patches),
        }

        if not raw["starter"]["Digimon"]:
            raw["starter"]["Digimon"] = "Random"

        if not any((
            self.Starter.Fresh,
            self.Starter.InTraining,
            self.Starter.Rookie,
            self.Starter.Champion,
            self.Starter.Ultimate,
        )):
            raw["starter"]["Rookie"] = True

        return raw

    def _resolve_output_path(self) -> str:
        """Compute the absolute output path the CLI should write to."""

        if not self.General.OutputFile:
            return ""

        base_dir = Path(self.General.InputFile).parent
        out_path = base_dir / self.General.OutputFile
        if out_path.suffix.lower() != ".bin":
            out_path = out_path.with_suffix(out_path.suffix + ".bin") \
                if out_path.suffix else out_path.with_name(out_path.name + ".bin")

        return str(out_path)


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def compute_settings_hash(raw: dict[str, Any]) -> str:
    """MD5 of the canonical serialisation of ``raw`` minus the excluded keys.

    Keys are sorted at every nesting depth so the digest is stable
    across runs and across machines. Matches the legacy Electron GUI's
    `object-hash`-based behaviour functionally (same exclusion list,
    same canonical key ordering, same algorithm).
    """

    cleaned = _strip_hash_excluded_keys(raw)
    canonical = json.dumps(cleaned, sort_keys=True, separators=(",", ":"))
    return hashlib.md5(canonical.encode("utf-8")).hexdigest()


def _strip_hash_excluded_keys(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_hash_excluded_keys(child)
            for key, child in value.items()
            if key not in _HASH_EXCLUDED_KEYS
        }
    if isinstance(value, list):
        return [_strip_hash_excluded_keys(child) for child in value]
    return value


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _populate(target: Any, source: dict[str, Any]) -> None:
    """Copy any matching attribute from ``source`` onto the dataclass
    ``target``. Unknown keys are silently ignored to keep the model
    forward-compatible with future settings additions."""

    for key, value in source.items():
        if hasattr(target, key):
            setattr(target, key, value)
