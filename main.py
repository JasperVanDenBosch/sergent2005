"""This is the main script to run the experiment
"""
from os.path import expanduser, join
from datetime import datetime
from os import makedirs
from math import isclose
import platform
from pandas import DataFrame
from experiment.constants import Constants
from experiment.timer import Timer
from experiment.trials import TrialGenerator
from experiment.engine import PsychopyEngine
from experiment.labs import getLabConfiguration
const = Constants()  # load fixed parameters wrt timing, sizing etc


## this object represents drawing and interactions via psychopy
engine = PsychopyEngine()

## user input
config = getLabConfiguration()
SITE = config['site']['abbreviation']
pidx = int(engine.askForString('Participant ID number: '))
sub = f'{SITE}{pidx:03}' # the subject ID is a combination of lab ID + subject index

## data directory and file paths
data_dir = expanduser(f'~/data/EMLsergent2005/sub-{sub}')
makedirs(data_dir, exist_ok=True) # ensure data directory exists
# current date+time to seconds, helps to generate unique files, prevent overwriting
dt_str = datetime.now().strftime(f'%Y%m%d%H%M%S')
# full file path to trials (structured) and log (unstructured) output 
trials_fpath = join(data_dir, f'sub-{sub}_run-{dt_str}_trials.csv')
log_fpath = join(data_dir, f'sub-{sub}_run-{dt_str}_log.txt')

## set log levels and log file location
engine.configureLog(log_fpath)

## setup psychopy monitor and window objects
engine.configureWindow(config)

## record some basic info
engine.logDictionary('SESSION', dict(
    participant_index=pidx,
    date_str=dt_str))
engine.logDictionary('PLATFORM', platform.uname()._asdict())
engine.logDictionary('SITE_CONFIG', config)
performance = engine.measureHardwarePerformance()
engine.logDictionary('PERFORMANCE', performance)
fr_conf = config['monitor']['refresh_rate']
fr_meas = 1000/performance['windowRefreshTimeAvg_ms']
msg = f'Configured ({fr_conf}) and measured ({fr_meas}) refresh rate differ by more than 1Hz'
assert isclose(fr_conf, fr_meas, abs_tol=2), msg

## setup serial port or other trigger port
engine.connectTriggerInterface(config['triggers'])

## stimuli
engine.loadStimuli(
    squareSize=const.square_size,
    squareOffset=const.target2_square_offset,
    fixSize=const.fix_cross_arm_len,
)

# Welcome the participant
engine.showMessage(const.welcome_message, const.LARGE_FONT)
engine.showMessage(const.instructions)
engine.showMessage(const.task_vis_instruct)



## counterbalance task type based on the participant index being odd or even
blocks = ('dual', 'single') if (pidx % 2) == 0 else ('single', 'dual')

timer = Timer()
timer.optimizeFlips(fr_conf, const)
trials = TrialGenerator(timer, const)

## before experiment
engine.showMessage(const.training_instructions)

for phase, block in zip(('train', 'test'), blocks):

    block_trials = trials.generate(phase, block)

    engine.showMessage(
        const.dual_block_start if block == 'dual' else const.single_block_start
    )

    for trial in block_trials:
        trial.run(engine, timer)
        if engine.exitRequested():
            break ## exit trial loop

    if engine.exitRequested():
        break ## exit phase/block loop

    if phase == 'train':
        engine.showMessage(const.finished_training)

## Create table from trials and save to csv file
df = DataFrame([t.todict() for t in trials.all])
df.to_csv(trials_fpath, float_format='%.4f')

if not engine.exitRequested():
    engine.showMessage(const.thank_you, confirm=False)
engine.stop()
