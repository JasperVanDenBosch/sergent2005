from __future__ import annotations
from typing import TYPE_CHECKING, Union, Literal, Tuple
from experiment.constants import Constants
from experiment.triggers import Triggers
if TYPE_CHECKING:
    from experiment.engine import PsychopyEngine
Phase = Union[Literal['train'], Literal['test']]
Task = Union[Literal['single'], Literal['dual']]
SoaCondition = Union[Literal['short'], Literal['long']]
constants = Constants()

class Trial(object):
    phase: Phase
    task: Task
    t2present: bool
    soa: SoaCondition
    soa_frames: int
    iti: int # aka T1_start or timing_T1_start
    t1: str
    t2: str
    masks: Tuple[str, str, str] # three masks of four characters each
    vis_init: int # random initial state of visibility rating

    @property
    def t1TriggerNr(self):
        return Triggers.get_number(
            forT2=False,
            t2Present=self.t2present,
            dualTask=self.task=='dual',
            longSOA=self.soa=='long'
        )
    
    @property
    def t2TriggerNr(self):
        return Triggers.get_number(
            forT2=True,
            t2Present=self.t2present,
            dualTask=self.task=='dual',
            longSOA=self.soa=='long'
        )

    ## construction
    #'Name': name, 'task':task, 'T2_presence':T2_presence, 'SOA':SOA, 'weight':weight}
    # T1_start = start_T1_slow if random.random() > .5 else start_T1_quick
    # training vs test
    # target2.text = random.choice(constants.target2_strings)
    # target1.text = constants.target1_strings[0] if random.random() > .5 else constants.target1_strings[1]
    # toDict() for results

    def run(self, engine: PsychopyEngine): # , port: TriggerPort

        # it starts with the fixation cross
        self.displayFixCross()
        core.wait(self.iti)

        textT1 = self.displayT1(self.t1TriggerNr)
        core.wait(constants.stimulus_duration) # - trigger??

        # display black screen between stimuli and masks
        # engine.emptyScreen(duration)
        SCREEN.flip()
        core.wait(constants.stimulus_duration)

        self.displayMask()
        core.wait(constants.stimulus_duration)

        # display the fixation cross either short_SOA - 129ms or long_SOA - 129ms,
        # since the target, the mask and the black screen was displayed for 43ms each
        self.displayFixCross()
        duration_SOA = self.soa_frames
        fix_dur = duration_SOA - constants.stimulus_duration*3 # TODO convert to frames

        textT2 = self.displayT2(self.t2present, self.t2TriggerNr)
        core.wait(constants.stimulus_duration)

        # display black screen between stimuli and masks
        # engine.emptyScreen(duration)
        SCREEN.flip()
        core.wait(constants.stimulus_duration)

        # display two masks after another with black screen inbetween
        self.displayMask()
        core.wait(constants.stimulus_duration)

        # engine.emptyScreen(duration)
        SCREEN.flip()
        core.wait(constants.stimulus_duration)

        self.displayMask()
        core.wait(constants.stimulus_duration)

        SCREEN.flip()
        core.wait(constants.visibility_scale_timing)

        # start the visibility rating (happens in single AND dual task conditions)
         # ratingT2 is tuple of rating, RT
        ratingT2 = engine.prompt2(
            constants.task2_text,
            ('nothing', 'maximal visibility'),
            constants.scale_length,
            self.vis_init,
            Triggers.taskT2visibility
        )

        # only in the dual task condition the question on target 1 is displayed
        if self.task == 'dual':
            ratingT1 = engine.prompt1(constants.task1_text, ('OO', 'XX'), Triggers.taskT1variant)
            # accuracy of answer
            correct = True if ratingT1[0] in textT1 else False # ratingT1 is tuple of rating, RT
            ratingT1.append(correct)
        else:
            ratingT1 = [None, None, None]

        return ratingT2, ratingT1, textT2, textT1 # ratingT2 is tuple of rating, RT


    def displayT1(self, triggerNr: int):
        '''
        Displays the first target (T1) consisting of either the string 'OXXO' or 'XOOX'
        '''
        target1.text = constants.target1_strings[0] if random.random() > .5 else constants.target1_strings[1]
        target1.draw()
        port.trigger(triggerNr)
        SCREEN.flip()
        return target1.text


    def displayT2(self, T2_present, triggerNr: int):
        '''
        Displays the second target (T2) constisting of 4 white squares and (if present
        condition is active) of a number word in capital letters.
        Parameters:
            T2_present bool: True for present or False for absent
        '''
        target2_square1.draw()
        target2_square2.draw()
        target2_square3.draw()
        target2_square4.draw()

        if T2_present:
            target2.text = random.choice(constants.target2_strings)
            target2.draw()
        else:
            target2.text = ''

        port.trigger(triggerNr)
        SCREEN.flip()
        return target2.text

    def displayMask(self):
        '''
        Displays a mask consisting of 4 consonants. The mask appears after the targets.
        The selection and order of consonants is ramdomly chosen at every execution.
        '''
        # create random consonants
        selected_string = random.sample(constants.possible_consonants, 4)
        mask.text = ''.join(selected_string)
        mask.draw()
        SCREEN.flip()

    def displayFixCross(self):
        fix_cross.draw()
        SCREEN.flip()
