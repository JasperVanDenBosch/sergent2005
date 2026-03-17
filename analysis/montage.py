from os.path import expanduser, join
from config import (DATA_DIR, DERIV_NAME, ROIS)
from mne.channels import make_standard_montage

data_dir = expanduser(DATA_DIR)
deriv_dir_root = join(data_dir, 'derivatives', DERIV_NAME)
montage = make_standard_montage('biosemi64', head_size='auto')

for roi_name, roi_ch_names in ROIS.items():

    fig = montage.plot(
        show_names=roi_ch_names,
        show=False
    )
    fig.savefig(join(deriv_dir_root, f'montage_roi-{roi_name}.png'))