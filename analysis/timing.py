from os.path import join, expanduser, basename
from glob import glob
from utils import read_events, print_warn, print_info
from pandas import DataFrame
from experiment.timer import Timer
from experiment.constants import Constants
from config import FRAME_RATE, DATA_DIR, DERIV_NAME
import matplotlib.pyplot as plt
import seaborn


print_info(f'## Evaluate timing')

timer = Timer()
const = Constants()
timer.optimizeFlips(FRAME_RATE, const)

SHORT_ORIG = 258
LONG_ORIG = 688
short_target = timer.flipsToSecs(const.short_SOA)*1000
long_target = timer.flipsToSecs(const.long_SOA)*1000

data_dir = expanduser(DATA_DIR)
sub_dirs = sorted(glob(join(data_dir, 'sub-*')))

trials = []
for sub_dir in sub_dirs:
    sub = basename(sub_dir)
    print_info(f'Reading events for {sub}..')

    df = read_events(data_dir, sub)
    for t in df.trial_index.unique():
        trial_events = df[df.trial_index == t]
        try:
            t1_event = trial_events[trial_events.trial_type == 't1'].iloc[0]
            t2_event = trial_events[trial_events.trial_type == 't2'].iloc[0]
        except IndexError:
            print_warn(f'Trial missing target: {sub} [{t}]')
            continue
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


## Seaborn box plot with entry per subject
plt.figure()
ax = seaborn.boxplot(data=trials_df, y='sub', x='ms', hue='soa')
ax.set(
    title='Timing: SOA (ms) per subject',
    ylabel='Subject',
    xlabel='SOA (ms)'
)

# Add vertical reference lines at target values
ax.axvline(x=SHORT_ORIG, color='blue', linestyle='--', linewidth=1, alpha=0.7)
ax.text(SHORT_ORIG, ax.get_ylim()[1], 'short_orig', va='bottom', ha='center', fontsize=9, color='blue', rotation=90)

ax.axvline(x=LONG_ORIG, color='red', linestyle='--', linewidth=1, alpha=0.7)
ax.text(LONG_ORIG, ax.get_ylim()[1], 'long_orig', va='bottom', ha='center', fontsize=9, color='red', rotation=90)

ax.axvline(x=short_target, color='cyan', linestyle=':', linewidth=1, alpha=0.7)
ax.text(short_target, ax.get_ylim()[1], 'short_target', va='bottom', ha='center', fontsize=9, color='cyan', rotation=90)

ax.axvline(x=long_target, color='orange', linestyle=':', linewidth=1, alpha=0.7)
ax.text(long_target, ax.get_ylim()[1], 'long_target', va='bottom', ha='center', fontsize=9, color='orange', rotation=90)

plt.tight_layout()
plt.savefig(join(data_dir, 'derivatives', DERIV_NAME, 'timing_soa.png'))
plt.close()
