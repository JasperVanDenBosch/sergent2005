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
from parameters import *
from functions import *
from psychopy.data import TrialHandlerExt, ExperimentHandler
import random
from ports import openTriggerPort


port = openTriggerPort(
    typ=chosen_settings['port_type'],
    address=chosen_settings['port_address'],
    rate=chosen_settings['port_baudrate'],
    win=SCREEN,
    scale=scale,
    viewPixBulbSize=7
)

# define an experiment handler
exp = ExperimentHandler(name=experiment_name,
    version='0.1',
    extraInfo=dict(
        participant=participantID,
        short_SOA=short_SOA,
        long_SOA=long_SOA,
        stimulus_duration=stimulus_duration
    ),
    runtimeInfo=None,
    originPath=None,
    savePickle=True,
    saveWideText=True,
    dataFileName=FPATH_DATA_CSV
)

# Welcome the participant
showMessage(welcome_message, LARGE_FONT)
showMessage(instructions)


for phase in ['train', 'test']:
    if phase == 'train':
        showMessage(training_instructions)
        showMessage('TRAINING STARTS', LARGE_FONT, wait=False)
    else:
        showMessage('MAIN EXPERIMENT STARTS', LARGE_FONT, wait=False)

    # compute the list of all different trial conditions and store it in two lists,
    # one for the single task and one for the dual task condition
    [stim_single, stim_dual] = computeStimulusList(False, n_trials_single,
        n_trials_dual_critical, n_trials_dual_easy)
    trials_dual = TrialHandlerExt(stim_dual, 1, method='fullRandom', name=f'{phase}_dual')
    trials_single = TrialHandlerExt(stim_single, 1, method='fullRandom', name=f'{phase}_single')

    # add the trial handlers to our experiment handler and show the instructions
    exp.addLoop(trials_dual)
    exp.addLoop(trials_single)

    # we loop over two training blocks (dual taks, single task)
    blocks = [trials_dual, trials_single]
    random.shuffle(blocks)
    for block in blocks:
        if 'dual' in block.name:
            showMessage(dual_block_start)
        else:
            showMessage(single_block_start)

        for currentTrial in block:
            # 50% chance that T1 is presented quick or slow after trial start
            T1_start = start_T1_slow if random.random() > .5 else start_T1_quick
            print('Current trial: ', currentTrial['Name'])
            ratingT2, ratingT1, stimulusT2, stimulusT1 = start_trial(
                dualTask=currentTrial['task']=='dual',
                timing_T1_start=T1_start,
                t2Present=currentTrial['T2_presence']=='present',
                longSOA=currentTrial['SOA']=='long',
                port=port
            )
            #save information in the csv-file
            block.addData('ratingT2', ratingT2[0])
            block.addData('RTtaskT2', ratingT2[1])
            block.addData('ratingT1', ratingT1[0])
            block.addData('RTtaskT1', ratingT1[1])
            block.addData('ACCtaskT1', ratingT1[2])
            block.addData('startingT1', T1_start)
            block.addData('stimulusT1', stimulusT1)
            block.addData('stimulusT2', stimulusT2)
            exp.nextEntry()

    if phase == 'train':
        showMessage(finished_training)
        
print(f'dropped frames: {SCREEN.nDroppedFrames}')
df = exp.saveAsWideText(FPATH_DATA_TXT)

showMessage(thank_you, wait=False)
print('Saved experiment file!')
