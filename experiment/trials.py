from __future__ import annotations
from typing import TYPE_CHECKING, Iterator, Tuple, List, Dict, Union, Literal
from dataclasses import dataclass, asdict
from experiment.trial import Trial, Phase, Task
from random import sample, shuffle
from math import ceil
if TYPE_CHECKING:
    from experiment.constants import Constants
    SoaCondition = Union[Literal['short'], Literal['long']]

@dataclass
class TrialRecipe(object):
    phase: Phase
    task: Task
    t2presence: bool
    soa: bool


def generateTrials(phase: Phase, task: Task, constants: Constants) -> List[Trial]:
    div = constants.n_training_trial_divisor if phase == 'train' else 1
    trials = []
    for presence in (False, True):
        for soa in (False, True):
            recipe = TrialRecipe(phase, task, presence, soa)
            if task == 'single':
                n = constants.n_trials_single // div
                trials += trialsFor(recipe, n)
            elif presence and (not soa):
                n = constants.n_trials_dual_critical // div
                trials += trialsFor(recipe, n)
            else:
                n = constants.n_trials_dual_easy // div
                trials += trialsFor(recipe, n)
    return trials

def trialsFor(recipe: TrialRecipe, n: int) -> Iterator[Trial]:
    """balances the remaining variables within the condition
    """
    delays = shuffledRepeatedList([0, 1], n)
    t1s = shuffledRepeatedList([0, 1], n)
    t2s = shuffledRepeatedList([0, 1, 2, 3], n)
    vis_inits = shuffledRepeatedList(list(range(21)), n)
    for t in range(n):
        yield createTrial(recipe, delays[t], t1s[t], t2s[t], vis_inits[t])

def shuffledRepeatedList(vals: List[int], length: int) -> List[int]:
    """Repeat the provided list until it is at least the given length,
    then return a shuffled version.
    """
    repeated_list = vals * ceil(length/len(vals))
    return sample(repeated_list, len(repeated_list))

def createTrial(recipe: TrialRecipe, delay: int, t1: int, t2: int, vis: int) -> Trial:
    """Create a single trial, initializing unbalanced random variables
    """
    return Trial(
        delay_index=delay,
        t1_index=t1,
        t2_index=t2,
        masks=('', '', ''),
        vis_init=vis,
        **asdict(recipe)
    )
