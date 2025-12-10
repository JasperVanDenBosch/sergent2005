"""Preprocessing without any artifact rejection

"""
from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import join, expanduser, isfile
import os
from colorama import init as colorama_init, Fore, Style
from mne.io import read_raw_bdf
from mne.channels import make_standard_montage
import mne, numpy
import matplotlib.pyplot as plt
from experiment.triggers import Triggers
from experiment.timer import Timer
from experiment.constants import Constants
from analyse_behavior import trials_df
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
LATENCY = 0.016
sub = 'sub-UOLM001'
data_dir = expanduser('~/data/eegmanylabs/Sergent2005/')

eeg_dir = join(data_dir, sub)
deriv_dir = join(data_dir, 'derivatives', 'dirty', sub)
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

## bad channels
bad_chans = ['A32','C12', 'C14', 'B23', 'B29', 'D24'] #'D5', 'D8', 'D16', 'D17']
raw.info['bads'].extend(bad_chans)

## apply average reference
raw = raw.drop_channels(['EXG1', 'EXG2']) # type: ignore
raw = raw.set_eeg_reference(ref_channels='average')

## determine electrode head locations
montage = make_standard_montage('biosemi64', head_size='auto')
fig = montage.plot(show=False)
fig.savefig('plots/montage.png')
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
    tmax=TMAX+LATENCY,
    baseline=(tmin, tmin+BASELINE),
    on_missing='warn',
)

epochs.save(join(deriv_dir, f'{sub}_dirty_epo.fif'), overwrite=True)
