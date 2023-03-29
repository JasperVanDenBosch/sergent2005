from __future__ import annotations
from typing import TYPE_CHECKING, Union, Literal, Tuple, Optional
from dataclasses import dataclass
from experiment.constants import Constants
from experiment.triggers import Triggers
if TYPE_CHECKING:
    from experiment.engine import PsychopyEngine
Phase = Union[Literal['train'], Literal['test']]
Task = Union[Literal['single'], Literal['dual']]
SoaCondition = Union[Literal['short'], Literal['long']]
CONSTANTS = Constants()


@dataclass(frozen=True)
class Trial(object):
    phase: Phase
    task: Task
    t2presence: bool
    soa: bool

    delay_index: int # t1 delay
    t1_index: int
    t2_index: int
    vis_init: int # random initial state of visibility rating

    masks: Tuple[str, str, str] # three masks of four characters each


    ## response data
    id_choice: Optional[int] = None
    id_rt: Optional[int] = None
    vis_rating: Optional[int] = None
    vis_rt: Optional[int] = None

    @property
    def t1TriggerNr(self):
        return Triggers.get_number(
            forT2=False,
            t2Present=self.t2presence,
            dualTask=self.task=='dual',
            longSOA=self.soa=='long'
        )
    
    @property
    def t2TriggerNr(self):
        return Triggers.get_number(
            forT2=True,
            t2Present=self.t2presence,
            dualTask=self.task=='dual',
            longSOA=self.soa=='long'
        )

    def run(self, engine: PsychopyEngine):
        """Present this trial

        Args:
            engine (PsychopyEngine): This is a wrapper for the experiment software
        """

        # it starts with the fixation cross
        engine.displayFixCross(self.iti)

        engine.displayT1(self.t1, self.t1TriggerNr, CONSTANTS.stimulus_duration)

        # display black screen between stimuli and masks
        engine.displayEmptyScreen(CONSTANTS.stimulus_duration)

        engine.displayMask(self.masks[0], CONSTANTS.stimulus_duration)

        # display the fixation cross either short_SOA - 129ms or long_SOA - 129ms,
        # since the target, the mask and the black screen was displayed for 43ms each
        fix_dur = self.soa_frames - CONSTANTS.stimulus_duration*3
        engine.displayFixCross(fix_dur)

        engine.displayT2(self.t2, self.t2TriggerNr, CONSTANTS.stimulus_duration)

        # display black screen between stimuli and masks
        engine.displayEmptyScreen(CONSTANTS.stimulus_duration)

        # display two masks after another with black screen inbetween
        engine.displayMask(self.masks[1], CONSTANTS.stimulus_duration)

        engine.displayEmptyScreen(CONSTANTS.stimulus_duration)

        engine.displayMask(self.masks[2], CONSTANTS.stimulus_duration)

        engine.displayEmptyScreen(CONSTANTS.visibility_scale_timing)

        # start the visibility rating (happens in single AND dual task conditions)
        # ratingT2 is tuple of rating, RT
        self.vis_rating, self.vis_rt = engine.promptVisibility(
            CONSTANTS.task2_text,
            ('nothing', 'maximal visibility'),
            CONSTANTS.scale_length,
            self.vis_init,
            Triggers.taskT2visibility
        )

        # only in the dual task condition the question on target 1 is displayed
        if self.task == 'dual':
            self.id_choice, self.id_rt = engine.promptIdentity(
                CONSTANTS.task1_text,
                ('OO', 'XX'),
                Triggers.taskT1variant
            )

