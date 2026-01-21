"""Load epoched data and plot ERPs
"""
from __future__ import annotations
from os.path import join, expanduser, basename
from glob import glob
import mne
from mne.io import read_raw_bdf
import matplotlib.pyplot as plt
from utils import read_selected_events, print_info
from config import (DATA_DIR, DERIV_NAME, ROIS, TIME_WINDOWS)


MODES = ('original',) #, 'auto'
data_dir = expanduser(DATA_DIR)
deriv_dir_root = join(data_dir, 'derivatives', DERIV_NAME)


sub_dirs = sorted(glob(join(data_dir, 'sub-*')))

for mode in MODES:

    for sub_dir in sub_dirs:
        sub = basename(sub_dir)
        print_info(f'Making ERPs for {sub}..')

        eeg_dir = join(data_dir, sub, 'eeg')
        deriv_dir = join(deriv_dir_root, sub)

        ## for accessing channel indices
        raw_fpath = join(eeg_dir, f'{sub}_task-ab_eeg.bdf')
        raw = read_raw_bdf(raw_fpath)


        epo_fname=f'{sub}_mode-{mode}_epo.fif'
        epochs = mne.read_epochs(join(deriv_dir, epo_fname))
        events_df = read_selected_events(deriv_dir_root, sub, mode)


        """
        In order to analyze the brain events underlying this bimodal distribu- tion, 
        we compared the ERPs evoked by T2 during the attentional blink (short SOA, dual task) 
        when T2 was seen and when it was not seen (empirically defined as visibility Z or o50%). 
        Because T1 and the masks also evoked ERPs, we extracted the potentials specifically 
        evoked by T2 by subtracting the ERPs evoked when T2 was absent and replaced by a blank screen 
        """

        ## subjective visibility as a percentage 0-100%
        events_df['vis_perc'] = (events_df['vis_rating'] / 0.20).astype(int)
        events_df['seen'] = events_df['vis_perc'] > 50

        ## mark false positives (to be discarded for EEG)
        events_df['false_alarm'] = events_df['seen'] & (~events_df['t2presence'])


        ### Mark incorrect and false alarm trials for discarding
        events_df['discard'] = (events_df['correct'] == False) | (events_df['false_alarm'] == True)
        n_before = len(epochs)
        n_false_alarm = events_df['false_alarm'].sum()
        n_incorrect = (events_df['correct'] == False).sum()
        n_discard = events_df.discard.sum()

        ## Remove these from both sides
        epochs[~events_df.discard]
        events_df = events_df[~events_df.discard]
        print_info(f'Discarding {n_discard}/{n_before}; {n_false_alarm}× false alarm, {n_incorrect}× incorrect')
        raise ValueError

        ## ERP for T2 absent trials
        erp_absent = epochs[~events_df.t2presence].average()

        ## ERP for seen trials
        erp_seen = epochs[(events_df.t2presence) & (events_df.seen)].average()
        erp_seen_min_absent = mne.combine_evoked([erp_seen, erp_absent], [1, -1])

        ## ERP for unseen trials
        erp_unseen = epochs[(events_df.t2presence) & (~events_df.seen)].average()
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


        for roi_name, roi_ch_names in ROIS.items():
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
                xmin=TIME_WINDOWS[roi_name][0],
                xmax=TIME_WINDOWS[roi_name][1],
                color='gray',
                alpha=0.2
            )
            figs[0].savefig(join(deriv_dir, f'mode-{mode}_roi-{roi_name}.png'))
            plt.close()
