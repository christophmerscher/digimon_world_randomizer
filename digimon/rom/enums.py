"""Domain enum tables (digimon types, levels, specialties, tech effects, names).

These dictionaries mirror the in-game enums and are read by both the binary
reader/writer and the user-facing logger. ID literals are kept as ``int``
values matching the ROM bytes.
"""

# Highest digimon ID belonging to the partner cast (player-controllable).
# Any digimon with id <= lastPartnerDigimon is referenced by evolution tables.
lastPartnerDigimon = 0x41

# Last tech ID that is NOT a finisher animation.
lastNonfinishTech = 0x39


# ---------------------------------------------------------------------------
# Type / level / specialty / range / effect lookups
# ---------------------------------------------------------------------------

types: dict[int, str] = {
    0x01: "DATA",
    0x02: "VACCINE",
    0x03: "VIRUS",
}

levels: dict[int, str] = {
    0x01: "FRESH",
    0x02: "IN-TRAINING",
    0x03: "ROOKIE",
    0x04: "CHAMPION",
    0x05: "ULTIMATE",
}

# Reverse lookup keyed by canonical level name.
levelsByName: dict[str, int] = {
    "FRESH":       0x01,
    "IN-TRAINING": 0x02,
    "ROOKIE":      0x03,
    "CHAMPION":    0x04,
    "ULTIMATE":    0x05,
}

specs: dict[int, str] = {
    0x00: "FIRE",
    0x01: "BATTLE",
    0x02: "AIR",
    0x03: "EARTH",
    0x04: "ICE",
    0x05: "MECH",
    0x06: "FILTH",
}

ranges: dict[int, str] = {
    0x01: "SHORT",
    0x02: "LARGE",
    0x03: "WIDE",
    0x04: "SELF",
}

effects: dict[int, str] = {
    0x00: "NONE",
    0x01: "POISON",
    0x02: "CONFUSE",
    0x03: "STUN",
    0x04: "FLAT",
}


# ---------------------------------------------------------------------------
# Tech names (id -> display name)
# ---------------------------------------------------------------------------

techs: dict[int, str] = {
    0x00: "Fire Tower",
    0x01: "Prominence Beam",
    0x02: "Spit Fire",
    0x03: "Red Inferno",
    0x04: "Magma Bomb",
    0x05: "Heat Laser",
    0x06: "Inifinity Burn",
    0x07: "Meltdown",
    0x08: "Thunder Justice",
    0x09: "Spinning Shot",
    0x0A: "Electric Cloud",
    0x0B: "Megalo Spark",
    0x0C: "Static Elect",
    0x0D: "Wind Cutter",
    0x0E: "Confused Storm",
    0x0F: "Hurricane",
    0x10: "Giga Freeze",
    0x11: "Ice Statue",
    0x12: "Winter Blast",
    0x13: "Ice Needle",
    0x14: "Water Blit",
    0x15: "Aqua Magic",
    0x16: "Aurora Freeze",
    0x17: "Tear Drop",
    0x18: "Power Crane",
    0x19: "All Range Beam",
    0x1A: "Metal Sprinter",
    0x1B: "Pulse Laser",
    0x1C: "Delete Program",
    0x1D: "DG Dimension",
    0x1E: "Full Potential",
    0x1F: "Reverse Prog",
    0x20: "Poison Powder",
    0x21: "Bug",
    0x22: "Mass Morph",
    0x23: "Insect Plague",
    0x24: "Charm Perfume",
    0x25: "Poison Claw",
    0x26: "Danger Sting",
    0x27: "Green Trap",
    0x28: "Tremar",
    0x29: "Muscle Charge",
    0x2A: "War Cry",
    0x2B: "Sonic Jab",
    0x2C: "Dynamite Kick",
    0x2D: "Counter",
    0x2E: "Megaton Punch",
    0x2F: "Buster Dive",
    0x30: "Dynamite Kick v2",
    0x31: "Odor Spray",
    0x32: "Poop Spd Toss",
    0x33: "Big Poop Toss",
    0x34: "Big Rnd Toss",
    0x35: "Poop Rnd Toss",
    0x36: "Rnd Spd Toss",
    0x37: "Horizontal Kick",
    0x38: "Ult Poop Hell",
    0x39: "Horizontal Kick v2",
    0x3A: "Blaze Blast",
    0x3B: "Pepper Breath",
    0x3C: "Lovely Attack",
    0x3D: "Fireball",
    0x3E: "Death Claw",
    0x3F: "Mega Flame",
    0x40: "Howling Blaster",
    0x41: "Party time",
    0x42: "Electric Shock",
    0x43: "Abduction Beam",
    0x44: "Smiley Bomb",
    0x45: "Spnning Needle",
    0x46: "Spiral Twister",
    0x47: "Boom Bubble",
    0x48: "Sweet Breath",
    0x49: "Bit Bomb",
    0x4A: "Deadly Bomb",
    0x4B: "Drill Spin",
    0x4C: "Electric Thread",
    0x4D: "Energy Bomb",
    0x4E: "Genoside Attack",
    0x4F: "Giga Scissor Claw",
    0x50: "Dark Shot",
    0x51: "Pummel Whack",
    0x52: "Hand of Fate",
    0x53: "Dark Claw",
    0x54: "Aerial Attack",
    0x55: "Bone Boomerang",
    0x56: "Solar Ray",
    0x57: "Hydro Pressure",
    0x58: "Ice Blast",
    0x59: "Iga School Knife Throw",
    0x5A: "Blasting Spout",
    0x5B: "Fist of the Beast King",
    0x5C: "Dark Network & Concert Crush",
    0x5D: "Electro Shocker",
    0x5E: "Meteor Wing",
    0x5F: "Super Slap",
    0x60: "Nightmare Syndromer",
    0x61: "Frozen Fire Shot",
    0x62: "Poison Ivy",
    0x63: "Blue Blaster",
    0x64: "Scissor Claw",
    0x65: "Super Thunder Strike",
    0x66: "Spiral Sword",
    0x67: "Variable Darts",
    0x68: "Volcanic Strike",
    0x69: "Subzero Ice Punch",
    0x6A: "Infinity Cannon",
    0x6B: "Party time",
    0x6C: "Party time",
    0x6D: "Crimson Flare",
    0x6E: "Glacial Blast",
    0x6F: "Mail Strome",
    0x70: "High Electro Shocker",
    0x71: "Bubble",
    0x72: "Bubble",
    0x73: "Bubble",
    0x74: "Bubble",
    0x75: "Bubble",
    0x76: "Bubble",
    0x77: "Bubble",
    0x78: "Bubble",
}


# ---------------------------------------------------------------------------
# Struct formats shared across many readers/writers
# ---------------------------------------------------------------------------

digimonIDFormat = "<B"
techIDFormat    = "<B"
animIDFormat    = "<B"

# IDs of the four canonical "starter" rookies referenced by the script.
rookies = (0x03, 0x04, 0x11, 0x12, 0x1F, 0x20, 0x2D, 0x2E, 0x39)
