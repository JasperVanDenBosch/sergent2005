"""Use contemporary tools to pre-process 

bad_chans = ['A32','C12', 'C14', 'B23', 'B29', 'D24'] #'D5', 'D8', 'D16', 'D17']

"""
from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import join, expanduser
import os
from colorama import init as colorama_init, Fore, Style
from mne.io import read_raw_bdf
from mne.channels import make_standard_montage
import matplotlib.pyplot as plt
from experiment.triggers import Triggers
from experiment.timer import Timer
from experiment.constants import Constants
from mne.preprocessing import ICA
import mne
from autoreject import AutoReject
from mne_icalabel import label_components
if TYPE_CHECKING:
    from mne.io.edf.edf import RawEDF
colorama_init()
def print_info(msg: str):
    print(f'{Fore.CYAN}{msg}{Style.RESET_ALL}')
def print_warn(msg: str):
    print(f'{Fore.MAGENTA}{msg}{Style.RESET_ALL}')


MODE = 'modern'
BASELINE = 0.250 ## duration of baseline
fr_conf  = 60 ## TODO double check
TMAX = 0.715
LATENCY = 0.016
N_INTERPOLATE = [4, 6, 8, 10, 12]
N_JOBS = 6
sub = 'sub-UOLM001'
data_dir = expanduser('~/data/eegmanylabs/Sergent2005/')

eeg_dir = join(data_dir, sub)
deriv_dir = join(data_dir, 'derivatives', 'modern', sub)
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
raw = raw.filter(l_freq=0.5, h_freq=20, picks=filter_picks)

## apply average reference
raw = raw.drop_channels(['EXG1', 'EXG2']) # type: ignore
raw = raw.set_eeg_reference(ref_channels='average')

## determine electrode head locations
montage = make_standard_montage('biosemi128', head_size='auto')
raw.set_montage(montage, on_missing='warn')

## find triggers
mask = sum([2**i for i in (8,9,10,11,12,13,14,15,16)])
events = mne.find_events(
    raw,
    verbose=False,
    mask=mask,
    mask_type='not_and'
)

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
    ## ICA advises not to do baseline beforehand
    baseline=None, #baseline=(tmin, tmin+BASELINE),
    on_missing='warn',
    preload=True
)
#epochs.save(join(deriv_dir, f'{sub}_{epo_name}_epo.fif'), overwrite=True)

## step 1 find bad epochs to exclude from ICA
ar = AutoReject(n_interpolate=N_INTERPOLATE, n_jobs=N_JOBS, verbose=True)
ar.fit(epochs)
_, reject_log = ar.transform(epochs, return_log=True)
reject_log.save(join(deriv_dir, 'reject_log_pre-ica.npz'), overwrite=True)

fig = reject_log.plot('horizontal', show=False)
fig.savefig('plots/reject_log_pre-ica.png')
plt.close()
## plot initial fit
#epochs[reject_log.bad_epochs].plot(scalings=dict(eeg=100e-6))


## step 2 ICA without bad epochs
ica = ICA(20) # n_components can leave away for 0.99 variance
ica.fit(epochs[~reject_log.bad_epochs])


#ica.plot_components() # ica.plot_components(exclude)


ic_labels = label_components(raw, ica, method='iclabel')

blink_ic_idx = [i for i, label in enumerate(ic_labels['labels']) if label == 'eye blink']
ica.exclude = blink_ic_idx
figs = ica.plot_properties(raw, picks=blink_ic_idx, show=False)
for f, fig in enumerate(figs):
    fig.savefig(f'plots/ic_props_{f}.png')
    plt.close()

# plot with and without eyeblink component
fig = ica.plot_overlay(epochs.average(), exclude=blink_ic_idx, show=False) ## todo save this plot
fig.savefig('plots/ica_overlay.png')
plt.close()

ica.apply(epochs, exclude=ica.exclude)


## step 3 apply autoreject
ar = AutoReject(n_interpolate=N_INTERPOLATE, n_jobs=N_JOBS, verbose=True)
ar.fit(epochs)
epochs_ar, reject_log = ar.transform(epochs, return_log=True)

epochs_clean = epochs_ar.apply_baseline(baseline=(tmin, tmin+BASELINE))

epochs_clean.save(join(deriv_dir, f'{sub}_clean_epo.fif'), overwrite=True)
reject_log.save(join(deriv_dir, 'reject_log_post-ica.npz'), overwrite=True)

fig = reject_log.plot('horizontal', show=False)
fig.savefig('plots/reject_log_post-ica.png')
plt.close()
