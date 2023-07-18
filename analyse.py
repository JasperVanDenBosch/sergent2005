"""Analysis of pilot data

EX1: left mastoid
EX2: right mastoid
EX3: bottom VEOG
EX4: top VEOG
EX5: left HEOG
EX6: right HEOG

trigger offset:
Decimal: 65280 Binary: 1111111100000000

In order to analyze the brain events underlying this bimodal distribu- tion, 
we compared the ERPs evoked by T2 during the attentional blink (short SOA, dual task) 
when T2 was seen and when it was not seen (empirically defined as visibility Z or o50%). 
Because T1 and the masks also evoked ERPs, we extracted the potentials specifically 
evoked by T2 by subtracting the ERPs evoked when T2 was absent and replaced by a blank screen 


 The remaining trials were averaged in synchrony with T2 onset (or T1 onset for T1-evoked ERPs),
   digitally transformed to an average reference, band-pass filtered (0.5-20 Hz)
   and corrected for baseline over a 250-ms window during fixation at the beginning of the trial.
"""

from os.path import join, expanduser
import glob, os
from mne.io import read_raw_bdf
from mne.channels import make_standard_montage
import mne
from experiment.triggers import Triggers

data_dir = expanduser('~/data/EMLsergent2005/')
sub = 'sub-UOBC001'
eeg_dir = join(data_dir, sub)
deriv_dir = join(data_dir, 'derivatives', 'mne', sub)
raw_fpaths = glob.glob(join(eeg_dir, '*.bdf'))
assert len(raw_fpaths) == 1

os.makedirs(deriv_dir, exist_ok=True)


## load raw data 
raw = read_raw_bdf(raw_fpaths[0])

## get rid of empty channels and mark channel types
unused_channels = ['GSR1', 'GSR2', 'Erg1', 'Erg2', 'Resp', 'Plet', 'Temp',
    'EXG7', 'EXG8']
raw = raw.drop_channels(unused_channels)
eog_channels = ['EXG3', 'EXG4', 'EXG5', 'EXG6']
raw.set_channel_types(mapping=dict([(c, 'eog') for c in eog_channels]))

## Bad channels and segments
raw.info['bads'] = ['A25', 'A26'] 

## pick channels to be filtered
filter_picks = mne.pick_types(raw.info, eeg=True, eog=True, stim=False)
raw.load_data()
raw = raw.filter(l_freq=0.5, h_freq=20, picks=filter_picks)

## reference to average of mastoids
mastoid_channels = ['EXG1', 'EXG2'] # best for biosemi, but methods plans to use average
raw.set_eeg_reference(ref_channels=mastoid_channels)

## find triggers
events = mne.find_events(raw)
# events = mne.find_events(raw, mask=65280, mask_type='not_and')
events[:, 2] = events[:, 2]-65280

# trigger definition (only epoch the T1 and T2 triggers)
event_ids = dict([(k, v) for (k, v) in Triggers().asdict().items() if v > 12])

## epoching
reject_criteria = dict(eeg=200e-6, eog=70e-6) # 200 µV, 70 µV
epochs = mne.Epochs(
    raw,
    events,
    event_id=event_ids, ## selected triggers for epochs
    tmin=-0.250,
    tmax=0.750,
    decim=4, ## downsample x4
    reject=reject_criteria,
    on_missing='warn',
)
epochs.save(join(deriv_dir, f'{sub}_epo.fif'), overwrite=True)


# ## plot power spectrum from 10mins to 30mins after start
# raw.plot_psd(picks=filter_picks, fmax=30, tmin=60*10, tmax=60*30)

# ## plot evoked response
# evoked = epochs.average()
# evoked.plot_joint(picks='eeg')

# ## determine electrode head locations
# montage = make_standard_montage('biosemi128', head_size='auto')
# raw.set_montage(montage)
