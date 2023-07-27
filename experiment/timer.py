from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from experiment.constants import Constants


class Timer:

    ORIG_FLIP_RATE = 70.0

    short_T1_delay = 0
    long_T1_delay = 0
    short_SOA = 0
    long_SOA = 0
    target_dur = 0
    task_delay = 0

    flipRate = 0.0

    def optimizeFlips(self, flipRate: float, consts: Constants) -> None:
        self.flipRate = flipRate
        factor = self.flipRate/self.ORIG_FLIP_RATE
        self.short_T1_delay = round(consts.short_T1_delay * factor)
        self.long_T1_delay = round(consts.long_T1_delay * factor)
        self.short_SOA = round(consts.short_SOA * factor)
        self.long_SOA = round(consts.long_SOA * factor)
        self.target_dur = round(consts.target_dur * factor)
        self.task_delay = round(consts.task_delay * factor)

    def secsToFlips(self, secs: float) -> int:
        return round(secs*self.flipRate)
    
    def flipsToSecs(self, flips: int) -> float:
        return flips * (1/self.flipRate)
