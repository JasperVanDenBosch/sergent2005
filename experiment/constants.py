"""Design-time parameters of the experiment
"""


class Constants(object):

    """These are the times in number of frames at 70Hz,
    the refresh rate in the original experiment, given
    the timing reported in the manuscript (in comments below).
    """
    short_T1_delay = 36 # 516ms
    long_T1_delay = 60  # 860ms
    short_SOA = 15      # 258ms
    long_SOA = 41       # 688ms
    target_dur = 3      # 43ms
    task_delay = 37     # 500ms

    ## The range of the inter trial interval in seconds
    iti_min_sec = 3 #seconds
    iti_max_sec = 4 #seconds

    ## number of trials
    n_trials_single = 32 # only visibility rating task
    n_trials_dual_critical = 96  # attentional blink condition!
    n_trials_dual_easy = 48 # no intentional blink
    n_training_trial_divisor = 8

    # number of options for visibility rating
    vis_scale_length = 21

    ####################################################
    # Visual features (targets, masks, fixation cross) #
    ####################################################

    # size of stimuli in degrees of visual angle
    square_size = 0.5
    string_height = 1

    target1_strings = ['XOOX', 'OXXO']
    target2_strings = ['ZERO', 'FOUR', 'FIVE', 'NINE']

    task_vis_labels = ('nothing', 'maximal visibility')
    task_identity_options = ('OO', 'XX')

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
    task_vis_instruct = """
Visibility Task

Use the scale to rate the visibility of the number word
as finely as possible. You can take your time.
The far left end of the scale should be used only when 
you're sure that you've not seen it. 
If you have any feeling of having seen it, even if you're not sure, 
shift the cursor away from the left extremity. 
Use the right extremity only for crisply visible T2s, 
and the rest of the scale relative to these extremes.

Please press 'space' to continue
"""
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
    thank_you = 'Great! You completed all trials. Thank you for your participation.'
    task_vis_text = 'Please indicate the visibility of the number word \n by choosing a rating on the scale below.\n' \
                 'Press \'space\' to confirm.\n\n'
    task_identity_text = 'Please indicate whether the two letters \n in the center of target 1 were ' \
                 '\'OO\' or \'XX\'\n'\
                 'Press \'space\' to confirm.\n\n'
