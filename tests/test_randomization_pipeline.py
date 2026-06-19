# Author: Christoph Merscher <dev@fmerscher.com>

"""Tests for the Strategy-pattern randomiser pipeline.

The pipeline is the most behaviour-critical extraction in the refactor —
any change to RNG ordering breaks seed stability.  These tests exercise
the shared picker services + pipeline construction without needing a
real ROM.
"""

from __future__ import annotations

import random
import unittest

from digimon.randomization import (
    ChestItemsRandomizer,
    RandomItemPicker,
    RandomTechPicker,
    RandomizationContext,
    RandomizationPipeline,
    RecruitmentsRandomizer,
    RecruitmentValidator,
    StatRequirementGenerator,
    TechGiftsRandomizer,
)
from digimon.rom.state import RomState
from digimon.rom.layouts import PAL_DE_LAYOUT


class _SilentLogger:
    def log(self, msg: str) -> None: pass
    def logChange(self, msg: str) -> None: pass
    def logError(self, msg: str) -> None: pass
    def getHeader(self, name: str) -> str: return name


class _ItemStub:
    def __init__(self, id, name="Item", price=100, *, isBanned=False, isFood=False,
                 isConsumable=True, isEvo=False, dropable=True) -> None:
        self.id           = id
        self.name         = name
        self.price        = price
        self.isBanned     = isBanned
        self.isFood       = isFood
        self.isConsumable = isConsumable
        self.isEvo        = isEvo
        self.dropable     = dropable


class _TechStub:
    def __init__(self, id, *, isFinisher=False, isDamaging=True, isLearnable=True) -> None:
        self.id          = id
        self.name        = f"Tech{id}"
        self.isFinisher  = isFinisher
        self.isDamaging  = isDamaging
        self.isLearnable = isLearnable


class _DigimonStub:
    def __init__(self, id, *, name=None, height=100, pp=0) -> None:
        self.id = id
        self.name = name if name is not None else f"Digi{id}"
        self.height = height
        self.pp = pp


class _Lookup:
    def __init__(self) -> None:
        self.randomizedRequirements = False
        self.digimonData = []

    def getItemName(self, id):      return f"item-{id}"
    def getTechName(self, id):      return f"tech-{id}"
    def getDigimonName(self, id):   return f"digi-{id}"
    def getLevelName(self, id):     return ""
    def getTypeName(self, id):      return ""
    def getSpecialtyName(self, id): return ""
    def getRangeName(self, id):     return ""
    def getEffectName(self, id):    return ""
    def getDigimonByName(self, name): return None
    def getPlayableDigimonByLevel(self, level, excludeSpecials=False): return []


def _make_ctx(state: RomState | None = None, *, layout=None) -> RandomizationContext:
    queued: list = []

    def queue(name, value):
        queued.append((name, value))

    state = state if state is not None else RomState()
    ctx = RandomizationContext(
        state=state, logger=_SilentLogger(),
        lookup=_Lookup(), queue_patch=queue,
        layout=layout,
    )
    ctx.queued_patches = queued  # type: ignore[attr-defined]
    return ctx


# -----------------------------------------------------------------------
# Picker services (DRY check + filter correctness)
# -----------------------------------------------------------------------

class RandomItemPickerTests(unittest.TestCase):
    def test_banned_items_are_always_rejected(self):
        state = RomState()
        state.itemData = [
            _ItemStub(0, isBanned=True),
            _ItemStub(1, isBanned=False),
        ]

        random.seed(0)
        picker = RandomItemPicker(state)
        for _ in range(20):
            self.assertEqual(picker.pick(), 1)

    def test_food_only_filter(self):
        state = RomState()
        state.itemData = [
            _ItemStub(0, isFood=False),
            _ItemStub(1, isFood=True),
            _ItemStub(2, isFood=True),
        ]

        random.seed(1)
        picker = RandomItemPicker(state)
        for _ in range(20):
            self.assertIn(picker.pick(foodOnly=True), {1, 2})

    def test_match_value_keeps_cheap_for_cheap(self):
        state = RomState()
        state.itemData = [
            _ItemStub(0, price=10),
            _ItemStub(1, price=10_000),
            _ItemStub(2, price=20),
        ]

        random.seed(2)
        picker = RandomItemPicker(state)
        for _ in range(20):
            self.assertIn(
                picker.pick(matchValueOf=0, matchValue=1000),
                {0, 2},   # only items below the cutoff
            )


class RandomTechPickerTests(unittest.TestCase):
    def test_learnable_only_filter(self):
        state = RomState()
        state.techData = [
            _TechStub(0, isLearnable=False),
            _TechStub(1, isLearnable=True),
        ]

        random.seed(3)
        picker = RandomTechPicker(state)
        for _ in range(20):
            self.assertEqual(picker.pick(learnableOnly=True), 1)


# -----------------------------------------------------------------------
# StatRequirementGenerator
# -----------------------------------------------------------------------

