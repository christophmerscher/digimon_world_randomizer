"""Technique (move) enums and lookups.

Re-exports the per-attribute enum classes so callers can do
``from data.technique import Techniques, TechniqueEffect, TechniquesRange``
instead of reaching into each submodule.
"""

from data.technique.technique_effect import TechniqueEffect
from data.technique.techniques import Techniques
from data.technique.techniques_range import TechniquesRange

__all__ = ["TechniqueEffect", "Techniques", "TechniquesRange", "tech_id"]


def tech_id(tech: Techniques) -> int:
    """Return the integer ROM ID for a :class:`Techniques` enum member."""

    return int(tech.value, 16)
