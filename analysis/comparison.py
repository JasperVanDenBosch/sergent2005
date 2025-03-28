"""Compare preproc methods with butterfly plots
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import join, expanduser
import os
from colorama import init as colorama_init, Fore, Style
import mne, numpy
from mne.io import read_raw_bdf
from mne.channels import make_standard_montage
import matplotlib.pyplot as plt
from analyse_behavior import trials_df
if TYPE_CHECKING:
    from mne.io.edf.edf import RawEDF
colorama_init()
def print_info(msg: str):
    print(f'{Fore.CYAN}{msg}{Style.RESET_ALL}')
def print_warn(msg: str):
    print(f'{Fore.MAGENTA}{msg}{Style.RESET_ALL}')


sub = 'sub-UOBC003'
data_dir = expanduser('~/data/eegmanylabs/Sergent2005/')
eeg_dir = join(data_dir, sub)

## for accessing channel indices
raw_fpath = join(eeg_dir, f'{sub}_eeg.bdf')
raw = read_raw_bdf(raw_fpath)
montage = make_standard_montage('biosemi128', head_size='auto')


modes = dict(
    dirty=dict(
        deriv_name='dirty',
        epo_fname=f'{sub}_dirty_epo.fif',
    ),
    classic=dict(
        deriv_name='classic',
        epo_fname=f'{sub}_T2-shortSOA_epo.fif',
    ),
    automated=dict(
        deriv_name='modern',
        epo_fname=f'{sub}_clean_epo.fif',
    ),
)
for mode, settings in modes.items():


    deriv_dir = join(data_dir, 'derivatives', settings['deriv_name'], sub)
    epochs = mne.read_epochs(join(deriv_dir, settings['epo_fname']))


    ## create a column where we indicate for which trials we have data
    ## since come may have been discarded as artifacts
    data_mask = numpy.zeros(trials_df.shape[0], dtype=bool)
    data_mask[epochs.selection] = True
    trials_df['valid_data'] = data_mask

    ## restrict the df to the epochs we currently have, short-SOA with valid data
    if mode == 'classic':
        epo_df = trials_df[(trials_df.soa_long == False) & (trials_df.valid_data == True)]
    elif mode == 'dirty':
        epo_df = trials_df[(trials_df.valid_data == True)]
        epochs = epochs[~epo_df.soa_long]
        epo_df = epo_df[~epo_df.soa_long]
    elif mode == 'automated': 
        epo_df = trials_df[(trials_df.valid_data == True)]
        epochs = epochs[(epo_df.soa_long == False) & (epo_df.task == "dual")]
        epo_df = epo_df[(epo_df.soa_long == False) & (epo_df.task == "dual")]
    
    ## they should now have the same number of entries
    assert len(epo_df) == len(epochs)

    print_info(mode)
    print_info(f'all: {len(epo_df)}')
    print_info(f't2 present: {epo_df.t2presence.sum()}')
    print_info(f'SOA long: {epo_df.soa_long.sum()}')
    print_info(f'training: {(epo_df.phase == "training").sum()}')
    print_info(f'single task: {(epo_df.task == "single").sum()}')
    ## automated still has more trials than dirty! T2 presence?
    
    evoked = epochs.average()


    ## butterfly (line per channel)
    fig = evoked.plot(
        picks='eeg',
        titles=dict(eeg=mode),
        spatial_colors=True,
        ylim=dict(eeg=[-15, 5]),
        show=False
    )
    fig.savefig(f'plots/butterfly_{mode}.png')
    plt.close()

    # PSD
    #epochs["auditory"].compute_psd().plot(picks='eeg', exclude='bads', amplitude=False)

    # row per channel
    #epochs.plot_image

    # compare evokeds for CI: If a [dict/list] of lists, the unweighted mean 
    # is plotted as a time series and the parametric confidence interval 
    # is plotted as a shaded area

    ## TODO: what do the red dots mean? (single-channel rejected epoch; but how is it treated)