class StatRequirementGeneratorTests(unittest.TestCase):
    def test_rookie_sets_exactly_three_stats_to_one(self):
        import digimon.data as data

        random.seed(4)
        result = StatRequirementGenerator().generate(data.levelsByName["ROOKIE"])

        ones    = [v for v in result if v == 1]
        unset   = [v for v in result if v == 0xFFFF]
        self.assertEqual(len(ones), 3)
        self.assertEqual(len(unset), 3)


# -----------------------------------------------------------------------
# RecruitmentValidator
# -----------------------------------------------------------------------

class RecruitmentValidatorTests(unittest.TestCase):
    class _NamedLookup:
        def __init__(self, names: dict[int, str]) -> None:
            self._names = names

        def getDigimonName(self, id: int) -> str:
            return self._names.get(id, "")

    def test_whamon_as_factorial_recruit_is_invalid(self):
        # trigger 211 → recruited digimon id 11 (Numemon — a Factorial-
        # Town recruit) — and the chosen replacement is Whamon. Without
        # Whamon being recruitable separately, the player can softlock.
        state = RomState()
        state.recruitData = {
            211: ((), 0x18, ()),   # 0x18 = Whamon's id (the "showed up")
        }
        lookup = self._NamedLookup({11: "Numemon", 0x18: "Whamon"})

        self.assertFalse(RecruitmentValidator(lookup).is_valid(state))

    def test_whamon_after_non_factorial_recruit_is_valid(self):
        state = RomState()
        state.recruitData = {
            245: ((), 0x18, ()),   # 245 - 200 = 45 → Biyomon
        }
        lookup = self._NamedLookup({45: "Biyomon", 0x18: "Whamon"})

        self.assertTrue(RecruitmentValidator(lookup).is_valid(state))


# -----------------------------------------------------------------------
# Pipeline factory
# -----------------------------------------------------------------------

class RandomizationPipelineTests(unittest.TestCase):
    def test_pipeline_run_executes_each_step_in_order(self):
        ctx = _make_ctx()
        order: list[str] = []

        class _StepA:
            def apply(self, c):     order.append("A")

        class _StepB:
            def apply(self, c):     order.append("B")

        RandomizationPipeline(ctx).add(_StepA()).add(_StepB()).run()
        self.assertEqual(order, ["A", "B"])

    def test_build_from_config_picks_only_enabled_sections(self):
        from tests.test_settings import _validConfig

        config = _validConfig()
        config["chests"]["Enabled"]    = True
        config["techGifts"]["Enabled"] = True

        ctx = _make_ctx()
        pipeline = RandomizationPipeline.build_from_config(config, ctx)

        # Internal accessor for testing: walk the steps list.
        steps = [type(s).__name__ for s in pipeline._steps]
        self.assertEqual(steps, ["ChestItemsRandomizer", "TechGiftsRandomizer"])


# -----------------------------------------------------------------------
# A pair of randomisers running end-to-end against a tiny stub state
# -----------------------------------------------------------------------

class IntegrationTests(unittest.TestCase):
    def test_chest_randomizer_replaces_every_chest_with_valid_item(self):
        state = RomState()
        state.itemData = [
            _ItemStub(0, name="A"),
            _ItemStub(1, name="B"),
            _ItemStub(2, name="C", isEvo=True),
            _ItemStub(3, name="D"),
        ]
        state.chestItems = {0x1000: 0, 0x2000: 1}

        random.seed(42)
        ChestItemsRandomizer(allow_evo=False).apply(_make_ctx(state))

        for new_id in state.chestItems.values():
            self.assertIn(new_id, {0, 1, 3})   # evo item must not appear

    def test_tech_gifts_randomizer_only_picks_learnable_techs(self):
        state = RomState()
        state.techData = [
            _TechStub(0, isLearnable=False),
            _TechStub(1, isLearnable=True),
            _TechStub(2, isLearnable=True),
            _TechStub(3, isLearnable=False),
        ]
        state.techGifts = {(0xA, 0xB): 0, (0xC, 0xD): 3}

        random.seed(123)
        TechGiftsRandomizer().apply(_make_ctx(state))

        for new_id in state.techGifts.values():
            self.assertIn(new_id, {1, 2})

    def test_pal_recruitment_queues_pp_patch_and_encodes_pp_bits(self):
        state = RomState()
        state.recruitData = {204: ((0x10,), 5, ())}
        state.digimonData = [_DigimonStub(i) for i in range(6)]
        state.digimonData[4] = _DigimonStub(4, name="Old", height=100, pp=0)
        state.digimonData[5] = _DigimonStub(5, name="New", height=200, pp=3)

        random.seed(1)
        ctx = _make_ctx(state, layout=PAL_DE_LAYOUT)

        RecruitmentsRandomizer().apply(ctx)

        self.assertEqual(ctx.queued_patches, [("pp", 0), ("ogremon", 0)])
        self.assertEqual(state.digimonData[4].height, 103)


if __name__ == "__main__":
    unittest.main()
