# Author: Christoph Merscher <dev@fmerscher.com>

"""Static UI layout: tabs → sections → elements.

Pure-data port of the legacy Electron ``gui/src/constants.ts``.  Every
checkbox label, every slider range, every tooltip lives here.  The
widget layer (added in later commits) walks this structure to build the
Qt UI.

Why a data table instead of hand-written widgets?

* Adding a new randomiser setting becomes: add a dataclass field +
  add a row here.  No new ``QCheckBox(...)`` boilerplate, no per-tab
  edits.
* The shape of the table is verified against ``SettingsModel`` by
  ``tests/test_gui_section_config.py`` so a typo in an ``attribute``
  fails CI instead of producing a silently broken widget.
* The same table can drive a future programmatic preset / dry-run
  helper without touching the widgets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from gui_qt.settings_model import (
    ITEM_VALUE_MAX,
    ITEM_VALUE_MIN,
    SPAWN_RATE_MAX,
    SPAWN_RATE_MIN,
)


# ---------------------------------------------------------------------------
# Element / section / tab dataclasses
# ---------------------------------------------------------------------------

class InputType(Enum):
    """The widget variant for a single :class:`ElementConfig`."""

    CHECKBOX    = auto()
    SLIDER      = auto()
    MULTISELECT = auto()   # Radio-group with N mutually exclusive options.
    DROPDOWN    = auto()


@dataclass(frozen=True)
class ElementConfig:
    """One control inside a section."""

    attribute:        str                    # name of the dataclass field on the section
    input_type:       InputType
    tooltip:          str
    label:            str | None = None
    min_value:        int | None = None      # SLIDER only
    max_value:        int | None = None      # SLIDER only
    options:          tuple[str, ...] = ()   # MULTISELECT / DROPDOWN values
    option_labels:    tuple[str, ...] = ()   # MULTISELECT display labels (parallel to options)
    placeholder:      str | None = None      # DROPDOWN placeholder option


@dataclass(frozen=True)
class SectionConfig:
    """One card in the UI; binds a tooltip + elements to a section
    attribute on :class:`gui_qt.settings_model.SettingsModel`."""

    title:        str
    tooltip:      str
    model_attr:   str                       # attribute on SettingsModel (e.g. "Digimon")
    elements:     tuple[ElementConfig, ...] = ()


@dataclass(frozen=True)
class TabConfig:
    """One tab in the main window."""

    title:    str
    sections: tuple[SectionConfig, ...]


# ---------------------------------------------------------------------------
# Digimon roster (used by the starter dropdown)
# ---------------------------------------------------------------------------

DIGIMON_NAMES: tuple[str, ...] = (
    "Botamon", "Koromon", "Agumon", "Betamon", "Greymon", "Devimon",
    "Airdramon", "Tyrannomon", "Meramon", "Seadramon", "Numemon",
    "MetalGreymon", "Mamemon", "Monzaemon", "Punimon", "Tsunomon",
    "Gabumon", "Elecmon", "Kabuterimon", "Angemon", "Birdramon",
    "Garurumon", "Frigimon", "Whamon", "Vegiemon", "SkullGreymon",
    "MetalMamemon", "Vademon", "Poyomon", "Tokomon", "Patamon",
    "Kunemon", "Unimon", "Ogremon", "Shellmon", "Centarumon", "Bakemon",
    "Drimogemon", "Sukamon", "Andromon", "Giromon", "Etemon", "Yuramon",
    "Tanemon", "Biyomon", "Palmon", "Monochromon", "Leomon", "Coelamon",
    "Kokatorimon", "Kuwagamon", "Mojyamon", "Nanimon", "Megadramon",
    "Piximon", "Digitamamon", "Penguinmon", "Ninjamon", "Phoenixmon",
    "H-Kabuterimon", "MegaSeadramon", "WereGarurumon", "Panjyamon",
    "Gigadramon", "MetalEtemon",
)


# ---------------------------------------------------------------------------
# Section tooltips
# ---------------------------------------------------------------------------

_STARTER_TOOLTIP = (
    "Enable starter randomization. This will select two random rookies to "
    "replace the starting partner digimon, Agumon and Gabumon. They will "
    "each be assigned a random starting tech from the new starter's pool "
    "of learnable techniques."
)

_DIGIMON_DATA_TOOLTIP = "Enable digimon data randomization."

_TECH_DATA_TOOLTIP = "Enable technique data randomization."

_EVOLUTION_TOOLTIP = (
    "Enable digivolution tree randomization. Randomizes which digimon each "
    "digimon can randomize into. Each fresh will get 1 target, each "
    "in-training will get 2 targets, each rookie gets 4-6 targets, and each "
    "champion gets 1-2 targets. Unless 'Obtain All' is set, not all "
    "playable digimon are guaranteed to be obtainable through natural "
    "digivolution."
)

_CHESTS_TOOLTIP = (
    "Enable item chest contents randomization. This will randomize the "
    "item contained in each of the 'computers'. Any item except "
    "digivolution items or quest items can be randomized into chests. "
    "Quest items include, for example, the Mansion Key, the Gear, and the "
    "stone for the Leomon quest."
)

_TOKOMON_TOOLTIP = (
    "Randomize the items given by Tokomon at the start of the game. This "
    "will by default include only consumable, non-quest items. It also "
    "does not include digivolution items. Tokomon will give 1-3 copies of "
    "6 different items chosen at random, with less valuable items being "
    "more likely to come in larger quantities."
)

_MAP_ITEM_TOOLTIP = (
    "Randomize items that spawn on maps (such as Digimushrooms). Only "
    "non-quest consumable items will be selected. Does not allow "
    "digivolution items to spawn. Uses the 'valuable item threshold' to "
    "exchange vanilla map items for similar-value random items. This "
    "helps preserve common items being typically less valuable than rare "
    "items. This setting affects the items that spawn in Centarumon's "
    "maze."
)

_RECRUIT_TOOLTIP = (
    "Enable recruitment randomization. Randomizes which recruit shows up "
    "in town when you recruit one. For example, it is possible to have "
    "Whamon show up in town (thus opening the dock to Factorial Town) "
    "when Bakemon is recruited. WARNING: poor luck can currently create a "
    "seed that cannot be completed for 100PP. The following recruits are "
    "not randomized, but will be supported later: Palmon, Vegiemon, "
    "Greymon, Birdramon, Centarumon, Angemon, and Monzaemon. The "
    "following cannot be randomized: Agumon, Airdramon, and MetalGreymon."
)

_TECH_GIFT_TOOLTIP = (
    "Randomize the three techniques that Seadramon can teach you, as well "
    "the one that can be taught in Beetle Land (Bug, in vanilla). They "
    "will still only be able to teach you a move that your current "
    "digimon can learn, so if you cannot learn the move then nothing will "
    "happen. Seadramon will teach his three techs in order, so if you "
    "already know the first you will get the second, and so on. If you "
    "know all three already, he will teach you nothing."
)

_PATCH_TOOLTIP = "Various patches to improve different aspects of the game."


# ---------------------------------------------------------------------------
# Element tooltips (one per setting, kept verbatim from constants.ts)
# ---------------------------------------------------------------------------

_TIP_STARTER_USE_WEAKEST = (
    "When this is enabled, the randomized starter will receive the lowest "
    "tier damaging move that it can use. NOTE: this does not mean the "
    "WEAKEST tech, it means the first tech you would learn from brain "
    "training (e.g. Spit Fire, Tear Drop)."
)

_TIP_STARTER_DIGIMON = (
    "Set starter digimon. Leave unchanged or select 'Random' to randomize "
    "from the selected levels. This will only set the DAY starter, the "
    "NIGHT starter will be randomized according to other selections."
)

_TIP_STARTER_LEVEL = (
    "Include {level} digimon in starter options. If no options are "
    "selected, only rookies will be included."
)

_TIP_DROPPED_ITEM = (
    "Randomize the item dropped by a digimon when it is defeated. Uses "
    "the 'valuable item threshold' to exchange vanilla dropped items for "
    "similar-value random items."
)

_TIP_DROP_RATE = (
    "Randomize the chance that an enemy will drop an item. Tends to "
    "prefer small changes from vanilla values, but will sometimes become "
    "much more frequent. 100% drop rates will remain 100%."
)

_TIP_MATCH_VALUE_DIGI = (
    "Randomize valuable drops to different valuable drops and lower value "
    "drops to similar value."
)

_TIP_VALUABLE_CUTOFF_DIGI = (
    "Set the threshold value for the cutoff between high and low value "
    "items. Maximum and minimum values for this field will behave the "
    "same as disabling this option."
)

_TIP_TECH_MODE = (
    "Mode of randomization for technique data. In general, 'Shuffle' "
    "keeps the vanilla values and shuffles them around. Meanwhile, "
    "'Random' generates all-new random values. Hover individual features "
    "to see how these options affect them."
)

_TIP_TECH_POWER = (
    "Randomize the power of each tech. When mode is 'Shuffle', the power "
    "of all techs will be shuffled amongst themselves. When mode is "
    "'Random', techs will be assigned a random power ranging from 30% "
    "below the weakest vanilla tech and 999, the max possible value."
)

_TIP_TECH_COST = (
    "Randomize the MP cost of each tech. When mode is 'Shuffle', the mp "
    "cost of all techs will be shuffled amongst themselves. When mode is "
    "'Random', techs will be assigned a random cost calculated from the "
    "power of the tech, ranging from 10% to 140% of the power."
)

_TIP_TECH_ACCURACY = (
    "Randomize the accuracy of each tech. When mode is 'Shuffle', the "
    "accuracy of all techs will be shuffled amongst themselves. When mode "
    "is 'Random', techs will be assigned a random accuracy ranging from "
    "33 to 100. The vast majority will fall between 50 and 100, with just "
    "over 10% being 100% and just under 10% being under 50."
)

_TIP_TECH_EFFECT = (
    "Randomize the status effect of each tech. This will make about 50% "
    "off all techniques have some status effect, and they will be roughly "
    "evenly distributed between Flat, Poison, Confusion, and Stun. This "
    "option is not affect by the mode."
)

_TIP_TECH_EFFECT_CHANCE = (
    "Randomize the chance of a status effect being inflicted for each "
    "tech. Techs will be assigned a random value between 1% and 70%. This "
    "option is not affected by the mode."
)

_TIP_TECH_TYPE_EFFECT = (
    "Randomizes the type effectiveness of different attributes. The "
    "values will be between 2 and 20, as in vanilla."
)

_TIP_EVO_REQUIREMENTS = (
    "Randomize the requirements to digivolve to each digimon. "
    "Requirements will generally look fairly similar to vanilla values, "
    "but totally random. All digimon will have a stat requirement, a care "
    "mistake required (min or max), a weight requirement (within 5 of), "
    "and a techs learned requirement. Digimon may randomly have other "
    "bonus requirements, including max/min battles fought, discipline, "
    "and happiness."
)

_TIP_EVO_SPECIAL = (
    "Randomize the result of some special evolutions. Specifically, this "
    "currently includes death digivolutions (such as Bakemon and "
    "Devimon), MetalMamemon's 'upgrade' digivolutions, and the Toy Town "
    "Monzemon suit. To preserve completion, Toy Town will be accessible "
    "by whatever the suit digivolves Numemon into, rather than by "
    "Monzaemon."
)

_TIP_EVO_OBTAIN_ALL = (
    "When this option is enabled, randomized evolutions are guaranteed to "
    "be organized in such a way that all natural evolution digimon can "
    "still be obtained naturally through evolution. That means each "
    "in-training, rookie, champion, and ultimate level digimon will have "
    "at least one digimon in the previous level that can naturally "
    "digivolve to it."
)

_TIP_CHEST_ALLOW_EVO = (
    "When this is enabled, digivolution items will be included in the "
    "available pool of items to be randomized into chests."
)

_TIP_TOKOMON_CONSUMABLE = (
    "When this is enabled, only consumable items will be given. This "
    "disallows items like Enemy Repel, Training Manual, and similar."
)

_TIP_MAP_FOOD_ONLY = (
    "Locks the randomly spawned items to be food only. This will only "
    "affect map spawns that are food in vanilla; thus, the weird spawns "
    "in Centarumon's maze will not be forced to be food with this "
    "setting."
)

_TIP_MAP_MATCH_VALUE = (
    "Randomize valuable spawns to different valuable drops and lower "
    "value drops to similar value. Helps preserve rare item spawns being "
    "generally more valuable than common ones."
)

_TIP_MAP_VALUABLE_CUTOFF = (
    "Set the threshold value for the cutoff between high and low value "
    "items. Maximum and minimum values for this field will behave the "
    "same as disabling this option. Default value is 1000, this value "
    "seems to work most effectively for preserving the rare/common split."
)

_TIP_PATCH_EVO_ITEM_STAT = (
    "Enable this to cause digivolution items to actually grant stats upon "
    "digivolution. In vanilla, digivolving does not grant any stats gain "
    "when it happens through an item."
)

_TIP_PATCH_QUEST_DROPPABLE = (
    "Enable this to allow dropping quest items (like the Mansion Key) "
    "from your inventory. In vanilla, these items cannot be dropped and "
    "must be deposited in the bank to get them out of your inventory."
)

_TIP_PATCH_BRAIN_TIER_ONE = (
    "Enable this to fix the bug in vanilla that prevents learning the "
    "lowest tier move for each specialty via brain training. For example, "
    "in vanilla it is impossible to learn Spit Fire via brain training. "
    "This patch makes that possible and assigns the tier one moves a 30% "
    "learn chance."
)

_TIP_PATCH_JUKEBOX = (
    "Enable this to fix the crash that happens when viewing the jukebox "
    "track list in the English version."
)

_TIP_PATCH_BATTLE_LEARN = (
    "Double the chance to learn techs after battle. This makes some techs "
    "learnable very quickly. This setting is helpful for a race "
    "environment, making it less likely to be long-term stuck with a "
    "terrible technique."
)

_TIP_PATCH_WOAH = (
    "Enable this to change the 'Woah!' text when picking up an item to "
    "say 'Oh shit!' instead. This has no real effect and is purely "
    "cosmetic."
)

_TIP_PATCH_GABU = (
    "This makes Gabumon as powerful as he was truly meant to be. Not for "
    "the faint of heart. Good luck."
)

_TIP_PATCH_HASH_INTRO = (
    "Show a hash of the settings used on the Jijimon intro screen when "
    "creating a new game. This is useful for on-the-fly verification that "
    "each race participant is using the same settings (and seed)."
)

_TIP_PATCH_SKIP_INTRO = (
    "Enable this to cut out the majority (as much as possible) of the "
    "intro dialogue when creating a new game. Does not conflict with "
    "'Display Settings' option."
)

_TIP_PATCH_UNLOCK = (
    "Remove digimon type (Vaccine, Data, Virus, Monzaemon) entry barriers "
    "to Greylord's Mansion, Ice Sanctuary and Toy Town, allowing any "
    "digimon to enter. This option helps alleviate the difficulty of "
    "getting a particular type of digimon when digivolution is random, "
    "for instance."
)

_TIP_PATCH_UNRIG_SLOTS = (
    "In Digimon World, the bonus try slots are not fair. When you start "
    "up the slots, the game has already decided whether or not you will "
    "be allowed to win, no matter how perfect you time it (though it "
    "still won't do everything for you, even if it is planning to let you "
    "win). This option removes that 'feature' and makes the bonus try "
    "slots fair and purely skill-based."
)

_TIP_PATCH_SPAWN_ENABLED = (
    "Enable this to set the chance for Mamemon, MetalMamemon, Piximon, "
    "and Otamamon appearing on their respective maps."
)

_TIP_PATCH_SPAWN_RATE = (
    "The percentage chance for the digimon to spawn. Disable to use "
    "vanilla behavior."
)

_TIP_PATCH_SOFTLOCK = "This fixes some movement related softlocks."

_TIP_PATCH_LEARN_MOVE_AND_CMD = (
    "This patch disables the text for learning new commands, allowing you "
    "to learn a command and a technique at the same session. This mainly "
    "helps if you're doing Bonus Tries to obtain new moves."
)

_TIP_PATCH_FIX_DV_CHIPS = (
    "Fixes DV Chip descriptions, to actually tell you what they do."
)

_TIP_PATCH_HAPPY_VENDING = (
    "Replaces Meat trade with a Happymushroom trade at the vending "
    "machine at Dragon Eye Lake's top area."
)


# ---------------------------------------------------------------------------
# Section definitions
# ---------------------------------------------------------------------------

STARTER_SECTION = SectionConfig(
    title="Starter",
    tooltip=_STARTER_TOOLTIP,
    model_attr="Starter",
    elements=(
        ElementConfig("UseWeakestTech", InputType.CHECKBOX, _TIP_STARTER_USE_WEAKEST,
                      label="Use Weakest Tech"),
        ElementConfig("Digimon", InputType.DROPDOWN, _TIP_STARTER_DIGIMON,
                      placeholder="Select Starter Digimon",
                      options=("Random",) + DIGIMON_NAMES),
        ElementConfig("Fresh",      InputType.CHECKBOX, _TIP_STARTER_LEVEL.format(level="Fresh"),       label="Include Fresh"),
        ElementConfig("InTraining", InputType.CHECKBOX, _TIP_STARTER_LEVEL.format(level="In-Training"), label="Include In-Training"),
        ElementConfig("Rookie",     InputType.CHECKBOX, _TIP_STARTER_LEVEL.format(level="Rookie"),      label="Include Rookie"),
        ElementConfig("Champion",   InputType.CHECKBOX, _TIP_STARTER_LEVEL.format(level="Champion"),    label="Include Champion"),
        ElementConfig("Ultimate",   InputType.CHECKBOX, _TIP_STARTER_LEVEL.format(level="Ultimate"),    label="Include Ultimate"),
    ),
)

DIGIMON_DATA_SECTION = SectionConfig(
    title="Digimon Data",
    tooltip=_DIGIMON_DATA_TOOLTIP,
    model_attr="Digimon",
    elements=(
        ElementConfig("DroppedItem", InputType.CHECKBOX, _TIP_DROPPED_ITEM,         label="Item Dropped"),
        ElementConfig("DropRate",    InputType.CHECKBOX, _TIP_DROP_RATE,            label="Drop Rate"),
        ElementConfig("MatchValue",  InputType.CHECKBOX, _TIP_MATCH_VALUE_DIGI,     label="Match Valuable Drops"),
        ElementConfig("ValuableItemCutoff", InputType.SLIDER, _TIP_VALUABLE_CUTOFF_DIGI,
                      min_value=ITEM_VALUE_MIN, max_value=ITEM_VALUE_MAX),
    ),
)

TECH_DATA_SECTION = SectionConfig(
    title="Technique Data",
    tooltip=_TECH_DATA_TOOLTIP,
    model_attr="Techs",
    elements=(
        ElementConfig("RandomizationMode", InputType.MULTISELECT, _TIP_TECH_MODE,
                      label="Randomization Mode",
                      options=("shuffle", "random"),
                      option_labels=("Shuffle", "Random")),
        ElementConfig("Power",             InputType.CHECKBOX, _TIP_TECH_POWER,         label="Power"),
        ElementConfig("Cost",              InputType.CHECKBOX, _TIP_TECH_COST,          label="MP Cost"),
        ElementConfig("Accuracy",          InputType.CHECKBOX, _TIP_TECH_ACCURACY,      label="Accuracy"),
        ElementConfig("Effect",            InputType.CHECKBOX, _TIP_TECH_EFFECT,        label="Status Effect"),
        ElementConfig("EffectChance",      InputType.CHECKBOX, _TIP_TECH_EFFECT_CHANCE, label="Status Effect Chance"),
        ElementConfig("TypeEffectiveness", InputType.CHECKBOX, _TIP_TECH_TYPE_EFFECT,   label="Type Effectiveness"),
    ),
)

EVOLUTION_SECTION = SectionConfig(
    title="Digivolutions",
    tooltip=_EVOLUTION_TOOLTIP,
    model_attr="Evolution",
    elements=(
        ElementConfig("Requirements",      InputType.CHECKBOX, _TIP_EVO_REQUIREMENTS, label="Requirements"),
        ElementConfig("SpecialEvolutions", InputType.CHECKBOX, _TIP_EVO_SPECIAL,      label="Special Digivolutions"),
        ElementConfig("ObtainAllMode",     InputType.CHECKBOX, _TIP_EVO_OBTAIN_ALL,   label="Obtain All"),
    ),
)

CHESTS_SECTION = SectionConfig(
    title="Chest Contents",
    tooltip=_CHESTS_TOOLTIP,
    model_attr="Chests",
    elements=(
        ElementConfig("AllowEvolutionItems", InputType.CHECKBOX, _TIP_CHEST_ALLOW_EVO,
                      label="Digivolution Items"),
    ),
)

TOKOMON_SECTION = SectionConfig(
    title="Tokomon Items",
    tooltip=_TOKOMON_TOOLTIP,
    model_attr="Tokomon",
    elements=(
        ElementConfig("ConsumableOnly", InputType.CHECKBOX, _TIP_TOKOMON_CONSUMABLE,
                      label="Consumable Only"),
    ),
)

MAP_ITEM_SECTION = SectionConfig(
    title="Map Item Spawns",
    tooltip=_MAP_ITEM_TOOLTIP,
    model_attr="MapItems",
    elements=(
        ElementConfig("FoodOnly",   InputType.CHECKBOX, _TIP_MAP_FOOD_ONLY,   label="Food Items Only"),
        ElementConfig("MatchValue", InputType.CHECKBOX, _TIP_MAP_MATCH_VALUE, label="Match Rare Spawns"),
        ElementConfig("ValuableItemCutoff", InputType.SLIDER, _TIP_MAP_VALUABLE_CUTOFF,
                      min_value=ITEM_VALUE_MIN, max_value=ITEM_VALUE_MAX),
    ),
)

RECRUITMENT_SECTION = SectionConfig(
    title="Recruitment",
    tooltip=_RECRUIT_TOOLTIP,
    model_attr="Recruitment",
    elements=(),
)

TECH_GIFTS_SECTION = SectionConfig(
    title="Technique Gifts",
    tooltip=_TECH_GIFT_TOOLTIP,
    model_attr="TechGifts",
    elements=(),
)

PATCHES_SECTION = SectionConfig(
    title="Miscellaneous Patches",
    tooltip=_PATCH_TOOLTIP,
    model_attr="Patches",
    elements=(
        ElementConfig("EvoItemStatGain",     InputType.CHECKBOX, _TIP_PATCH_EVO_ITEM_STAT,     label="Item Stat Gain"),
        ElementConfig("QuestItemsDroppable", InputType.CHECKBOX, _TIP_PATCH_QUEST_DROPPABLE,   label="Drop Quest Items"),
        ElementConfig("BrainTrainTierOne",   InputType.CHECKBOX, _TIP_PATCH_BRAIN_TIER_ONE,    label="Brain Train Learning"),
        ElementConfig("JukeboxGlitch",       InputType.CHECKBOX, _TIP_PATCH_JUKEBOX,           label="Giromon Glitch"),
        ElementConfig("IncreaseLearnChance", InputType.CHECKBOX, _TIP_PATCH_BATTLE_LEARN,      label="Battle Learn Chance"),
        ElementConfig("Woah",                InputType.CHECKBOX, _TIP_PATCH_WOAH,              label="Change Woah Text"),
        ElementConfig("Gabu",                InputType.CHECKBOX, _TIP_PATCH_GABU,              label="Gabumon Mode"),
        ElementConfig("ShowHashIntro",       InputType.CHECKBOX, _TIP_PATCH_HASH_INTRO,        label="Display Settings"),
        ElementConfig("SkipIntro",           InputType.CHECKBOX, _TIP_PATCH_SKIP_INTRO,        label="Skip Intro"),
        ElementConfig("UnlockAreas",         InputType.CHECKBOX, _TIP_PATCH_UNLOCK,            label="Unlock Areas"),
        ElementConfig("UnrigSlots",          InputType.CHECKBOX, _TIP_PATCH_UNRIG_SLOTS,       label="Fair Bonus Try"),
        ElementConfig("SpawnRateEnabled",    InputType.CHECKBOX, _TIP_PATCH_SPAWN_ENABLED,     label="Recruit Spawn Rate"),
        ElementConfig("SpawnRate",           InputType.SLIDER,   _TIP_PATCH_SPAWN_RATE,        label="Recruit Spawn Rate",
                      min_value=SPAWN_RATE_MIN, max_value=SPAWN_RATE_MAX),
        ElementConfig("Softlock",            InputType.CHECKBOX, _TIP_PATCH_SOFTLOCK,          label="Fix Softlocks"),
        ElementConfig("LearnMoveAndCommand", InputType.CHECKBOX, _TIP_PATCH_LEARN_MOVE_AND_CMD, label="Fix Brains Learning"),
        ElementConfig("FixDVChips",          InputType.CHECKBOX, _TIP_PATCH_FIX_DV_CHIPS,      label="Fix DV Chip descriptions"),
        ElementConfig("HappyVending",        InputType.CHECKBOX, _TIP_PATCH_HAPPY_VENDING,     label="Happymushroom Vending"),
    ),
)


# ---------------------------------------------------------------------------
# Tab layout (mirrors gui/src/MainContainer.tsx)
# ---------------------------------------------------------------------------

TABS: tuple[TabConfig, ...] = (
    TabConfig(
        title="Digimon",
        sections=(DIGIMON_DATA_SECTION, EVOLUTION_SECTION, TECH_DATA_SECTION),
    ),
    TabConfig(
        title="Items",
        sections=(MAP_ITEM_SECTION, CHESTS_SECTION, TOKOMON_SECTION),
    ),
    TabConfig(
        title="Progression",
        sections=(STARTER_SECTION, RECRUITMENT_SECTION, TECH_GIFTS_SECTION),
    ),
    TabConfig(
        title="Misc. Patches",
        sections=(PATCHES_SECTION,),
    ),
)
