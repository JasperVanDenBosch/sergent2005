from __future__ import annotations
from typing import TYPE_CHECKING, Iterator, List
from dataclasses import dataclass, asdict
from experiment.trial import Trial, Phase, Task
from random import sample
from math import ceil
from experiment.triggers import Triggers
if TYPE_CHECKING:
    from experiment.constants import Constants

@dataclass
class TrialRecipe(object):
    phase: Phase
    task: Task
    t2presence: bool
    soa: bool


def generateTrials(phase: Phase, task: Task, const: Constants) -> List[Trial]:
    """Compile a list of Trial objects for a training or test phase,
    single or dual task.
    """
    div = const.n_training_trial_divisor if phase == 'train' else 1
    trials = []
    for presence in (False, True):
        for soa in (False, True):
            recipe = TrialRecipe(phase, task, presence, soa)
            if task == 'single':
                n = const.n_trials_single // div
                trials += trialsFor(recipe, n, const)
            elif presence and (not soa):
                n = const.n_trials_dual_critical // div
                trials += trialsFor(recipe, n, const)
            else:
                n = const.n_trials_dual_easy // div
                trials += trialsFor(recipe, n, const)
    return trials

def trialsFor(recipe: TrialRecipe, n: int, const: Constants) -> Iterator[Trial]:
    """balances the remaining variables within the condition
    """
    delays = shuffledRepeatedList([0, 1], n)
    t1s = shuffledRepeatedList([0, 1], n)
    t2s = shuffledRepeatedList([0, 1, 2, 3], n)
    vis_inits = shuffledRepeatedList(list(range(21)), n)
    for t in range(n):
        yield createTrial(recipe, delays[t], t1s[t], t2s[t], vis_inits[t], const)

def shuffledRepeatedList(vals: List[int], length: int) -> List[int]:
    """Repeat the provided list until it is at least the given length,
    then return a shuffled version.
    """
    repeated_list = vals * ceil(length/len(vals))
    return sample(repeated_list, len(repeated_list))

def createTrial(recipe: TrialRecipe, delay: int, t1: int, t2: int, vis: int, 
                const: Constants) -> Trial:
    """Create a single trial, initializing unbalanced random variables
    """
    masks = [''.join(sample(const.possible_consonants, 4)) for _ in range(3)]
    return Trial(
        delay_index=delay,
        t1_index=t1,
        t2_index=t2,
        t1_trigger=Triggers.get_number(
            forT2=False,
            t2Present=recipe.t2presence,
            dualTask=recipe.task=='dual',
            longSOA=recipe.soa
        ),
        t2_trigger=Triggers.get_number(
            forT2=True,
            t2Present=recipe.t2presence,
            dualTask=recipe.task=='dual',
            longSOA=recipe.soa
        ),
        masks=tuple(masks),
        vis_init=vis,
        **asdict(recipe)
    )
