"""Some simple "parent" waveforms across conditions as a sense check
"""
from __future__ import annotations
from os.path import join, expanduser, basename
from glob import glob
import mne
from mne.io import read_raw_bdf
import matplotlib.pyplot as plt
from utils import read_selected_events, print_info
from config import (DATA_DIR, DERIV_NAME, ROIS_DIAG, TIME_WINDOWS, SELECTED_EVENTS)


MODES = ('original', 'auto')
n_conds = len(SELECTED_EVENTS)
data_dir = expanduser(DATA_DIR)
deriv_dir_root = join(data_dir, 'derivatives', DERIV_NAME)


sub_dirs = sorted(glob(join(data_dir, 'sub-*')))
group_erps = []
for mode in MODES:

    for sub_dir in sub_dirs:
        sub = basename(sub_dir)
        print_info(f'Making ERPs for {sub}..')

        eeg_dir = join(data_dir, sub, 'eeg')
        deriv_dir = join(deriv_dir_root, sub)

        ## for accessing channel indices
        raw_fpath = join(eeg_dir, f'{sub}_task-ab_eeg.bdf')
        raw = read_raw_bdf(raw_fpath)


        epo_fname=f'{sub}_mode-{mode}_conds-{n_conds}_epo.fif'
        epochs = mne.read_epochs(join(deriv_dir, epo_fname))
        events_df = read_selected_events(deriv_dir_root, sub, mode, n_conds)

        ## ERP for seen trials

        ## TODO select epochs
        # For T2:
        # - present short
        # - present long
        # Use mne-style indexing instead? 'a/b/c'

        erp_present = epochs[(events_df.t2presence) & (events_df.) )].average()


        erps = dict(
            absent=erp_absent,
            seen=erp_seen,
            unseen=erp_unseen,
            seen_min_absent=erp_seen_min_absent,
            unseen_min_absent=erp_unseen_min_absent,
        )
        print_info('\n\nNumber of epochs:')
        for name, evoked in erps.items():
            print_info(f'{name}: {evoked.nave}')
        print('\n\n')
        group_erps.append(erps)


        for roi_name, roi_ch_names in ROIS_DIAG.items():
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
            figs[0].savefig(join(deriv_dir, f'{sub}_mode-{mode}_{roi_name}.png'))
            plt.close()

    ## Group level
    erps = dict()
    names = list(group_erps[0].keys())
    for name in names:
        indiv_erps = [erps[name] for erps in group_erps]
        erps[name] = mne.combine_evoked(indiv_erps, 'equal')


    for roi_name, roi_ch_names in ROIS.items():
        ch_idx = mne.pick_channels(raw.info['ch_names'], roi_ch_names)

        erp_seen_min_absent_roi = mne.channels.combine_channels(
            erps['seen_min_absent'],
            dict(roi=ch_idx),
            method='mean'
        )

        erp_unseen_min_absent_roi = mne.channels.combine_channels(
            erps['unseen_min_absent'],
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
        figs[0].savefig(join(deriv_dir_root, f'grandavg_mode-{mode}_{roi_name}.png'))
        plt.close()
