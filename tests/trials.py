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