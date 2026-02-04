"""Automated artifect rejection pre-process 

"""
from __future__ import annotations
from os.path import join, expanduser, isfile, basename
import os
from glob import glob
from mne.io import read_raw_bdf
from mne.channels import make_standard_montage
import mne
from mne.preprocessing import ICA
from autoreject import AutoReject
from mne_icalabel import label_components
from experiment.triggers import Triggers
from experiment.timer import Timer
from experiment.constants import Constants
from utils import read_events, read_channels, print_info
from config import (DATA_DIR, DERIV_NAME, FRAME_RATE,
                    BASELINE, TMAX, LATENCY, N_JOBS, N_INTERPOLATE)


data_dir = expanduser(DATA_DIR)
deriv_dir_root = join(data_dir, 'derivatives', DERIV_NAME)

MODE_NAME = 'auto'

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
        baseline=None,
        on_missing='warn',
        preload=True
    )


    n_channels = len(epochs.copy().pick(['eeg'], exclude='bads').ch_names)
    n_ics = n_channels - 1
    ## Pre-ICA AutoReject
    ar = AutoReject(n_jobs=N_JOBS, n_interpolate=N_INTERPOLATE, verbose=False)
    ar.fit(epochs)
    _, reject_log = ar.transform(epochs.copy(), return_log=True)
    ica_epoch_selection = ~reject_log.bad_epochs

    ## Display overview of rejected and/or interpolated channels/segments
    fig = reject_log.plot('horizontal', show=False)
    fig.suptitle('Reject Log before ICA')
    report.savefig(fig)
    plt.close()

    ## step 2 ICA without bad epochs
    ica = ICA(n_ics, method='infomax', fit_params=dict(extended=True)) 
    ica.fit(epochs[ica_epoch_selection])

    ## Use the IClabel library to identify artifact components
    ic_labels = label_components(raw, ica, method='iclabel')

    artifact_ic_idx = [i for i, label in enumerate(ic_labels['labels']) if label not in ('brain', 'other')]

    ## plot artifact ICs
    if len(artifact_ic_idx):
        figs = ica.plot_properties(raw, picks=artifact_ic_idx, show=False)
        for f, fig in enumerate(figs):
            label = ic_labels['labels'][artifact_ic_idx[f]]
            fig.suptitle(f'Properties of IC {f}: ({label})')
            report.savefig(fig)
            plt.close()

    ## demix artifacts
    meta['n_bad_ics'] = len(artifact_ic_idx)
    ica.exclude = artifact_ic_idx
    ica.apply(epochs, exclude=ica.exclude)

    ## step 3 apply autoreject
    ar = AutoReject(n_jobs=N_JOBS, n_interpolate=N_INTERPOLATE, verbose=False)
    ar.fit(epochs)
    epochs, reject_log = ar.transform(epochs, return_log=True)

    meta['n_bad_epochs'] = (reject_log.labels == 1).sum().item()
    meta['n_interp_epochs'] = (reject_log.labels == 2).sum().item()
    
    ## Display overview of rejected and/or interpolated channels/segments
    fig = reject_log.plot('horizontal', show=False)
    fig.suptitle(f'Reject log after ICA')
    report.savefig(fig)
    plt.close()

    ## apply baseline
    epochs.apply_baseline()


    ## Read the raw data events
    events_df = read_events(data_dir, sub)

    ## Make subset of events based on selected triggers and 
    ## non-rejected epochs (indices with regard to full MNE events array)
    events_df = events_df.iloc[epochs.selection]

    ## Check that they match (10 is an arbitrary index)
    assert len(events_df) == len(epochs)
    assert events_df.iloc[10].value == epochs.events[10, 2]

    ## Store alongside epochs
    events_fpath = join(deriv_dir, f'{sub}_mode-{MODE_NAME}_events.tsv')
    events_df.to_csv(events_fpath, sep='\t', index=False, float_format = '%.12g')

    print_info(f'Epoched {len(epochs)} trials')
    epochs.save(join(deriv_dir, f'{sub}_mode-{MODE_NAME}_epo.fif'), overwrite=True)
