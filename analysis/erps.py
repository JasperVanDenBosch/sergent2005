"""Load epoched data and plot ERPs
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import join, expanduser, isfile
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

    ## ERP for T2 absent trials
    erp_absent = epochs[~epo_df.t2presence].average()

    ## ERP for seen trials
    erp_seen = epochs[(epo_df.t2presence) & (epo_df.seen)].average()
    erp_seen_min_absent = mne.combine_evoked([erp_seen, erp_absent], [1, -1])

    ## ERP for unseen trials
    erp_unseen = epochs[(epo_df.t2presence) & (~epo_df.seen)].average()
    erp_unseen_min_absent = mne.combine_evoked([erp_unseen, erp_absent], [1, -1])

    erps = dict(
        absent=erp_absent,
        seen=erp_seen,
        unseen=erp_unseen,
    )
    print_info('\n\nNumber of epochs:')
    for name, evoked in erps.items():
        print_info(f'{name}: {evoked.nave}')
    print('\n\n')

    """ 
    We use both O1 and O2 as the foci for the bilaterally-distributed N1 component 
    (i.e., an ROI covering the 5 closest electrodes to O1 and 5 closest electrodes to O2;
    see Figure 2 of the original manuscript) 

    and Pz as the P3b component focus (see Figure 5 of original study).  """

    """Our temporal ROI bounds are 
    528ms-624ms for N1
    160ms-200ms for P3b 
    """

    ## See montage_marked.png
    rois = dict(
        Central = ['A4', 'A5', 'A3', 'A17', 'A19', 'A20', 'A21', 'A30', 'A31', 'A32'],
        Occipital = ['A10', 'A14', 'A15', 'A16', 'A23', 'A24', 'A27', 'A28', 'A29', 'B7'],
    )
    time_windows = dict(
        Central = (0.160, 0.200),
        Occipital = (0.528, 0.624),
    )
    for roi_name, roi_ch_names in rois.items():
        ch_idx = mne.pick_channels(raw.info['ch_names'], roi_ch_names)

        erp_seen_min_absent_roi = mne.channels.combine_channels(
            erp_seen_min_absent,
            dict(roi=ch_idx),
            method='mean'
        )

        erp_unseen_min_absent_roi = mne.channels.combine_channels(
            erp_unseen_min_absent,
            dict(roi=ch_idx),
            method='mean'
        )

        figs = mne.viz.plot_compare_evokeds( ## or another fn that allows showing two with highlight
            dict(
                seen=erp_seen_min_absent_roi,
                unseen=erp_unseen_min_absent_roi
            ),
            colors=('#1b9e77', '#7570b3'),
            linestyles=('solid', 'dotted'),
            ylim=dict(eeg=[-5, 5]),
            show=False
        )
        plt.axvspan(
            xmin=time_windows[roi_name][0],
            xmax=time_windows[roi_name][1],
            color='gray',
            alpha=0.2
        )
        figs[0].savefig(f'plots/{mode}_{roi_name}.png')
        plt.close()


        fig = montage.plot(
            scale_factor=6,
            show_names=roi_ch_names,
            show=False
        )
        fig.savefig(f'plots/montage_{roi_name}.png')
