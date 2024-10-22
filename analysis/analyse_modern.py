"""Use contemporary tools to pre-process 
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import join, expanduser
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

MODE = 'modern'
BASELINE = 0.250 ## duration of baseline
fr_conf  = 114 ## TODO double check
REJECT_CRIT = dict(eeg=200e-6, eog=70e-6) # 200 µV, 70 µV
TMAX = 0.715
LATENCY = 0.016
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

## bad channels
bad_chans = ['A32','C12', 'C14', 'B23', 'B29', 'D24'] #'D5', 'D8', 'D16', 'D17']
raw.info['bads'].extend(bad_chans)


## apply average reference
raw = raw.drop_channels(['EXG1', 'EXG2']) # type: ignore
raw = raw.set_eeg_reference(ref_channels='average')

## determine electrode head locations
montage = make_standard_montage('biosemi128', head_size='auto')
fig = montage.plot(show=False)
fig.savefig('plots/montage.png')
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
epo_name = f'T2-shortSOA'
epochs.save(join(deriv_dir, f'{sub}_{epo_name}_epo.fif'), overwrite=True)

## create a column where we indicate for which trials we have data
## since come may have been discarded as artifacts
data_mask = numpy.zeros(events.shape[0], dtype=bool)
data_mask[epochs.selection] = True
trials_df['valid_data'] = data_mask

## restrict the df to the epochs we currently have, short-SOA with valid data
epo_df = trials_df[(trials_df.soa_long == False) & (trials_df.valid_data == True)]

## they should now have the same number of entries
assert len(epo_df) == len(epochs)

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
    Central = (0.528, 0.624),
    Occipital = (0.160, 0.200),
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
    figs[0].savefig(f'plots/{MODE}_together_{roi_name}.png')
    plt.close()


    fig = montage.plot(
        scale_factor=6,
        show_names=roi_ch_names,
        show=False
    )
    fig.savefig(f'plots/montage_{roi_name}.png')
