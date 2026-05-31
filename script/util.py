# Author: Tristan Challener <challenert@gmail.com>
# Copyright: please don't steal this that is all

"""Script-text encoding / decoding + instruction compiler.

The Digimon World engine stores in-game dialogue and event triggers
as a small bytecode. This module ports just enough of that bytecode
for the randomizer's needs:

* :func:`encode` / :func:`decode` turn ASCII strings into the engine's
  two-byte-per-character text format and back. Used by the recruitment
  reader/writer to verify name placeholders and by the intro-hash
  patch to inject the settings hash into Jijimon's dialogue.
* :func:`compile` emits the raw bytes for a single instruction
  (``jumpTo``, ``learnMove``, …). Used by the intro-skip patch.

The opcode constants below mirror the values the engine treats as
"start of <command>" markers; the reader/writer compare them to
detect that they are looking at the right kind of script entry.
"""

from __future__ import annotations

import struct


# ---------------------------------------------------------------------------
# Script opcodes (engine-defined)
# ---------------------------------------------------------------------------

giveItem   = 0x28
spawnItem  = 0x74
learnMove  = 0x2D
spawnChest = 0x75
jumpTo     = 0x16


# ---------------------------------------------------------------------------
# Text encoding (two bytes per character; one byte per case bucket)
# ---------------------------------------------------------------------------

def encode(text: str) -> bytes:
    """Encode an ASCII string in the engine's two-byte-per-char text format.

    Supports the lowercase + uppercase Latin alphabets, digits, space,
    and newline. Unsupported characters print an error and are skipped.
    """

    packed = b""

    for char in text:
        if char in "abcdefghijklmnopqrstuvwxyz":
            packed += struct.pack("<BB", 0x82, 0x81 + ord(char) - ord("a"))
        elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            packed += struct.pack("<BB", 0x82, 0x60 + ord(char) - ord("A"))
        elif char in "0123456789":
            packed += struct.pack("<BB", 0x82, 0x4F + int(char))
        elif char == " ":
            packed += struct.pack("<BB", 0x81, 0x40)
        elif char == "\n":
            packed += struct.pack("<BB", 0x0D, 0x00)
        else:
            print("Error: trying to encode unsupported character")

    return packed


def decode(data: bytes) -> str:
    """Inverse of :func:`encode` — recover an ASCII string.

    Reads every second byte (the case-bucket selector + offset combined)
    and walks the same case ranges in reverse. Only alphanumeric +
    space + newline characters are recognised.
    """

    out = ""

    for byte in data[1::2]:
        if not isinstance(byte, int):
            byte = ord(byte)

        if byte == 0:
            out += "\n"
            continue

        if byte < 0x40:
            print("Error: trying to encode unsupported character")
            continue

        offset = byte - 0x40
        if offset < 0x0F:
            out += " "
            continue

        offset -= 0x0F
        if offset < 0x11:
            out += "0123456789"[offset]
            continue

        offset -= 0x11
        if offset < 0x21:
            out += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[offset]
            continue

        offset -= 0x21
        out += "abcdefghijklmnopqrstuvwxyz"[offset]

    return out


# ---------------------------------------------------------------------------
# Instruction compiler (used by patches)
# ---------------------------------------------------------------------------

def compile(inst: str, *args) -> bytes:
    """Pack a single script instruction into its raw byte form."""

    if inst == "spawnChest":
        return struct.pack("<BBhhhhh", spawnChest, *args[:6])
    if inst == "giveItem":
        return struct.pack("<BBBB", giveItem, 0x00, args[0], args[1])
    if inst == "spawnItem":
        return struct.pack("<BBhh", spawnItem, args[0], args[1], args[2])
    if inst in ("learnMove", "move"):
        return struct.pack("<BB", learnMove, args[0])
    if inst == "jumpTo":
        return struct.pack("<BxH", jumpTo, args[0])

    raise ValueError(f"Unknown script instruction: {inst!r}")
