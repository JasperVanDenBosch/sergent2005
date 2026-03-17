"""Analyse behavioural data

Trial numbers spreadsheet: https://docs.google.com/spreadsheets/d/14jrOEcPnLSVjfQn3yfuNDqvA0M7qz-dA0L19HOADiRs/edit#gid=0
(Useful for understanding number of trials acros the various conditions)
"""
from __future__ import annotations
from os.path import join, expanduser, basename
from math import ceil
import os
from glob import glob
from pandas import DataFrame
import seaborn
import matplotlib.pyplot as plt
from experiment.timer import Timer
from experiment.constants import Constants
from utils import read_events, print_info
from config import DATA_DIR, DERIV_NAME, FRAME_RATE

print_info(f'## Behaviour: Visualize blink')

data_dir = expanduser(DATA_DIR)
sub_dirs = sorted(glob(join(data_dir, 'sub-*')))

const = Constants()
timer = Timer()
timer.optimizeFlips(FRAME_RATE, const)

trials = []
for sub_dir in sub_dirs:
    sub = basename(sub_dir)
    print_info(f'Reading events for {sub}..')

    eeg_dir = join(data_dir, sub)
    deriv_dir = join(data_dir, 'derivatives', DERIV_NAME, sub)
    os.makedirs(deriv_dir, exist_ok=True)

    events_df = read_events(data_dir, sub)

    ## get rid of training trials
    events_df = events_df[events_df['phase'] == 'test']

    ## BIDS event file is by event, let's gather behavior by trial
    for t in events_df.trial_index.unique():
        trial_events = events_df[events_df.trial_index == t]
        ## We just need a row with a target for all behavior columns
        event = trial_events[trial_events.trial_type == 't1'].iloc[0]
        ## Some derivations relevant for selection criteria
        ## 1. visibility rating as a percentage
        vis_perc=round(event.vis_rating / 0.2)
        ## 2. visibility over 50% is considered "seen"
        seen = vis_perc > 50
        ## 3. T2 reported seen, when not actually presented
        false_alarm = seen and (not event.t2presence)
        trials.append(
            dict(
                sub = sub,
                vis_perc = vis_perc,
                seen = seen,
                false_alarm=false_alarm,
                **event.to_dict()
            )
        )

df = DataFrame(trials)


## T2 present during the AB (Dual task, short SOA)
variants = dict(
    plain=dict(),
    stacked=dict(hue='sub')
)
for variant, kwargs in variants.items():
    plt.figure()
    ab_trials_mask = (df['dual_task'] == True) & (df['soa_long'] == False) & (df['t2presence'] == True)
    ax = seaborn.histplot(
        data=df[ab_trials_mask],
        x='vis_perc',
        stat='percent',
        bins=20,
        multiple='stack',
        **kwargs
    )
    ax.set(
        title='(Dual task, short SOA)',
        xlabel='Subjective visibility',
        ylabel='Percent of trials'
    )
    fig = ax.get_figure()
    fig.suptitle('Fig 1B: T2 present during the AB')
    assert fig is not None
    fpath = join(data_dir, 'derivatives', DERIV_NAME, f'fig_1b_{variant}.png')
    fig.savefig(fpath)
    plt.close()


"""
Trials with an incorrect response to T1 (11% ± 5%) were discarded 
from subsequent behavioral and ERP analysis. 

NOTE: unclear if this is in critical condition or overall.. seems low
"""
incorrect = df[['sub', 'correct']][df.correct == False].value_counts()
avg = incorrect.mean()
std = incorrect.std()
upper = incorrect.quantile(0.95)
lower = incorrect.quantile(0.05)
ci_perc = ceil(((max(abs(upper-avg), abs(lower-avg))/avg)*100))
print_info(f'Trials with an incorrect response to T1: {avg:.2f} ±{ci_perc}% (std={std:.2f})')

"""
‘False positive trials’ (that is, ‘T2 absent’ trials in which 
subjective visibility was above 50%) were discarded 
from the ERP analysis (fewer than 2% of the ‘T2 absent’ trials in each condition).
"""
t2_absent = df[df.t2presence == False]
n_trials = t2_absent.size
n_false_alarm = t2_absent[t2_absent.false_alarm == True].size
fp_percent = (n_false_alarm / n_trials)*100
print_info(f'False positive trials (overall): {fp_percent:.1f}%')
## TODO: break down by "condition" (whatever that means)
