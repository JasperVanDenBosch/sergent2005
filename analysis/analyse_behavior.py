"""Analyse behavioral data of pilot

trial numbers spreadsheet: https://docs.google.com/spreadsheets/d/14jrOEcPnLSVjfQn3yfuNDqvA0M7qz-dA0L19HOADiRs/edit#gid=0

Trials with an incorrect response to T1 (11 ± 5%) were discarded from subsequent behavioral 
and ERP analysis. ‘False positive trials’ (that is, ‘T2 absent’ trials 
in which subjective visibility was above 50%) were discarded from the ERP analysis 
(fewer than 2% of the ‘T2 absent’ trials in each condition).
"""
from __future__ import annotations
from os.path import join, expanduser
import os
from colorama import init as colorama_init, Fore, Style
import pandas, seaborn
import matplotlib.pyplot as plt
from experiment.timer import Timer
from experiment.constants import Constants
colorama_init()
def print_info(msg: str):
    print(f'{Fore.CYAN}{msg}{Style.RESET_ALL}')
def print_warn(msg: str):
    print(f'{Fore.MAGENTA}{msg}{Style.RESET_ALL}')


BASELINE = 0.250 ## duration of baseline
fr_conf  = 60 ## TODO double check
REJECT_CRIT = dict(eeg=200e-6, eog=70e-6) # 200 µV, 70 µV
TMAX = 0.715
LATENCY = 0.016
sub = 'sub-UOLM001'
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
trials_df = df.drop(['vis_perc', 'target1', 'id_choice', 'id_rt', 'vis_rating', 'soa',
    'vis_rt', 't1_onset', 't1_offset', 't2_onset', 't2_offset', 'target1', 'target2'], axis=1)

