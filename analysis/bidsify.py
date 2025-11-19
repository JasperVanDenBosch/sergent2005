"""
Restructure collected data into BIDS format.
Looks for data in "sourcedata" folder
"""
from os.path import expanduser, join
from os import makedirs
from glob import glob
from copy import copy
from mne.io import read_raw_bdf
from mne.export import export_raw
from mne import find_events
from numpy import diff, isin
from string import Template
from pandas import read_csv, DataFrame

BUFFER_SEC = 5
TASK_DESC = {
    'passive': "Participant views images and responds when they see a chair.",
    'animacy': "Participant views images and responds whether the image depicts a living being or an artifact."
}
COLS = {
    'target': 'trial_type',
    'TriggerNum': 'value',
    'TrialKeyResp.rt': 'rt',
    'imgfileP2': 'identity',
    'Trial.started': 'onset'
}

## session 20250228 weird triggers:
ROWS_NO_TRIGGER_IDX = dict(
    passive=[62, 295, 413, 414], # passive TODO: 414=470?
    animacy=[]
)
TRIGGERS_NO_ROWS = dict(
    passive=[400, 210093, 1008609], 
    animacy=[1822741]
)
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
    with open(join('templates', filename)) as fhandle:
        templates[filename] = Template(fhandle.read())


data_dir = expanduser('~/data/phb')
s = 0
for session_dir in sorted(glob(join(data_dir, 'sourcedata', '2025*'))):

    s += 1
    sub = f'sub-{s:02}'
    sub_dir = join(data_dir, sub)
    eeg_dir = join(sub_dir, 'eeg')
    makedirs(eeg_dir, exist_ok=True)
    beh_dir = join(sub_dir, 'beh')
    makedirs(beh_dir, exist_ok=True)


    bdf_files = glob(join(session_dir, '*.bdf'))
    raw = read_raw_bdf(bdf_files[0])
    sfreq = raw.info['sfreq']

    channels = []
    for name in raw.info['ch_names']:
        for channel in CHANNELS:
            if channel['name'] == name:
                channels.append(copy(channel))
                break
        else:
            channels.append(dict(name=name, type='EEG', units='uV', description='n/a'))

    evt = find_events(raw, consecutive=True, shortest_event=0)
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
    fpath_eeg_json = join(eeg_dir, f'{sub}_task-{task}_eeg.json')
    with open(fpath_eeg_json, 'w') as fhandle:
        fhandle.write(
            templates['eeg.json'].substitute(
                dict(
                    task=task,
                    description=TASK_DESC[task],
                    sfreq=sfreq
                )
            )
        )

    ## evts for this task
    evt_task = find_events(raw_task, consecutive=True, shortest_event=0)
    if '20250228' in session_dir:
        ## remove this trigger as it's not in the behavior
        mask = ~isin(evt_task[:,0], TRIGGERS_NO_ROWS[task])
        evt_task = evt_task[mask]
    evt_task_filt = evt_task[evt_task[:,2] < 200,:] ## drop 254 and 255

    ## process event file
    csv_files = glob(join(session_dir, f'_{task_pseudonym}*.csv'))
    assert len(csv_files) == 1
    df = read_csv(csv_files[0])
    df = df[df.target.notna()] ## dropta empty rows
    df = df[COLS.keys()] ## keep only relevant columns
    if '20250228' in session_dir:
        df = df.iloc[~isin(df.index, ROWS_NO_TRIGGER_IDX[task])]
    df['sample'] = evt_task_filt[:, 0] - raw_task.first_samp ## add "sample" column
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
    fpath_evt_json = join(eeg_dir, f'{sub}_task-{task}_events.json')
    with open(fpath_evt_json, 'w') as fhandle:
        fhandle.write(
            templates['events.json'].substitute(
                dict(trigger_lookup=trigger_lookup)
            ).replace('\'', '"')
        )

    ## create channels file
    fpath_chan = join(eeg_dir, f'{sub}_task-{task}_channels.tsv')
    DataFrame(channels).to_csv(fpath_chan, sep='\t', index=False)


