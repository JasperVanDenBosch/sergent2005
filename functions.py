'''
This script contains all functions needed to execute the attentional blink
experiment by running the main.py file located in the same folder.
'''
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Union
from parameters import *
from psychopy import visual, event, core
import random
from parallel import Parallel
from serialport import SerialPort
if TYPE_CHECKING:
    TriggerPort = Union[SerialPort, Parallel]


def openTriggerPort(settings: Dict) -> TriggerPort:
    if settings.get('port_type') == 'parallel':
        return Parallel()
    elif settings.get('port_type') == 'serial':
        return SerialPort(
            settings['port_address'],
            baud=settings['port_baudrate']
        )
    else:
        raise ValueError('Unknown port type in lab settings.')

def computeStimulusList(training, single_trials, dual_critical_trials, dual_easy_trials):
    '''
    In this function a list of dictionaries containing all possible combination of
    trial types is created. It returns two lists, one for the dual task condition
    and one for the single task condition. These lists are handed over to TrialHandlers
    that control for randomized (and weighted) trials execution in training and
    testing sessions.
    Parameters:
        training bool : True if this is used for a training session
        single_trials int : Number of trials in the single condition
        dual_critical_trials int : Number of trials in the critical dual task
                                   condition (short SOA and present T2).
        dual_easy_trials int : Number of trials in the easy dual task conditions
                               (short SOA/T2 absent or long SOA).
    '''
    stimList = []
    for task in ['single', 'dual']:
        for T2_presence in ['present', 'absent']:
            for SOA in ['short', 'long']:
                name = '_'.join([task, T2_presence, SOA])
                if training:
                    name = name + '_training'
                if task=='single':
                    weight = single_trials
                elif task=='dual' and SOA=='short' and T2_presence=='present':
                    weight = dual_critical_trials
                else:
                    weight = dual_easy_trials

                stimList.append({'Name': name, 'task':task, 'T2_presence':T2_presence, 'SOA':SOA, 'weight':weight})

    stimuli_single = stimList[0:int(len(stimList)/2)]
    stimuli_dual = stimList[int(len(stimList)/2):len(stimList)]
    print('Single: ')
    [print(single) for single in stimuli_single]
    print('DUAL: ')
    [print(dual) for dual in stimuli_dual]

    return stimuli_single, stimuli_dual


def displayT1(p: TriggerPort):
    '''
    Displays the first target (T1) consisting of either the string 'OXXO' or 'XOOX'
    '''
    target1.text = target1_strings[0] if random.random() > .5 else target1_strings[1]
    target1.draw()
    SCREEN.flip()
    p.setData(trigger_T1)
    core.wait(0.01)
    p.setData(0)
    return target1.text


def displayT2(T2_present, p: TriggerPort):
    '''
    Displays the second target (T2) constisting of 4 white squares and (if present
    condition is active) of a number word in capital letters.
    Parameters:
        T2_present bool: True for present or False for absent
    '''
    target2_square1.draw()
    target2_square2.draw()
    target2_square3.draw()
    target2_square4.draw()

    if T2_present:
        trigger_T2 = trigger_T2_present
        target2.text = random.choice(target2_strings)
        target2.draw()
    else:
        trigger_T2 = trigger_T2_absent
        target2.text = ''

    SCREEN.flip()
    p.setData(trigger_T2)
    core.wait(0.01)
    p.setData(0)
    return target2.text

def displayMask():
    '''
    Displays a mask consisting of 4 consonants. The mask appears after the targets.
    The selection and order of consonants is ramdomly chosen at every execution.
    '''
    # create random consonants
    selected_string = random.sample(possible_consonants, 4)
    mask.text = ''.join(selected_string)
    mask.draw()
    SCREEN.flip()


def displayFixCross():
    fix_cross.draw()
    SCREEN.flip()


