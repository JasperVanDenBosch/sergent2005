## For UOLM site. TODO: base this on lab config
FRAME_RATE = 60

## local BIDS data directory
DATA_DIR = '~/data/eegmanylabs/sergent2005'

## Name of the derivative directory
DERIV_NAME = 'stage1'

BASELINE = 0.250 ## duration of baseline
TMAX = 0.715
LATENCY = 0.016 ## based on latrec recording


## Regions of Interest
""" 
We use both O1 and O2 as the foci for the bilaterally-distributed N1 component 
(i.e., an ROI covering the 5 closest electrodes to O1 and 5 closest electrodes to O2;
see Figure 2 of the original manuscript) and Pz as the P3b component focus 
(see Figure 5 of original study). 
"""
ROIS = dict(
    Central = ['A4', 'A5', 'A3', 'A17', 'A19', 'A20', 'A21', 'A30', 'A31', 'A32'],
    Occipital = ['A10', 'A14', 'A15', 'A16', 'A23', 'A24', 'A27', 'A28', 'A29', 'B7'],
)

## Time Windows for ERPs
"""Our temporal ROI bounds are 
528ms-624ms for N1
160ms-200ms for P3b 
"""
TIME_WINDOWS = dict(
    Central = (0.160, 0.200),
    Occipital = (0.528, 0.624),
)
