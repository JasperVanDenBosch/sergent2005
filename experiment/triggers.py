from __future__ import annotations
from dataclasses import dataclass, asdict
OFFSET = True

def trigger_logic():
    """Print overview of how the trigger numbers relate to conditions
    """
    def boolify(k0: str, k1: str):
        return list(zip((k0, k1), (False, True)))
    for stim, b1 in boolify('t1', 't2'):
        for t2, b2 in boolify('absent', 'present'):
            for task, b3 in boolify('single', 'dual'):
                for soa, b4 in boolify('short', 'long'):
                    bools = [OFFSET, b1, b2, b3, b4]
                    number = int(''.join([str(int(b)) for b in bools]), 2)
                    name = f'{stim}_{t2}_{task}Task_{soa}SOA'
                    print(f'{name:32} {number}')


@dataclass(frozen=True)
class Triggers:
    t1_absent_singleTask_shortSOA  : int =  16
    t1_absent_singleTask_longSOA   : int =  17
    t1_absent_dualTask_shortSOA    : int =  18
    t1_absent_dualTask_longSOA     : int =  19
    t1_present_singleTask_shortSOA : int =  20
    t1_present_singleTask_longSOA  : int =  21
    t1_present_dualTask_shortSOA   : int =  22
    t1_present_dualTask_longSOA    : int =  23
    t2_absent_singleTask_shortSOA  : int =  24
    t2_absent_singleTask_longSOA   : int =  25
    t2_absent_dualTask_shortSOA    : int =  26
    t2_absent_dualTask_longSOA     : int =  27
    t2_present_singleTask_shortSOA : int =  28
    t2_present_singleTask_longSOA  : int =  29
    t2_present_dualTask_shortSOA   : int =  30
    t2_present_dualTask_longSOA    : int =  31
    taskT1variant: int = 1
    taskT2visibility: int = 2

    t1_absent_singleTask_shortSOA_training  : int =  32
    t1_absent_singleTask_longSOA_training   : int =  33
    t1_absent_dualTask_shortSOA_training    : int =  34
    t1_absent_dualTask_longSOA_training     : int =  35
    t1_present_singleTask_shortSOA_training : int =  36
    t1_present_singleTask_longSOA_training  : int =  37
    t1_present_dualTask_shortSOA_training   : int =  38
    t1_present_dualTask_longSOA_training    : int =  39
    t2_absent_singleTask_shortSOA_training  : int =  40
    t2_absent_singleTask_longSOA_training   : int =  41
    t2_absent_dualTask_shortSOA_training    : int =  42
    t2_absent_dualTask_longSOA_training     : int =  43
    t2_present_singleTask_shortSOA_training : int =  44
    t2_present_singleTask_longSOA_training  : int =  45
    t2_present_dualTask_shortSOA_training   : int =  46
    t2_present_dualTask_longSOA_training    : int =  47
    taskT1variant_training: int = 11
    taskT2visibility_training: int = 12

    @classmethod
    def get_number(cls, training=False, forT2=False, t2Present=False, dualTask=False, longSOA=False) -> int:
        bools = [training, not training, forT2, t2Present, dualTask, longSOA]
        return int(''.join([str(int(b)) for b in bools]), 2)

    def asdict(self):
        return asdict(self)
