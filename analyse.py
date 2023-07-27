"""Analysis of pilot data

## Pilot idiosyncrasies
- [('train', 'single'), ('test', 'dual')] 
- no bad channels

## TODO

- vis rating 0 becomes -999
- plot actual and designed duration of T1 / T2 / SOA
- visibility plots as figure 1B
- performance on ID by condition
- performance on ID by visibility
- discard incorrect trials (how many)
- discard false positive trials (how many)
- baseline 250ms



Issue A baseline

We can sample baseline before -SOA from T2. 
Now if we want to sample the same baseline regardless of SOA,
the baseline would start before the "T1 delay"  /fixation cross comes on, 
if the T1 delay is short and SOA is too. (since delay-short < (SOA-diff+baseline))
If we sample the baseline differently based on SOA, 
we may pick up on a different readiness phase.
(I will pick this solution for now.)



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


"""
from __future__ import annotations
from typing import TYPE_CHECKING
from os.path import join, expanduser
import glob, os
from mne.io import read_raw_bdf
from mne.channels import make_standard_montage
import mne
from experiment.triggers import Triggers
from experiment.timer import Timer
from experiment.constants import Constants
if TYPE_CHECKING:
    from mne.io.edf.edf import RawEDF


BASELINE = 0.250 ## duration of baseline
BUFFER = 0.05 ## take into account timing inprecision
fr_conf  = 114 ## TODO double check
REJECT_CRIT = dict(eeg=200e-6, eog=70e-6) # 200 µV, 70 µV
TMAX = 0.700

timer = Timer()
timer.optimizeFlips(fr_conf, Constants())

data_dir = expanduser('~/data/EMLsergent2005/')
sub = 'sub-UOBC001'
eeg_dir = join(data_dir, sub)
deriv_dir = join(data_dir, 'derivatives', 'mne', sub)
raw_fpath = join(eeg_dir, f'{sub}_eeg.bdf')

os.makedirs(deriv_dir, exist_ok=True)

## load raw data 
raw = read_raw_bdf(raw_fpath)

## get rid of empty channels and mark channel types
raw: RawEDF = raw.drop_channels(['EXG7', 'EXG8']) # type: ignore
eog_channels = ['EXG3', 'EXG4', 'EXG5', 'EXG6']
raw.set_channel_types(mapping=dict([(c, 'eog') for c in eog_channels]))

## pick channels to be filtered
filter_picks = mne.pick_types(raw.info, eeg=True, eog=True, stim=False)
raw.load_data()
raw = raw.filter(l_freq=0.5, h_freq=20, picks=filter_picks)

## reference to average of mastoids
mastoid_channels = ['EXG1', 'EXG2'] # best for biosemi, but methods plans to use average
raw.set_eeg_reference(ref_channels=mastoid_channels)
raw: RawEDF = raw.drop_channels(mastoid_channels) # type: ignore

## determine electrode head locations
montage = make_standard_montage('biosemi128', head_size='auto')
raw.set_montage(montage, on_missing='warn')

## find triggers
events = mne.find_events(raw, mask=2**17 -256, mask_type='not_and', consecutive=True)

## T2 epoching
all_T2_epochs = dict()
for soaName, longSOA in [('short', False), ('long', True)]:
    if longSOA:
        soa = timer.flipsToSecs(timer.long_SOA)
    else:
        soa = timer.flipsToSecs(timer.short_SOA)
    tmin = - (soa + BASELINE + BUFFER)
    event_ids = dict()
    for presenceName, presence in [('absent', False), ('present', True)]:
        event_ids[f'{soaName}SOA_{presenceName}'] = Triggers().get_number(
            training=False,
            forT2=True,
            dualTask=True,
            longSOA=longSOA,
            t2Present=presence,
        )
    epochs = mne.Epochs(
        raw,
        events,
        event_id=event_ids, ## selected triggers for epochs
        tmin=tmin,
        tmax=TMAX,
        baseline=(tmin, tmin+BASELINE),
        decim=4, ## downsample x4
        #reject=REJECT_CRIT,
        on_missing='warn',
    )
    epo_name = f'T2-{soaName}SOA'
    all_T2_epochs[epo_name] = epochs
    epochs.save(join(deriv_dir, f'{sub}_{epo_name}_epo.fif'), overwrite=True)


# ## plot power spectrum from 10mins to 30mins after start
# raw.plot_psd(picks=filter_picks, fmax=30, tmin=60*10, tmax=60*30)



# ## plot evoked response
# evoked = epochs.average()
# evoked.plot_joint(picks='eeg')


