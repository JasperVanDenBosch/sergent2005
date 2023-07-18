from __future__ import annotations
from typing import TYPE_CHECKING, Union, Literal, Tuple, Optional, Dict, Any
from dataclasses import dataclass, asdict
from experiment.constants import Constants
if TYPE_CHECKING:
    from experiment.engine import PsychopyEngine
    from experiment.timer import Timer
Phase = Union[Literal['train'], Literal['test']]
Task = Union[Literal['single'], Literal['dual']]
CONSTANTS = Constants()


@dataclass()
class Trial(object):
    phase: Phase
    task: Task
    t2presence: bool
    soa_long: bool
    soa: int
    delay_index: int # t1 delay
    delay: int
    iti: int
    t1_index: int
    t2_index: int
    vis_init: int # random initial state of visibility rating
    t1_trigger: int
    t2_trigger: int
    masks: Tuple[str, str, str] # three masks of four characters each
    id_trigger: int
    vis_trigger: int

    ## response data
    id_choice: Optional[int] = None
    id_onset: Optional[float] = None
    id_rt: Optional[int] = None
    vis_rating: Optional[int] = None
    vis_onset: Optional[float] = None
    vis_rt: Optional[int] = None
    t1_onset: Optional[float] = None
    t1_offset: Optional[float] = None
    t2_onset: Optional[float] = None
    t2_offset: Optional[float] = None

    @property 
    def target1(self):
        return CONSTANTS.target1_strings[self.t1_index]

    @property   
    def target2(self):
        return CONSTANTS.target2_strings[self.t2_index]
    
    def todict(self) -> Dict[str, Any]:
        full_dict = asdict(self)
        full_dict['delay'] = self.delay
        full_dict['soa'] = self.soa
        full_dict['target1'] = self.target1
        full_dict['target2'] = self.target2
        return full_dict

    def run(self, engine: PsychopyEngine, timer: Timer):
        """Present this trial

        Args:
            engine (PsychopyEngine): This is a wrapper for the experiment software
        """
        engine.displayEmptyScreen(self.iti)

        # it starts with the fixation cross
        engine.displayFixCross(self.delay)

        self.t1_onset = engine.displayT1(self.target1, self.t1_trigger, timer.target_dur)

        # display black screen between stimuli and masks
        self.t1_offset = engine.displayEmptyScreen(timer.target_dur)

        engine.displayMask(self.masks[0], timer.target_dur)

        # display the fixation cross either short_SOA - 129ms or long_SOA - 129ms,
        # since the target, the mask and the black screen was displayed for 43ms each
        fix_dur = self.soa - timer.target_dur*3
        engine.displayFixCross(fix_dur)

        self.t2_onset = engine.displayT2(self.target2, self.t2_trigger, timer.target_dur)

        # display black screen between stimuli and masks
        self.t2_offset = engine.displayEmptyScreen(timer.target_dur)

        # display two masks after another with black screen inbetween
        engine.displayMask(self.masks[1], timer.target_dur)

        engine.displayEmptyScreen(timer.target_dur)

        engine.displayMask(self.masks[2], timer.target_dur)

        engine.displayEmptyScreen(timer.task_delay)

        # start the visibility rating (happens in single AND dual task conditions)
        # ratingT2 is tuple of rating, RT
        self.vis_rating, self.vis_onset, self.vis_rt = engine.promptVisibility(
            CONSTANTS.task_vis_text,
            CONSTANTS.task_vis_labels,
            CONSTANTS.vis_scale_length,
            self.vis_init,
            self.vis_trigger
        )

        # only in the dual task condition the question on target 1 is displayed
        if self.task == 'dual':
            self.id_choice, self.id_onset, self.id_rt = engine.promptIdentity(
                CONSTANTS.task_identity_text,
                CONSTANTS.task_identity_options,
                self.id_trigger
            )

            if True:
                engine.showMessage('FALSE', confirm=False)

        engine.flush()

