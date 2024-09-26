"""Artifect rejection implemented as MNE annotations

This lines up with timing of events. 
But why are all bad events in the first half?
Is because of the conditions?

Should:
- [ ] do annotations on all events regardless of condition (separate script)
- [ ] make sure bad channels not used during rejection
- [ ] does subtraction EOG make sense without baseline correction?
- [ ] annotation timing still seems off!

"""
from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import join, expanduser, isfile
import os
from colorama import init as colorama_init, Fore, Style
from mne.io import read_raw_bdf
from mne.channels import make_standard_montage
import mne, pandas, seaborn, numpy
import matplotlib.pyplot as plt
from experiment.triggers import Triggers
from experiment.timer import Timer
from experiment.constants import Constants
if TYPE_CHECKING:
    from mne.io.edf.edf import RawEDF
colorama_init()
def print_info(msg: str):
    print(f'{Fore.CYAN}{msg}{Style.RESET_ALL}')
def print_warn(msg: str):
    print(f'{Fore.MAGENTA}{msg}{Style.RESET_ALL}')


BASELINE = 0.250 ## duration of baseline
fr_conf  = 114 ## TODO double check
TMAX = 0.715
sub = 'sub-UOBC003'
data_dir = expanduser('~/data/eegmanylabs/Sergent2005/')

eeg_dir = join(data_dir, sub)
deriv_dir = join(data_dir, 'derivatives', 'mne', sub)
raw_fpath = join(eeg_dir, f'{sub}_eeg.bdf')
os.makedirs(deriv_dir, exist_ok=True)
annots_fpath = join(deriv_dir, f'{sub}_annotations.txt')

timer = Timer()
timer.optimizeFlips(fr_conf, Constants())

## load raw data 
raw = read_raw_bdf(raw_fpath)

## get rid of empty channels and mark channel types
raw: RawEDF = raw.drop_channels(['EXG7', 'EXG8', 'GSR1', 'GSR2', 'Erg1', 'Erg2', 'Resp', 'Plet', 'Temp']) # type: ignore
eog_channels = ['EXG3', 'EXG4', 'EXG5', 'EXG6']
raw.set_channel_types(mapping=dict([(c, 'eog') for c in eog_channels]))

## bad channels
bad_chans = ['A32','C12', 'C14', 'B23', 'B29'] #'D5', 'D8', 'D16', 'D17']
raw.info['bads'].extend(bad_chans)

## remove the mastoids
raw = raw.drop_channels(['EXG1', 'EXG2']) # type: ignore


#raise ValueError
## find triggers
events = mne.find_events(raw, mask=2**17 -256, mask_type='not_and', consecutive=True, min_duration=0.1)

## triggers for T2 (experiment + training)
t2_triggers = list(range(24, 31+1)) + list(range(40, 47+1))

## index for full events array where event is T2
events_mask =[e[2] in t2_triggers for e in events ]

## only keep the T2 events. This way there are as many events as trials
## this helps with indexing later
events_selected = events[events_mask]

## T2 epoching
soa = timer.flipsToSecs(timer.short_SOA)
buffer = timer.flipsToSecs(timer.target_dur)
tmin = - (soa + BASELINE + buffer)


epochs = mne.Epochs(
    raw,
    events,
    event_id=t2_triggers, ## selected triggers for epochs
    tmin=tmin,
    tmax=TMAX,
    baseline=(tmin, tmin+BASELINE),
    on_missing='warn',
)


## trial rejection
"""
We rejected voltage exceeding ±200 uV,
transients exceeding ±100 uV, 
or electrooculogram activity exceeding ±70 mV.

EX3: bottom HEOG
EX4: top HEOG
EX5: left VEOG
EX6: right VEOG
"""
## maybe do epoching twice
# 1. to get bads
# 2. to get data
THRESH_TRANS = 100
THRESH_PEAK = 200
THRESH_EOG = 70

eeg = epochs.get_data('eeg', units='uV') # trials x channels x time
eog_dual = epochs.get_data('eog', units='uV') # trials x channels x time
direction_mask = numpy.array([True, False, True, False])
eog = eog_dual[:, direction_mask, :] - eog_dual[:, ~direction_mask, :]
n_epochs = eeg.shape[0]
n_eog_rejects = 0
bad_epochs = []
counts = dict(trans=0, peak=0, eog=0)
for e in range(n_epochs):
    transients = numpy.abs(numpy.diff(eeg[e, :, :])) ## absolute
    if numpy.any(transients > THRESH_TRANS):
        bad_epochs.append(e)
        counts['trans'] += 1
        continue

    eeg_epoch = eeg[e, :, :].T
    eeg_peaks = eeg_epoch - eeg_epoch.mean(axis=0)
    if numpy.any(numpy.abs(eeg_peaks) > THRESH_PEAK):
        bad_epochs.append(e)
        counts['peak'] += 1
        continue

    eog_epoch = eog[e, :, :].T
    eog_peaks = eog_epoch - eog_epoch.mean(axis=0)
    if numpy.any(numpy.abs(eog_peaks) > THRESH_EOG):
        bad_epochs.append(e)
        counts['eog'] += 1
        continue

## comvert the above to annotations
event_onsets = events_selected[bad_epochs, 0] / raw.info["sfreq"]
onsets = event_onsets - 0.100
durations = [0.5] * len(event_onsets)
descriptions = ["bad"] * len(event_onsets)
annots = mne.Annotations(
    onsets, durations, descriptions, orig_time=raw.info["meas_date"]
)
annots.save(annots_fpath, overwrite=True)
print_warn(f'Stored annotations at {annots_fpath}')

"""
    
In [5]: annots[-1]
Out[5]:
OrderedDict([('onset', 1404.87265625),
             ('duration', 0.5),
             ('description', 'bad'),
             ('orig_time',
              datetime.datetime(2024, 6, 12, 14, 46, 59, tzinfo=datetime.timezone.utc))])

In [6]: raw.info
Out[6]:
<Info | 9 non-empty values
 bads: 5 items (A32, C12, C14, B23, B29)
 ch_names: A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, ...
 chs: 128 EEG, 4 EOG, 1 Stimulus
 custom_ref_applied: False
 highpass: 0.0 Hz
 lowpass: 52.0 Hz
 meas_date: 2024-06-12 14:46:59 UTC
 nchan: 133
 projs: []
 sfreq: 256.0 Hz
 subject_info: 1 item (dict)
>

In [38]: epochs[-1].events
Out[38]: array([[1089098,      18,      26]])

In [41]: bad_epochs[-5:]
Out[41]: [401, 402, 405, 406, 411] ## some of the later epochs rejected

In [7]: raw.get_data().shape
Out[7]: (133, 1096448)

In [8]: 1096448/256
Out[8]: 4283.0

 lowpass: 52.0 Hz


 - annotations stop at 1404s, but recording is ~4000s. last event is at 4259.08203125
 - is there no T2's after 1400?
 - lowpass filter 52Hz? from activescan??

"""




