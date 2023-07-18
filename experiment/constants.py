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

    task_vis_labels = ("didn't see", 'maximum visibility')
    task_identity_options = ('O', 'X')

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
    welcome_message = 'Welcome to the experiment. \n\n Please press \'space\' if you are ready to start.'
    training_instructions = 'The training phase starts now'
    finished_training = 'Great! You have completed the training phase. \n\nPress \'space\' if you are ready to continue with the test phase.'
    dual_block_start = 'In the following trials you will have to perform TWO tasks!' \
                        ' \n\n Please press \'space\' if you are ready to start.'
    single_block_start = 'In the following trials you will have to perform only ONE task!' \
                        ' \n\n Please press \'space\' if you are ready to start.'
    thank_you = 'Great! You completed all trials. Thank you for your participation.'
    task_vis_text = 'Please indicate the visibility of the number word.\n' \
                 'Press \'space\' to confirm.\n\n'
    task_identity_text = 'Please indicate what the two letters \n in the center of target 1 were. \n' \
                 'Press \'space\' to confirm.\n\n'
