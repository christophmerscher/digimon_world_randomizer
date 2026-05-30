"""ROM layout descriptors, binary IO, and patch byte tables.

Sub-packages collect the hard-coded constants that describe the Digimon World
PSX ROM image: enum tables (`enums`), variable-length data blocks (`blocks`),
script-command offset tables (`script_offsets`), and binary payloads for the
optional patches (`patch_data`).

These modules contain no behaviour, only descriptors. Behaviour lives in
`digimon.rom.reader`, `digimon.rom.writer`, and the patch Strategy classes
under `digimon.rom.patches` (added in later phases of the refactor).
"""
