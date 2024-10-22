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
import mne
if TYPE_CHECKING:
    from mne.io.edf.edf import RawEDF
colorama_init()
def print_info(msg: str):
    print(f'{Fore.CYAN}{msg}{Style.RESET_ALL}')
def print_warn(msg: str):
    print(f'{Fore.MAGENTA}{msg}{Style.RESET_ALL}')

MODE = 'modern'
sub = 'sub-UOBC003'
data_dir = expanduser('~/data/eegmanylabs/Sergent2005/')

eeg_dir = join(data_dir, sub)
deriv_dir = join(data_dir, 'derivatives', 'mne', sub)
raw_fpath = join(eeg_dir, f'{sub}_eeg.bdf')
os.makedirs(deriv_dir, exist_ok=True)


## load raw data 
raw = read_raw_bdf(raw_fpath)

## get rid of empty channels and mark channel types
raw: RawEDF = raw.drop_channels(['EXG7', 'EXG8', 'GSR1', 'GSR2', 'Erg1', 'Erg2', 'Resp', 'Plet', 'Temp']) # type: ignore
eog_channels = ['EXG3', 'EXG4', 'EXG5', 'EXG6']
raw.set_channel_types(mapping=dict([(c, 'eog') for c in eog_channels]))

## pick channels to be filtered
filter_picks = mne.pick_types(raw.info, eeg=True, eog=True, stim=False)

# https://autoreject.github.io/stable/auto_examples/plot_autoreject_workflow.html
# https://autoreject.github.io/stable/auto_examples/index.html
# https://mne.tools/stable/auto_tutorials/preprocessing/40_artifact_correction_ica.html