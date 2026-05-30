# Digimon World Randomizer

> **Original author and project creator: [Tristan Challener](mailto:challenert@gmail.com)**.
> The entire ROM-modification work, the binary offset research, the
> Electron GUI, and every randomisation feature listed below originate from
> Tristan's project. This repository is a refactored fork that preserves
> 100% of the original behaviour. All credit for the underlying
> randomizer belongs to him.
>
> Refactor and modernisation maintainer: [Christoph Merscher](mailto:dev@fmerscher.com).

A data randomizer for **Digimon World 1 (PSX)**, patches a clean ROM image
to produce a fresh, unique playthrough. Randomise starters, evolutions,
techniques, drops, chest contents, map items, recruits, special
evolutions, and apply a long list of quality-of-life patches.

---

## Table of contents

- [Quickstart](#quickstart)
  - [Using the GUI (Windows)](#using-the-gui-windows)
  - [Using the CLI (cross-platform)](#using-the-cli-cross-platform)
- [What you can randomise](#what-you-can-randomise)
  - [1. Starter digimon](#1-starter-digimon)
  - [2. Digimon data (drops + drop rates)](#2-digimon-data-drops--drop-rates)
  - [3. Technique data](#3-technique-data)
  - [4. Evolutions](#4-evolutions)
  - [5. Recruitments](#5-recruitments)
  - [6. Chest contents](#6-chest-contents)
  - [7. Tokomon gifts](#7-tokomon-gifts)
  - [8. Map item spawns](#8-map-item-spawns)
  - [9. Technique gifts (Seadramon + Beetle Land)](#9-technique-gifts-seadramon--beetle-land)
- [Quality-of-life patches](#quality-of-life-patches)
- [Race mode](#race-mode)
- [Settings file format](#settings-file-format)
- [Logging](#logging)
- [Project architecture](#project-architecture)
- [Development](#development)
- [Changelog](#changelog)

---

## Quickstart

You need a clean **Digimon World 1 (PSX, USA)** ROM image in `.bin` format.
The randomizer **does not** distribute the ROM, you must supply your own.

### Using the GUI (Windows)

1. Download the latest release of `digimon_randomizer.zip`.
2. Unzip wherever you like.
3. Launch `digimon_randomize.exe`.
4. Pick the input ROM (your clean `.bin`) and an output ROM path.
5. Toggle the features you want, every option has a hover tooltip.
6. Click **Randomize**.
7. Load the produced `.bin` in your preferred PSX emulator.

### Using the CLI (cross-platform)

Requires **Python 3.11+** (3.12 / 3.13 supported).

```bash
python digimon_randomize.py -settings '<json-settings-string>'
```

The `-settings` argument is the full JSON settings object. The GUI
writes this file for you (`settings.ini`), but you can also generate or
hand-write it, see [Settings file format](#settings-file-format).

A minimal CLI run:

```bash
python digimon_randomize.py -settings "$(cat my-settings.json)"
```

The randomizer writes the new ROM to `OutputFile` and a companion log to
`randomize-<seed>.log` in the current directory.

---

## What you can randomise

Every section below maps 1:1 to a key in the settings JSON. Each section
has an `Enabled` flag plus per-feature toggles. Sections you don't
enable are passed through untouched.

### 1. Starter digimon

Settings key: `starter` &nbsp; · &nbsp; Code:
[`digimon/randomization/starters.py`](digimon/randomization/starters.py)

Picks two random different starter digimon to replace Agumon and
Gabumon. Each starter is also assigned a random starting tech from its
own learnable-tech pool.

| Option | What it does |
|---|---|
| `Enabled` | Master switch for starter randomization. |
| `UseWeakestTech` | When on, each starter gets the **lowest-tier damaging** tech it can use (think Spit Fire, Tear Drop), useful for racing. When off, picks a random learnable damaging tech. |
| `Digimon` | Force a specific day-starter (the night-starter is still random). Use `"Random"` for full randomization. |
| `Fresh`, `InTraining`, `Rookie`, `Champion`, `Ultimate` | Per-level toggles for which evolution stages can be picked as starters. If none are selected, only Rookies are included. |

### 2. Digimon data (drops + drop rates)

Settings key: `digimon` &nbsp; · &nbsp; Code:
[`digimon/randomization/digimon_data.py`](digimon/randomization/digimon_data.py)

Randomises what each enemy digimon drops, and (optionally) how often.

| Option | What it does |
|---|---|
| `Enabled` | Master switch. |
| `DroppedItem` | Randomise the item each enemy drops. Picks similar-value items so vanilla cheap drops stay cheap (when `MatchValue` is on). |
| `DropRate` | Randomise the drop chance. Tends to wobble around the vanilla value but can occasionally produce a much higher rate. **Always-100 % drops stay at 100 %.** |
| `MatchValue` | Use the cutoff below to keep cheap-for-cheap and expensive-for-expensive when swapping drops. |
| `ValuableItemCutoff` | Price threshold (in bits) that separates "cheap" and "expensive" items. Default `1000`. Min/max produces the same behaviour as disabling `MatchValue`. |

### 3. Technique data

Settings key: `techs` &nbsp; · &nbsp; Code:
[`digimon/randomization/tech_data.py`](digimon/randomization/tech_data.py)

Randomises the stats (power, MP cost, accuracy, status effect) of every
learnable technique.

| Option | What it does |
|---|---|
| `Enabled` | Master switch. |
| `RandomizationMode` | `"shuffle"` keeps vanilla values and reshuffles them between techs. `"random"` first shuffles, then jitters each value within a sensible range. |
| `Power` | Randomise tech power. Shuffle: swap between techs. Random: 70-130 % of vanilla per tech, capped at 999. |
| `Cost` | Randomise MP cost. Shuffle: swap between techs. Random: 10-140 % of the tech's power. |
| `Accuracy` | Randomise accuracy. Shuffle: swap between techs. Random: weighted roll, most land 50-100, a few are 100, a few are under 50. |
| `Effect` | ~50 % chance per tech to gain a random status effect (Poison, Confuse, Stun, Flat). Not affected by the mode. |
| `EffectChance` | If a tech has an effect, give it a random 1-70 % proc chance. |
| `TypeEffectiveness` | Randomise the 7×7 type-effectiveness chart. Each cell picks from `{2, 5, 10, 15, 20}`. |

### 4. Evolutions

Settings key: `evolution` &nbsp; · &nbsp; Code:
[`digimon/randomization/evolutions.py`](digimon/randomization/evolutions.py)
+ [`evolution_requirements.py`](digimon/randomization/evolution_requirements.py)
+ [`special_evolutions.py`](digimon/randomization/special_evolutions.py)

Rebuilds the entire evolution tree. Each fresh gets 1 target, each
in-training gets 2 targets, each rookie gets 4-6 targets, each champion
gets 1-2 targets.

| Option | What it does |
|---|---|
| `Enabled` | Master switch. |
| `Requirements` | Randomise the stat / weight / care-mistake / battle requirements to evolve to each digimon. Champion + Ultimate requirements roughly mirror vanilla difficulty curves. |
| `SpecialEvolutions` | Randomise the result of special evolutions: Bakemon, Devimon, Monzaemon (Toy Town suit), MetalMamemon, Giromon, SkullGreymon, Phoenixmon, Vademon, Sukamon, Nanimon, Coelamon, Kunemon, Monochromon, Ninjamon, Airdramon. Toy Town stays accessible via whatever the suit turns Numemon into. |
| `ObtainAllMode` | Guarantees every natural-evolution digimon is reachable through a random evo path. Without this, some digimon can become unobtainable through natural evolution. |

### 5. Recruitments

Settings key: `recruitment` &nbsp; · &nbsp; Code:
[`digimon/randomization/recruitments.py`](digimon/randomization/recruitments.py)

Shuffles which digimon shows up in town when you complete each recruit
quest. For example, beating Bakemon could now make Whamon (Factorial
Town access) appear. The randomizer automatically rejects shuffles that
would softlock the run (Factorial-Town gatekeeper logic), automatically
queues the **PP-calculation rewrite patch** so prosperity points stay
correct for the substituted recruits, and queues the
**Ogremon-softlock patch**.

| Option | What it does |
|---|---|
| `Enabled` | Master switch, no sub-options. |

> ⚠️ **Not randomized:** Palmon, Vegiemon, Greymon, Birdramon, Centarumon,
> Angemon, Monzaemon. **Cannot be randomized:** Agumon, Airdramon,
> MetalGreymon.

### 6. Chest contents

Settings key: `chests` &nbsp; · &nbsp; Code:
[`digimon/randomization/chests.py`](digimon/randomization/chests.py)

Randomises the item inside every "computer" chest in the game. Quest
items (Mansion Key, Gear, Leomon stone, …) are excluded so the main
quest can always be finished.

| Option | What it does |
|---|---|
| `Enabled` | Master switch. |
| `AllowEvolutionItems` | Include evolution items (Power Plant, Sage Plant, …) in the random pool. |

### 7. Tokomon gifts

Settings key: `tokomon` &nbsp; · &nbsp; Code:
[`digimon/randomization/tokomon.py`](digimon/randomization/tokomon.py)

Randomises the six starting items Tokomon hands you. Each gift becomes
1-3 copies of a random item, expensive items are weighted to come in
smaller stacks.

| Option | What it does |
|---|---|
| `Enabled` | Master switch. |
| `ConsumableOnly` | Only consumable items qualify (no Enemy Repel, Training Manual, etc). |

### 8. Map item spawns

Settings key: `mapItems` &nbsp; · &nbsp; Code:
[`digimon/randomization/map_items.py`](digimon/randomization/map_items.py)

Randomises every item that spawns on a map (Digimushrooms, MP Floppies,
food drops, etc) including the special items in Centarumon's maze. Only
non-quest consumables are picked.

| Option | What it does |
|---|---|
| `Enabled` | Master switch. |
| `FoodOnly` | Lock food spawns to be swapped only with other food. Doesn't apply to non-food map spawns. |
| `MatchValue` | Preserve cheap-for-cheap / rare-for-rare semantics. |
| `ValuableItemCutoff` | Price threshold; default `1000`. Min/max disables the matching. |

### 9. Technique gifts (Seadramon + Beetle Land)

Settings key: `techGifts` &nbsp; · &nbsp; Code:
[`digimon/randomization/tech_gifts.py`](digimon/randomization/tech_gifts.py)

Randomises the three techs Seadramon can teach plus the Bug-replacement
tech taught in Beetle Land. Seadramon still teaches in order: first
unknown move, then the next, then the next.

| Option | What it does |
|---|---|
| `Enabled` | Master switch, no sub-options. |

---

## Quality-of-life patches

Settings key: `patches` &nbsp; · &nbsp; Code:
[`digimon/rom/patches/`](digimon/rom/patches/)

Each patch is implemented as a self-contained Strategy class, one file
per patch. Two patches (`_evoTargetUnify` and `_resetButton`) are always
applied; the rest are opt-in below.

| Setting | Patch | What it does |
|---|---|---|
| `EvoItemStatGain` | `fixEvoItems` | Evolution items now grant stats + lifetime on use (vanilla grants nothing). |
| `QuestItemsDroppable` | `allowDrop` | Quest items can be dropped from the menu. |
| `BrainTrainTierOne` | `learnTierOne` | Brain training can teach the lowest-tier move of every specialty (Spit Fire, Tear Drop, …) at a 30 % rate. |
| `JukeboxGlitch` | `giromon` | Truncates over-long jukebox track names so the English jukebox stops crashing. |
| `IncreaseLearnChance` | `upLearnChance` | Doubles the chance to learn a tech in battle + brain training; previously-zero brain cells gain a small floor chance. |
| `Woah` | `woah` | Changes the "Woah!" pickup text. |
| `Gabu` | `gabumon` | Boosts enemy Gabumon to ridiculous stats. |
| `ShowHashIntro` | `hash` | Embeds a hash of your settings into Jijimon's intro dialogue, used to verify race participants generated the same ROM. Requires `general.Hash`. |
| `SkipIntro` | `intro` | Skips most of the new-game intro dialogue. |
| `UnlockAreas` | `unlock` | Drops the type-locks on Greylord's Mansion, Ice Sanctuary, and Toy Town so any digimon can enter. |
| `UnrigSlots` | `slots` | Makes the bonus-training slot machine purely skill-based instead of rigged. |
| `SpawnRateEnabled` + `SpawnRate` | `spawn` | Sets the spawn chance for Mamemon, MetalMamemon, Piximon and Otamamon. `SpawnRate` is 1-100. |
| `Softlock` | `softlock` | Fixes four movement-related softlocks (rotation, entityMoveTo, Toy Town, Leomon's cave Nanimon). |
| `LearnMoveAndCommand` | `learnmoveandcommand` | Lets you learn a command **and** a tech in the same brain-training session. |
| `FixDVChips` | `fixDVChips` | Rewrites the DV-chip description text to actually describe what each chip does. |
| `HappyVending` | `happyVending` | Swaps the Dragon Eye Lake vending-machine output for a HappyMushroom trade. ⚠️ Known broken in legacy code; will raise `NameError` if enabled. |
| *always on* | `_evoTargetUnify` | Unifies two near-duplicate evo-target functions to free memory for the reset-button hook. |
| *always on* | `_resetButton` | Adds a button combination that reboots the game. |

When a patch's queued name doesn't match any registered patch, the
randomizer logs an error and continues, see
[`digimon/rom/patches/registry.py`](digimon/rom/patches/registry.py).

---

## Race mode

The randomizer supports **bit-for-bit reproducible** runs across machines
so multiple players can race the same ROM.

1. Pick a seed (or generate one with a normal run and copy it from the log).
2. Set `general.LogLevel` to `"race"` and enable `patches.ShowHashIntro`.
3. Set `general.Hash` to anything, it appears on Jijimon's intro screen so
   you can verify every player's ROM came from the same settings + seed.
4. Share the settings file with everyone.
5. Each participant updates `general.InputFile` / `OutputFile` to their
   own paths and runs the randomizer.
6. All produced `.bin` files will be byte-identical. The Jijimon intro
   will display the same hash for every participant.

Internally, `"race"` mode also burns one RNG step right after seeding.
This guarantees a race ROM is **different** from a casual ROM made from
the same seed, so racers can't reuse a casual run to peek ahead. See
[`digimon/seeding.py`](digimon/seeding.py).

---

## Settings file format

The Electron GUI writes and reads this JSON file. The schema is enforced
by [`digimon/settings/schema.py`](digimon/settings/schema.py).

A minimal example:

```json
{
  "general": {
    "InputFile": "DigimonWorld.bin",
    "OutputFile": "DigimonWorld-randomized.bin",
    "LogLevel": "casual",
    "Seed": "12345",
    "Hash": ""
  },
  "digimon":      { "Enabled": true, "DroppedItem": true, "DropRate": false,
                    "MatchValue": true, "ValuableItemCutoff": 1000 },
  "techs":        { "Enabled": false, "RandomizationMode": "random",
                    "Power": false, "Cost": false, "Accuracy": false,
                    "Effect": false, "EffectChance": false, "TypeEffectiveness": false },
  "starter":      { "Enabled": true, "UseWeakestTech": true, "Digimon": "Random",
                    "Fresh": false, "InTraining": false, "Rookie": true,
                    "Champion": false, "Ultimate": false },
  "recruitment":  { "Enabled": false },
  "chests":       { "Enabled": true, "AllowEvolutionItems": false },
  "tokomon":      { "Enabled": true, "ConsumableOnly": true },
  "techGifts":    { "Enabled": false },
  "mapItems":     { "Enabled": true, "FoodOnly": false,
                    "MatchValue": true, "ValuableItemCutoff": 1000 },
  "evolution":    { "Enabled": true, "Requirements": false,
                    "SpecialEvolutions": true, "ObtainAllMode": true },
  "patches":      { "Enabled": true, "EvoItemStatGain": true,
                    "QuestItemsDroppable": false, "BrainTrainTierOne": true,
                    "JukeboxGlitch": true, "IncreaseLearnChance": false,
                    "SpawnRateEnabled": false, "SpawnRate": 50,
                    "ShowHashIntro": false, "SkipIntro": true, "Woah": false,
                    "Gabu": false, "Softlock": true, "UnlockAreas": false,
                    "UnrigSlots": true, "LearnMoveAndCommand": true,
                    "FixDVChips": true, "HappyVending": false }
}
```

The full schema (every key, every valid value, every cross-field rule) is
defined declaratively in
[`digimon/settings/schema.py:SETTINGS_SCHEMA`](digimon/settings/schema.py).

---

## Logging

The randomizer writes a log file named `randomize-<seed>.log` next to the
output ROM. The verbosity is controlled by `general.LogLevel`:

| Level | What it logs |
|---|---|
| `full` | Every detail: original ROM data, every randomisation change, every patch step. **Use for debugging.** |
| `casual` | Only the changes made + errors. **Good default.** |
| `race` | Same content as `casual`, plus the RNG advance described above. **Use for races.** |

> The log contains spoilers, it lists every chest contents, every
> evolution path, every recruit. Don't open it during a blind race.

---

## Project architecture

The code follows SOLID + DRY with one concern per file. Key directories:

```
digimon_world_randomizer/
├── digimon_randomize.py          # Thin CLI shim → digimon.app.run
├── digimon/
│   ├── app.py                    # Orchestrator: settings → state → randomise → patch → write
│   ├── handler.py                # Facade kept for backward compat
│   ├── seeding.py                # SeedingPolicy (race-mode RNG behaviour)
│   ├── settings/                 # JSON load + schema + adapters + errors
│   ├── rom/
│   │   ├── file.py               # RomFile (binary IO wrapper)
│   │   ├── reader.py             # RomReader, ROM to RomState
│   │   ├── writer.py             # RomWriter, RomState to ROM
│   │   ├── state.py              # RomState dataclass
│   │   ├── struct_codec.py       # Block IO primitives (with exclusions)
│   │   ├── blocks.py             # Block layout descriptors
│   │   ├── script_offsets.py     # Per-script command offsets
│   │   ├── patch_data.py         # Byte payloads for every patch
│   │   └── patches/              # One Strategy class per patch (Factory + Pipeline)
│   ├── models/                   # Digimon / Item / Tech (depend on narrow Protocols)
│   └── randomization/            # One Strategy class per randomiser + shared pickers
├── data/
│   ├── digimon/                  # Enum-based digimon roster + helpers
│   ├── technique/                # Enum-based tech catalogue
│   └── item/                     # Item category enum + ID range helpers
├── log/logger.py                 # Three-tier verbosity logger
├── script/util.py                # Script byte-encoding utilities
├── tests/                        # 69-test pytest/unittest suite
└── gui/                          # Electron GUI (TypeScript)
```

**Design patterns in play:**

- **Strategy**, every patch and every randomiser is a small class
  conforming to a one-method ABC (`Patch.apply`, `Randomizer.apply`).
- **Factory**, patches and randomisers are looked up by name from
  registry dictionaries in
  [`digimon/rom/patches/registry.py`](digimon/rom/patches/registry.py)
  and [`digimon/randomization/pipeline.py`](digimon/randomization/pipeline.py).
- **Pipeline**, `PatchPipeline.apply()` and `RandomizationPipeline.run()`
  iterate their queues in deterministic order.
- **Facade**, `DigimonWorldHandler` wires the subsystems together while
  preserving the historical attribute surface that legacy callers use.
- **Protocol-based DI**, models depend on `NameLookup` and `RosterLookup`
  Protocols instead of the full handler, so they unit-test in isolation.

---

## Development

### Requirements

- Python **3.11+** (3.12 / 3.13 supported).
- For the GUI: Node.js + npm.

### Run the test suite

```bash
python -m unittest discover tests
```

Expected: **69 tests passing**.

### Optional dev dependencies

```bash
pip install -r requirements-dev.txt   # pytest + mypy + ruff
```

### Build the Windows release (GUI + bundled CLI)

```bash
build.bat
```

Produces `dist/digimon_randomizer.zip` containing the Electron GUI and a
PyInstaller-bundled CLI executable.

### Adding a new patch

1. Drop a new module under `digimon/rom/patches/` containing a class
   that inherits `Patch` and defines a unique `name` + an `apply` method.
2. Add an instance of it to the `PATCHES` dict in
   `digimon/rom/patches/registry.py`.
3. (If user-toggleable) add it to the GUI options in
   `gui/src/constants.ts` and to the schema in
   `digimon/settings/schema.py`.

### Adding a new randomiser

1. Drop a new module under `digimon/randomization/` containing a class
   that inherits `Randomizer` and defines an `apply(ctx)` method.
2. Add a step to `RandomizationPipeline.build_from_config` in
   `digimon/randomization/pipeline.py`.
3. (If user-toggleable) update the GUI + schema as above.

---

## Changelog

The full release history lives in [CHANGELOG.md](CHANGELOG.md).

