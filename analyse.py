"""Analysis of pilot data


## TODO

- [x] use colorama to distinguish output from mne verbosity
- [ ] sanity check reference
- [ ] sanity check filter
- [ ] sanity check timing
- [ ] artifact rejection
- [ ] match vis ratings with epochs
- [ ] timing changes

## behaviour

- [x] vis rating 0 becomes -999
- [x] plot actual and designed duration of T1 / T2 / SOA (from log and/or from eeg triggers)
- [x] visibility plots as figure 1B
- [x] discard incorrect trials (how many)
- [x] discard false positive trials (how many)


Issue A baseline

We can sample baseline before -SOA from T2. 
Now if we want to sample the same baseline regardless of SOA,
the baseline would start before the "T1 delay"  /fixation cross comes on, 
if the T1 delay is short and SOA is too. (since delay-short < (SOA-diff+baseline))
If we sample the baseline differently based on SOA, 
we may pick up on a different readiness phase.
(I will pick this solution for now.)

Solution:
Sample same baseline wrt to T0 ie (-250 - 0)



trial numbers spreadsheet: https://docs.google.com/spreadsheets/d/14jrOEcPnLSVjfQn3yfuNDqvA0M7qz-dA0L19HOADiRs/edit#gid=0

EX1: left mastoid
EX2: right mastoid
EX3: bottom HEOG
EX4: top HEOG
EX5: left VEOG
EX6: right VEOG


Trials with an incorrect response to T1 (11 ± 5%) were discarded from subsequent behavioral 
and ERP analysis. ‘False positive trials’ (that is, ‘T2 absent’ trials 
in which subjective visibility was above 50%) were discarded from the ERP analysis 
(fewer than 2% of the ‘T2 absent’ trials in each condition).


In order to analyze the brain events underlying this bimodal distribu- tion, 
we compared the ERPs evoked by T2 during the attentional blink (short SOA, dual task) 
when T2 was seen and when it was not seen (empirically defined as visibility Z or o50%). 
Because T1 and the masks also evoked ERPs, we extracted the potentials specifically 
evoked by T2 by subtracting the ERPs evoked when T2 was absent and replaced by a blank screen 


The remaining trials were averaged in synchrony with T2 onset (or T1 onset for T1-evoked ERPs),
digitally transformed to an average reference, band-pass filtered (0.5-20 Hz)
and corrected for baseline over a 250-ms window during fixation at the beginning of the trial.

TIMING TO IMPROVE
Each trial begins with a fixation cross, presented for either 
514ms or 857ms (36-frames and 60-frames respectively; 
reported as 516ms and 860ms in the manuscript), 
selected at random per trial. 
Six items are then presented in the following order: T1, mask, fixation cross, 
T2 (present or absent), mask, mask. In the original study, each of T1, T2, 
and the masks were presented for 43ms (3-frames), 
separated by a blank screen of 43ms (3-frames). 
To create the short and long TOA conditions, the fixation cross between T1 and T2 was presented 
for either 43ms (3-frames) or 471ms (33-frames), 
followed by a blank screen of 43ms (3-frames), 
thus creating T1->T2 TOAs of 257ms and 686ms (18-frames and 48-frames, respectively; 
reported as 258ms and 688ms in the manuscript), respectively.

"""
from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import join, expanduser, isfile
import os
from colorama import init as colorama_init, Fore, Style
from mne.io import read_raw_bdf
from mne.channels import make_standard_montage
import mne, pandas, seaborn, numpy
import matplotlib.pyplot as plt
from experiment.triggers import Triggers
from experiment.timer import Timer
from experiment.constants import Constants
if TYPE_CHECKING:
    from mne.io.edf.edf import RawEDF
colorama_init()
def print_info(msg: str):
    print(f'{Fore.CYAN}{msg}{Style.RESET_ALL}')
def print_warn(msg: str):
    print(f'{Fore.MAGENTA}{msg}{Style.RESET_ALL}')


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

df = pandas.read_csv(join(eeg_dir, f'{sub}_trials.csv'), index_col=0)

## get rid of training trials
df = df[df['phase'] == 'test']

## lose columns that we dont need
df = df.drop(['id_trigger', 'vis_trigger', 'delay_index', 'delay', 't1_trigger', 
              't2_trigger', 'iti', 't1_index', 't2_index', 'masks', 'id_onset', 'vis_onset', 'vis_init'], axis=1)

## timing analysis
soa_df = df[df.soa_long == False].copy()
observed_series = (soa_df.t2_onset - soa_df.t1_onset)*1000
observed_soas = observed_series.values - observed_series.values.mean()
planned_flips = soa_df.soa.iloc[0]
planned_ms = timer.flipsToSecs(planned_flips)*1000
plt.figure()
ax = seaborn.histplot(observed_soas, bins=41)
ax.set(
    title='Timing: Short SOA (ms) based on reported flip time',
    xlabel='+/- ms from mean',
    ylabel='Percent of trials'
)
ax.get_figure().savefig('plots/soa_variability.png')
plt.close()

## pilot: -999 is 0 vis
df['vis_rating'] = df['vis_rating'].replace(-999, 0)
## subjective visibility as a percentage 0-100%
df['vis_perc'] = (df['vis_rating'] / 0.20).astype(int)
"""
Trials with an incorrect response to T1 (11 ± 5%) were discarded 
from subsequent behavioral and ERP analysis. 
‘False positive trials’ (that is, ‘T2 absent’ trials in which 
subjective visibility was above 50%) were discarded 
from the ERP analysis (fewer than 2% of the ‘T2 absent’ trials in each condition).
"""

## turn float response into chosen target string 
df['id_choice'] = df['id_choice'].replace({0.0: 'XOOX', 1.0: 'OXXO'})
## mark correctness of T1 responses (to discard incorrect trials)
df['correct'] = df['id_choice'] == df['target1']
incorrect_perc = (df.correct == False).mean()*100
print_info(f'Incorrect trials: {incorrect_perc:.1f}%')
## visibility Z or o50%). 
df['seen'] = df['vis_perc'] > 50
## mark false positives (to be discarded for EEG)
df['false_alarm'] = df['seen'] & (~df['t2presence'])



## T2 present during the AB (Dual task, short SOA)
plt.figure()
ab_trials_mask = (df['task'] == 'dual') & (df['soa_long'] == False) & (df['t2presence'] == True)
ax = seaborn.histplot(data=df[ab_trials_mask], x='vis_perc', stat='percent', bins=20)
ax.set(
    title='Fig 1B: T2 present during the AB',
    xlabel='Subjective visibility',
    ylabel='Percent of trials'
)
ax.get_figure().savefig('plots/blink_visibility.png')
plt.close()


## done with behavior, we can now drop more columns
df = df.drop(['vis_perc', 'target1', 'id_choice', 'id_rt', 'vis_rating', 'soa',
    'vis_rt', 't1_onset', 't1_offset', 't2_onset', 't2_offset', 'target1', 'target2'], axis=1)


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

annots_fpath = join(deriv_dir, f'{sub}_annotations.txt')
assert isfile(annots_fpath), 'missing annotations file'
annots = mne.read_annotations(annots_fpath)
raw.set_annotations(annots)

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
df['valid_data'] = data_mask

## restrict the df to the epochs we currently have, short-SOA with valid data
epo_df = df[(df.soa_long == False) & (df.valid_data == True)]

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
    figs[0].savefig(f'plots/together_{roi_name}.png')
    plt.close()


    fig = montage.plot(
        scale_factor=6,
        show_names=roi_ch_names,
        show=False
    )
    fig.savefig(f'plots/montage_{roi_name}.png')
