from __future__ import annotations
from typing import TYPE_CHECKING, Iterator, List
from dataclasses import dataclass, asdict
from experiment.trial import Trial, Phase, Task
from random import sample, shuffle, random as rand
from math import ceil
from experiment.triggers import Triggers
if TYPE_CHECKING:
    from experiment.constants import Constants
    from experiment.timer import Timer


@dataclass
class TrialRecipe(object):
    phase: Phase
    task: Task
    t2presence: bool
    soa_long: bool


class TrialGenerator:

    const: Constants
    timer: Timer
    all: List[Trial]

    def __init__(self, timer: Timer, const: Constants):
        self.const = const
        self.timer = timer
        self.all = []

    def generate(self, phase: Phase, task: Task) -> List[Trial]:
        """Compile a list of Trial objects for a training or test phase,
        single or dual task.
        """
        div = self.const.n_training_trial_divisor if phase == 'train' else 1
        trials = []
        for presence in (False, True):
            for soa in (False, True):
                recipe = TrialRecipe(phase, task, presence, soa)
                if task == 'single':
                    n = self.const.n_trials_single // div
                    trials += self.trialsFor(recipe, n)
                elif presence and (not soa):
                    n = self.const.n_trials_dual_critical // div
                    trials += self.trialsFor(recipe, n)
                else:
                    n = self.const.n_trials_dual_easy // div
                    trials += self.trialsFor(recipe, n)
        shuffle(trials)
        self.all += trials
        return trials

    def trialsFor(self, recipe: TrialRecipe, n: int) -> Iterator[Trial]:
        """balances the remaining variables within the condition
        """
        delays = self.shuffledRepeatedList([0, 1], n)
        t1s = self.shuffledRepeatedList([0, 1], n)
        t2s = self.shuffledRepeatedList([0, 1, 2, 3], n)
        vis_inits = self.shuffledRepeatedList(list(range(21)), n)
        iti_min = self.const.iti_min_sec
        iti_var = self.const.iti_max_sec - iti_min
        itis = [iti_min + rand()*iti_var for _ in range(n)]
        for t in range(n):
            yield self.createTrial(recipe, itis[t], delays[t], t1s[t], t2s[t], vis_inits[t])

    def shuffledRepeatedList(self, vals: List[int], length: int) -> List[int]:
        """Repeat the provided list until it is at least the given length,
        then return a shuffled version.
        """
        repeated_list = vals * ceil(length/len(vals))
        return sample(repeated_list, len(repeated_list))

    def createTrial(self, recipe: TrialRecipe, iti_s: float, delay: int, t1: int, t2: int, vis: int) -> Trial:
        """Create a single trial, initializing unbalanced random variables
        """
        masks = [''.join(sample(self.const.possible_consonants, 4)) for _ in range(3)]
        task_variant_trigger = Triggers.taskT1variant
        task_visibility_trigger = Triggers.taskT2visibility
        if recipe.phase=='train':
            task_variant_trigger = Triggers.taskT1variant_training
            task_visibility_trigger = Triggers.taskT2visibility_training
        return Trial(
            delay_index=delay,
            delay = [self.timer.short_T1_delay, self.timer.long_T1_delay][delay],
            soa = self.timer.long_SOA if recipe.soa_long else self.timer.short_SOA,
            iti=self.timer.secsToFlips(iti_s),
            t1_index=t1,
            t2_index=t2,
            t1_trigger=Triggers.get_number(
                training=recipe.phase=='train',
                forT2=False,
                t2Present=recipe.t2presence,
                dualTask=recipe.task=='dual',
                longSOA=recipe.soa_long
            ),
            t2_trigger=Triggers.get_number(
                training=recipe.phase=='train',
                forT2=True,
                t2Present=recipe.t2presence,
                dualTask=recipe.task=='dual',
                longSOA=recipe.soa_long
            ),
            id_trigger=task_variant_trigger,
            vis_trigger=task_visibility_trigger,
            masks=tuple(masks),
            vis_init=vis,
            **asdict(recipe)
        )
