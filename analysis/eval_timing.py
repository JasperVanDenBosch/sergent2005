from os.path import join, expanduser, basename
from glob import glob
from utils import read_events
from pandas import DataFrame
from experiment.timer import Timer
from experiment.constants import Constants
from config import FRAME_RATE, DATA_DIR

timer = Timer()
const = Constants()
timer.optimizeFlips(FRAME_RATE, const)

data_dir = expanduser(DATA_DIR)
sub_dirs = sorted(glob(join(data_dir, 'sub-*')))

trials = []
for sub_dir in sub_dirs:
    sub = basename(sub_dir)

    df = read_events(data_dir, sub)
    for t in df.trial_index.unique():
        trial_events = df[df.trial_index == 1]
        t1_event = trial_events[trial_events.trial_type == 't1'].iloc[0]
        t2_event = trial_events[trial_events.trial_type == 't2'].iloc[0]
        t1_onset = t1_event.onset
        t2_onset = t2_event.onset
        trials.append(
            dict(
                sub=sub,
                soa='long' if t2_event.soa_long else 'short',
                ms=(t2_onset-t1_onset)*1000
            )
        )


trials_df = DataFrame(trials)
# planned_ms = timer.flipsToSecs(planned_flips)*1000



# ## Seaborn box plot with entry per subject
# plt.figure()
# ax = seaborn.histplot(observed_soas, bins=41)
# ax.set(
#     title='Timing: Short SOA (ms) based on reported flip time',
#     xlabel='+/- ms from mean',
#     ylabel='Percent of trials'
# )
# ax.get_figure().savefig('plots/soa_variability.png')
# plt.close()