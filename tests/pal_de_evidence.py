# Author: Christoph Merscher <dev@fmerscher.com>

"""German PAL ROM evidence used by the local layout tests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScriptEvidence:
    """Classified PAL script offsets outside the special-evolution table."""

    name: str
    offsets: tuple[int, ...]
    confidence: str
    note: str


@dataclass(frozen=True)
class PatchEvidence:
    """Classified PAL evidence for optional patch offset groups."""

    name: str
    offsets: tuple[int, ...]
    confidence: str
    note: str


@dataclass(frozen=True)
class ScenarioBankEvidence:
    """Expected German PAL scenario-bank metadata from the local disc."""

    path: str
    lba: int
    raw_offset: int
    reported_size: int
    allocated_size: int
    pointer_count: int
    first_pointer: int
    last_pointer: int


@dataclass(frozen=True)
class RecruitmentScanEvidence:
    """Raw PAL recruitment scan evidence.

    These values document why raw little-endian trigger matches and name
    anchors are too noisy to promote wholesale. The production PAL source
    promotes only canonical ``0x19`` status/check trigger operands.
    """

    name: str
    trigger: int
    ntsc_name_offsets: int
    pal_name_hits: int
    pal_trigger_candidates: int
    confidence: str
    note: str


@dataclass(frozen=True)
class SpecEvoEvidence:
    """Classified PAL special-evolution evidence.

    ``confidence`` is intentionally explicit so candidate bytes do not look
    equivalent to offsets we are ready to write in a PAL script layout.
    """

    name: str
    target_id: int
    from_id: int
    offsets: tuple[int, ...]
    confidence: str
    note: str


@dataclass(frozen=True)
class SpecEvoResultTableEvidence:
    """PAL result-table candidate bytes for special-evolution messages."""

    name: str
    target_id: int
    offsets: tuple[int, ...]


TYPE_EFFECTIVENESS_VALUES = {2, 5, 10, 15, 20}
MUELLBERG_BEI_NACHT = bytes.fromhex(
    "82 6c 83 58 82 8c 82 8c 82 82 82 85 82 92 82 87"
    " 81 40 82 82 82 85 82 89 81 40 82 6d 82 81 82 83 82 88 82 94"
)
KAEFER_POKAL = bytes.fromhex(
    "82 6a 83 56 82 86 82 85 82 92 81 40 82 6f 82 8f 82 8b 82 81 82 8c"
)

PAL_DE_STARTER_CHECK_OFFSETS = (0x157023BC, 0x157023E0)
PAL_DE_STARTER_LEARN_TECH_OFFSETS = (0x157023D4, 0x157023F8)
PAL_DE_STARTER_EQUIP_ANIM_OFFSETS = (0x157023C8, 0x157023EC)
PAL_DE_STARTER_SET_OFFSETS = (0x15782634, 0x15782640)
PAL_DE_STARTER_STAT_CHECK_OFFSET = 0x14A2BF39

PAL_DE_ACTIVE_SCENARIO_PATH = "SCN/DG2.SCN"
PAL_DE_ACTIVE_SCENARIO_LBA = 146899
PAL_DE_ACTIVE_SCENARIO_RAW_OFFSET = 0x149802A8
PAL_DE_ACTIVE_SCENARIO_REPORTED_SIZE = 0xC5000
PAL_DE_ACTIVE_SCENARIO_ALLOCATED_SIZE = 0xE23E0
PAL_DE_ACTIVE_SCENARIO_POINTER_COUNT = 223
PAL_DE_ACTIVE_SCENARIO_FIRST_POINTER = 0x800
PAL_DE_ACTIVE_SCENARIO_LAST_POINTER = 0xC5000
PAL_DE_SCENARIO_BANK_EVIDENCE = (
    ScenarioBankEvidence("SCN/DG0.SCN", 146107, 0x147B9628, 0xC4000, 0xE1180, 223, 0x800, 0xC4000),
    ScenarioBankEvidence("SCN/DG1.SCN", 146499, 0x1489A7A8, 0xC8000, 0xE5B00, 223, 0x800, 0xC8000),
    ScenarioBankEvidence("SCN/DG2.SCN", 146899, 0x149802A8, 0xC5000, 0xE23E0, 223, 0x800, 0xC5000),
    ScenarioBankEvidence("SCN/DG3.SCN", 147293, 0x14A62688, 0xC8000, 0xE5B00, 223, 0x800, 0xC8000),
    ScenarioBankEvidence("SCN/DG4.SCN", 147693, 0x14B48188, 0xCF000, 0xEDBA0, 223, 0x800, 0xCF000),
)
PAL_DE_CHEST_OBJECT_CANDIDATE_COUNT = 149
PAL_DE_CHEST_OBJECT_LOGICAL_GROUP_COUNT = 79
PAL_DE_MAP_ITEM_CANDIDATE_COUNT = 515
PAL_DE_SPAWN_RATE_ACTIVE_RANDOM_COMMAND_CANDIDATE_COUNT = 2061
PAL_DE_SPAWN_RATE_ALL_BANK_RANDOM_COMMAND_CANDIDATE_COUNTS = (
    ("SCN/DG0.SCN", 2070),
    ("SCN/DG1.SCN", 2095),
    ("SCN/DG2.SCN", 2061),
    ("SCN/DG3.SCN", 2089),
    ("SCN/DG4.SCN", 2082),
)

PAL_DE_RECRUITMENT_REQUIRED_PATCH_NAMES = ("ogremon",)
PAL_DE_RECRUITMENT_PROMOTED_TRIGGER_CHECK_COUNT = 459
PAL_DE_RECRUITMENT_NAME_OFFSETS_PROMOTED = 0
PAL_DE_RECRUITMENT_SCAN_EVIDENCE = (
    RecruitmentScanEvidence(
        name="Betamon",
        trigger=204,
        ntsc_name_offsets=2,
        pal_name_hits=3,
        pal_trigger_candidates=75,
        confidence="raw-scan-audit",
        note="Two likely dialogue anchors plus one active result/list-table hit.",
    ),
    RecruitmentScanEvidence(
        name="Gabumon",
        trigger=217,
        ntsc_name_offsets=7,
        pal_name_hits=7,
        pal_trigger_candidates=17,
        confidence="raw-scan-audit",
        note="PAL name-hit count matches NTSC, but trigger candidates still include unrelated checks.",
    ),
    RecruitmentScanEvidence(
        name="Ogremon",
        trigger=234,
        ntsc_name_offsets=1,
        pal_name_hits=8,
        pal_trigger_candidates=30,
        confidence="raw-scan-audit",
        note="Includes the softlock-fix trigger value, so the dependent patch must be mapped separately.",
    ),
    RecruitmentScanEvidence(
        name="Shellmon",
        trigger=235,
        ntsc_name_offsets=2,
        pal_name_hits=3,
        pal_trigger_candidates=19,
        confidence="raw-scan-audit",
        note="This is the replacement trigger used by the Ogremon softlock patch.",
    ),
    RecruitmentScanEvidence(
        name="Mojyamon",
        trigger=252,
        ntsc_name_offsets=5,
        pal_name_hits=12,
        pal_trigger_candidates=52,
        confidence="raw-scan-audit",
        note="Localized duplicate dialogue creates more PAL anchors than the NTSC write table.",
    ),
)

PAL_DE_TOKOMON_ITEM_OFFSETS = (
    0x14A1ECE0,
    0x14A1ECE4,
    0x14A1ECE8,
    0x14A1ECEC,
    0x14A1ECF0,
    0x14A1ECF4,
)

PAL_DE_LEARN_MOVE_OFFSETS = (
    0x149D4DDE,
    0x1498D058,
    0x1498D0A0,
    0x1498D0E4,
)
PAL_DE_CHECK_MOVE_OFFSETS = (
    0x149D4A22,
    0x1498D050,
    0x1498D098,
    0x1498D0DC,
)

PAL_DE_SCRIPT_EVIDENCE = (
    ScriptEvidence(
        name="starter-set",
        offsets=PAL_DE_STARTER_SET_OFFSETS,
        confidence="verified-write",
        note="MIPS immediate writes feed the partner setup path.",
    ),
    ScriptEvidence(
        name="starter-learning-check",
        offsets=PAL_DE_STARTER_CHECK_OFFSETS,
        confidence="verified-write",
        note="MIPS immediate checks for the two starter Digimon IDs.",
    ),
    ScriptEvidence(
        name="starter-learning-tech",
        offsets=PAL_DE_STARTER_LEARN_TECH_OFFSETS,
        confidence="verified-write",
        note="MIPS immediate tech IDs learned by the two starters.",
    ),
    ScriptEvidence(
        name="starter-equip-animation",
        offsets=PAL_DE_STARTER_EQUIP_ANIM_OFFSETS,
        confidence="verified-write",
        note="Animation immediates decode to the starter tech slots.",
    ),
    ScriptEvidence(
        name="starter-stat-check",
        offsets=(PAL_DE_STARTER_STAT_CHECK_OFFSET,),
        confidence="verified-write",
        note="Single-byte starter stat check in the PAL script command stream.",
    ),
    ScriptEvidence(
        name="tokomon-items",
        offsets=PAL_DE_TOKOMON_ITEM_OFFSETS,
        confidence="verified-write",
        note="Six giveItem records match the German Tokomon gift context.",
    ),
    ScriptEvidence(
        name="tech-gift-learn",
        offsets=PAL_DE_LEARN_MOVE_OFFSETS,
        confidence="verified-write",
        note="Four learnMove command records for Beetle Land and Seadramon gifts.",
    ),
    ScriptEvidence(
        name="tech-gift-check",
        offsets=PAL_DE_CHECK_MOVE_OFFSETS,
        confidence="verified-write",
        note="Four matching tech-check bytes for Beetle Land and Seadramon gifts.",
    ),
)

PAL_DE_MONZAEMON_SPEC_EVO_OFFSETS = (
    0x149F42D8,
    0x149F434E,
    0x149F43AF,
    0x149F443F,
    0x149F4CB0,
)
PAL_DE_TOY_TOWN_LOCK_CHECK_OFFSETS = (
    0x149F4BC8,
    0x149F4C44,
)
PAL_DE_TOY_TOWN_UNLOCK_CANDIDATE_VALUE = bytes.fromhex("01 00 5d 01")
PAL_DE_FIX_EVO_ITEMS_OFFSET = 0x1573041C
PAL_DE_FIX_EVO_ITEMS_CONTEXT = bytes.fromhex(
    "21 90 80 00 00 19 12 00 14 80 02 3c 28 4c 42 24"
    " 21 10 43 00 08 00 42 8c 00 00 00 00 ff 00 42 30"
)
PAL_DE_OGREMON_SOFTLOCK_OFFSETS = (
    0x1499BF6A,
    0x14A61626,
)
PAL_DE_SHELLMON_STATUS_CHECK_OFFSET = 0x14A6048E
PAL_DE_PP_CALCULATION_CANDIDATE_OFFSET = 0x15762DAC
PAL_DE_PP_CALCULATION_ORIGINAL_CONTEXT = bytes.fromhex(
    "00 00 22 a6 0a 00 03 92 00 00 00 00 c0 10 03 00"
    " 20 10 43 00 40 18 02 00 34 00 a2 87 00 00 00 00"
    " 20 10 43 00 00 1c 02 00 03 1c 03 00"
)
PAL_DE_PP_CALCULATION_PATCH_VALUE = bytes.fromhex(
    "0f 19 04 0c ff ff 64 32 1e 00 40 10 00 00 00 00"
    " 14 80 02 3c 14 4b 42 24 21 10 52 00 00 00 42 90"
    " 03 00 42 30 21 88 51 00 16 00 00 10"
)
PAL_DE_UNLOCK_GREYLORD_OFFSETS = (0x149A2DE4,)
PAL_DE_UNLOCK_GREYLORD_VALUE = bytes.fromhex("ca 04")
PAL_DE_UNLOCK_ICE_OFFSETS = (0x149C7FC8, 0x149C8164)
PAL_DE_UNLOCK_ICE_VALUE = bytes.fromhex("3c 00")
PAL_DE_UNRIG_SLOTS_TRN_REL_CANDIDATE_OFFSET = 0x177004
PAL_DE_UNRIG_SLOTS_TRN2_REL_CANDIDATE_OFFSET = 0x16D9D4
PAL_DE_UNRIG_SLOTS_CANDIDATE_OFFSETS = (
    PAL_DE_UNRIG_SLOTS_TRN_REL_CANDIDATE_OFFSET,
    PAL_DE_UNRIG_SLOTS_TRN2_REL_CANDIDATE_OFFSET,
)
PAL_DE_UNRIG_SLOTS_CANDIDATE_CONTEXTS = (
    bytes.fromhex(
        "20 10 51 00 80 10 02 00 20 18 51 00 09 80 02 3c"
        " 7c 03 42 24 21 18 43 00 2c 00 a2 8f 00 00 00 00"
        " 21 10 43 00 00 00 42 80 00 00 00 00 ff ff 42 20"
        " 40 11 02 00 ff 00 42 30"
    ),
    bytes.fromhex(
        "20 10 51 00 80 10 02 00 20 18 51 00 09 80 02 3c"
        " 58 e8 42 24 21 18 43 00 2c 00 a2 8f 00 00 00 00"
        " 21 10 43 00 00 00 42 80 00 00 00 00 ff ff 42 20"
        " 40 11 02 00 ff 00 42 30"
    ),
)
PAL_DE_LEARN_MOVE_AND_COMMAND_REJECTED_CANDIDATE_OFFSET = 0x1721BC
PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_OFFSET = 0x1717B4
PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_CONTEXT = bytes.fromhex(
    "20 10 52 00 40 90 02 00 30 00 a2 87 00 00 00 00"
    " 68 00 40 14 00 00 00 00 2c 00 a2 87 00 00 00 00"
    " 09 00 40 10 00 00 00 00 2c 00 a2 87 03 00 01 24"
    " 05 00 41 10 00 00 00 00 2c 00 a2 87 04 00 01 24"
)
PAL_DE_LEARN_MOVE_AND_COMMAND_REJECTED_CANDIDATE_CONTEXT = bytes.fromhex(
    "14 80 02 3c 50 8d 42 24 21 18 43 00 50 00 a2 8f"
    " 00 00 00 00 21 10 43 00 0f 00 42 90 00 00 00 00"
)
PAL_DE_WOAH_NAIVE_SLES_DELTA_CANDIDATE_OFFSET = 0x157B1814
PAL_DE_WOAH_TEXT_OFFSETS = (
    0x14845392,
    0x14846882,
    0x14854BBA,
    0x1485714E,
    0x14857ACA,
)
PAL_DE_WOAH_TEXT_CONTEXT = bytes.fromhex(
    "0d 00 00 00 1b fd 1a 00"
    " 82 76 82 8f 82 81 82 88 81 49 81 40 82 60 81 40"
    " 01 06 82 62 82 88 82 81"
)
PAL_DE_WOAH_TEXT_CONTEXTS = (PAL_DE_WOAH_TEXT_CONTEXT,) * len(PAL_DE_WOAH_TEXT_OFFSETS)
PAL_DE_WOAH_ENCODED_TEXT = bytes.fromhex("82 76 82 8f 82 81 82 88")
PAL_DE_WOAH_PAYLOAD = bytes.fromhex("82 6e 82 88 82 81 81 49")
PAL_DE_WOAH_NTSC_REPLACEMENT_AS_PAL_TEXT = bytes.fromhex(
    "82 6e 82 88 81 40 82 93 82 88 82 89 82 94"
)
PAL_DE_GABUMON_NTSC_RAW_CANDIDATE_OFFSET = 0x0A7EEA8C
PAL_DE_GABUMON_NAIVE_DELTA_CANDIDATE_OFFSET = 0x0B2293AC
PAL_DE_GABUMON_TFS_PATH = "MAP/MAP9/GCAN04_2.TFS"
PAL_DE_GABUMON_TFS_OFFSET = 0x0A7BAEF8
PAL_DE_GABUMON_TFS_RELATIVE_PATCH_OFFSET = 0x33B94
PAL_DE_GABUMON_PATCH_ORIGINAL_CONTEXT = bytes.fromhex(
    "65 78 56 4a 4a 65 a0 a0 a0 8e 8e 4f 61 b5 e1 e1"
    " c1 c1 c1 a0 8e 8e 78 56 a0 a0 a0 78 8e 78 78 65"
    " 65 65 47 47 47 47 2a 56 2a 10 00 00 03 00 03 03"
    " 01 0d 03 03 04 01 02 20 75 93 75 99 91 77 cf d0"
    " 81 a9 64 6f cf c5 0d 67 84 9e b7 e5 e0 fc fc fc"
    " f8 f5 f5 f8 f5 f5 33 2f 1a 1a 05 10 10 10 2a 2f"
    " 47 56 65 78 78 78 4a 2a 4a 56 56 78 78 56 2a 10"
)
PAL_DE_SOFTLOCK_NAIVE_SLES_DELTA_CANDIDATE_OFFSETS = (
    0x15721BE0,
    0x15721D84,
    0x15715A60,
    0x15715ABC,
)
PAL_DE_SOFTLOCK_ROTATION_BRANCH_OFFSETS = (
    0x15721F70,
    0x15722148,
)
PAL_DE_SOFTLOCK_ROTATION_BRANCH_CONTEXTS = (
    bytes.fromhex(
        "20 10 43 00 40 10 02 00 20 18 43 00 13 80 02 3c"
        " a0 54 42 24 21 10 43 00 21 10 42 02 00 00 42 80"
        " 00 00 00 00 4c 00 a2 af 4c 00 a2 8f 00 00 00 00"
        " 58 00 40 18 00 00 00 00 4c 00 a2 8f 00 00 00 00"
        " ff ff 44 30 63 f1 03 0c 00 00 00 00 01 00 01 24"
        " 30 00 41 14 00 00 00 00"
    ),
    bytes.fromhex(
        "20 10 43 00 40 10 02 00 20 18 43 00 13 80 02 3c"
        " a0 54 42 24 21 10 43 00 21 10 42 02 05 00 42 80"
        " 00 00 00 00 4c 00 a2 af 4c 00 a2 8f 00 00 00 00"
        " 58 00 40 18 00 00 00 00 4c 00 a2 8f 00 00 00 00"
        " ff ff 44 30 63 f1 03 0c 00 00 00 00 01 00 01 24"
        " 30 00 41 14 00 00 00 00"
    ),
)
PAL_DE_SOFTLOCK_MOVE_TO_BRANCH_OFFSETS = (
    0x15715B20,
)
PAL_DE_SOFTLOCK_MOVE_TO_BRANCH_CONTEXT = bytes.fromhex(
    "21 10 00 00 0b 00 40 14 ff ff 02 24 13 80 02 3c"
    " d8 ab 42 8c 00 00 00 00 00 00 42 8c 00 01 03 3c"
    " 24 10 43 00 03 00 40 10 21 10 00 00 c9 ff 40 12"
    " 01 00 02 24 2c 00 bf 8f"
)
PAL_DE_SOFTLOCK_TOY_TOWN_COORDINATE_OFFSETS = (
    0x149F4A74,
    0x149F4D78,
)
PAL_DE_SOFTLOCK_TOY_TOWN_COMMAND_CONTEXTS = (
    bytes.fromhex(
        "4f 12 b0 ff 18 04 6c 06 9c ff de 06 14 00 4a 06"
        " 4d 06 00 00 67 00 f7 b0 5e 09 3a a5 96 64 b3 7b"
    ),
    bytes.fromhex(
        "4f 12 b0 ff 18 04 6c 06 9c ff de 06 14 00 4a 06"
        " 4d 06 00 00 67 00 05 00 56 00 06 1e 56 00 fd 10"
    ),
)
PAL_DE_SOFTLOCK_LEOMON_CAVE_OFFSETS = (
    0x149DC436,
    0x149DC4D8,
    0x149DCDE0,
    0x149DCE82,
    0x149DD8D4,
    0x149DD976,
    0x149DE268,
    0x149DE30A,
)
PAL_DE_SOFTLOCK_LEOMON_CAVE_CONTEXTS = (
    bytes.fromhex(
        "1c 04 19 00 57 00 03 00 4e fd aa f8 54 0b 01 00"
        " 4a fd 56 00 fd 0c 67 00 0a 00 57 00 03 01 5a 00"
    ),
    bytes.fromhex(
        "c2 04 19 00 57 00 04 00 4e fd aa f8 54 0b 01 00"
        " 4a fd 56 00 fd 0c 67 00 0a 00 57 00 04 01 5a 00"
    ),
    bytes.fromhex(
        "1c 04 19 00 57 00 03 00 4e fd aa f8 54 0b 01 00"
        " 4a fd 56 00 fd 0c 67 00 0a 00 57 00 03 01 5a 00"
    ),
    bytes.fromhex(
        "c2 04 19 00 57 00 04 00 4e fd aa f8 54 0b 01 00"
        " 4a fd 56 00 fd 0c 67 00 0a 00 57 00 04 01 5a 00"
    ),
    bytes.fromhex(
        "1c 04 19 00 57 00 03 00 4e fd aa f8 54 0b 01 00"
        " 4a fd 56 00 fd 0c 67 00 0a 00 57 00 03 01 5a 00"
    ),
    bytes.fromhex(
        "c2 04 19 00 57 00 04 00 4e fd aa f8 54 0b 01 00"
        " 4a fd 56 00 fd 0c 67 00 0a 00 57 00 04 01 5a 00"
    ),
    bytes.fromhex(
        "1c 04 19 00 57 00 03 00 4e fd aa f8 54 0b 01 00"
        " 4a fd 56 00 fd 0c 67 00 0a 00 57 00 03 01 5a 00"
    ),
    bytes.fromhex(
        "c2 04 19 00 57 00 04 00 4e fd aa f8 54 0b 01 00"
        " 4a fd 56 00 fd 0c 67 00 0a 00 57 00 04 01 5a 00"
    ),
)
PAL_DE_RESET_BUTTON_NAIVE_SLES_DELTA_CANDIDATE_OFFSETS = (
    0x15711E40,
    0x15754334,
    0x15754390,
    0x15754CA8,
)
PAL_DE_EVO_TARGET_UNIFY_OFFSETS = (
    0x1575CE94,
    0x1575CEA0,
    0x1575CEAC,
)
PAL_DE_EVO_TARGET_UNIFY_CONTEXT_OFFSET = 0x1575CE8C
PAL_DE_EVO_TARGET_UNIFY_ORIGINAL_CONTEXT = bytes.fromhex(
    "f8 ff bd 27 00 00 b0 af 08 00 a4 af 0c 00 a5 af"
    " 21 80 00 00 6e 00 00 10 00 00 00 00 c0 10 10 00"
    " 22 10 50 00 c0 18 02 00 17 80 02 3c b8 87 42 24"
    " 21 10 43 00 33 00 42 90 01 00 01 24 63 00 41 10"
    " 00 00 00 00 08 00 a4 87 c0 10 10 00 22 10 50 00"
    " c0 18 02 00 17 80 02 3c b8 87 42 24 21 10 43 00"
    " 00 00 44 ac 44 ff 04 24 c0 10 10 00 22 10 50 00"
    " c0 18 02 00 17 80 02 3c b8 87 42 24 21 10 43 00"
    " 04 00 44 ac 0c 00 a4 87 c0 10 10 00 22 10 50 00"
)
PAL_DE_RESET_BUTTON_CUSTOM_FUNCTION_OFFSET = 0x1575CEF0
PAL_DE_RESET_BUTTON_CUSTOM_FUNCTION_ORIGINAL_BYTES = bytes.fromhex(
    "44 ff 04 24 c0 10 10 00 22 10 50 00 c0 18 02 00"
    " 17 80 02 3c b8 87 42 24 21 10 43 00 04 00 44 ac"
    " 0c 00 a4 87"
)
PAL_DE_RESET_BUTTON_HOOK_OFFSET = 0x1576E244
PAL_DE_RESET_BUTTON_HOOK_CONTEXT_OFFSET = 0x1576E230
PAL_DE_RESET_BUTTON_HOOK_ORIGINAL_CONTEXT = bytes.fromhex(
    "09 08 04 24 21 28 40 02 10 80 06 3c b0 2e c6 24"
    " 10 80 07 3c 94 2e e7 24 8b 8a 02 0c 00 00 00 00"
    " 2c 00 a2 8f"
)
PAL_DE_HAPPY_VENDING_ACTIVE_TEXT_CANDIDATE_OFFSET = 0x149E0748
PAL_DE_HAPPY_VENDING_MENU_OFFSETS = (0x147C7368, 0x147C7CEC)
PAL_DE_HAPPY_VENDING_RESULT_OFFSETS = (0x147C74A0, 0x147C7E24)
PAL_DE_HAPPY_VENDING_PRICE_OFFSETS = (
    0x147C73F2,
    0x147C7D76,
    0x147C7498,
    0x147C7E1C,
)
PAL_DE_HAPPY_VENDING_ITEM_ID_OFFSETS = (
    0x147C74C6,
    0x147C74D8,
    0x147C7522,
    0x147C7E4A,
    0x147C7E5C,
    0x147C7EA6,
)
PAL_DE_HAPPY_VENDING_MENU_CONTEXTS = (
    bytes.fromhex(
        "82 6c 82 85 82 81 82 94 81 40 81 46 81 40"
        "82 94 82 88 82 92 82 85 82 85 81 40 82 88"
        "82 95 82 8e 82 84 81 40 82 82 82 89 82 94"
        "82 93 0d 00 82 63 82 89 82 87 82 89 82 6c"
        "82 95 82 93 82 88 82 92 82 8f 82 8f 82 8d"
        "82 93 81 46 82 93 82 89 82 98 81 40 82 88"
        "82 95 82 8e 82 84 81 40 82 82 82 89 82 94"
        "82 93 0d 00 82 63 82 8f 82 8e 81 66 82 94"
        "81 40 82 82 82 95 82 99 0d 00 00 00"
    ),
) * 2
PAL_DE_HAPPY_VENDING_RESULT_CONTEXTS = (
    bytes.fromhex(
        "01 06 82 6c 82 85 82 81 82 94 01 01 81 40"
        "82 83 82 81 82 8d 82 85 81 40 82 8f 82 95"
        "82 94 81 49 0d 00 00 00"
    ),
) * 2
PAL_DE_HASH_RELATIVE_CANDIDATE_OFFSET = 0xE7A09
PAL_DE_HASH_DG4_CANDIDATE_OFFSET = 0x14C2FB91
PAL_DE_HASH_DG4_CANDIDATE_CONTEXT = bytes.fromhex(
    "94 82 81 82 84 82 8f 81 49 0d 00 00 00 1b ff 1a"
    " 00 83 6e 82 6b 82 81 81 40 82 86 82 85 82 8c"
    " 82 89 82 83 82 89 82 84 82 81 82 84 81 40 82 88 82"
)
PAL_DE_INTRO_HASH_OFFSET = 0x14A2C080
PAL_DE_INTRO_HASH_SIZE = 0x60
PAL_DE_INTRO_HASH_ORIGINAL_TEXT = bytes.fromhex(
    "82 68 82 83 82 88 81 40 82 88 82 81 82 82 82 85"
    " 81 40 82 84 82 89 82 83 82 88 81 40 82 88 82 85"
    " 82 92 82 87 82 85 82 82 82 85 82 94 82 85 82 8e"
    " 81 43 0d 00 82 84 82 81 82 8d 82 89 82 94 81 40"
    " 82 84 82 95 81 40 82 95 82 8e 82 93 81 40 82 92"
    " 82 85 82 94 82 94 82 85 82 93 82 94 81 44 0d 00"
)
PAL_DE_INTRO_SKIP_OUTSIDE_OFFSET = 0x14A2CE1A
PAL_DE_INTRO_SKIP_OUTSIDE_DEST = 0x03FE
PAL_DE_INTRO_SKIP_OUTSIDE_ORIGINAL_COMMAND = bytes.fromhex("56 00 08 00")
PAL_DE_INTRO_SKIP_OUTSIDE_TARGET_OFFSET = 0x14A2CEA6
PAL_DE_INTRO_SKIP_OUTSIDE_TARGET_COMMAND = bytes.fromhex("56 00 fd 00")
PAL_DE_INTRO_SKIP_INSIDE_OFFSET = 0x14A2C0E2
PAL_DE_INTRO_SKIP_INSIDE_DEST = 0x0FF8
PAL_DE_INTRO_SKIP_INSIDE_ORIGINAL_COMMAND = bytes.fromhex("56 00 05 00")
PAL_DE_INTRO_SKIP_INSIDE_TARGET_OFFSET = 0x14A2CAA0
PAL_DE_INTRO_SKIP_INSIDE_TARGET_COMMAND = bytes.fromhex("56 00 05 1d")
PAL_DE_SPAWN_RATE_MAMEMON_OFFSETS = (0x149815AF,)
PAL_DE_SPAWN_RATE_PIXIMON_OFFSETS = (
    0x149812FB,
    0x149841B1,
    0x149841BB,
    0x1498AF41,
)
PAL_DE_SPAWN_RATE_METALMAMEMON_OFFSETS = (0x1498313F, 0x1498479D)
PAL_DE_SPAWN_RATE_OTAMAMON_OFFSETS = (0x14982D67,)
PAL_DE_SPAWN_RATE_COMMANDS = (
    (PAL_DE_SPAWN_RATE_MAMEMON_OFFSETS[0], bytes.fromhex("64 02")),
    (PAL_DE_SPAWN_RATE_PIXIMON_OFFSETS[0], bytes.fromhex("64 02")),
    (PAL_DE_SPAWN_RATE_PIXIMON_OFFSETS[1], bytes.fromhex("6e 09")),
    (PAL_DE_SPAWN_RATE_PIXIMON_OFFSETS[2], bytes.fromhex("6e 01")),
    (PAL_DE_SPAWN_RATE_PIXIMON_OFFSETS[3], bytes.fromhex("64 02")),
    (PAL_DE_SPAWN_RATE_METALMAMEMON_OFFSETS[0], bytes.fromhex("6e 02")),
    (PAL_DE_SPAWN_RATE_METALMAMEMON_OFFSETS[1], bytes.fromhex("6e 07")),
    (PAL_DE_SPAWN_RATE_OTAMAMON_OFFSETS[0], bytes.fromhex("6e 00")),
)
PAL_DE_DV_CHIP_DESCRIPTION_CANDIDATE_OFFSETS = (
    0x157A0830,
    0x157A084C,
    0x157A0868,
)
PAL_DE_DV_CHIP_DESCRIPTION_CANDIDATE_CONTEXTS = (
    bytes.fromhex(
        "82 94 81 40 82 9a 82 95 81 40 82 6a 82 95 82 97"
        " 82 81 82 87 82 81 82 8d 82 8f 82 8e 81 49 00 00"
    ),
    bytes.fromhex(
        "81 49 00 00 82 63 82 89 82 87 82 89 3a 4f 3a cb"
        " e2 9f e9 24 1b 2b d3 38 83 8f 6f e9 61 96 cd"
    ),
    bytes.fromhex(
        "61 96 cd 0d d7 d3 04 b9 1c 5a 87 89 73 89 3d 43"
        " 37 1c 5f f2 e8 1b d7 a1 28 dd 6c 97 f8 39 cc"
    ),
)
PAL_DE_DV_CHIP_DESCRIPTION_OFFSETS = (
    0x157A03D4,
    0x157A0414,
    0x157A0448,
)
PAL_DE_DV_CHIP_DESCRIPTION_CONTEXTS = (
    bytes.fromhex(
        "82 6d 82 81 82 88 82 92 82 95 82 8e 82 87 81 44"
        " 81 40 82 72 83 56 82 94 82 94 82 89 82 87 82 94"
        " 81 40 82 63 82 89 82 87 82 89 82 8d 82 8f 82 8e"
        " 81 40 82 93 82 85 82 88 82 92 81 44"
    ),
    bytes.fromhex(
        "82 81 82 95 82 86 81 43 81 40 82 85 82 92 82 88"
        " 83 5a 82 88 82 94 81 40 82 6b 81 44 82 85 82 92"
        " 82 97 82 81 82 92 82 94 82 95 82 8e 82 87 81 49"
    ),
    bytes.fromhex(
        "82 6d 82 81 82 88 82 92 82 95 82 8e 82 87 81 44"
        " 81 40 82 64 82 92 82 88 83 5a 82 88 82 94 81 40"
        " 82 66 82 8c 83 58 82 83 82 8b 81 43 81 40 82 8e"
        " 81 44 81 40 82 8f 82 88 82 8e 82 85"
    ),
)
PAL_DE_DEVI_CHIP_NAME_OFFSETS = (
    0x1579E974,
    0x1579E98C,
    0x1579E9A4,
)
PAL_DE_DEVI_CHIP_NAME_CONTEXTS = (
    bytes.fromhex("82 63 82 85 82 96 82 89 81 7c 82 62 82 88 82 89 82 90 81 40 82 60"),
    bytes.fromhex("82 63 82 85 82 96 82 89 81 7c 82 62 82 88 82 89 82 90 81 40 82 63"),
    bytes.fromhex("82 63 82 85 82 96 82 89 81 7c 82 62 82 88 82 89 82 90 81 40 82 64"),
)
PAL_DE_PATCH_EVIDENCE = (
    PatchEvidence(
        name="fix-evo-items",
        offsets=(PAL_DE_FIX_EVO_ITEMS_OFFSET,),
        confidence="verified-write",
        note="SLES-relative executable code site matching the already verified PAL type-table mapping.",
    ),
    PatchEvidence(
        name="type-effectiveness",
        offsets=(0x157A1318,),
        confidence="verified-write",
        note="The PAL-DE layout maps and tests the 7x7 type chart and the patch reads the layout offset.",
    ),
    PatchEvidence(
        name="ogremon-softlock",
        offsets=PAL_DE_OGREMON_SOFTLOCK_OFFSETS,
        confidence="verified-write",
        note="Two Ogremon status/recruitment checks mirror the NTSC Shellmon-trigger softlock fix.",
    ),
    PatchEvidence(
        name="pp-calculation",
        offsets=(PAL_DE_PP_CALCULATION_CANDIDATE_OFFSET,),
        confidence="verified-write",
        note="Executable code site matches the PP calculation path with a PAL-specific height-table address.",
    ),
    PatchEvidence(
        name="unlock-areas",
        offsets=(
            *PAL_DE_UNLOCK_GREYLORD_OFFSETS,
            *PAL_DE_UNLOCK_ICE_OFFSETS,
            *PAL_DE_TOY_TOWN_LOCK_CHECK_OFFSETS,
        ),
        confidence="verified-write",
        note="Greylord, Ice Sanctuary, and Toy Town lock operands are verified in the active German script.",
    ),
    PatchEvidence(
        name="intro-hash",
        offsets=(PAL_DE_INTRO_HASH_OFFSET,),
        confidence="verified-write",
        note="PAL hash writes into a German Jijimon intro text slot and pads the full original field.",
    ),
    PatchEvidence(
        name="intro-skip",
        offsets=(PAL_DE_INTRO_SKIP_OUTSIDE_OFFSET, PAL_DE_INTRO_SKIP_INSIDE_OFFSET),
        confidence="verified-write",
        note="Two German Jijimon intro command sites are replaced with same-slice jumpTo commands.",
    ),
    PatchEvidence(
        name="spawn-rate",
        offsets=(
            *PAL_DE_SPAWN_RATE_MAMEMON_OFFSETS,
            *PAL_DE_SPAWN_RATE_PIXIMON_OFFSETS,
            *PAL_DE_SPAWN_RATE_METALMAMEMON_OFFSETS,
            *PAL_DE_SPAWN_RATE_OTAMAMON_OFFSETS,
        ),
        confidence="verified-write",
        note="Broad PAL random scans stay noisy; these active German rare-spawn gate bytes are structurally verified.",
    ),
    PatchEvidence(
        name="training-slots",
        offsets=PAL_DE_UNRIG_SLOTS_CANDIDATE_OFFSETS,
        confidence="verified-write",
        note="Both PAL training REL candidate sites match the NTSC control-flow shape; the jump payloads skip to the same +0x8C post-rigging label in each REL.",
    ),
    PatchEvidence(
        name="movement-softlocks",
        offsets=(
            *PAL_DE_SOFTLOCK_ROTATION_BRANCH_OFFSETS,
            *PAL_DE_SOFTLOCK_MOVE_TO_BRANCH_OFFSETS,
            *PAL_DE_SOFTLOCK_TOY_TOWN_COORDINATE_OFFSETS,
            *PAL_DE_SOFTLOCK_LEOMON_CAVE_OFFSETS,
        ),
        confidence="verified-write",
        note="Rotation, move-to, Toy Town coordinate, and Leomon cave/tablet movement sites are independently mapped for the active German PAL build.",
    ),
    PatchEvidence(
        name="learn-move-and-command",
        offsets=(
            PAL_DE_LEARN_MOVE_AND_COMMAND_BRANCH_CANDIDATE_OFFSET,
            PAL_DE_LEARN_MOVE_AND_COMMAND_REJECTED_CANDIDATE_OFFSET,
        ),
        confidence="verified-write",
        note="PAL branch-shaped lead matches the NTSC learn-move/command gate; the old simple TRN-relative candidate remains a rejected address-load lookalike.",
    ),
    PatchEvidence(
        name="gabumon",
        offsets=(PAL_DE_GABUMON_NTSC_RAW_CANDIDATE_OFFSET,),
        confidence="verified-file-relative-write",
        note="The legacy byte site is file-relative 0x33B94 inside PAL MAP/MAP9/GCAN04_2.TFS, matching the NTSC raw patch location; the simple PAL delta remains rejected.",
    ),
    PatchEvidence(
        name="woah",
        offsets=PAL_DE_WOAH_TEXT_OFFSETS,
        confidence="verified-write",
        note="PAL stores Woah as 8 bytes of encoded script text; the PAL layout uses a same-size encoded payload and rejects the NTSC ASCII payload.",
    ),
    PatchEvidence(
        name="happy-vending",
        offsets=(
            *PAL_DE_HAPPY_VENDING_MENU_OFFSETS,
            *PAL_DE_HAPPY_VENDING_RESULT_OFFSETS,
            *PAL_DE_HAPPY_VENDING_PRICE_OFFSETS,
            *PAL_DE_HAPPY_VENDING_ITEM_ID_OFFSETS,
        ),
        confidence="verified-write",
        note="Two PAL vending script copies match the NTSC write structure; PAL uses encoded text payloads that fit the original fields.",
    ),
    PatchEvidence(
        name="intro-hash-relative-candidate",
        offsets=(PAL_DE_HASH_DG4_CANDIDATE_OFFSET,),
        confidence="deferred-scenario-padding",
        note="The NTSC-relative lead lands inside DG4 allocation padding after the reported SCN payload.",
    ),
    PatchEvidence(
        name="dv-chip-descriptions",
        offsets=PAL_DE_DV_CHIP_DESCRIPTION_OFFSETS,
        confidence="verified-write",
        note="PAL Devi-Chip A/D/E descriptions are variable encoded text fields after the normal stat-chip descriptions.",
    ),
    PatchEvidence(
        name="always-on-executable-hooks",
        offsets=(
            *PAL_DE_EVO_TARGET_UNIFY_OFFSETS,
            PAL_DE_RESET_BUTTON_CUSTOM_FUNCTION_OFFSET,
            PAL_DE_RESET_BUTTON_HOOK_OFFSET,
        ),
        confidence="verified-write",
        note="PAL executable sites match the duplicate evo-target function and reset callback registration shape; the simple SLES delta candidates remain rejected.",
    ),
)
PAL_DE_STATE_SAFE_PATCH_NAMES = (
    "allowDrop",
    "giromon",
    "learnTierOne",
    "upLearnChance",
)
PAL_DE_LAYOUT_AWARE_ROM_PATCH_NAMES = (
    "fixDVChips",
    "fixEvoItems",
    "gabumon",
    "hash",
    "happyVending",
    "intro",
    "learnmoveandcommand",
    "ogremon",
    "pp",
    "slots",
    "spawn",
    "softlock",
    "typeEffectiveness",
    "unlock",
    "woah",
)
PAL_DE_UNMAPPED_ROM_PATCH_NAMES = ()
PAL_DE_INCOMPATIBLE_ROM_PATCH_NAMES = ()
GLOBAL_DISABLED_PATCH_NAMES = ()
PAL_DE_UNMAPPED_ALWAYS_ON_PATCH_NAMES = ()
PAL_DE_MONZAEMON_BOX_CHOICE_CONTEXT_OFFSETS = (
    0x149F7194,
    0x149F8806,
)
PAL_DE_MONZAEMON_REACTION_CONTEXT_OFFSETS = (
    0x149F7394,
    0x149F7DD6,
    0x149F8A06,
    0x149F91C4,
)
PAL_DE_SUKAMON_SPEC_EVO_CANDIDATE_OFFSETS = (
    (0x14A2991A, 0x14A29926),
    (0x14A29F7A, 0x14A29F86),
)
PAL_DE_SUKAMON_SPEC_EVO_OFFSETS = tuple(
    offset
    for offsets in PAL_DE_SUKAMON_SPEC_EVO_CANDIDATE_OFFSETS
    for offset in offsets
)
PAL_DE_MAMEMON_SPEC_EVO_CANDIDATE_OFFSETS = (
    (0x149C91AC, 0x149C9232),
    (0x149C93F4, 0x149C947A),
)
PAL_DE_GIROMON_SPEC_EVO_OFFSETS = tuple(
    offsets[0] for offsets in PAL_DE_MAMEMON_SPEC_EVO_CANDIDATE_OFFSETS
)
PAL_DE_METALMAMEMON_SPEC_EVO_OFFSETS = tuple(
    offsets[1] for offsets in PAL_DE_MAMEMON_SPEC_EVO_CANDIDATE_OFFSETS
)
PAL_DE_MAMEMON_SPEC_EVO_LANGUAGE_COPY_CANDIDATE_OFFSETS = (
    (0x1480252C, 0x148025B4),
    (0x14802764, 0x148027EC),
    (0x148E3FDC, 0x148E4054),
    (0x148E4212, 0x148E428A),
    (0x149C91AC, 0x149C9232),
    (0x149C93F4, 0x149C947A),
    (0x14AABEBC, 0x14AABF46),
    (0x14AAC0F4, 0x14AAC17E),
    (0x14B922EC, 0x14B9237E),
    (0x14B92536, 0x14B925C8),
)
PAL_DE_SUKAMON_SPEC_EVO_LANGUAGE_COPY_CANDIDATE_OFFSETS = (
    (0x1485FEAA, 0x1485FEB6),
    (0x148604F4, 0x14860500),
    (0x149462DA, 0x149462E6),
    (0x1494697A, 0x14946986),
    (0x14A2991A, 0x14A29926),
    (0x14A29F7A, 0x14A29F86),
    (0x14B0CF5A, 0x14B0CF66),
    (0x14B0D56C, 0x14B0D578),
    (0x14BF6AAA, 0x14BF6AB6),
    (0x14BF70FE, 0x14BF710A),
)
PAL_DE_RESULT_TABLE_SPEC_EVO_CANDIDATE_OFFSETS = (
    (0x14A5D741, 0x25),  # Bakemon
    (0x14A5D465, 0x1A),  # SkullGreymon
    (0x14A5DE3B, 0x3B),  # Phoenixmon
    (0x14A5CDD3, 0x06),  # Devimon
    (0x14A5CE1D, 0x07),  # Airdramon
    (0x14A5DDF3, 0x3A),  # Ninjamon
    (0x14A5D9D3, 0x2F),  # Monochromon
    (0x14A5D5EF, 0x20),  # Kunemon
    (0x14A5DA5F, 0x31),  # Coelamon
    (0x14A5DB6F, 0x35),  # Nanimon
    (0x14A5D4E5, 0x1C),  # Vademon
)
PAL_DE_RESULT_TABLE_SPEC_EVO_FROM_IDS = (
    0x03,  # Bakemon
    0x0C,  # SkullGreymon
    0x32,  # Phoenixmon
    0x14,  # Devimon
    0x0A,  # Airdramon
    0x19,  # Ninjamon
    0x26,  # Monochromon
    0x02,  # Kunemon
    0x18,  # Coelamon
    0x35,  # Nanimon
    0x1C,  # Vademon
)
PAL_DE_RESULT_TABLE_SPEC_EVO_OFFSETS = tuple(
    (offset, target_id, from_id)
    for (offset, target_id), from_id in zip(
        PAL_DE_RESULT_TABLE_SPEC_EVO_CANDIDATE_OFFSETS,
        PAL_DE_RESULT_TABLE_SPEC_EVO_FROM_IDS,
    )
)
PAL_DE_RESULT_TABLE_SPEC_EVO_LANGUAGE_COPY_CANDIDATES = (
    SpecEvoResultTableEvidence(
        "Bakemon",
        0x25,
        (0x1489574D, 0x1497B321, 0x14A5D741, 0x14B43201, 0x14C30E99),
    ),
    SpecEvoResultTableEvidence(
        "SkullGreymon",
        0x1A,
        (0x14895391, 0x1497B057, 0x14A5D465, 0x14B42F37, 0x14C30B8D),
    ),
    SpecEvoResultTableEvidence(
        "Phoenixmon",
        0x3B,
        (0x14895C69, 0x1497B9EF, 0x14A5DE3B, 0x14B438CF, 0x14C315EB),
    ),
    SpecEvoResultTableEvidence(
        "Devimon",
        0x06,
        (
            0x14894EC9,
            0x14896247,
            0x1497A9EB,
            0x1497BF11,
            0x14A5CDD3,
            0x14A5E359,
            0x14B428CD,
            0x14B43DB1,
            0x14C304A9,
            0x14C31B47,
        ),
    ),
    SpecEvoResultTableEvidence(
        "Airdramon",
        0x07,
        (
            0x14894F0B,
            0x14896289,
            0x1497AA33,
            0x1497BF59,
            0x14A5CE1D,
            0x14A5E3A3,
            0x14B42915,
            0x14B43DF9,
            0x14C304F7,
            0x14C31B95,
        ),
    ),
    SpecEvoResultTableEvidence(
        "Ninjamon",
        0x3A,
        (0x14895C29, 0x1497B9A9, 0x14A5DDF3, 0x14B43889, 0x14C3159F),
    ),
    SpecEvoResultTableEvidence(
        "Monochromon",
        0x2F,
        (0x1489598F, 0x1497B59F, 0x14A5D9D3, 0x14B4347F, 0x14C31153),
    ),
    SpecEvoResultTableEvidence(
        "Kunemon",
        0x20,
        (0x14895621, 0x1497B1D9, 0x14A5D5EF, 0x14B430B9, 0x14C30D33),
    ),
    SpecEvoResultTableEvidence(
        "Coelamon",
        0x31,
        (0x14895A0B, 0x1497B627, 0x14A5DA5F, 0x14B43507, 0x14C311E7),
    ),
    SpecEvoResultTableEvidence(
        "Nanimon",
        0x35,
        (0x14895AFD, 0x1497B72F, 0x14A5DB6F, 0x14B4360F, 0x14C31437),
    ),
    SpecEvoResultTableEvidence(
        "Vademon",
        0x1C,
        (0x14895531, 0x1497B0D3, 0x14A5D4E5, 0x14B42FB3, 0x14C30C15),
    ),
)

PAL_DE_SPEC_EVO_EVIDENCE = (
    SpecEvoEvidence(
        name="Monzaemon/Toy Town",
        target_id=0x0E,
        from_id=0x0B,
        offsets=PAL_DE_MONZAEMON_SPEC_EVO_OFFSETS,
        confidence="verified-layout",
        note="Five target bytes match the local Monzaemon/Toy Town script.",
    ),
    SpecEvoEvidence(
        name="Giromon",
        target_id=0x29,
        from_id=0x0D,
        offsets=PAL_DE_GIROMON_SPEC_EVO_OFFSETS,
        confidence="verified-layout",
        note="Two active German Mamemon-family command blocks.",
    ),
    SpecEvoEvidence(
        name="MetalMamemon",
        target_id=0x1B,
        from_id=0x0D,
        offsets=PAL_DE_METALMAMEMON_SPEC_EVO_OFFSETS,
        confidence="verified-layout",
        note="Two active German Mamemon-family command blocks.",
    ),
    *(
        SpecEvoEvidence(
            name="Result table " + str(target_id),
            target_id=target_id,
            from_id=from_id,
            offsets=(offset,),
            confidence="verified-layout",
            note="Active German special-evolution result-table target byte.",
        )
        for offset, target_id, from_id in PAL_DE_RESULT_TABLE_SPEC_EVO_OFFSETS
    ),
    SpecEvoEvidence(
        name="Sukamon",
        target_id=0x27,
        from_id=0x27,
        offsets=PAL_DE_SUKAMON_SPEC_EVO_OFFSETS,
        confidence="verified-layout",
        note="Two active German Sukamon command blocks with two target bytes each.",
    ),
)
