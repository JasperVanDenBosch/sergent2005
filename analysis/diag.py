"""Some simple "parent" waveforms across conditions as a sense check
"""
from __future__ import annotations
from os.path import join, expanduser, basename
from glob import glob
import mne
from mne.io import read_raw_bdf
import matplotlib.pyplot as plt
from utils import read_selected_events, print_info
from config import (DATA_DIR, DERIV_NAME, ROIS_DIAG, TOPO_TIMES, SELECTED_EVENTS)


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


        erps = dict(
            T2_short=epochs['short/present'].average(),
            T2_long=epochs['long/present'].average(),
            # unseen=erp_unseen,
            # seen_min_absent=erp_seen_min_absent,
            # unseen_min_absent=erp_unseen_min_absent,
        )
        group_erps.append(erps)

        for cond_name, evoked in erps.items():
            for roi_name, roi_ch_names in ROIS_DIAG.items():
                print(f'{sub}_mode-{mode}_cond-{cond_name}_roi-{roi_name}')

                fig = evoked.copy().pick(roi_ch_names).plot(
                    ylim=dict(eeg=[-7, 7]),
                    selectable=False,
                    show=False
                )
                plt.title(f'{cond_name} {roi_name}')
                fig.savefig(join(deriv_dir, f'{sub}_mode-{mode}_cond-{cond_name}_roi-{roi_name}.png'))
                plt.close()

                fig = evoked.plot_topomap(TOPO_TIMES, show=False)
                plt.title(f'{cond_name} {roi_name}')
                fig.savefig(join(deriv_dir, f'{sub}_mode-{mode}_cond-{cond_name}_roi-{roi_name}_topo.png'))
                plt.close()

    ## Group level
    erps = dict()
    names = list(group_erps[0].keys())
    for name in names:
        indiv_erps = [erps[name] for erps in group_erps]
        erps[name] = mne.combine_evoked(indiv_erps, 'equal')


        for cond_name, evoked in erps.items():
            for roi_name, roi_ch_names in ROIS_DIAG.items():

                print(f'grandavg__mode-{mode}_cond-{cond_name}_roi-{roi_name}')

                fig = evoked.copy().pick(roi_ch_names).plot(
                    ylim=dict(eeg=[-7, 7]),
                    selectable=False,
                    show=False
                )
                plt.title(f'{cond_name} {roi_name}')
                fig.savefig(join(deriv_dir_root, f'grandavg__mode-{mode}_cond-{cond_name}_roi-{roi_name}.png'))
                plt.close()

                fig = evoked.plot_topomap(TOPO_TIMES, show=False)
                plt.title(f'{cond_name} {roi_name}')
                fig.savefig(join(deriv_dir_root, f'grandavg__mode-{mode}_cond-{cond_name}_roi-{roi_name}_topo.png'))
                plt.close()
