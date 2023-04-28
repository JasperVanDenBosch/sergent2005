from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from experiment.constants import Constants


class Timer:

    short_T1_delay = 0
    long_T1_delay = 0
    short_SOA = 0
    long_SOA = 0
    target_dur = 0
    task_delay = 0

    fliprate = 0.0

    def optimizeFlips(self, flipRate: float, consts: Constants) -> None:
        pass

    def secsToFlips(self, secs: float) -> int:
        return -99
