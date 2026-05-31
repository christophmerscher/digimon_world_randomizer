# Author: Christoph Merscher <dev@fmerscher.com>

"""Colour palette for the modern PyQt6 theme.

A single :class:`Palette` dataclass holds every colour the stylesheet
needs. Putting them on one object instead of scattering ``"#1a1b1e"``
literals through the QSS makes it easy to tweak the look (or add a
light variant later) without hunting through string templates.

Colours follow a low-saturation neutral dark scheme with a single
vibrant violet accent — the visual language of contemporary developer
tools (VS Code, JetBrains, Linear, Raycast).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    """Named colour roles used throughout the GUI."""

    # ------------------------------------------------------------------
    # Backgrounds / surfaces
    # ------------------------------------------------------------------
    background:      str   # window background
    surface:         str   # card / panel background
    surface_hover:   str   # card hover state
    surface_pressed: str   # card pressed state

    # ------------------------------------------------------------------
    # Borders / dividers
    # ------------------------------------------------------------------
    border:          str   # subtle outlines around cards / inputs
    border_strong:   str   # focus / selection outline

    # ------------------------------------------------------------------
    # Text
    # ------------------------------------------------------------------
    text:            str   # primary readable text
    text_secondary:  str   # secondary / supporting text
    text_muted:      str   # placeholders / disabled labels

    # ------------------------------------------------------------------
    # Accent (primary action colour)
    # ------------------------------------------------------------------
    accent:          str
    accent_hover:    str
    accent_pressed:  str
    accent_text:     str   # text colour used on top of the accent

    # ------------------------------------------------------------------
    # Status colours
    # ------------------------------------------------------------------
    success:         str
    error:           str
    info:            str


# Canonical dark theme used by :func:`gui_qt.theme.apply_theme`.
DARK_PALETTE = Palette(
    background      = "#16171b",
    surface         = "#1f2025",
    surface_hover   = "#272930",
    surface_pressed = "#2e3038",

    border          = "#2c2e35",
    border_strong   = "#3d3f48",

    text            = "#e8e9ec",
    text_secondary  = "#a3a5ad",
    text_muted      = "#6c6e77",

    accent          = "#7c5cff",
    accent_hover    = "#9474ff",
    accent_pressed  = "#5e44d6",
    accent_text     = "#ffffff",

    success         = "#22c55e",
    error           = "#f87171",
    info            = "#60a5fa",
)
