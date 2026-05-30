# Author: Christoph Merscher <dev@fmerscher.com>

"""Dependency-free schema validation for the randomizer settings JSON.

The schema mirrors the shape produced by the Electron GUI in
``gui/src/``; any field added there needs a matching entry here.
"""

from __future__ import annotations

from digimon.settings.errors import SettingsValidationError


def validateSettings(config: dict) -> None:
    """Validate ``config`` against :data:`SETTINGS_SCHEMA`.

    Raises :class:`SettingsValidationError` on the first failure batch
    (every error in the dict is collected, then raised together).
    """

    errors: list[str] = []
    _validateValue(config, SETTINGS_SCHEMA, "$", errors)
    _validateSettingsRules(config, errors)

    if errors:
        raise SettingsValidationError(errors)


# ---------------------------------------------------------------------------
# Walker
# ---------------------------------------------------------------------------

def _validateValue(value, schema, path, errors):
    expectedType = schema.get("type")
    if expectedType is not None and not _matchesType(value, expectedType):
        errors.append(path + " must be " + _describeType(expectedType))
        return

    if "enum" in schema and value not in schema["enum"]:
        errors.append(path + " must be one of: " + ", ".join(schema["enum"]))

    if _matchesType(value, "object"):
        _validateObject(value, schema, path, errors)

    if _matchesType(value, "number") or _matchesType(value, "integer"):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(path + " must be at least " + str(schema["minimum"]))
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(path + " must be at most " + str(schema["maximum"]))

    if _matchesType(value, "string") and "minLength" in schema:
        if len(value) < schema["minLength"]:
            errors.append(path + " must not be empty")


def _validateSettingsRules(config, errors):
    if not _matchesType(config, "object"):
        return

    patches = config.get("patches", {})
    general = config.get("general", {})
    starter = config.get("starter", {})

    if _matchesType(patches, "object") and patches.get("ShowHashIntro"):
        if not _matchesType(general, "object") or not general.get("Hash"):
            errors.append(
                "$.general.Hash is required when $.patches.ShowHashIntro is true"
            )

    if _matchesType(starter, "object") and starter.get("Enabled"):
        level_keys = ["Fresh", "InTraining", "Rookie", "Champion", "Ultimate"]
        if not any(starter.get(key) for key in level_keys):
            errors.append(
                "$.starter must enable at least one starter level when "
                "$.starter.Enabled is true"
            )


def _validateObject(value, schema, path, errors):
    properties = schema.get("properties", {})

    for key in schema.get("required", []):
        if key not in value:
            errors.append(_joinPath(path, key) + " is required")

    for key, child_value in value.items():
        child_path = _joinPath(path, key)
        if key in properties:
            _validateValue(child_value, properties[key], child_path, errors)
        elif not schema.get("additionalProperties", True):
            errors.append(child_path + " is not allowed")


def _matchesType(value, expectedType):
    if isinstance(expectedType, (list, tuple)):
        return any(_matchesType(value, t) for t in expectedType)
    if expectedType == "object":  return isinstance(value, dict)
    if expectedType == "array":   return isinstance(value, list)
    if expectedType == "string":  return isinstance(value, str)
    if expectedType == "boolean": return isinstance(value, bool)
    if expectedType == "integer": return isinstance(value, int) and not isinstance(value, bool)
    if expectedType == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    return False


def _describeType(expectedType):
    if isinstance(expectedType, (list, tuple)):
        return " or ".join(expectedType)
    return expectedType


def _joinPath(path, key):
    return path + "." + key if path != "$" else "$." + key


# ---------------------------------------------------------------------------
# Schema-builder DSL
# ---------------------------------------------------------------------------

def _object(properties, required=None):
    if required is None:
        required = list(properties.keys())
    return {
        "type": "object",
        "required": required,
        "properties": properties,
        "additionalProperties": False,
    }


def _boolean():
    return {"type": "boolean"}


def _integer(minimum=None, maximum=None):
    schema = {"type": "integer"}
    if minimum is not None: schema["minimum"] = minimum
    if maximum is not None: schema["maximum"] = maximum
    return schema


def _string(enum=None, minLength=None):
    schema = {"type": "string"}
    if enum is not None:        schema["enum"] = enum
    if minLength is not None:   schema["minLength"] = minLength
    return schema


def _toggleable(properties=None):
    merged = {"Enabled": _boolean()}
    if properties:
        merged.update(properties)
    return _object(merged)


# ---------------------------------------------------------------------------
# The schema (matches what the Electron GUI emits)
# ---------------------------------------------------------------------------

ITEM_VALUE_MIN = 0
ITEM_VALUE_MAX = 10000
SPAWN_RATE_MIN = 1
SPAWN_RATE_MAX = 100


SETTINGS_SCHEMA = _object({
    "general": _object(
        {
            "InputFile":  _string(minLength=1),
            "OutputFile": _string(minLength=1),
            "LogLevel":   _string(["full", "casual", "race"]),
            "Seed":       {"type": ["string", "integer"]},
            "Hash":       _string(),
        },
        required=["InputFile", "OutputFile", "LogLevel"],
    ),
    "digimon": _toggleable({
        "DroppedItem":          _boolean(),
        "DropRate":             _boolean(),
        "MatchValue":           _boolean(),
        "ValuableItemCutoff":   _integer(ITEM_VALUE_MIN, ITEM_VALUE_MAX),
    }),
    "techs": _toggleable({
        "RandomizationMode": _string(["shuffle", "random"]),
        "Power":             _boolean(),
        "Cost":              _boolean(),
        "Accuracy":          _boolean(),
        "Effect":            _boolean(),
        "EffectChance":      _boolean(),
        "TypeEffectiveness": _boolean(),
    }),
    "starter": _toggleable({
        "UseWeakestTech": _boolean(),
        "Fresh":          _boolean(),
        "InTraining":     _boolean(),
        "Rookie":         _boolean(),
        "Champion":       _boolean(),
        "Ultimate":       _boolean(),
        "Digimon":        _string(),
    }),
    "recruitment": _toggleable(),
    "chests": _toggleable({
        "AllowEvolutionItems": _boolean(),
    }),
    "tokomon": _toggleable({
        "ConsumableOnly": _boolean(),
    }),
    "techGifts": _toggleable(),
    "mapItems": _toggleable({
        "FoodOnly":           _boolean(),
        "MatchValue":         _boolean(),
        "ValuableItemCutoff": _integer(ITEM_VALUE_MIN, ITEM_VALUE_MAX),
    }),
    "evolution": _toggleable({
        "Requirements":      _boolean(),
        "SpecialEvolutions": _boolean(),
        "ObtainAllMode":     _boolean(),
    }),
    "patches": _toggleable({
        "EvoItemStatGain":     _boolean(),
        "QuestItemsDroppable": _boolean(),
        "BrainTrainTierOne":   _boolean(),
        "JukeboxGlitch":       _boolean(),
        "IncreaseLearnChance": _boolean(),
        "SpawnRateEnabled":    {"type": ["boolean", "string"]},
        "SpawnRate":           _integer(SPAWN_RATE_MIN, SPAWN_RATE_MAX),
        "ShowHashIntro":       _boolean(),
        "SkipIntro":           _boolean(),
        "Woah":                _boolean(),
        "Gabu":                _boolean(),
        "Softlock":            _boolean(),
        "UnlockAreas":         _boolean(),
        "UnrigSlots":          _boolean(),
        "LearnMoveAndCommand": _boolean(),
        "FixDVChips":          _boolean(),
        "HappyVending":        _boolean(),
    }),
})
