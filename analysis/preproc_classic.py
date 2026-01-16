"""Preprocessing in line with original manuscript

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

"""
from __future__ import annotations
from os.path import join, expanduser, isfile, basename
import os
from glob import glob
from mne.io import read_raw_bdf
from mne.channels import make_standard_montage
import mne
from experiment.triggers import Triggers
from experiment.timer import Timer
from experiment.constants import Constants
from utils import read_events, read_channels, print_info
from config import (DATA_DIR, DERIV_NAME, FRAME_RATE,
                    BASELINE, TMAX, LATENCY)


data_dir = expanduser(DATA_DIR)
deriv_dir_root = join(data_dir, 'derivatives', DERIV_NAME)

MODE_NAME = 'original'

const = Constants()
timer = Timer()
timer.optimizeFlips(FRAME_RATE, const)

sub_dirs = sorted(glob(join(data_dir, 'sub-*')))
for sub_dir in sub_dirs:
    sub = basename(sub_dir)
    print_info(f'Reading EEG data for {sub}..')

    eeg_dir = join(data_dir, sub, 'eeg')
    deriv_dir = join(deriv_dir_root, sub)
    raw_fpath = join(eeg_dir, f'{sub}_task-ab_eeg.bdf')
    os.makedirs(deriv_dir, exist_ok=True)

    ## load raw data 
    raw = read_raw_bdf(raw_fpath)

    chans_df = read_channels(data_dir, sub)

    ## remove unused channels
    misc_chans = chans_df[chans_df.type == 'MISC']['name'].to_list()
    raw.drop_channels(misc_chans)

    ## mark channel type for EOG
    eog_channels = chans_df[chans_df.description.str.contains('EOG')]['name'].to_list()
    raw.set_channel_types(mapping=dict([(c, 'eog') for c in eog_channels]))

    ## mark bad channels
    bad_chans = chans_df[chans_df.status == 'bad']['name'].to_list()
    raw.info['bads'].extend(bad_chans)

    ## remove the mastoids
    refs_chans = chans_df[chans_df.type == 'REF']['name'].to_list()
    raw.drop_channels(refs_chans)

    ## pick channels to be filtered
    filter_picks = mne.pick_types(raw.info, eeg=True, eog=True, stim=False)
    print_info('Loading data and filtering..')
    raw.load_data()
    raw.filter(l_freq=0.5, h_freq=20, picks=filter_picks)

    ## read the artifact annotations
    annots_fpath = join(deriv_dir, f'{sub}_annotations.txt')
    assert isfile(annots_fpath), 'missing annotations file'
    annots = mne.read_annotations(annots_fpath)
    raw.set_annotations(annots)

    ## apply average reference
    raw = raw.set_eeg_reference(ref_channels='average')

    ## determine electrode head locations
    montage = make_standard_montage('biosemi64', head_size='auto')
    raw.set_montage(montage, on_missing='warn')

    ## find triggers
    mask = sum([2**i for i in (8,9,10,11,12,13,14,15,16)])
    events = mne.find_events(
        raw,
        verbose=False,
        mask=mask,
        mask_type='not_and'
    )

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
        event_id=event_ids,
        tmin=tmin,
        tmax=TMAX+LATENCY,
        baseline=(tmin, tmin+BASELINE),
        on_missing='warn',
        preload=True
    )

    ## Read the raw data events
    events_df = read_events(data_dir, sub)

    ## Make subset of events based on selected triggers and 
    ## non-rejected epochs (indices with regard to full MNE events array)
    events_df = events_df.iloc[epochs.selection]

    ## Check that they match
    assert len(events_df) == len(epochs)
    assert events_df.iloc[10].value == epochs.events[10, 2]

    ## Store alongside epochs
    events_fpath = join(deriv_dir, f'{sub}_mode-{MODE_NAME}_events.tsv')
    events_df.to_csv(events_fpath, sep='\t', index=False, float_format = '%.12g')

    print_info(f'Epoched {len(epochs)} trials')
    epochs.save(join(deriv_dir, f'{sub}_mode-{MODE_NAME}_epo.fif'), overwrite=True)
