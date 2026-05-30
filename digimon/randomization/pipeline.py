"""Build and run the per-section randomiser sequence from settings."""

from __future__ import annotations

from typing import Any

from digimon.randomization.base import RandomizationContext, Randomizer
from digimon.randomization.chests import ChestItemsRandomizer
from digimon.randomization.digimon_data import DigimonDataRandomizer
from digimon.randomization.evolution_requirements import EvolutionRequirementsRandomizer
from digimon.randomization.evolutions import EvolutionsRandomizer
from digimon.randomization.map_items import MapItemsRandomizer
from digimon.randomization.recruitments import RecruitmentsRandomizer
from digimon.randomization.special_evolutions import (
    DevimonStatGainOverride,
    SpecialEvolutionsRandomizer,
)
from digimon.randomization.starters import StartersRandomizer
from digimon.randomization.tech_data import TechDataRandomizer
from digimon.randomization.tech_gifts import TechGiftsRandomizer
from digimon.randomization.tokomon import TokomonItemsRandomizer


# Default cutoff matches the legacy ``DEFAULT_ITEM_VALUE_CUTOFF``.
DEFAULT_PRICE_CUTOFF = 10000


class RandomizationPipeline:
    """Sequence of :class:`Randomizer` instances that run in handler-order."""

    def __init__(self, ctx: RandomizationContext) -> None:
        self._ctx = ctx
        self._steps: list[Randomizer] = []

    # ------------------------------------------------------------------
    def add(self, randomizer: Randomizer) -> "RandomizationPipeline":
        self._steps.append(randomizer)
        return self

    def run(self) -> None:
        for step in self._steps:
            step.apply(self._ctx)

    # ------------------------------------------------------------------
    @classmethod
    def build_from_config(
        cls,
        config: dict[str, Any],
        ctx: RandomizationContext,
        *,
        price_parser=int,
    ) -> "RandomizationPipeline":
        """Construct a pipeline matching the legacy ``_applyRandomizationSettings``.

        ``price_parser`` is a function the caller uses to parse the
        configured "valuable item cutoff" string into an int. The
        existing CLI (``digimon/randomizer.py``) passes one that logs a
        fatal error on a bad value; the default ``int`` here is fine for
        tests and the future :mod:`digimon.app`.
        """

        pipeline = cls(ctx)

        digimon_cfg = config["digimon"]
        if digimon_cfg["Enabled"]:
            pipeline.add(DigimonDataRandomizer(
                drop_item=digimon_cfg["DroppedItem"],
                drop_rate=digimon_cfg["DropRate"],
                price=cls._price(digimon_cfg, price_parser),
            ))

        techs_cfg = config["techs"]
        if techs_cfg["Enabled"]:
            pipeline.add(TechDataRandomizer(
                mode=techs_cfg["RandomizationMode"],
                power=techs_cfg["Power"],
                cost=techs_cfg["Cost"],
                accuracy=techs_cfg["Accuracy"],
                effect=techs_cfg["Effect"],
                effect_chance=techs_cfg["EffectChance"],
            ))
            if techs_cfg["TypeEffectiveness"]:
                ctx.queue_patch("typeEffectiveness", 0)

        starter_cfg = config["starter"]
        if starter_cfg["Enabled"]:
            pipeline.add(StartersRandomizer(
                use_weakest_tech=starter_cfg["UseWeakestTech"],
                force_digimon=starter_cfg["Digimon"],
                allowed_levels=_allowed_starter_levels(starter_cfg),
            ))

        if config["recruitment"]["Enabled"]:
            pipeline.add(RecruitmentsRandomizer())

        chests_cfg = config["chests"]
        if chests_cfg["Enabled"]:
            pipeline.add(ChestItemsRandomizer(allow_evo=chests_cfg["AllowEvolutionItems"]))

        tokomon_cfg = config["tokomon"]
        if tokomon_cfg["Enabled"]:
            pipeline.add(TokomonItemsRandomizer(consumable_only=tokomon_cfg["ConsumableOnly"]))

        if config["techGifts"]["Enabled"]:
            pipeline.add(TechGiftsRandomizer())

        map_items_cfg = config["mapItems"]
        if map_items_cfg["Enabled"]:
            pipeline.add(MapItemsRandomizer(
                food_only=map_items_cfg["FoodOnly"],
                price=cls._price(map_items_cfg, price_parser),
            ))

        evolution_cfg = config["evolution"]
        if evolution_cfg["Enabled"]:
            if evolution_cfg["Requirements"]:
                pipeline.add(EvolutionRequirementsRandomizer())

            pipeline.add(EvolutionsRandomizer(obtain_all=evolution_cfg["ObtainAllMode"]))

            if evolution_cfg["SpecialEvolutions"]:
                pipeline.add(SpecialEvolutionsRandomizer())
                pipeline.add(DevimonStatGainOverride())

        return pipeline

    # ------------------------------------------------------------------
    @staticmethod
    def _price(section_cfg, price_parser) -> int:
        # Mirror the legacy ``getPriceCutoff`` semantics.
        raw = section_cfg["ValuableItemCutoff"] if section_cfg["MatchValue"] else DEFAULT_PRICE_CUTOFF
        return price_parser(raw)


def _allowed_starter_levels(starter_cfg) -> list[int]:
    """Convert the per-level toggles into the list of allowed level IDs.

    Local helper so the pipeline factory has zero import dependencies on
    :mod:`digimon.settings`.
    """

    from digimon.rom.enums import levels

    flags = (
        starter_cfg["Fresh"],
        starter_cfg["InTraining"],
        starter_cfg["Rookie"],
        starter_cfg["Champion"],
        starter_cfg["Ultimate"],
    )
    return [level for enabled, level in zip(flags, list(levels.keys())) if enabled]
