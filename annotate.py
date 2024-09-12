"""Artifect rejection implemented as MNE annotations

- [ ] ignore condition

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
data_dir = expanduser('~/data/EMLsergent2005/')

eeg_dir = join(data_dir, sub)
deriv_dir = join(data_dir, 'derivatives', 'mne', sub)
raw_fpath = join(eeg_dir, f'{sub}_eeg.bdf')
os.makedirs(deriv_dir, exist_ok=True)

timer = Timer()
timer.optimizeFlips(fr_conf, Constants())


## load raw data 
raw = read_raw_bdf(raw_fpath)

## get rid of empty channels and mark channel types
raw: RawEDF = raw.drop_channels(['EXG7', 'EXG8', 'GSR1', 'GSR2', 'Erg1', 'Erg2', 'Resp', 'Plet', 'Temp']) # type: ignore
eog_channels = ['EXG3', 'EXG4', 'EXG5', 'EXG6']
raw.set_channel_types(mapping=dict([(c, 'eog') for c in eog_channels]))

## pick channels to be filtered
filter_picks = mne.pick_types(raw.info, eeg=True, eog=True, stim=False)
raw.load_data()
raw = raw.filter(l_freq=0.5, h_freq=35, picks=filter_picks)

## bad channels
bad_chans = ['A32','C12', 'C14', 'B23', 'B29'] #'D5', 'D8', 'D16', 'D17']
raw.info['bads'].extend(bad_chans)

# ## reference to average of mastoids: best for biosemi, but methods plans to use average
# mastoid_channels = ['EXG1', 'EXG2'] 
# raw.set_eeg_reference(ref_channels=mastoid_channels)
# raw: RawEDF = raw.drop_channels(mastoid_channels) # type: ignore

## apply average reference
raw = raw.drop_channels(['EXG1', 'EXG2']) # type: ignore
raw = raw.set_eeg_reference(ref_channels='average')

## determine electrode head locations
montage = make_standard_montage('biosemi128', head_size='auto')
raw.set_montage(montage, on_missing='warn')

annots_fpath = join(deriv_dir, f'{sub}_annotations.txt')


## find triggers
events = mne.find_events(raw, mask=2**17 -256, mask_type='not_and', consecutive=True, min_duration=0.1)

## triggers for T2
t2_triggers = list(range(24, 31+1))

## index for full events array where event is T2
events_mask =[e[2] in t2_triggers for e in events ]

## only keep the T2 events. This way there are as many events as trials
## this helps with indexing later
events = events[events_mask]

## T2 epoching
soa = timer.flipsToSecs(timer.short_SOA)
buffer = timer.flipsToSecs(timer.target_dur)
tmin = - (soa + BASELINE + buffer)

event_ids = dict()
for presenceName, presence in [('absent', False), ('present', True)]:
    event_ids[f'{presenceName}'] = Triggers().get_number(
        training=False,
        forT2=True,
        dualTask=True,
        longSOA=False,
        t2Present=presence,
    )

epochs = mne.Epochs(
    raw,
    events,
    event_id=event_ids, ## selected triggers for epochs
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
    transients = numpy.diff(eeg[e, :, :]) ## absolute
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

print_warn('bla todo')


## comvert the above to annotations
"""This lines up with timing of events. 
But why are all bad events in the first half?
Is because of the conditions?

Should:
- [ ] do annotations on all events regardless of condition (separate script)


"""
event_onsets = events[bad_epochs, 0] / raw.info["sfreq"]
onsets = event_onsets - 0.100
durations = [0.5] * len(event_onsets)
descriptions = ["bad"] * len(event_onsets)
annots = mne.Annotations(
    onsets, durations, descriptions, orig_time=raw.info["meas_date"]
)
annots.save(join(deriv_dir, f'{sub}_annotations.txt'), overwrite=True)




