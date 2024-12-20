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
        deriv_name='mne',
        epo_fname=f'{sub}_dirty_epo.fif',
    ),
    classic=dict(
        deriv_name='mne',
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
    else: 
        epo_df = trials_df[(trials_df.valid_data == True)]
        epochs = epochs[~epo_df.soa_long]
        epo_df = epo_df[~epo_df.soa_long]
    
    
    assert len(epo_df) == len(epochs)

    ## they should now have the same number of entries
    

    """
    In order to analyze the brain events underlying this bimodal distribu- tion, 
    we compared the ERPs evoked by T2 during the attentional blink (short SOA, dual task) 
    when T2 was seen and when it was not seen (empirically defined as visibility Z or o50%). 
    Because T1 and the masks also evoked ERPs, we extracted the potentials specifically 
    evoked by T2 by subtracting the ERPs evoked when T2 was absent and replaced by a blank screen 
    """

    ## ERP for T2 regardless of trial type, all T2-present without difference
    ## TODO: watch out! the classic + dirty pipelines do not include LONG SOA
    ## so either select SHORT SOA only (easiest) or adapt both pipelines and select later
    erp_absent = epochs[~epo_df.t2presence].average()

    erps = dict(
        absent=erp_absent,
        seen=erp_seen,
        unseen=erp_unseen,
    )
    print_info('\n\nNumber of epochs:')
    for name, evoked in erps.items():
        print_info(f'{name}: {evoked.nave}')
    print('\n\n')


    ## butterfly (line per channel)
    evks["aud/left"].plot(picks="mag", spatial_colors=True, gfp=True)

    # PSD
    epochs["auditory"].compute_psd().plot(picks="eeg", exclude="bads", amplitude=False)

    # row per channel
    epochs.plot_image

    # compare evokeds for CI: If a [dict/list] of lists, the unweighted mean 
    # is plotted as a time series and the parametric confidence interval 
    # is plotted as a shaded area

    ## TODO: what do the red dots mean? (single-channel rejected epoch; but how is it treated)