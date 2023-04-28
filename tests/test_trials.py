from __future__ import annotations
from typing import List
from unittest import TestCase
from unittest.mock import Mock
from itertools import groupby
from itertools import chain
from experiment.triggers import Triggers


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
        self.consts.iti_min = 3s
        self.consts.iti_max = 4s

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
        cond_trials = filter(lambda t: t.t2presence and t.soa_long, trials)
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
        present_short = filter(lambda t: t.t2presence and (not t.soa_long), trials)
        self.assertEqual(len(list(present_short)), self.consts.n_trials_dual_critical)
        present_long = filter(lambda t: t.t2presence and t.soa_long, trials)
        self.assertEqual(len(list(present_long)), self.consts.n_trials_dual_easy)
        absent_short = filter(lambda t: t.t2presence == False and (not t.soa_long), trials)
        self.assertEqual(len(list(absent_short)), self.consts.n_trials_dual_easy)
        absent_long = filter(lambda t: t.t2presence == False and t.soa_long, trials)
        self.assertEqual(len(list(absent_long)), self.consts.n_trials_dual_easy)

    def test_count_by_conditions_single_task(self):
        from experiment.trials import generateTrials
        trials = generateTrials('test', 'single', self.consts)
        self.assertEqual(len(trials), 128, 'total trials should be 128')
        present_short = filter(lambda t: t.t2presence and (not t.soa_long), trials)
        self.assertEqual(len(list(present_short)), self.consts.n_trials_single)
        present_long = filter(lambda t: t.t2presence and t.soa_long, trials)
        self.assertEqual(len(list(present_long)), self.consts.n_trials_single)
        absent_short = filter(lambda t: t.t2presence == False and (not t.soa_long), trials)
        self.assertEqual(len(list(absent_short)), self.consts.n_trials_single)
        absent_long = filter(lambda t: t.t2presence == False and t.soa_long, trials)
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

    def test_mask_sampling(self):
        masks_by_trial = [t.masks for t in self.sampleTrials()]
        ## three masks per trial
        self.assertEqual(len(masks_by_trial[0]), 3)
        ## mask is 4 chars long
        self.assertEqual(len(masks_by_trial[0][0]), 4)
        ## all masks unique
        all_masks = list(chain.from_iterable(masks_by_trial))
        self.assertAlmostEqual(len(set(all_masks)), len(all_masks), delta=1)
        
    def test_triggers_numbers_preset(self):
        from experiment.trials import generateTrials
        trials = generateTrials('test', 'dual', self.consts)
        present_short = filter(lambda t: t.t2presence and (not t.soa_long), trials)
        a_trial = list(present_short)[0]
        self.assertEqual(
            a_trial.t1_trigger,
            Triggers.t1_present_dualTask_shortSOA
        )
        self.assertEqual(
            a_trial.id_trigger,
            Triggers.taskT1variant
        )
        self.assertEqual(
            a_trial.vis_trigger,
            Triggers.taskT2visibility
        )

    def test_triggers_numbers_preset_training(self):
        from experiment.trials import generateTrials
        trials = generateTrials('train', 'single', self.consts)
        absent_long = filter(lambda t: (not t.t2presence) and t.soa_long, trials)
        a_trial = list(absent_long)[0]
        self.assertEqual(
            a_trial.t2_trigger,
            Triggers.t2_absent_singleTask_longSOA_training
        )
        self.assertEqual(
            a_trial.id_trigger,
            Triggers.taskT1variant_training
        )
        self.assertEqual(
            a_trial.vis_trigger,
            Triggers.taskT2visibility_training
        )

    def test_iti_sampling(self):
        itis = [t.iti for t in self.sampleTrials()]
        ## iti range
        self.assertTrue(all([iti > x for iti in itis]))
        self.assertTrue(all([iti > x for iti in itis]))
        ## all unique
        self.assertEqual(len(set(itis)), len(itis))
