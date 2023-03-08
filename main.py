'''

TODO:
- backup parameters
- counterbalanced single/dual block order
- i18n
- ensure psychopy is logging draws as backup
- computeStimulusList has fewer trials for training (n_training_trial_divisor)
- computeStimulusList decide t1 slow or fast
Counterbalance by pid
- ITI 3-4s Fixation cross off then on
- integrate ports with engine
'''
from os.path import expanduser, join
from os import makedirs
from experiment.parameters import *
from experiment.trials import computeStimulusList
from experiment.ports import openTriggerPort
from experiment.engine import PsychopyEngine
from experiment.labs import getLabConfiguration
from experiment.window import configureWindow
from functions import start_trial
from unittest.mock import Mock
import random

## User input
pid = int(input('Type in participant ID number: '))
chosen_settings = getLabConfiguration()

# create folder for data and error logging
data_dir = expanduser(f'~/data/{experiment_name}/{pid:03}')
makedirs(data_dir, exist_ok=True)

# sub-01_TS

log_fpath = join('logging', f'subject{participantID}.log')
#logFile = logging.LogFile(log_fpath, level=logging.EXP)
#logging.console.setLevel(logging.INFO)



SCREEN, scale = configureWindow(chosen_settings)

# port = openTriggerPort(
#     typ=chosen_settings['port_type'],
#     address=chosen_settings['port_address'],
#     rate=chosen_settings['port_baudrate'],
#     win=SCREEN,
#     scale=scale,
#     viewPixBulbSize=7
# )
port = Mock()

# this object represents interactions with psychopy, ie for the actual drawing 
# and interactions
engine = PsychopyEngine()

## stimuli
target1 = engine.createTextStim(height=string_height)# , units='deg'
target2 = engine.createTextStim(height=string_height)
target2_square1 = engine.createRect(size=(square_size, square_size), target2_square1_pos=(-5,-5))
target2_square2 = engine.createRect(size=(square_size, square_size), target2_square2_pos=(5,-5))
target2_square3 = engine.createRect(size=(square_size, square_size), target2_square3_pos=(-5,5))
target2_square4 = engine.createRect(size=(square_size, square_size), target2_square4_pos=(5,5))
mask = engine.createTextStim(text='INIT', height=string_height)

# Welcome the participant
engine.showMessage(welcome_message, LARGE_FONT)
engine.showMessage(instructions)

## before experiment
engine.showMessage(training_instructions)

for phase in ('train', 'test'):
    # engine.showMessage('TRAINING STARTS', LARGE_FONT, wait=False)

    for block in ('single', 'dual'):
        [trials, _] = computeStimulusList(
            phase=='train', # training
            block=='dual',
            n_trials_single,
            n_trials_dual_critical,
            n_trials_dual_easy
        )
        random.shuffle(trials)
        if block=='dual':
            engine.showMessage(dual_block_start)
        else:
            engine.showMessage(single_block_start)

        for currentTrial in trials:
            # 50% chance that T1 is presented quick or slow after trial start
            T1_start = start_T1_slow if currentTrial['slow_T1']=='long' else start_T1_quick
            duration_SOA = long_SOA if currentTrial['SOA']=='long' else short_SOA
            target2_presence = True if currentTrial['T2_presence']=='present' else False
            print('Current trial: ', currentTrial['Name'])
            ratingT2, ratingT1, stimulusT2, stimulusT1 = start_trial(
                currentTrial['task'],
                T1_start,
                target2_presence,
                duration_SOA, 
                None, #p
            )
            # save information in the csv-file
            # block.addData('ratingT2', ratingT2[0])
            # block.addData('RTtaskT2', ratingT2[1])
            # block.addData('ratingT1', ratingT1[0])
            # block.addData('RTtaskT1', ratingT1[1])
            # block.addData('ACCtaskT1', ratingT1[2])
            # block.addData('startingT1', T1_start)
            # block.addData('stimulusT1', stimulusT1)
            # block.addData('stimulusT2', stimulusT2)

    print(f'{phase} done!')
    engine.showMessage(finished_training) # TODO phase

engine.showMessage(thank_you, wait=False)
