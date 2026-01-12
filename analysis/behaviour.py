"""Analyse behavioural data

trial numbers spreadsheet: https://docs.google.com/spreadsheets/d/14jrOEcPnLSVjfQn3yfuNDqvA0M7qz-dA0L19HOADiRs/edit#gid=0

Trials with an incorrect response to T1 (11 ± 5%) were discarded from subsequent behavioral 
and ERP analysis. ‘False positive trials’ (that is, ‘T2 absent’ trials 
in which subjective visibility was above 50%) were discarded from the ERP analysis 
(fewer than 2% of the ‘T2 absent’ trials in each condition).
"""
from __future__ import annotations
from os.path import join, expanduser, basename
import os
from glob import glob
import seaborn
import matplotlib.pyplot as plt
from experiment.timer import Timer
from experiment.constants import Constants
from utils import read_events, print_info
from config import DATA_DIR, DERIV_NAME, FRAME_RATE

print_info(f'## Visualize performance')

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

    df = read_events(data_dir, sub)

    ## get rid of training trials
    df = df[df['phase'] == 'test']

    ## lose columns that we dont need
    df = df.drop(['id_trigger', 'vis_trigger', 'delay_index', 'delay', 't1_trigger', 
                't2_trigger', 'iti', 't1_index', 't2_index', 'masks', 'id_onset', 'vis_onset', 'vis_init'], axis=1)


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
