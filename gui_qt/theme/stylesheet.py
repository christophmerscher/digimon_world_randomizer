# Author: Christoph Merscher <dev@fmerscher.com>

"""QSS stylesheet template for the modern dark theme.

The stylesheet is built from a :class:`~gui_qt.theme.palette.Palette`
so every colour is centralised. Split into named helpers so each chunk
stays small enough to read.

Conventions used throughout:

* All border-radii are 6 px (10 px for the larger cards) for a
  consistent corner language.
* All controls use 1 px borders in the muted neutral colour so the
  flat surface is visible without harsh outlines.
* Focus / hover states tint the border instead of adding box shadows
  (QSS supports neither glow nor shadow effects natively).
* Padding is generous; cramped controls are the #1 thing that makes a
  Qt app look old.
"""

from __future__ import annotations

from gui_qt.theme.palette import Palette


def build_stylesheet(palette: Palette) -> str:
    """Compose the full QSS body for the given palette."""

    return "\n".join((
        _base(palette),
        _buttons(palette),
        _accent_button(palette),
        _line_edit(palette),
        _combo_box(palette),
        _checkbox(palette),
        _radio_button(palette),
        _slider(palette),
        _group_box(palette),
        _tab_widget(palette),
        _terminal(palette),
        _scrollbars(palette),
    )).strip()


# ---------------------------------------------------------------------------
# Base / global
# ---------------------------------------------------------------------------

def _base(p: Palette) -> str:
    return f"""
/* --- Base ----------------------------------------------------------- */

QWidget {{
    background-color: {p.background};
    color: {p.text};
    font-size: 10pt;
}}

QLabel {{
    background: transparent;
    color: {p.text};
}}

QLabel[secondary="true"] {{
    color: {p.text_secondary};
}}

QToolTip {{
    background-color: {p.surface_pressed};
    color: {p.text};
    border: 1px solid {p.border_strong};
    padding: 6px 8px;
    border-radius: 4px;
}}
"""


# ---------------------------------------------------------------------------
# QPushButton
# ---------------------------------------------------------------------------

def _buttons(p: Palette) -> str:
    return f"""
/* --- Buttons -------------------------------------------------------- */

QPushButton {{
    background-color: {p.surface};
    color: {p.text};
    border: 1px solid {p.border};
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {p.surface_hover};
    border-color: {p.border_strong};
}}

QPushButton:pressed {{
    background-color: {p.surface_pressed};
}}

QPushButton:disabled {{
    color: {p.text_muted};
    border-color: {p.border};
    background-color: {p.surface};
}}
"""


# ---------------------------------------------------------------------------
# Primary / accent button (Randomize)
# ---------------------------------------------------------------------------

def _accent_button(p: Palette) -> str:
    return f"""
/* --- Accent button -------------------------------------------------- */

QPushButton#primaryButton {{
    background-color: {p.accent};
    color: {p.accent_text};
    border: 1px solid {p.accent};
    font-weight: 600;
    padding: 8px 18px;
}}

QPushButton#primaryButton:hover {{
    background-color: {p.accent_hover};
    border-color: {p.accent_hover};
}}

QPushButton#primaryButton:pressed {{
    background-color: {p.accent_pressed};
    border-color: {p.accent_pressed};
}}

QPushButton#primaryButton:disabled {{
    background-color: {p.surface};
    color: {p.text_muted};
    border-color: {p.border};
}}
"""


# ---------------------------------------------------------------------------
# Text inputs
# ---------------------------------------------------------------------------

def _line_edit(p: Palette) -> str:
    return f"""
/* --- Line edits ----------------------------------------------------- */

QLineEdit {{
    background-color: {p.surface};
    color: {p.text};
    border: 1px solid {p.border};
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: {p.accent};
    selection-color: {p.accent_text};
}}

QLineEdit:hover {{
    border-color: {p.border_strong};
}}

QLineEdit:focus {{
    border-color: {p.accent};
}}

QLineEdit:disabled {{
    color: {p.text_muted};
    background-color: {p.surface};
}}

QLineEdit:read-only {{
    color: {p.text_secondary};
}}
"""


# ---------------------------------------------------------------------------
# Combo boxes (dropdowns)
# ---------------------------------------------------------------------------

def _combo_box(p: Palette) -> str:
    return f"""
/* --- Combo boxes ---------------------------------------------------- */

QComboBox {{
    background-color: {p.surface};
    color: {p.text};
    border: 1px solid {p.border};
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 18px;
}}

QComboBox:hover {{
    border-color: {p.border_strong};
}}

QComboBox:focus {{
    border-color: {p.accent};
}}

QComboBox::drop-down {{
    border: none;
    width: 22px;
}}

/* Use a unicode chevron so we don't ship a binary asset. */
QComboBox::down-arrow {{
    image: none;
    width: 0;
    height: 0;
    border-left:  4px solid transparent;
    border-right: 4px solid transparent;
    border-top:   5px solid {p.text_secondary};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {p.surface};
    color: {p.text};
    border: 1px solid {p.border_strong};
    selection-background-color: {p.accent};
    selection-color: {p.accent_text};
    padding: 4px;
    border-radius: 6px;
}}
"""


