'''
This script contains all functions needed to execute the attentional blink
experiment by running the main.py file located in the same folder.
'''
from __future__ import annotations
from typing import TYPE_CHECKING
from experiment.triggers import Triggers
import random
from experiment.constants import Constants
CONSTANTS  = Constants()
if TYPE_CHECKING:
    from experiment.ports import TriggerInterface as TriggerPort


def displayT1(port: TriggerPort, triggerNr: int):
    '''
    Displays the first target (T1) consisting of either the string 'OXXO' or 'XOOX'
    '''
    target1.text = CONSTANTS.target1_strings[0] if random.random() > .5 else CONSTANTS.target1_strings[1]
    target1.draw()
    port.trigger(triggerNr)
    SCREEN.flip()
    return target1.text


def displayT2(T2_present, port: TriggerPort, triggerNr: int):
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
        target2.text = random.choice(CONSTANTS.target2_strings)
        target2.draw()
    else:
        target2.text = ''

    port.trigger(triggerNr)
    SCREEN.flip()
    return target2.text

def displayMask():
    '''
    Displays a mask consisting of 4 consonants. The mask appears after the targets.
    The selection and order of consonants is ramdomly chosen at every execution.
    '''
    # create random consonants
    selected_string = random.sample(CONSTANTS.possible_consonants, 4)
    mask.text = ''.join(selected_string)
    mask.draw()
    SCREEN.flip()


def displayFixCross():
    fix_cross.draw()
    SCREEN.flip()


def displayTask1(p: TriggerPort):
    '''
    Diplay of choice making task that indicates if the participant correctly
    recognized T1 as either 'OXXO' or 'XOOX'.
    '''

    task1_text = 'Please indicate whether the two letters \n in the center of target 1 were ' \
                 '\'OO\' or \'XX\'\n'\
                 'Press \'space\' to confirm.\n\n'
    p.trigger(Triggers.taskT1variant)
    while True:
        ## This loop is a trick to force a choice; if the dummy middle choice is chosen,
        ## we simply create a new RatingScale
        rating_scaleT1 = RatingScale(SCREEN, noMouse=True,
            choices=['OO', '', 'XX'], markerStart=1, #labels=['OO', '', 'XX'],
            scale=task1_text, acceptKeys='space', lineColor='DarkGrey',
            markerColor='DarkGrey', pos=(0.0, 0.0), showAccept=False)
        rating_scaleT1.draw()
        SCREEN.flip()
        while rating_scaleT1.noResponse:
            rating_scaleT1.draw()
            SCREEN.flip()
        if rating_scaleT1.getRating() != '':
            ## valid choice; continue
            break

    print('The answer is: ', rating_scaleT1.getRating())
    # get and return the rating
    return [rating_scaleT1.getRating(), rating_scaleT1.getRT()]


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
    random_init = random.choice(range(scale_length))
    rating_scaleT2 = RatingScale(SCREEN, low=0, high=scale_length-1, labels=['nothing', 'maximal visibility'],
                                        acceptKeys='space', scale=task2_text, noMouse=True, lineColor='DarkGrey',
                                        markerColor='LightGrey', pos=(0.0, 0.0), showAccept=False, markerStart=random_init)

    rating_scaleT2.draw()
    p.trigger(Triggers.taskT2visibility)
    SCREEN.flip()

    # Show scale and instruction und confirmation of rating is done
    while rating_scaleT2.noResponse:
        rating_scaleT2.draw()
        SCREEN.flip()

    print('The rating is: ', rating_scaleT2.getRating())

    # get and return the rating
    return [rating_scaleT2.getRating(), rating_scaleT2.getRT()]


def start_trial(dualTask: bool, timing_T1_start: float, t2Present: bool, longSOA: bool, port: TriggerPort):
    '''
    Starts the real experiment trial.
    Parameters:
        task_condition str : 'dual_task' or 'single_task'
        timing_T1_start float : quick or slow (exact values are defined in parameters)
        target2_presence bool : False for 'absent' or True for 'present'
        duration_SOA float : 'short' or 'long' (values taken from parameter file)
    '''
    #T1_start = CONSTANTS.start_T1_slow if currentTrial['slow_T1']=='long' else CONSTANTS.start_T1_quick
    #target2_presence = True if currentTrial['T2_presence']=='present' else False
    duration_SOA = CONSTANTS.long_SOA if longSOA else CONSTANTS.short_SOA
    print('++++++ start trial +++++++')
    #return [None, None, None, None]


    # it starts with the fixation cross
    displayFixCross()
    core.wait(timing_T1_start)

    t1TriggerNr = Triggers.get_number(forT2=False, t2Present=t2Present, dualTask=dualTask, longSOA=longSOA)
    textT1 = displayT1(port, t1TriggerNr)
    core.wait(CONSTANTS.stimulus_duration) # - trigger??

    # display black screen between stimuli and masks
    SCREEN.flip()
    core.wait(CONSTANTS.stimulus_duration)

    displayMask()
    core.wait(CONSTANTS.stimulus_duration)

    # display the fixation cross either short_SOA - 129ms or long_SOA - 129ms,
    # since the target, the mask and the black screen was displayed for 43ms each
    displayFixCross()
    core.wait(duration_SOA - CONSTANTS.stimulus_duration*3)

    t2TriggerNr = Triggers.get_number(forT2=True, t2Present=t2Present, dualTask=dualTask, longSOA=longSOA)
    textT2 = displayT2(t2Present, port, t2TriggerNr)
    core.wait(CONSTANTS.stimulus_duration)

    # display black screen between stimuli and masks
    SCREEN.flip()
    core.wait(CONSTANTS.stimulus_duration)

    # display two masks after another with black screen inbetween
    displayMask()
    core.wait(CONSTANTS.stimulus_duration)
    SCREEN.flip()
    core.wait(CONSTANTS.stimulus_duration)
    displayMask()
    core.wait(CONSTANTS.stimulus_duration)

    SCREEN.flip()
    core.wait(CONSTANTS.visibility_scale_timing)

    # start the visibility rating (happens in single AND dual task conditions)
    ratingT2 = displayTask2(port)

    # only in the dual task condition the question on target 1 is displayed
    if dualTask:
        ratingT1 = displayTask1(port)
        # accuracy of answer
        correct = True if ratingT1[0] in textT1 else False
        ratingT1.append(correct)
    else:
        ratingT1 = [None, None, None]

    return ratingT2, ratingT1, textT2, textT1
