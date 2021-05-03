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

'''
import psychopy
# use the latest psychopy version due to crucial bug fixes on TrialHandlerExt
#psychopy.useVersion('2021.1.4')
from parameters import *
from functions import *
from psychopy import data
import random

# we only have two different blocks, (dual and single)
exp_conditions = ['single', 'dual']
# we have 368 trials in total, half of this is short SOA and the other half is long SOA

# define an experiment handler
exp = data.ExperimentHandler(name=experiment_name,
                version='0.1',
                extraInfo={'participant':participantID, 'age':23, 'short_SOA':short_SOA, 'long_SOA':long_SOA, 'stimulus_duration':stimulus_duration},
                runtimeInfo=None,
                originPath=None,
                savePickle=True,
                saveWideText=True,
                dataFileName=f'%s\%s_%i' % (DATAPATH, experiment_name, participantID))

# Welcome the participant
showMessage(welcome_message, 0.1)
showMessage(instructions, 0.07)

###############################
#          TRAINING           #
###############################
showMessage(training_instructions)
showMessage('TRAINING STARTS', wait=False)

# calculate how many trials we need for the training
n_train_trials_single = int(n_trials_single/n_training_trial_divisor)
n_train_trials_dual_critical = int(n_trials_dual_critical/n_training_trial_divisor)
n_train_trials_dual_easy = int(n_trials_dual_easy/n_training_trial_divisor)

# copmute the list of all different trial conditions and store it in two lists,
# one for the single task and one for the dual task condition
[train_stim_single, train_stim_dual] = computeStimulusList(True, n_train_trials_single,
                                        n_train_trials_dual_critical, n_train_trials_dual_easy)
train_trials_dual = data.TrialHandlerExt(train_stim_dual, 1, method='fullRandom', name='train_dual')
train_trials_single = data.TrialHandlerExt(train_stim_single, 1, method='fullRandom', name='train_single')

# add the trial handlers to our experiment handler and show the instructions
exp.addLoop(train_trials_dual)
exp.addLoop(train_trials_single)

# we loop over two training blocks (dual taks, single task)
training_blocks = [train_trials_dual, train_trials_single]
random.shuffle(training_blocks)
for block in training_blocks:
    if block.name=='train_dual':
        showMessage(dual_block_start)
    else:
        showMessage(single_block_start)

    for currentTrial in block:
        # 50% chance that T1 is presented quick or slow after trial start
        T1_start = start_T1_slow if random.random() > .5 else start_T1_quick
        duration_SOA = long_SOA if currentTrial['SOA']=='long' else short_SOA
        target2_presence = True if currentTrial['T2_presence']=='present' else False
        print('Current trial: ', currentTrial['Name'])
        ratingT2, ratingT1, stimulusT2, stimulusT1 = start_trial(currentTrial['task'], T1_start, target2_presence, duration_SOA)
        # save information in the csv-file
        block.addData('ratingT2', ratingT2[0])
        block.addData('RTtaskT2', ratingT2[1])
        block.addData('ratingT1', ratingT1[0])
        block.addData('RTtaskT1', ratingT1[1])
        block.addData('ACCtaskT1', ratingT1[2])
        block.addData('startingT1', T1_start)
        block.addData('stimulusT1', stimulusT1)
        block.addData('stimulusT2', stimulusT2)
        exp.nextEntry()

print('Training done!')
showMessage(finished_training)

##################################################
#          TESTING (experiment starts)           #
##################################################

showMessage('EXPERIMENT STARTS', wait=False)

[test_stim_single, test_stim_dual] = computeStimulusList(False, n_trials_single,
                                        n_trials_dual_critical, n_trials_dual_easy)
test_trials_dual = data.TrialHandlerExt(test_stim_dual, name='test_dual', method='fullRandom', nReps=1)
test_trials_single = data.TrialHandlerExt(test_stim_single, name='test_single', method='fullRandom', nReps=1)
test_blocks = [test_trials_dual, test_trials_single]
random.shuffle(test_blocks)
# we loop over the real test blocks
for block in test_blocks:
    if block.name=='test_dual':
        showMessage(dual_block_start)
    else:
        showMessage(single_block_start)

    for currentTrial in block:
        # 50% chance that T1 is presented quick or slow after trial start
        T1_start = start_T1_slow if random.random() > .5 else start_T1_quick
        duration_SOA = long_SOA if currentTrial['SOA']=='long' else short_SOA
        target2_presence = True if currentTrial['T2_presence']=='present' else False
        print('Current trial: ', currentTrial['Name'])
        ratingT2, ratingT1, stimulusT2, stimulusT1 = start_trial(currentTrial['task'], T1_start, target2_presence, duration_SOA)
        # save information in the csv-file
        block.addData('ratingT2', ratingT2[0])
        block.addData('RTtaskT2', ratingT2[1])
        block.addData('ratingT1', ratingT1[0])
        block.addData('RTtaskT1', ratingT1[1])
        block.addData('ACCtaskT1', ratingT1[2])
        block.addData('startingT1', T1_start)
        block.addData('stimulusT1', stimulusT1)
        block.addData('stimulusT2', stimulusT2)
        exp.nextEntry()

# save the whole data as txt (additionally to the csv file), this also returns a dataFrame
df = exp.saveAsWideText(f"behavioral_data\%s_%i.txt" % (experiment_name, participantID))

showMessage(thank_you, wait=False)
print('Saved experiment file!')