# ---------------------------------------------------------------------------
# Checkbox + radio
# ---------------------------------------------------------------------------

def _checkbox(p: Palette) -> str:
    return f"""
/* --- Checkboxes ----------------------------------------------------- */

QCheckBox {{
    color: {p.text};
    spacing: 8px;
    padding: 2px 0;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {p.border_strong};
    border-radius: 4px;
    background-color: {p.surface};
}}

QCheckBox::indicator:hover {{
    border-color: {p.accent};
}}

QCheckBox::indicator:checked {{
    background-color: {p.accent};
    border-color: {p.accent};
}}

QCheckBox::indicator:disabled {{
    background-color: {p.surface};
    border-color: {p.border};
}}

QCheckBox:disabled {{
    color: {p.text_muted};
}}
"""


def _radio_button(p: Palette) -> str:
    return f"""
/* --- Radios --------------------------------------------------------- */

QRadioButton {{
    color: {p.text};
    spacing: 8px;
    padding: 2px 0;
}}

QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {p.border_strong};
    border-radius: 8px;
    background-color: {p.surface};
}}

QRadioButton::indicator:hover {{
    border-color: {p.accent};
}}

QRadioButton::indicator:checked {{
    background-color: {p.accent};
    border: 4px solid {p.surface};
    outline: 1px solid {p.accent};
}}

QRadioButton:disabled {{
    color: {p.text_muted};
}}
"""


# ---------------------------------------------------------------------------
# Sliders
# ---------------------------------------------------------------------------

def _slider(p: Palette) -> str:
    return f"""
/* --- Sliders -------------------------------------------------------- */

QSlider::groove:horizontal {{
    background: {p.surface_pressed};
    height: 4px;
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background: {p.accent};
    height: 4px;
    border-radius: 2px;
}}

QSlider::add-page:horizontal {{
    background: {p.surface_pressed};
    height: 4px;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {p.accent};
    border: 2px solid {p.background};
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: {p.accent_hover};
}}

QSlider::handle:horizontal:disabled {{
    background: {p.border_strong};
}}
"""


# ---------------------------------------------------------------------------
# Cards (group boxes)
# ---------------------------------------------------------------------------

def _group_box(p: Palette) -> str:
    return f"""
/* --- Section cards (QGroupBox) -------------------------------------- */

QGroupBox {{
    background-color: {p.surface};
    border: 1px solid {p.border};
    border-radius: 10px;
    margin-top: 14px;
    padding: 18px 14px 14px 14px;
    font-weight: 600;
    color: {p.text};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    background-color: {p.background};
    color: {p.text_secondary};
    font-size: 9pt;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}}
"""


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

def _tab_widget(p: Palette) -> str:
    return f"""
/* --- Tabs ----------------------------------------------------------- */

QTabWidget::pane {{
    background-color: {p.background};
    border: none;
    border-top: 1px solid {p.border};
    margin-top: -1px;
    padding-top: 12px;
}}

QTabBar {{
    background: transparent;
    qproperty-drawBase: 0;
}}

QTabBar::tab {{
    background: transparent;
    color: {p.text_secondary};
    padding: 9px 18px;
    margin-right: 4px;
    border: none;
    border-bottom: 2px solid transparent;
    font-weight: 500;
}}

QTabBar::tab:hover {{
    color: {p.text};
}}

QTabBar::tab:selected {{
    color: {p.text};
    border-bottom: 2px solid {p.accent};
}}

QTabBar::tab:disabled {{
    color: {p.text_muted};
}}
"""


# ---------------------------------------------------------------------------
# Terminal panel (QPlainTextEdit)
# ---------------------------------------------------------------------------

def _terminal(p: Palette) -> str:
    return f"""
/* --- Terminal panel ------------------------------------------------- */

QPlainTextEdit {{
    background-color: {p.surface};
    color: {p.text};
    border: 1px solid {p.border};
    border-radius: 8px;
    padding: 10px 12px;
    selection-background-color: {p.accent};
    selection-color: {p.accent_text};
}}

QPlainTextEdit:focus {{
    border-color: {p.border_strong};
}}

/* The QScrollArea used inside each tab keeps the same background as
   its parent — no inset border. */
QScrollArea {{
    border: none;
    background: transparent;
}}
"""


# ---------------------------------------------------------------------------
# Scrollbars (thin, no chrome)
# ---------------------------------------------------------------------------

def _scrollbars(p: Palette) -> str:
    return f"""
/* --- Scrollbars ----------------------------------------------------- */

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 4px 2px;
    border: none;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 2px 4px;
    border: none;
}}

QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {{
    background: {p.border_strong};
    border-radius: 4px;
    min-height: 24px;
    min-width: 24px;
}}

QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover {{
    background: {p.text_muted};
}}

/* Hide the line / page buttons entirely — pure handle, no arrows. */
QScrollBar::add-line,
QScrollBar::sub-line {{
    background: none;
    border: none;
    width: 0;
    height: 0;
}}

QScrollBar::add-page,
QScrollBar::sub-page {{
    background: transparent;
}}
"""
