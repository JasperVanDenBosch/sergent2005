# -*- coding: utf-8 -*-
######################################################
# The timing of consciousness related brain activity #
# An attentional blink experiment                    #
######################################################

'''
About the experiment:
This implementation replicates the experiment presented in the paper 'Timing of
brain events underlying acces to consciousness during attentional blink'
(Sergent et. al., 2005) in the framework of #eegmanylabs.

In this experiment the subject has to indicate visibility of a second target stimulus
that in one condition is displayed during the attentional blink and in the other
condition it is displayed outside of the attentional blink.
In 50% of the trials the second target is present and in the other 50% only an
empty screen is displayed.
The attentional blink is induced by a task on the first target stimulus which is
presented before the second target.

TODO:
- backup parameters
- counterbalanced single/dual block order
- i18n
- ensure psychopy is logging draws as backup
- computeStimulusList has fewer trials for training (n_training_trial_divisor)
- computeStimulusList decide t1 slow or fast
'''
from parameters import *
from functions import *
# from psychopy import data
import random
from experiment.engine import PsychopyEngine
from unittest.mock import Mock


#p = openTriggerPort(chosen_settings)
p = Mock()

# this object represents interactions with psychopy, ie for the actual drawing 
# and interactions
engine = PsychopyEngine()

# Welcome the participant
engine.showMessage(welcome_message, LARGE_FONT)
engine.showMessage(instructions)

## before experiment
engine.showMessage(training_instructions)


for phase in ('train', 'test'):
    engine.showMessage('TRAINING STARTS', LARGE_FONT, wait=False)

    # compute the list of all different trial conditions and store it in two lists,
    # one for the single task and one for the dual task condition
    for block in ('single', 'dual'):
        [trials, trials] = computeStimulusList(
            #block, 
            True, # training
            n_trials_single,
            n_trials_dual_critical,
            n_trials_dual_easy
        )
        random.shuffle(trials)
        # this just randomizes the order
        #train_trials_dual = data.TrialHandlerExt(train_stim_dual, 1, method='fullRandom', name='train_dual')
        #train_trials_single = data.TrialHandlerExt(train_stim_single, 1, method='fullRandom', name='train_single')

        # we loop over two training blocks (dual taks, single task)

        if block=='dual':
            engine.showMessage(dual_block_start)
        else:
            engine.showMessage(single_block_start)

        for currentTrial in trials:
            # 50% chance that T1 is presented quick or slow after trial start
            T1_start = start_T1_slow if random.random() > .5 else start_T1_quick
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

