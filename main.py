'''
TODO:
- ensure psychopy is logging draws as backup
- ITI 3-4s Fixation cross off then on -  where did this come from - add this to T1 delay
- identity RT needs to be sum if redrawing scale (middle button)
- check meas fliprate vs configured
'''
from os.path import expanduser, join
from datetime import datetime
from os import makedirs
import random, platform
from pandas import DataFrame
from experiment.constants import Constants
from experiment.timer import Timer
from experiment.trials import TrialGenerator
#from experiment.engine import PsychopyEngine
from experiment.fake_engine import FakeEngine
from experiment.labs import getLabConfiguration
const = Constants()  # load fixed parameters wrt timing, sizing etc

## user input
config = getLabConfiguration()
SITE = config['site']['abbreviation']
pidx = int(input('Type in participant ID number: '))
sub = f'{SITE}{pidx:03}' # the subject ID is a combination of lab ID + subject index

## data directory and file paths
data_dir = expanduser(f'~/data/EMLsergent2005/sub-{sub}')
makedirs(data_dir, exist_ok=True) # ensure data directory exists
# current date+time to seconds, helps to generate unique files, prevent overwriting
dt_str = datetime.now().strftime(f'%Y%m%d%H%M%S')
# full file path to trials (structured) and log (unstructured) output 
trials_fpath = join(data_dir, f'sub-{sub}_run-{dt_str}_trials.csv')
log_fpath = join(data_dir, f'sub-{sub}_run-{dt_str}_log.txt')

# this object represents drawing and interactions via psychopy
#engine = PsychopyEngine()
engine = FakeEngine()

## set log levels and log file location
engine.configureLog(log_fpath)

## record some basic info
engine.logDictionary('SESSION', dict(
    participant_index=pidx,
    date_str=dt_str))
engine.logDictionary('PLATFORM', platform.uname()._asdict())
engine.logDictionary('SITE_CONFIG', config)
performance = engine.measureHardwarePerformance()
engine.logDictionary('PERFORMANCE', performance)

## setup psychopy monitor and window objects
engine.configureWindow(config)

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

## before experiment
engine.showMessage(const.training_instructions)

## counterbalance task type based on the participant index being odd or even
blocks = ('dual', 'single') if (pidx % 2) == 0 else ('single', 'dual')

timer = Timer()
timer.optimizeFlips(99999.9, const)
trials = TrialGenerator(timer, const)
for phase in ('train', 'test'):
    # engine.showMessage('TRAINING STARTS', LARGE_FONT, wait=False) # TODO

    for block in blocks:
        block_trials = trials.generate(phase, block)

        if block == 'dual':
            engine.showMessage(const.dual_block_start)
        else:
            engine.showMessage(const.single_block_start)

        for trial in block_trials:
            trial.run(engine, timer)

    if phase == 'train':
        engine.showMessage(const.finished_training)

## Create table from trials and save to csv file
df = DataFrame([t.todict() for t in trials.all])
df.to_csv(trials_fpath, float_format='%.4f')

engine.showMessage(const.thank_you, confirm=False)
engine.stop()