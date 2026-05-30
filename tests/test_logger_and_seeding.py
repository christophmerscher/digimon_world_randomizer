# Author: Christoph Merscher <dev@fmerscher.com>

"""Tests for the modernised :class:`Logger` and the new :class:`SeedingPolicy`."""

from __future__ import annotations

import os
import random
import tempfile
import unittest

from digimon.seeding import SeedingPolicy
from log.logger import Logger


class LoggerVerbosityTests(unittest.TestCase):
    def test_full_verbosity_writes_every_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "full.log")
            with Logger("full", filename=path) as log:
                log.log("debug-msg")
                log.logChange("change-msg")

            with open(path) as f:
                contents = f.read()

            self.assertIn("debug-msg", contents)
            self.assertIn("change-msg", contents)

    def test_casual_verbosity_suppresses_debug_messages(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "casual.log")
            with Logger("casual", filename=path) as log:
                log.log("debug-msg")
                log.logChange("change-msg")

            with open(path) as f:
                contents = f.read()

            self.assertNotIn("debug-msg", contents)
            self.assertIn("change-msg", contents)

    def test_error_messages_set_the_flag_and_always_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "race.log")
            with Logger("race", filename=path) as log:
                self.assertFalse(log.error)
                log.logError("boom")
                self.assertTrue(log.error)

            with open(path) as f:
                self.assertIn("boom", f.read())

    def test_context_manager_closes_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "cm.log")
            with Logger("full", filename=path) as log:
                log.logChange("inside")

            # Inside the open() context the file should be closed.
            self.assertIsNone(log.file)

    def test_rename_moves_the_log_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = os.path.join(tmp, "before.log")
            renamed  = os.path.join(tmp, "after.log")

            with Logger("full", filename=original) as log:
                log.logChange("hi")

            log.rename(renamed)
            self.assertTrue(os.path.exists(renamed))
            self.assertFalse(os.path.exists(original))


class SeedingPolicyTests(unittest.TestCase):
    def test_explicit_seed_is_returned_unchanged(self):
        seed = SeedingPolicy(verbose="full").seed(12345)
        self.assertEqual(seed, 12345)

    def test_random_seed_is_picked_when_none_passed(self):
        seed = SeedingPolicy(verbose="full").seed(None)
        self.assertIsInstance(seed, int)
        self.assertGreaterEqual(seed, 0)

    def test_race_mode_advances_rng_versus_casual(self):
        # Same seed, different verbosity → different next random draw.
        casual_first = self._first_draw_after_seed("casual", seed=42)
        race_first   = self._first_draw_after_seed("race",   seed=42)
        self.assertNotEqual(casual_first, race_first)

    @staticmethod
    def _first_draw_after_seed(verbose: str, seed: int) -> int:
        SeedingPolicy(verbose=verbose).seed(seed)
        return random.randint(0, 10_000_000)


if __name__ == "__main__":
    unittest.main()
