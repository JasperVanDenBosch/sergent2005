'''
This script contains all parameters needed to execute the attentional blink
experiment by running the main.py file located in the same folder.
'''

import os
from os.path import join
import psychopy
from psychopy import visual, core, logging, monitors
from labs import lab_settings
import wx



###########################
# Experimental parameters #
###########################

experiment_name = 'eegmanylabs_sergent2005'
start_T1_quick = 0.514
start_T1_slow = 0.857

short_SOA = 0.257
long_SOA = 0.686
stimulus_duration = 0.043 #in seconds
visibility_scale_timing = 0.500 # after third mask offset

n_trials_single = 160 # only visibility rating task
n_trials_dual_critical = 160 # attentional blink condition!
n_trials_dual_easy = 160 # no intentional blink
# to calculate the number of trials of each condition in the training session,
# each number of test trial will be divided by n_training_trial_divisor
n_training_trial_divisor = 8

####################################################
# Visual features (targets, masks, fixation cross) #
####################################################


# pull resolution from system
app = wx.App(False)
width, height = wx.GetDisplaySize()
print(f'Detected display resolution: {width}x{height}')

## User input
labs_str = ''.join([f'[{l}] ' for l in lab_settings.keys()])
lab_name = input(f'Please select your lab {labs_str}:')
assert lab_name in lab_settings.keys(), 'Unknown lab'
participantID = int(input('Type in participant ID number: '))

chosen_settings = lab_settings[lab_name]
width_cm = chosen_settings['mon_width']
dist_cm = chosen_settings['mon_dist']

# set monitor details
my_monitor = monitors.Monitor(name='my_monitor', distance=dist_cm)
my_monitor.setSizePix((width, height))
my_monitor.setWidth(width_cm)
my_monitor.saveMon()
SCREEN = visual.Window(monitor='my_monitor',
                       color=(-1,-1,-1),
                       fullscr=True,
                       units='deg')
#m = event.Mouse(win=SCREEN)
#m.setVisible(0) # mouse could disturb measurements, thus it is deactivated

# size of stimuli in degrees of visual angle
square_size = 0.5
string_height = 1

target2_strings = ['ZERO', 'FOUR', 'FIVE', 'NINE']
target1_strings = ['OXXO', 'XOOX']
target1 = visual.TextStim(SCREEN, height=string_height, units='deg')
target2 = visual.TextStim(SCREEN, height=string_height, units='deg')
target2_square1 = visual.Rect(SCREEN, size=(square_size, square_size), units='deg', pos=(-5,-5), lineColor=(1, 1, 1), fillColor=(1, 1, 1))
target2_square2 = visual.Rect(SCREEN, size=(square_size, square_size), units='deg', pos=(5,-5), lineColor=(1, 1, 1), fillColor=(1, 1, 1))
target2_square3 = visual.Rect(SCREEN, size=(square_size, square_size), units='deg', pos=(-5,5), lineColor=(1, 1, 1), fillColor=(1, 1, 1))
target2_square4 = visual.Rect(SCREEN, size=(square_size, square_size), units='deg', pos=(5,5), lineColor=(1, 1, 1), fillColor=(1, 1, 1))

# the mask is set of 4 capital letters (randomly generated in function file)
possible_consonants = ['W', 'R', 'Z', 'P', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'C', 'B', 'Y', 'N', 'M']
mask = visual.TextStim(SCREEN, text='INIT', height=string_height)

# the fixation cross
fix_cross_arm_len = 0.4
fix_cross = visual.ShapeStim(
    SCREEN,
    pos=(0.0, 0.0),
    vertices=(
        (0,-fix_cross_arm_len),
        (0,fix_cross_arm_len),
        (0,0),
        (-fix_cross_arm_len,0),
        (fix_cross_arm_len,0)
    ),
    units = 'deg',
    lineWidth = fix_cross_arm_len,
    closeShape = False,
    lineColor = (1, 1, 1)
)


#################
# Trigger codes #
#################

trigger_T1 = 10
trigger_T2_present = 11
trigger_T2_absent = 12
trigger_task1 = 13
trigger_task2 = 14
trigger_start_trial = 15

####################################################
# Data/error logging  and experimental data saving #
####################################################

# create folder for data and error logging
if not os.path.isdir('logging'):
    os.makedirs('logging')
if not os.path.isdir('behavioral_data'):
    os.makedirs('behavioral_data')

FPATH_DATA_TXT = join('behavioral_data', f'{experiment_name}_{participantID}.txt')
FPATH_DATA_CSV = join('behavioral_data', f'{experiment_name}_{participantID}.csv')

log_fpath = join('logging', f'subject{participantID}.log')
logFile = logging.LogFile(log_fpath, level=logging.EXP)
# this outputs to the screen, not a file (setting to critical means silencing
# console output by ignoring WARNING)
logging.console.setLevel(logging.CRITICAL)


################################################
#               Instructions/Text              #
################################################

LARGE_FONT = 1
welcome_message = 'Welcome to the experiment. \n\n Please press \'space\' if you are ready to start with reading the instructions.'
instructions = 'In the experiment you will see two different target stimuli that will quickly be hidden by a mask.\n\n'\
               'Target 1: \'OXXO\' or \'XOOX\'\n Target 2: a number word (e.g.,\'FIVE\')\n' \
               'Mask: 4 consonants (e.g., \'BKGF\')\n \nThere are two tasks you have to perform after you saw the targets.\n \n' \
               'Task 1: You will have to rate the visibility of the number word on a rating scale.\n' \
               'Task 2: You will be asked to answer if Target 1 (\'OXXO\' or \'XOOX\') contained the string \'XX\' or \'OO\'.\n\n' \
               'Please press \'space\' to go to the training instructions.'
training_instructions = 'Before we start the experiment, you will have the chance to train ' \
                        'the tasks.\n\n Remember: First you will see target 1 (\'OXXO\' or \'XOOX\') followed by a consonant-string.\n\n' \
                        'Before the trials start you will be informed if you only have to perform the visibility rating of target 2, or '\
                        'if you will additionally be asked to answer if target 1 contained the string \'XX\' OR \'OO\'. \n\nTry to give the answers ' \
                        'and ratings as accurate as possible.'
finished_training = 'Great! You have completed the training phase. \n\nPress \'space\' if you are ready to continue with the test phase.'
dual_block_start = 'In the following trials you will have to perform two tasks! \n\nFirst you will have to rate the visibility of the number word.' \
                   '\n and the additional question on target 1 (\'OXXO\' or \'XOOX\'). \n\n Please press \'space\' if you are ready to start.'
single_block_start = 'In the following trials you will have to perform only one task! \n\nYou will only have to rate the visibility of the number word. \n\n' \
                     'There won\'t  be a question on target 1 (\'OXXO\' or \'XOOX\').' \
                     ' \n\n Please press \'space\' if you are ready to start.'
start_trial_text = 'Press \'space\' to start the trial.'
thank_you = 'Great! You completed all trials. Thank you for your participation.'
