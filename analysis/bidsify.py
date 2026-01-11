"""
Restructure collected data into BIDS format.
Looks for data in "sourcedata" folder
"""
from __future__ import annotations
from os.path import expanduser, join
from os import makedirs
from glob import glob
from copy import copy
from mne.io import read_raw_bdf
from mne import find_events
from string import Template
from pandas import read_csv, DataFrame
from event import event_dict, EventType
from experiment.constants import Constants
from experiment.timer import Timer
from experiment.triggers import Triggers

TASK_DESC = {
    'ab': 'Attentional Blink paradigm',
}
TASK = 'ab'
FRAMERATE = 60 ## from lab config file uolm.toml

## Determine the duration of targets (for events sidecar)
const = Constants()
timer = Timer()
timer.optimizeFlips(FRAMERATE, const)
target_dur_s = timer.flipsToSecs(const.target_dur)

CHANNELS = [
    dict(name='EXG1', type='REF', units='uV', description='left mastoid'),
    dict(name='EXG2', type='REF', units='uV', description='right mastoid'),
    dict(name='EXG3', type='HEOG', units='uV', description='right HEOG'),
    dict(name='EXG4', type='HEOG', units='uV', description='left HEOG'),
    dict(name='EXG5', type='VEOG', units='uV', description='bottom VEOG'),
    dict(name='EXG6', type='VEOG', units='uV', description='top VEOG'),
    dict(name='EXG7', type='MISC', units='n/a', description='not used'),
    dict(name='EXG8', type='MISC', units='n/a', description='not used'),
    dict(name='Status', type='MISC', units='n/a', description='trigger channel'),
]

templates = dict()
for filename in ('eeg.json', 'events.json'):
    with open(join('analysis/templates', filename)) as fhandle:
        templates[filename] = Template(fhandle.read())


data_dir = expanduser('~/data/eegmanylabs/sergent2005')
source_dirs = sorted(glob(join(data_dir, 'sourcedata', 'sub-UOLM*')))
s = 0
for source_dir in source_dirs:

    s += 1
    sub = f'sub-{s:02}'
    sub_dir = join(data_dir, sub)
    eeg_dir = join(sub_dir, 'eeg')
    makedirs(eeg_dir, exist_ok=True)


    bdf_fpath = glob(join(source_dir, '*.bdf'))[0]
    raw = read_raw_bdf(bdf_fpath)
    sfreq = round(raw.info['sfreq'])


    ## Generate channels file
    channels = []
    for name in raw.info['ch_names']:
        for channel in CHANNELS:
            if channel['name'] == name:
                channels.append(copy(channel))
                break
        else:
            channels.append(dict(name=name, type='EEG', units='uV', description='n/a'))
    fpath_chan = join(eeg_dir, f'{sub}_task-{TASK}_channels.tsv')
    DataFrame(channels).to_csv(fpath_chan, sep='\t', index=False)


    ## process event file
    csv_files = glob(join(source_dir, f'*_trials.csv'))
    assert len(csv_files) == 1
    trials_df = read_csv(csv_files[0])

    mask = sum([2**i for i in (8,9,10,11,12,13,14,15,16)])
    evt = find_events(raw, mask=mask, mask_type='not_and')


    """

    At least in UOLM001, the trigger for the task (1,2,11,12) 
    seems to often be missing.

    """
    # missing 8
    if s == 3:
        trials_offset = 8
    elif s == 5:
        trials_offset = 16
    else:
        trials_offset = 0

    e = 0
    events = []
    for _, trial in trials_df.iloc[trials_offset:].iterrows():

        te = 0
        assert trial.t1_trigger == evt[e+te, 2]
        events.append(event_dict(EventType.T1, trial, tuple(evt[e+te, :]), sfreq, target_dur_s))


        te += 1
        assert trial.t2_trigger == evt[e+te, 2]
        events.append(event_dict(EventType.T2, trial, tuple(evt[e+te, :]), sfreq, target_dur_s))

        te += 1
        for _ in range(2):
            if e+te < evt.shape[0]:
                if evt[e+te, 2] in (1, 2, 11, 12):
                    events.append(event_dict(EventType.TASK, trial, tuple(evt[e+te, :]), sfreq, None))
                    te += 1
        if te <= 2:
            # No prompt trigger in trial {t}
            pass
        
        e += te
    df_events = DataFrame(events)
    df_events.to_csv(join(eeg_dir, f'{sub}_task-{TASK}_events.tsv'), sep='\t', index=False, float_format = '%.12g')


    ## create events sidecar file
    triggers = set(df_events.value)
    trigger_lookup = {str(v): k for k, v in Triggers().asdict().items()}
    fpath_evt_json = join(eeg_dir, f'{sub}_task-{TASK}_events.json')
    with open(fpath_evt_json, 'w') as fhandle:
        fhandle.write(
            templates['events.json'].substitute(
                dict(trigger_lookup=trigger_lookup)
            ).replace('\'', '"')
        )

    ## create eeg sidecar file
    fpath_eeg_json = join(eeg_dir, f'{sub}_task-ab_eeg.json')
    with open(fpath_eeg_json, 'w') as fhandle:
        fhandle.write(
            templates['eeg.json'].substitute(
                dict(
                    task=TASK,
                    description=TASK_DESC[TASK],
                    sfreq=sfreq
                )
            )
        )
