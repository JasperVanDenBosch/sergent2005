from unittest import TestCase
from unittest.mock import Mock


class TrialGenerationTests(TestCase):

    def test_phase(self):
        from experiment.trials import generateTrials
        consts = Mock()
        trials = generateTrials('train', 'single', consts)
        self.assertEqual(len(trials), 4)
        # all trainn

    def test_conditions(self):
        #0.5 SOA
        #0.5 T2pres
        self.fail('todo')

    def test_repetitions(self):
        self.fail('todo')

    def test_iti_range(self):
        self.fail('todo')

    def test_t1_sampling(self):
        self.fail('todo')

    def test_t2_sampling(self):
        self.fail('todo')


## trial creation SNIPPETS
    # T1
    #target1.text = CONSTANTS.target1_strings[0] if random.random() > .5 else CONSTANTS.target1_strings[1]
# T2
# target2.text = random.choice(CONSTANTS.target2_strings)

    # if T2_present:
    #     target2.text = random.choice(CONSTANTS.target2_strings)
    #     target2.draw()
    # else:
    #     target2.text = ''

# masks x3
#    selected_string = random.sample(CONSTANTS.possible_consonants, 4)
        # create random consonants


            # # 50% chance that T1 is presented quick or slow after trial start
            # T1_start = CONSTANTS.start_T1_slow if currentTrial['slow_T1']=='long' else CONSTANTS.start_T1_quick
            # duration_SOA = CONSTANTS.long_SOA if currentTrial['SOA']=='long' else CONSTANTS.short_SOA
            # print('Current trial: ', currentTrial['Name'])
            # ratingT2, ratingT1, stimulusT2, stimulusT1 = start_trial(
            #     dualTask=currentTrial['task']=='dual',
            #     timing_T1_start=T1_start,
            #     t2Present=currentTrial['T2_presence']=='present',
            #     longSOA=currentTrial['SOA']=='long',
            #     port=engine.port,
            # )

                ## construction
    #'Name': name, 'task':task, 'T2_presence':T2_presence, 'SOA':SOA, 'weight':weight}
    # T1_start = start_T1_slow if random.random() > .5 else start_T1_quick
    # training vs test
    # target2.text = random.choice(CONSTANTS.target2_strings)
    # target1.text = CONSTANTS.target1_strings[0] if random.random() > .5 else CONSTANTS.target1_strings[1]
    # toDict() for results

    #     @property
    # def t1TriggerNr(self):
    #     return Triggers.get_number(
    #         forT2=False,
    #         t2Present=self.t2present,
    #         dualTask=self.task=='dual',
    #         longSOA=self.soa=='long'
    #     )
    
    # @property
    # def t2TriggerNr(self):
    #     return Triggers.get_number(
    #         forT2=True,
    #         t2Present=self.t2present,
    #         dualTask=self.task=='dual',
    #         longSOA=self.soa=='long'
    #     )