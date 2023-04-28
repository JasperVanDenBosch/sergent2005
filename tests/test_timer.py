from __future__ import annotations
from unittest import TestCase
from unittest.mock import Mock


class TimerTests(TestCase):

    def setUp(self) -> None:
        self.consts = Mock()
        self.consts.short_T1_delay = 36     # 516ms
        self.consts.long_T1_delay = 60      # 860ms
        self.consts.short_SOA = 15          # 258ms
        self.consts.long_SOA = 41           # 688ms
        self.consts.target_dur = 3          # 43ms
        self.consts.task_delay = 37         # 500ms
        self.consts.iti_min_sec = 3 #seconds
        self.consts.iti_max_sec = 4 #seconds

    def test_70Hz_same(self):
        from experiment.timer import Timer
        timer = Timer()
        timer.optimizeFlips(70, self.consts)
        self.assertEqual(timer.short_T1_delay, self.consts.short_T1_delay)
        self.assertEqual(timer.long_T1_delay, self.consts.long_T1_delay)
        self.assertEqual(timer.short_SOA, self.consts.short_SOA)
        self.assertEqual(timer.long_SOA, self.consts.long_SOA)
        self.assertEqual(timer.target_dur, self.consts.target_dur)
        self.assertEqual(timer.task_delay, self.consts.task_delay)

    def test_123Hz(self):
        from experiment.timer import Timer
        timer = Timer()
        timer.optimizeFlips(123.45, self.consts)
        self.assertEqual(timer.short_T1_delay, 63)
        self.assertEqual(timer.long_T1_delay, 106)
        self.assertEqual(timer.short_SOA, 26)
        self.assertEqual(timer.long_SOA, 72)
        self.assertEqual(timer.target_dur, 5)
        self.assertEqual(timer.task_delay, 65)

    def test_secsToFlips(self):
        from experiment.timer import Timer
        timer = Timer()
        timer.optimizeFlips(123.45, self.consts)
        self.assertEqual(timer.secsToFlips(3.5), 432.075)
