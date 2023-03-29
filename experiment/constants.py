'''
This script contains all parameters needed to execute the attentional blink
experiment by running the main.py file located in the same folder.
'''


class Constants(object):

    ###########################
    # Experimental parameters #
    ###########################

    ## original study: 70Hz, 14.286ms
    ## current flip nrs for 60hz

    experiment_name = 'eegmanylabs_sergent2005'
    start_T1_quick = 0.514
    start_T1_slow = 0.857

    short_SOA = 15 # 0.257
    long_SOA = 41 # 0.686
    stimulus_duration = 3 #0.043s #in seconds
    visibility_scale_timing = 30 # 0.500s # after third mask offset

    n_trials_single = 32 # only visibility rating task
    n_trials_dual_critical = 96  # attentional blink condition!
    n_trials_dual_easy = 48 # no intentional blink
    # to calculate the number of trials of each condition in the training session,
    # each number of test trial will be divided by n_training_trial_divisor
    n_training_trial_divisor = 8

    # number of options for visibility rating
    vis_scale_length = 21

    ####################################################
    # Visual features (targets, masks, fixation cross) #
    ####################################################

    # size of stimuli in degrees of visual angle
    square_size = 0.5
    string_height = 1

    target2_strings = ['ZERO', 'FOUR', 'FIVE', 'NINE']
    target1_strings = ['OXXO', 'XOOX']

    target2_square1_pos=(-5,-5)
    target2_square2_pos=(5,-5)
    target2_square3_pos=(-5,5)
    target2_square4_pos=(5,5)
    target2_square_offset = 5

    fix_cross_arm_len = 0.4

    # the mask is set of 4 capital letters (randomly generated in function file)
    possible_consonants = ['W', 'R', 'Z', 'P', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'C', 'B', 'Y', 'N', 'M']


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
    task2_text = 'Please indicate the visibility of the number word \n by choosing a rating on the scale below.\n' \
                 'Press \'space\' to confirm.\n\n'
    task1_text = 'Please indicate whether the two letters \n in the center of target 1 were ' \
                 '\'OO\' or \'XX\'\n'\
                 'Press \'space\' to confirm.\n\n'
