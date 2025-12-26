from __future__ import annotations
from typing import Tuple, Any, Dict
from enum import Enum
from pandas import Series

class EventType(Enum):
     TASK = 0
     T1 = 1
     T2 = 2


def event_dict(kind: EventType, trial: Series, evt: Tuple[int, int, int], sfreq: int) -> Dict[str, Any]:
    """Make a BIDS events row from the trial row and the MNE event
    """
    onset = round(evt[0] / sfreq, 3)
    if kind == EventType.TASK:
        return dict(
            onset = onset,
            sample = evt[0],
            value = evt[2],
            trial_type='prompt_t1' if evt[2] in (1, 11) else 'prompt_t2',
            trial_index=trial['Unnamed: 0'],
            phase=trial.phase,
            dual_task=trial.task=='dual',
        )
    else:
        if trial.task=='dual':
            id_string = {0.0: 'XOOX', 1.0: 'OXXO'}[trial.id_choice]
            correct = id_string == trial.target1
        else:
            correct = None
        return dict(
            onset = onset,
            sample = evt[0],
            value = evt[2],
            trial_type=kind.name.lower(),
            trial_index=trial['Unnamed: 0'],
            phase=trial.phase,
            dual_task=trial.task=='dual',
            t2presence=trial.t2presence,
            soa_long=trial.soa_long,
            stimulus=trial.target1 if kind==EventType.T1 else trial.target2,
            vis_rating=trial.vis_rating,
            vis_init=trial.vis_init,
            correct=correct,
        )
