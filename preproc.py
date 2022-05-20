from os.path import join, expanduser
from mne.io import read_raw_bdf
from mne.channels import make_standard_montage
import mne

data_dir = expanduser('~/Data/sergent2005EML/pilot/')
eeg_dir = join(data_dir, 'sub-pilot1', 'eeg')
deriv_dir = join(data_dir, 'derivatives', 'mne', 'sub-pilot1', 'eeg')
fpath = join(eeg_dir, 'sub-pilot1_task-training_raw.bdf')


## load raw data 
raw = read_raw_bdf(fpath) #, preload=True

## get rid of empty channels and mark channel types
unused_channels = ['GSR1', 'GSR2', 'Erg1', 'Erg2', 'Resp', 'Plet', 'Temp',
    'EXG7', 'EXG8']
raw.drop_channels(unused_channels)
eog_channels = ['EXG3', 'EXG4', 'EXG5', 'EXG6']
raw.set_channel_types(mapping=dict([(c, 'eog') for c in eog_channels]))

## Bad channels and segments
## browsing data shows artifacts from t=6263 to t=6264.5 on B26 and B27
## B26 is wobbly for a longer period
raw.info['bads'] = ['B26'] 
annots = mne.Annotations([6263], [1.5], ['artifact'],
    orig_time=raw.info['meas_date'])
raw.set_annotations(annots)

## find triggers
raw.load_data() # (requires ~18GB RAM)
events = mne.find_events(raw)

## downsample from 2048Hz to 512Hz
raw, events = raw.resample(512, events=events)

## reference to average of mastoids
mastoid_channels = ['EXG1', 'EXG2'] # best for biosemi, but methods plans to use average
raw.set_eeg_reference(ref_channels=mastoid_channels)
raw.drop_channels(mastoid_channels)

## determine electrode head locations
montage = make_standard_montage('biosemi128', head_size='auto')
raw.set_montage(montage)

## pick channels to be filtered
filter_picks = mne.pick_types(raw.info, eeg=True, eog=True, stim=False)

## band-pass filter
raw = raw.filter(l_freq=0.5, h_freq=20, picks=filter_picks)

## plot power spectrum from 10mins to 30mins after start
raw.plot_psd(picks=filter_picks, fmax=30, tmin=60*10, tmax=60*30)

## epoching
reject_criteria = dict(eeg=200e-6, eog=70e-6) # 200 µV, 70 µV
epochs = mne.Epochs(
    raw,
    events,
    event_id=dict(t1=10),
    tmin=-0.293,
    tmax=0.715,
    reject=reject_criteria,
    reject_by_annotation=True,
    preload=True
)
epochs.save(join(deriv_dir, 'sub-pilot1_task-training_epo.fif'), overwrite=True)

## plot evoked response
evoked = epochs.average()
evoked.plot_joint(picks='eeg')
