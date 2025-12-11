"""
Restructure collected data into BIDS format.
Looks for data in "sourcedata" folder


- split up tasks?
- mark bad segments
- bad channels
"""
from os.path import expanduser, join
from os import makedirs
from glob import glob
from copy import copy
from mne.io import read_raw_bdf
from mne import find_events
from numpy import diff
from string import Template
from pandas import read_csv, DataFrame

BUFFER_SEC = 5
TASK_DESC = {
    'blink': 'Attentional Blink paradigm',
}
COLS = {
    'target': 'trial_type',
    'TriggerNum': 'value',
    'TrialKeyResp.rt': 'rt',
    'imgfileP2': 'identity',
    'Trial.started': 'onset'
}
TASK = 'blink'

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
    beh_dir = join(sub_dir, 'beh')
    makedirs(beh_dir, exist_ok=True)


    bdf_fpath = glob(join(source_dir, '*.bdf'))[0]
    raw = read_raw_bdf(bdf_fpath)
    sfreq = raw.info['sfreq']


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


    evt = find_events(raw, shortest_event=0)

    mask = sum([2**i for i in (8,9,10,11,12,13,14,15,16)])
    evt = find_events(raw, mask=mask, mask_type='not_and')


    raise ValueError
    last_evt_index = diff(evt[:,0]).argmax()
    evt_slices = dict(passive=slice(0, last_evt_index+1), animacy=slice(last_evt_index+1, None))
    key_times = dict(
        passive=(
            evt[evt_slices['passive'], 0][0]/sfreq - BUFFER_SEC,
            evt[evt_slices['passive'], 0][-1]/sfreq + BUFFER_SEC
        ),
        animacy=(
            evt[evt_slices['animacy'], 0][0]/sfreq - BUFFER_SEC,
            evt[evt_slices['animacy'], 0][-1]/sfreq + BUFFER_SEC
        )
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

    ## evts for this task
    evt_task = find_events(raw)

    ## process event file
    csv_files = glob(join(source_dir, f'*_trials.csv'))
    assert len(csv_files) == 1
    df = read_csv(csv_files[0])
    df = df[df.target.notna()] ## dropta empty rows
    df = df[COLS.keys()] ## keep only relevant columns

    df['sample'] = evt_task_filt[:, 0] - raw.first_samp ## add "sample" column
    df = df.rename(columns=COLS) ## rename columns
    df['identity'] = df['identity'].astype(int)
    df['value'] = df['value'].astype(int)
    df['onset'] = df['sample'] / sfreq
    df['stimulus'] = df.trial_type + df.identity.astype(str) ## add column for full stimulus id
    df.to_csv(join(eeg_dir, f'{sub}_task-{task}_events.tsv'), sep='\t', index=False)

    ## create events sidecar file
    triggers = set(df.value)
    trigger_lookup = dict()
    for trigger in triggers:
        name= df[(df.value == trigger)].iloc[0].stimulus
        trigger_lookup[str(trigger)] = name
    fpath_evt_json = join(eeg_dir, f'{sub}_task-{TASK}_events.json')
    with open(fpath_evt_json, 'w') as fhandle:
        fhandle.write(
            templates['events.json'].substitute(
                dict(trigger_lookup=trigger_lookup)
            ).replace('\'', '"')
        )




