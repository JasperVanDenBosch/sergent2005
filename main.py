'''
TODO:
- backup parameters on run
- ensure psychopy is logging draws as backup
- script to summarize divergence from timing
- ITI 3-4s Fixation cross off then on  --> this is on top of t1 slow/ quick
- some "empty room" recording 
- calculate correct column # correct = True if ratingT1[0] in self.t1 else False # ratingT1 is tuple of rating, RT
- cols for evts
- optimize flip count based on refresh rate (print while logging)
- ITI 3-4s Fixation cross off then on -  where did this come from - add this to T1 delay
- get refresh rate https://psychopy.org/api/info.html
'''
from os.path import expanduser, join
from datetime import datetime
from os import makedirs
import random
from experiment.constants import Constants
from experiment.trials import generateTrials
#from experiment.engine import PsychopyEngine
from experiment.fake_engine import FakeEngine
from experiment.labs import getLabConfiguration
CONSTANTS  = Constants()  # load fixed parameters wrt timing, sizing etc

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
# full file path to events (structured) and log (unstructured) output 
evt_fpath = join(data_dir, f'sub-{sub}_run-{dt_str}_events.tsv')
log_fpath = join(data_dir, f'sub-{sub}_run-{dt_str}_log.txt')

# this object represents drawing and interactions via psychopy
engine = PsychopyEngine()
#engine = FakeEngine()

## set log levels and log file location
engine.configureLog(log_fpath)

## setup psychopy monitor and window objects
engine.configureWindow(config)

## setup serial port or other trigger port
engine.connectTriggerInterface(**config)

## stimuli
engine.loadStimuli(
    squareSize=CONSTANTS.square_size,
    squareOffset=CONSTANTS.target2_square_offset,
    fixSize=CONSTANTS.fix_cross_arm_len,
)

# Welcome the participant
engine.showMessage(CONSTANTS.welcome_message, CONSTANTS.LARGE_FONT)
engine.showMessage(CONSTANTS.instructions)

## before experiment
engine.showMessage(CONSTANTS.training_instructions)

## counterbalance task type based on the participant index being odd or even
blocks = ('dual', 'single') if (pidx % 2) == 0 else ('single', 'dual')

for phase in ('train', 'test'):
    # engine.showMessage('TRAINING STARTS', LARGE_FONT, wait=False)

    for block in blocks:
        trials = generateTrials(phase, block, CONSTANTS)
        random.shuffle(trials)

        if block == 'dual':
            engine.showMessage(CONSTANTS.dual_block_start)
        else:
            engine.showMessage(CONSTANTS.single_block_start)

        for trial in trials:
            trial.run(engine)

    if phase == 'train':
        engine.showMessage(CONSTANTS.finished_training)

engine.showMessage(CONSTANTS.thank_you, confirm=False)
engine.stop()