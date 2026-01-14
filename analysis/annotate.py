"""Artifect rejection implemented as MNE annotations

"""
from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import join, expanduser, basename
import os
from glob import glob
from mne.io import read_raw_bdf
import mne, numpy
from experiment.timer import Timer
from experiment.constants import Constants
from utils import print_info, read_channels 
from config import (DATA_DIR, DERIV_NAME, FRAME_RATE,
                    BASELINE, TMAX, LATENCY)
if TYPE_CHECKING:
    from mne.io.edf.edf import RawEDF

print_info(f'## Annotate: Threshold based artifact rejection')

data_dir = expanduser(DATA_DIR)
deriv_dir_root = join(data_dir, 'derivatives', DERIV_NAME)

const = Constants()
timer = Timer()
timer.optimizeFlips(FRAME_RATE, const)

sub_dirs = sorted(glob(join(data_dir, 'sub-*')))
for sub_dir in sub_dirs:
    sub = basename(sub_dir)
    print_info(f'Reading EEG data for {sub}..')


    deriv_dir = join(deriv_dir_root, sub)
    os.makedirs(deriv_dir, exist_ok=True)
    annots_fpath = join(deriv_dir, f'{sub}_annotations.txt')

    ## load raw data 
    eeg_dir = join(data_dir, sub, 'eeg')
    raw_fpath = join(eeg_dir, f'{sub}_task-ab_eeg.bdf')
    raw = read_raw_bdf(raw_fpath)

    chans_df = read_channels(data_dir, sub)

    ## mark channel types
    misc_channels = chans_df[chans_df.type == 'MISC']['name'].to_list()
    raw: RawEDF = raw.drop_channels(misc_channels) # type: ignore
    eog_channels = chans_df[chans_df.description.str.contains('EOG')]['name'].to_list()
    raw.set_channel_types(mapping=dict([(c, 'eog') for c in eog_channels]))

    ## mark bad channels
    bad_chans = chans_df[chans_df.status == 'bad']['name'].to_list()
    raw.info['bads'].extend(bad_chans)

    ## remove the mastoids
    refs_chans = chans_df[chans_df.type == 'REF']['name'].to_list()
    raw = raw.drop_channels(refs_chans) # type: ignore

    ## find triggers
    mask = sum([2**i for i in (8,9,10,11,12,13,14,15,16)])
    events = mne.find_events(
        raw,
        verbose=False,
        mask=mask,
        mask_type='not_and'
    )

    ## triggers for T2 (experiment + training)
    t2_triggers = list(range(24, 31+1)) + list(range(40, 47+1))

    ## index for full events array where event is T2
    events_mask =[e[2] in t2_triggers for e in events ]

    ## The rejections are trial-wise. So we only need one epoch per trial
    ## on which to apply the thresholds. Let's use the T2 events. 
    events_selected = events[events_mask]

    ## T2 epoching
    soa = timer.flipsToSecs(timer.short_SOA)
    buffer = timer.flipsToSecs(timer.target_dur)
    tmin = - (soa + BASELINE + buffer) + LATENCY


    epochs = mne.Epochs(
        raw,
        events,
        event_id=t2_triggers, ## selected triggers for epochs
        tmin=tmin,
        tmax=TMAX+LATENCY,
        baseline=(tmin, tmin+BASELINE),
        on_missing='warn',
    )


    ## trial rejection
    """
    We rejected voltage exceeding ±200 uV,
    transients exceeding ±100 uV, 
    or electrooculogram activity exceeding ±70 mV.
    """
    THRESH_TRANS = 100
    THRESH_PEAK = 200
    THRESH_EOG = 70

    eeg = epochs.get_data('eeg', units='uV') # trials x channels x time
    eog_dual = epochs.get_data('eog', units='uV') # trials x channels x time
    direction_mask = numpy.array([True, False, True, False])
    eog = eog_dual[:, direction_mask, :] - eog_dual[:, ~direction_mask, :]
    n_epochs = eeg.shape[0]
    n_eog_rejects = 0
    bad_epochs = []
    counts = dict(trans=0, peak=0, eog=0)
    descriptions = []
    for e in range(n_epochs):
        transients = numpy.abs(numpy.diff(eeg[e, :, :]))
        if numpy.any(transients > THRESH_TRANS):
            bad_epochs.append(e)
            descriptions.append('bad transient')
            counts['trans'] += 1
            continue

        eeg_epoch = eeg[e, :, :].T
        eeg_peaks = eeg_epoch - eeg_epoch.mean(axis=0)
        if numpy.any(numpy.abs(eeg_peaks) > THRESH_PEAK):
            bad_epochs.append(e)
            descriptions.append('bad peak')
            counts['peak'] += 1
            continue

        eog_epoch = eog[e, :, :].T
        eog_peaks = eog_epoch - eog_epoch.mean(axis=0)
        if numpy.any(numpy.abs(eog_peaks) > THRESH_EOG):
            bad_epochs.append(e)
            descriptions.append('bad blink')
            counts['eog'] += 1
            continue

    print_info(f'Total trials {n_epochs}')
    for reason, count in counts.items():
        print_info(f'Rejected {count} trials as [{reason}]')

    ## comvert the above to annotations
    event_onsets = events_selected[bad_epochs, 0] / raw.info['sfreq']
    onsets = event_onsets + tmin # tmin is negative
    durations = [-tmin+TMAX] * len(event_onsets)
    annots = mne.Annotations(
        onsets, durations, descriptions, orig_time=raw.info['meas_date']
    )
    annots.save(annots_fpath, overwrite=True)
    print_info(f'Stored annotations at {annots_fpath}')
