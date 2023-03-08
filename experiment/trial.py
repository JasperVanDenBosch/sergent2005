from __future__ import annotations
from typing import TYPE_CHECKING, Union, Literal
if TYPE_CHECKING:
    from experiment.engine import PsychopyEngine
Phase = Union[Literal['train'], Literal['test']]
Task = Union[Literal['single'], Literal['dual']]
SoaCondition = Union[Literal['short'], Literal['long']]

class Trial(object):
    phase: Phase
    task: Task
    t2present: bool
    soa: SoaCondition
    soa_frames: int
    iti: int
    t1: str
    t2: str

    def run(self, engine: PsychopyEngine):
        pass

#'Name': name, 'task':task, 'T2_presence':T2_presence, 'SOA':SOA, 'weight':weight}
# T1_start = start_T1_slow if random.random() > .5 else start_T1_quick
# training vs test
# target2.text = random.choice(CONSTANTS.target2_strings)
# target1.text = CONSTANTS.target1_strings[0] if random.random() > .5 else CONSTANTS.target1_strings[1]
# toDict() for results