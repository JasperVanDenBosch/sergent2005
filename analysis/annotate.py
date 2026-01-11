"""Artifect rejection implemented as MNE annotations

"""
from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import join, expanduser
import os
from colorama import init as colorama_init, Fore, Style
from mne.io import read_raw_bdf
import mne, numpy
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
fr_conf  = 60 ## TODO double check
TMAX = 0.715
LATENCY = 0.016 ## based on latrec recording
sub = 'sub-UOLM001'
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
raw: RawEDF = raw.drop_channels(['EXG7', 'EXG8']) # type: ignore
eog_channels = ['EXG3', 'EXG4', 'EXG5', 'EXG6']
raw.set_channel_types(mapping=dict([(c, 'eog') for c in eog_channels]))

## bad channels
bad_chans = [] #'D5', 'D8', 'D16', 'D17']
raw.info['bads'].extend(bad_chans)

## remove the mastoids
raw = raw.drop_channels(['EXG1', 'EXG2']) # type: ignore


#raise ValueError
## find triggers
mask = sum([2**i for i in (8,9,10,11,12,13,14,15,16)])
events = mne.find_events(
    raw,
    verbose=False,
    mask=mask,
    mask_type='not_and'
)

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
tmin = - (soa + BASELINE + buffer) + LATENCY


epochs = mne.Epochs(
    raw,
    events,
    event_id=t2_triggers, ## selected triggers for epochs
    tmin=tmin,
    tmax=TMAX+LATENCY,
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
descriptions = []
for e in range(n_epochs):
    transients = numpy.abs(numpy.diff(eeg[e, :, :])) ## absolute
    if numpy.any(transients > THRESH_TRANS):
        bad_epochs.append(e)
        descriptions.append('bad transient')
        counts['trans'] += 1
        continue

    eeg_epoch = eeg[e, :, :].T
    eeg_peaks = eeg_epoch - eeg_epoch.mean(axis=0)
    if numpy.any(numpy.abs(eeg_peaks) > THRESH_PEAK):
        bad_epochs.append(e)
        descriptions.append('bad peak')
        counts['peak'] += 1
        continue

    eog_epoch = eog[e, :, :].T
    eog_peaks = eog_epoch - eog_epoch.mean(axis=0)
    if numpy.any(numpy.abs(eog_peaks) > THRESH_EOG):
        bad_epochs.append(e)
        descriptions.append('bad blink')
        counts['eog'] += 1
        continue

## comvert the above to annotations
event_onsets = events_selected[bad_epochs, 0] / raw.info["sfreq"]
onsets = event_onsets + tmin # tmin is negative
durations = [-tmin+TMAX] * len(event_onsets)
annots = mne.Annotations(
    onsets, durations, descriptions, orig_time=raw.info["meas_date"]
)
annots.save(annots_fpath, overwrite=True)
print_warn(f'Stored annotations at {annots_fpath}')
