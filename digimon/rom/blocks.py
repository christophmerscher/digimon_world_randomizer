"""Descriptors for the large variable-length data blocks in the ROM.

Each block is a contiguous run of fixed-size records (techs, items, digimon
stats, evolution tables, jukebox track names). The PSX binary has small
"holes" inside several of these blocks that the engine never touches — those
are listed as ``ExclusionOffsets`` and the reader/writer skip them.

Module attributes are grouped by record kind so they can be discovered with
plain text search (``techDataBlockOffset``, ``itemDataFormat``, …).
"""


# ---------------------------------------------------------------------------
# Technique stat block
# ---------------------------------------------------------------------------

techDataFormat           = "<3H8Bxx"

techDataBlockOffset      = 0x14D66DF4
techDataBlockSize        = 0x8C0
techDataBlockCount       = 0x79

techDataExclusionOffsets = (
    0x14D673B8,
)
techDataExclusionSize    = 0x130


# ---------------------------------------------------------------------------
# Technique battle-learn-chance block
# ---------------------------------------------------------------------------

techLearnFormat          = "<BBB"

techLearnBlockOffset     = 0x14D66A2C
techLearnBlockSize       = 0x1DE
techLearnBlockCount      = 0x3A

techLearnExclusionOffsets = (
    0x14D66A88,
)
techLearnExclusionSize   = 0x130


# ---------------------------------------------------------------------------
# Technique brain-training learn chance block
# ---------------------------------------------------------------------------

techBrainFormat          = "<BBB"

techBrainBlockOffset     = 0x14C8E58C
techBrainBlockSize       = 0x18
techBrainBlockCount      = 0x08

techBrainExclusionOffsets: tuple[int, ...] = ()
techBrainExclusionSize   = 0x130


# ---------------------------------------------------------------------------
# Technique tier list table
# ---------------------------------------------------------------------------

techTierListFormat       = "<8B"

techTierListBlockOffset  = 0x14C8E554
techTierListBlockSize    = 0x38
techTierListBlockCount   = 0x07

techTierListExclusionOffsets: tuple[int, ...] = ()  # block is tiny; no holes
techTierListExclusionSize = 0x130


# ---------------------------------------------------------------------------
# Digimon stat block
# ---------------------------------------------------------------------------

digimonDataFormat        = "<20sihh23Bx"

digimonDataBlockOffset   = 0x14D6E9DC
digimonDataBlockSize     = 0x2A80
digimonDataBlockCount    = 0xB4

digimonDataExclusionOffsets = (
    0x14D6EB28,   # in Devimon
    0x14D6F458,   # in Biyomon
    0x14D6FD88,   # in Piddomon
    0x14D706B8,   # in Master Tyrannomon
    0x14D70FE8,   # in Biyomon
)
digimonDataExclusionSize = 0x130


# ---------------------------------------------------------------------------
# Digivolution to/from table
# ---------------------------------------------------------------------------

evoToFromFormat          = "<11B"

evoToFromBlockOffset     = 0x14D6CE04
evoToFromBlockSize       = 0x3DA
evoToFromBlockCount      = 0x3E

evoToFromExclusionOffsets = (
    0x14D6CF98,   # in to Bakemon 3-4
)
evoToFromExclusionSize   = 0x130


# ---------------------------------------------------------------------------
# Digivolution stat gains
# ---------------------------------------------------------------------------

evoStatsFormat           = "<6HH"

evoStatsBlockOffset      = 0x14D6CA68
evoStatsBlockSize        = 0x39C
evoStatsBlockCount       = 0x42

evoStatsExclusionOffsets: tuple[int, ...] = ()
evoStatsExclusionSize    = 0x130


# ---------------------------------------------------------------------------
# Digivolution requirements
# ---------------------------------------------------------------------------

evoReqsFormat            = "<11Hh2H"

evoReqsBlockOffset       = 0x14D6C254
evoReqsBlockSize         = 0x814
evoReqsBlockCount        = 0x3F

evoReqsExclusionOffsets = (
    0x14D6C668,   # in Bakemon
)
evoReqsExclusionSize     = 0x130


# ---------------------------------------------------------------------------
# Item block
# ---------------------------------------------------------------------------

itemDataFormat           = "<20sIHHb?2x"

itemDataBlockOffset      = 0x14D676C4
itemDataBlockSize        = 0x1260
itemDataBlockCount       = 0x80

itemDataExclusionOffsets = (
    0x14D67CE8,   # in Red Berry
    0x14D68618,   # in Coral charm
)
itemDataExclusionSize    = 0x130


# ---------------------------------------------------------------------------
# Giromon jukebox track names
# ---------------------------------------------------------------------------

trackNameBlockOffset     = 0x14D717E8
trackNameBlockSize       = 0x738

trackNameExclusionOffsets = (
    0x14D71918,   # in Lava Cave Theme
)
trackNameExclusionSize   = 0x130
