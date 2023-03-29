from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List, Dict, Union, Literal
from dataclasses import dataclass, asdict
from experiment.trial import Trial, Phase, Task
from random import shuffle
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

def trialsFor(recipe: TrialRecipe, n: int) -> List[Trial]:
    delays = [True, False] * ceil(n/2)
    shuffle(delays)
    trials = []
    for t in range(n):
        trials.append(Trial(
            delay=delays[t],
            t1='',
            t2='',
            masks=('', '', ''),
            vis_init=1,
            **asdict(recipe)
        ))
    return trials


def computeStimulusList(
        training: bool,
        dual_task: bool,
        single_trials: int,
        dual_critical_trials: int,
        dual_easy_trials: int
    ) -> Tuple[List[Dict], List[Dict]]:
    '''
    In this function a list of dictionaries containing all possible combination of
    trial types is created. It returns two lists, one for the dual task condition
    and one for the single task condition. These lists are handed over to TrialHandlers
    that control for randomized (and weighted) trials execution in training and
    testing sessions.
    Parameters:
        training bool : True if this is used for a training session
        single_trials int : Number of trials in the single condition
        dual_critical_trials int : Number of trials in the critical dual task
                                   condition (short SOA and present T2).
        dual_easy_trials int : Number of trials in the easy dual task conditions
                               (short SOA/T2 absent or long SOA).
    '''

    # T1_start = start_T1_slow if random.random() > .5 else start_T1_quick
    # duration_SOA = long_SOA if currentTrial['SOA']=='long' else short_SOA
    # target2_presence = True if currentTrial['T2_presence']=='present' else False


    # if training:
    #     ntrials_div = n_training_trial_divisor
    # else:
    #     ntrials_div = 1

    # stimList = []
    # for task in ['single', 'dual']:
    #     for T2_presence in ['present', 'absent']:
    #         for SOA in ['short', 'long']:
    #             name = '_'.join([task, T2_presence, SOA])
    #             if training:
    #                 name = name + '_training'
    #             if task=='single':
    #                 weight = int(single_trials/ntrials_div)
    #             elif task=='dual' and SOA=='short' and T2_presence=='present':
    #                 weight = int(dual_critical_trials/ntrials_div)
    #             else:
    #                 weight = int(dual_easy_trials/ntrials_div)

    #             stimList.append({'Name': name, 'task':task, 'T2_presence':T2_presence, 'SOA':SOA, 'weight':weight})

    # stimuli_single = stimList[0:int(len(stimList)/2)]
    # stimuli_dual = stimList[int(len(stimList)/2):len(stimList)]
    # print('Single: ')
    # [print(single) for single in stimuli_single]
    # print('DUAL: ')
    # [print(dual) for dual in stimuli_dual]

    return stimuli_single, stimuli_dual