'''

TODO:
- backup parameters on run
- counterbalanced single/dual block order
- i18n
- ensure psychopy is logging draws as backup
- store site in config file instead
- Counterbalance by pid + SITE: counterbalance the task order (single/dual): 
- ITI 3-4s Fixation cross off then on
- integrate ports with engine
- squares as list
- duration simulating engine
- printing engine
- responding engine
- calculate correct column # correct = True if ratingT1[0] in self.t1 else False # ratingT1 is tuple of rating, RT
- cols for evts
    # save information in the csv-file
    # block.addData('ratingT2', ratingT2[0])
    # block.addData('RTtaskT2', ratingT2[1])
    # block.addData('ratingT1', ratingT1[0])
    # block.addData('RTtaskT1', ratingT1[1])
    # block.addData('ACCtaskT1', ratingT1[2])
    # block.addData('startingT1', T1_start)
    # block.addData('stimulusT1', stimulusT1)
    # block.addData('stimulusT2', stimulusT2)
'''
from os.path import expanduser, join
from datetime import datetime
from os import makedirs
from experiment.constants import Constants
from experiment.trials import generateTrials
from experiment.engine import PsychopyEngine
from experiment.labs import getLabConfiguration
from unittest.mock import Mock
import random
from typing import TYPE_CHECKING
CONSTANTS  = Constants()  # load fixed parameters wrt timing, sizing etc

## user input
SITE = 'TST'
pidx = int(input('Type in participant ID number: '))
sub = f'{SITE}{pidx:03}' # the subject ID is a combination of lab ID + subject index
chosen_settings = getLabConfiguration() # maybe get from config file instead

## data directory and file paths
data_dir = expanduser(f'~/data/{CONSTANTS.experiment_name}/sub-{sub}')
makedirs(data_dir, exist_ok=True) # ensure data directory exists
# current date+time to seconds, helps to generate unique files, prevent overwriting
dt_str = datetime.now().strftime(f'%y%m%d%H%M%S')
# full file path to events (structured) and log (unstructured) output 
evt_fpath = join(data_dir, f'sub-{sub}_run-{dt_str}_events.tsv')
log_fpath = join(data_dir, f'sub-{sub}_run-{dt_str}_log.txt')

# this object represents drawing and interactions via psychopy
engine = PsychopyEngine()

## set log levels and log file location
engine.configureLog(log_fpath)

## setup psychopy monitor and window objects
engine.configureWindow(chosen_settings)

## setup serial port or other trigger port
engine.connectTriggerInterface(**chosen_settings)

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

for phase in ('train', 'test'):
    # engine.showMessage('TRAINING STARTS', LARGE_FONT, wait=False)

    for block in ('single', 'dual'):
        trials = generateTrials(phase, block, CONSTANTS)
        random.shuffle(trials) # TODO check if this is good enough, do we worry about conseq reps

        if block == 'dual':
            engine.showMessage(CONSTANTS.dual_block_start)
        else:
            engine.showMessage(CONSTANTS.single_block_start)

        for trial in trials:
            trial.run(engine)

    print(f'{phase} done!')
    engine.showMessage(CONSTANTS.finished_training) # TODO phase

engine.showMessage(CONSTANTS.thank_you, wait=False)
