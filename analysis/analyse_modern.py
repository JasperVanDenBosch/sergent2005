"""Use contemporary tools to pre-process 

bad_chans = ['A32','C12', 'C14', 'B23', 'B29', 'D24'] #'D5', 'D8', 'D16', 'D17']

- ICA
- autoreject

"""
from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import join, expanduser
import os
from colorama import init as colorama_init, Fore, Style
from mne.io import read_raw_bdf
from mne.channels import make_standard_montage
from mne.preprocessing import ICA
import mne
from autoreject import AutoReject
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


MODE = 'modern'
BASELINE = 0.250 ## duration of baseline
fr_conf  = 114 ## TODO double check
TMAX = 0.715
LATENCY = 0.016
N_INTERPOLATE = list(range(16))
N_JOBS = 4
sub = 'sub-UOBC003'
data_dir = expanduser('~/data/eegmanylabs/Sergent2005/')

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

## apply average reference
raw = raw.drop_channels(['EXG1', 'EXG2']) # type: ignore
raw = raw.set_eeg_reference(ref_channels='average')

## determine electrode head locations
montage = make_standard_montage('biosemi128', head_size='auto')
raw.set_montage(montage, on_missing='warn')

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
tmin = - (soa + BASELINE + buffer) + LATENCY
epochs = mne.Epochs(
    raw,
    events,
    tmin=tmin,
    tmax=TMAX+LATENCY,
    baseline=None,
    on_missing='warn',
    preload=True
)
#epochs.save(join(deriv_dir, f'{sub}_{epo_name}_epo.fif'), overwrite=True)

## step 1 find bad epochs to exclude from ICA
ar = AutoReject(n_interpolate=N_INTERPOLATE, n_jobs=N_JOBS, verbose=True)
ar.fit(epochs[:20])  # fit on the first 20 epochs to save time
_, reject_log = ar.transform(epochs, return_log=True)

## plot initial fit
#epochs[reject_log.bad_epochs].plot(scalings=dict(eeg=100e-6))
#reject_log.plot('horizontal')


## step 2 ICA without bad epochs
ica = ICA(20) # n_components can leave away for 0.99 variance
ica.fit(epochs[~reject_log.bad_epochs])
print(f'comps {ica.n_components_}')


# We can see in the plots below that ICA effectively removed eyeblink
# artifact.
#
# plot source components to see which is made up of blinks
# exclude = [0,  # blinks
#            2  # saccades
#            ]
ica.plot_components() # ica.plot_components(exclude)
raise ValueError
ica.exclude = exclude


# plot with and without eyeblink component
ica.plot_overlay(epochs.average(), exclude=ica.exclude)
ica.apply(epochs, exclude=ica.exclude)


## step 3 apply autoreject
ar = AutoReject(n_interpolate=N_INTERPOLATE, n_jobs=N_JOBS, verbose=True)
ar.fit(epochs[:20])  # fit on the first 20 epochs to save time
epochs_ar, reject_log = ar.transform(epochs, return_log=True)
epochs[reject_log.bad_epochs].plot(scalings=dict(eeg=100e-6))


# We will do a few more visualizations to see that removing the bad epochs
# found by ``autoreject`` is still important even with preprocessing first.
# This is especially important if your analyses include trial-level statistics
# such as looking for bursting activity. We'll visualize why autoreject
# excluded these epochs and the effect that including these bad epochs would
# have on the data.
#
# First, we will visualize the reject log
reject_log.plot('horizontal')


# Next, we will visualize the cleaned average data and compare it against
# the bad segments.
evoked_bad = epochs[reject_log.bad_epochs].average()
plt.figure()
plt.plot(evoked_bad.times, evoked_bad.data.T * 1e6, 'r', zorder=-1)
epochs_ar.average().plot(axes=plt.gca())

raise ValueError

# As a last optional step, we can do inspect the reject_log and make manual
# corrections to the reject_log. For instance, if data is limited, we may
# not want to drop epochs but retain the list of bad epochs for quality
# assurance metrics.

reject_log = ar.get_reject_log(epochs)
bad_epochs = reject_log.bad_epochs.copy()
reject_log.bad_epochs[:] = False  # no bad epochs


# The modified reject log can be applied to the data as follows.
epochs_ar = ar.transform(epochs, reject_log=reject_log)
print(f'Number of epochs originally: {len(epochs)}, '
      f'after autoreject: {len(epochs_ar)}')
