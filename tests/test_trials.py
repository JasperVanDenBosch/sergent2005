from __future__ import annotations
from typing import List
from unittest import TestCase, skip
from unittest.mock import Mock
from itertools import groupby


class TrialGenerationTests(TestCase):

    def setUp(self) -> None:
        self.consts = Mock()
        self.consts.start_T1_quick = 31
        self.consts.start_T1_slow = 51
        self.consts.short_SOA = 15
        self.consts.long_SOA = 41
        self.consts.n_trials_single = 32
        self.consts.n_trials_dual_critical = 96
        self.consts.n_trials_dual_easy = 48
        self.consts.n_training_trial_divisor = 8
        self.consts.target2_strings = ['ZERO', 'FOUR', 'FIVE', 'NINE']
        self.consts.target1_strings = ['OXXO', 'XOOX']
        self.consts.possible_consonants = list([c for c in 'WRZPSDFGHJKCBYNM'])
        self.consts.vis_scale_length = 21

    def assertMeanEqual(self, exp: float, vals: List[bool] | List[int]) -> None:
        mean = sum(vals) / len(vals)
        self.assertEqual(exp, mean)

    def assertMeanAlmostEqual(self, exp: float, vals: List[bool] | List[int], delta: float) -> None:
        mean = sum(vals) / len(vals)
        self.assertAlmostEqual(exp, mean, delta=delta)
    
    def assertMaxConsecReps(self, exp: int, vals: List[bool] | List[int]) -> None:
        reps = [len(list(g)) for _, g in groupby(vals)]
        if max(reps) > exp:
            print(vals)
        self.assertLessEqual(max(reps), exp)

    def sampleTrials(self):
        from experiment.trials import generateTrials
        trials = generateTrials('test', 'dual', self.consts)
        cond_trials = filter(lambda t: t.t2presence and t.soa, trials)
        return list(cond_trials)

    def test_phase(self):
        from experiment.trials import generateTrials
        trials = generateTrials('train', 'single', self.consts)
        self.assertEqual(len(trials), 16)
        trials = generateTrials('train', 'dual', self.consts)
        self.assertEqual(len(trials), 30)

    def test_count_by_conditions_dual_task(self):
        from experiment.trials import generateTrials
        trials = generateTrials('test', 'dual', self.consts)
        self.assertEqual(len(trials), 240, 'total trials should be 240')
        present_short = filter(lambda t: t.t2presence and (not t.soa), trials)
        self.assertEqual(len(list(present_short)), self.consts.n_trials_dual_critical)
        present_long = filter(lambda t: t.t2presence and t.soa, trials)
        self.assertEqual(len(list(present_long)), self.consts.n_trials_dual_easy)
        absent_short = filter(lambda t: t.t2presence == False and (not t.soa), trials)
        self.assertEqual(len(list(absent_short)), self.consts.n_trials_dual_easy)
        absent_long = filter(lambda t: t.t2presence == False and t.soa, trials)
        self.assertEqual(len(list(absent_long)), self.consts.n_trials_dual_easy)

    def test_count_by_conditions_single_task(self):
        from experiment.trials import generateTrials
        trials = generateTrials('test', 'single', self.consts)
        self.assertEqual(len(trials), 128, 'total trials should be 128')
        present_short = filter(lambda t: t.t2presence and (not t.soa), trials)
        self.assertEqual(len(list(present_short)), self.consts.n_trials_single)
        present_long = filter(lambda t: t.t2presence and t.soa, trials)
        self.assertEqual(len(list(present_long)), self.consts.n_trials_single)
        absent_short = filter(lambda t: t.t2presence == False and (not t.soa), trials)
        self.assertEqual(len(list(absent_short)), self.consts.n_trials_single)
        absent_long = filter(lambda t: t.t2presence == False and t.soa, trials)
        self.assertEqual(len(list(absent_long)), self.consts.n_trials_single)

    def test_delay_sampling(self):
        sample1 = [t.delay_index for t in self.sampleTrials()]
        sample2 = [t.delay_index for t in self.sampleTrials()]
        self.assertMeanEqual(0.5, sample1)
        self.assertMaxConsecReps(7, sample1)
        self.assertNotEqual(sample1, sample2)

    def test_t1_sampling(self):
        sample1 = [t.t1_index for t in self.sampleTrials()]
        sample2 = [t.t1_index for t in self.sampleTrials()]
        self.assertMeanEqual(0.5, sample1)
        self.assertMaxConsecReps(7, sample1)
        self.assertNotEqual(sample1, sample2)

    def test_t2_sampling(self):
        sample1 = [t.t2_index for t in self.sampleTrials() if t.t2presence]
        sample2 = [t.t2_index for t in self.sampleTrials() if t.t2presence]
        self.assertMeanEqual(1.5, sample1)
        self.assertMaxConsecReps(5, sample1)
        self.assertNotEqual(sample1, sample2)

    def test_init_vis_sampling(self):
        sample1 = [t.vis_init for t in self.sampleTrials()]
        sample2 = [t.vis_init for t in self.sampleTrials()]
        self.assertMeanAlmostEqual(self.consts.vis_scale_length/2, sample1, delta=1)
        self.assertMaxConsecReps(2, sample1)
        self.assertNotEqual(sample1, sample2)

    @skip('todo')
    def test_mask_sampling(self):
        self.fail('todo')

    @skip('todo')
    def test_triggers_numbers_preset(self):
        pass

    # def test_t2_absent(self):
    #     sample = [t.t2_index for t in self.sampleTrials() if t.t2presence]
    #     self.assertEqual(1.5, sample1)
    #     self.assertMaxConsecReps(3, sample1)
    #     self.assertNotEqual(sample1, sample2)


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