def displayTask2(p: TriggerPort):
    '''
    Diplay of rating scale that indicates visibility of target 2. Above the rating
    scale a short instruction is shown.
    '''
    # the rating scale has to be re-initialized in every function call, because
    # the marker start can't be randomized and updated when using the same rating
    # scale object again and again.
    # The marker start needs to be defined randomly beforehand
    scale_length = 21 # the maximum visibiliy rating
    task2_text = 'Please indicate the visibility of the number word \n by choosing a rating on the scale below.\n' \
                 'Press \'space\' to confirm.\n\n'
    rating_scaleT2 = visual.RatingScale(SCREEN, low=1, high=scale_length, labels=['nothing', 'maximal visibility'],
                                        acceptKeys='space', scale=task2_text, noMouse=True, lineColor='DarkGrey',
                                        markerColor='LightGrey', pos=(0.0, 0.0), showAccept=False, markerStart=random.choice(range(scale_length)))

    rating_scaleT2.draw()
    SCREEN.flip()
    p.setData(trigger_task2)
    core.wait(0.01)
    p.setData(0)

    # Show scale and instruction und confirmation of rating is done
    while rating_scaleT2.noResponse:
        rating_scaleT2.draw()
        SCREEN.flip()

    print('The rating is: ', rating_scaleT2.getRating())

    # get and return the rating
    return [rating_scaleT2.getRating(), rating_scaleT2.getRT()]



def displayTask1(p: TriggerPort):
    '''
    Diplay of choice making task that indicates if the participant correctly
    recognized T1 as either 'OXXO' or 'XOOX'.
    '''

    task1_text = 'Please indicate whether the two letters \n in the center of target 1 were ' \
                 '\'OO\' or \'XX\'\n'\
                 'Press \'space\' to confirm.\n\n'
    rating_scaleT1 = visual.RatingScale(SCREEN, noMouse=True, choices=['OO', 'XX'], markerStart=0.5, labels=['OO', 'XX'],
                                        scale=task1_text, acceptKeys='space', lineColor='DarkGrey', markerColor='DarkGrey',
                                        pos=(0.0, 0.0), showAccept=False)
    rating_scaleT1.draw()
    SCREEN.flip()
    p.setData(trigger_task1)
    core.wait(0.01)
    p.setData(0)

    while rating_scaleT1.noResponse:
        rating_scaleT1.draw()
        SCREEN.flip()

    print('The answer is: ', rating_scaleT1.getRating())
    # get and return the rating
    return [rating_scaleT1.getRating(), rating_scaleT1.getRT()]



def start_trial(task_condition, timing_T1_start, target2_presence, duration_SOA, p: TriggerPort):
    '''
    Starts the real experiment trial.
    Parameters:
        task_condition str : 'dual_task' or 'single_task'
        timing_T1_start float : quick or slow (exact values are defined in parameters)
        target2_presence bool : False for 'absent' or True for 'present'
        duration_SOA float : 'short' or 'long' (values taken from parameter file)
    '''

    print('++++++ start trial +++++++')
    p.setData(trigger_start_trial)
    core.wait(0.01)
    p.setData(0)
    # it starts with the fixation cross
    displayFixCross()
    core.wait(timing_T1_start)

    textT1 = displayT1(p)
    core.wait(stimulus_duration)

    # display black screen between stimuli and masks
    SCREEN.flip()
    core.wait(stimulus_duration)

    displayMask()
    core.wait(stimulus_duration)

    # display the fixation cross either short_SOA - 129ms or long_SOA - 129ms,
    # since the target, the mask and the black screen was displayed for 43ms each
    displayFixCross()
    core.wait(duration_SOA - stimulus_duration*3)

    textT2 = displayT2(target2_presence, p)
    core.wait(stimulus_duration)

    # display black screen between stimuli and masks
    SCREEN.flip()
    core.wait(stimulus_duration)

    # display two masks after another with black screen inbetween
    displayMask()
    core.wait(stimulus_duration)
    SCREEN.flip()
    core.wait(stimulus_duration)
    displayMask()
    core.wait(stimulus_duration)

    SCREEN.flip()
    core.wait(visibility_scale_timing)

    # start the visibility rating (happens in single AND dual task conditions)
    ratingT2 = displayTask2(p)

    # only in the dual task condition the question on target 1 is displayed
    if task_condition == 'dual':
        ratingT1 = displayTask1(p)
        # accuracy of answer
        correct = True if ratingT1[0] in textT1 else False
        ratingT1.append(correct)
    else:
        ratingT1 = [None, None, None]

    return ratingT2, ratingT1, textT2, textT1

def showMessage(message, text_height=0.6, wait=True):
    text_to_display = visual.TextStim(SCREEN, text=message, height=text_height)
    text_to_display.draw()
    SCREEN.flip()
    if wait:
        event.waitKeys(keyList='space')
    else:
        core.wait(1.5)
