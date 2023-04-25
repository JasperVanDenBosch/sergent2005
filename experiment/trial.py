from __future__ import annotations
from typing import TYPE_CHECKING, Union, Literal, Tuple, Optional
from dataclasses import dataclass
from experiment.constants import Constants
if TYPE_CHECKING:
    from experiment.engine import PsychopyEngine
Phase = Union[Literal['train'], Literal['test']]
Task = Union[Literal['single'], Literal['dual']]
SoaCondition = Union[Literal['short'], Literal['long']]
CONSTANTS = Constants()


@dataclass()
class Trial(object):
    phase: Phase
    task: Task
    t2presence: bool
    soa_long: bool
    delay_index: int # t1 delay
    t1_index: int
    t2_index: int
    vis_init: int # random initial state of visibility rating
    t1_trigger: int
    t2_trigger: int
    masks: Tuple[str, str, str] # three masks of four characters each
    task_variant_trigger: int
    task_visibility_trigger: int

    ## response data
    id_choice: Optional[int] = None
    id_rt: Optional[int] = None
    vis_rating: Optional[int] = None
    vis_rt: Optional[int] = None

    @property
    def delay(self):
        vals = [CONSTANTS.start_T1_quick, CONSTANTS.start_T1_slow]
        return vals[self.delay_index]

    @property
    def soa(self):
        return CONSTANTS.long_SOA if self.soa_long else CONSTANTS.short_SOA

    @property 
    def target1(self):
        return CONSTANTS.target1_strings[self.t1_index]

    @property   
    def target2(self):
        return CONSTANTS.target2_strings[self.t2_index]

    def run(self, engine: PsychopyEngine):
        """Present this trial

        Args:
            engine (PsychopyEngine): This is a wrapper for the experiment software
        """

        # it starts with the fixation cross
        engine.displayFixCross(self.delay)

        engine.displayT1(self.target1, self.t1_trigger, CONSTANTS.stimulus_duration)

        # display black screen between stimuli and masks
        engine.displayEmptyScreen(CONSTANTS.stimulus_duration)

        engine.displayMask(self.masks[0], CONSTANTS.stimulus_duration)

        # display the fixation cross either short_SOA - 129ms or long_SOA - 129ms,
        # since the target, the mask and the black screen was displayed for 43ms each
        fix_dur = self.soa - CONSTANTS.stimulus_duration*3
        engine.displayFixCross(fix_dur)

        engine.displayT2(self.target2, self.t2_trigger, CONSTANTS.stimulus_duration)

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
            CONSTANTS.task_vis_text,
            CONSTANTS.task_vis_labels,
            CONSTANTS.vis_scale_length,
            self.vis_init,
            self.task_visibility_trigger
        )

        # only in the dual task condition the question on target 1 is displayed
        if self.task == 'dual':
            self.id_choice, self.id_rt = engine.promptIdentity(
                CONSTANTS.task_identity_text,
                CONSTANTS.task_identity_options,
                self.task_variant_trigger
            )

        engine.flush()

