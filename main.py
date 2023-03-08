'''

TODO:
- refactor start_trial
- refactor computeStimulusList
- backup parameters
- counterbalanced single/dual block order
- i18n
- ensure psychopy is logging draws as backup
- computeStimulusList has fewer trials for training (n_training_trial_divisor)
- computeStimulusList decide t1 slow or fast
- store site in config file instead
Counterbalance by pid
- ITI 3-4s Fixation cross off then on
- integrate ports with engine
- squares as list
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
from functions import start_trial
from unittest.mock import Mock
import random
from typing import TYPE_CHECKING, Union, Literal
if TYPE_CHECKING:
    from experiment.trial import Trial
CONSTANTS  = Constants()

## user input
SITE = 'TST'
pidx = int(input('Type in participant ID number: '))
sub = f'{SITE}{pidx:03}'
chosen_settings = getLabConfiguration() # maybe get from config file instead

## data directory and file paths
data_dir = expanduser(f'~/data/{CONSTANTS.experiment_name}/sub-{sub}')
makedirs(data_dir, exist_ok=True)
dt_str = datetime.now().strftime(f'%y%m%d%H%M%S')
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
target1 = engine.createTextStim('UNSET_TARGET1')
target2 = engine.createTextStim('UNSET_TARGET2')
square_size = (CONSTANTS.square_size, CONSTANTS.square_size)
target2_square1 = engine.createRect(size=square_size, pos=CONSTANTS.target2_square1_pos)
target2_square2 = engine.createRect(size=square_size, pos=CONSTANTS.target2_square2_pos)
target2_square3 = engine.createRect(size=square_size, pos=CONSTANTS.target2_square3_pos)
target2_square4 = engine.createRect(size=square_size, pos=CONSTANTS.target2_square4_pos)
mask = engine.createTextStim('UNSET_MASK')

# Welcome the participant
engine.showMessage(CONSTANTS.welcome_message, CONSTANTS.LARGE_FONT)
engine.showMessage(CONSTANTS.instructions)

## before experiment
engine.showMessage(CONSTANTS.training_instructions)

for phase in ('train', 'test'):
    # engine.showMessage('TRAINING STARTS', LARGE_FONT, wait=False)

    for block in ('single', 'dual'):
        trials = generateTrials(phase, block, CONSTANTS)
        random.shuffle(trials)

        if block == 'dual':
            engine.showMessage(CONSTANTS.dual_block_start)
        else:
            engine.showMessage(CONSTANTS.single_block_start)

        for trial in trials:
            # # 50% chance that T1 is presented quick or slow after trial start
            # T1_start = CONSTANTS.start_T1_slow if currentTrial['slow_T1']=='long' else CONSTANTS.start_T1_quick
            # duration_SOA = CONSTANTS.long_SOA if currentTrial['SOA']=='long' else CONSTANTS.short_SOA
            # print('Current trial: ', currentTrial['Name'])
            # ratingT2, ratingT1, stimulusT2, stimulusT1 = start_trial(
            #     dualTask=currentTrial['task']=='dual',
            #     timing_T1_start=T1_start,
            #     t2Present=currentTrial['T2_presence']=='present',
            #     longSOA=currentTrial['SOA']=='long',
            #     port=engine.port,
            # )
            trial.run(engine)

    print(f'{phase} done!')
    engine.showMessage(CONSTANTS.finished_training) # TODO phase

engine.showMessage(CONSTANTS.thank_you, wait=False)
