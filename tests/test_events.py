from __future__ import annotations
from unittest import TestCase
from unittest.mock import Mock
from numpy.testing import assert_array_equal
from numpy import nan


class EventsTests(TestCase):

    def setUp(self):
        trial0 = Mock()
        trial0.phase = 'train'
        trial0.task = 'single'
        trial0.t2presence = False
        trial0.soa_long = False
        trial0.delay_index = 0
        trial0.t1_index = 0
        trial0.t2_index = 0
        trial0.vis_init = 9
        trial0.t1_trigger = 32
        trial0.t2_trigger = 40
        trial0.task_variant_trigger = 11
        trial0.task_visibility_trigger = 12
        trial0.id_choice = None
        trial0.id_onset = None
        trial0.id_rt = None
        trial0.vis_rating = 3
        trial0.vis_onset = 3.678
        trial0.vis_rt = 3456
        trial0.t1_onset = 1.123
        trial0.t1_offset = 1.345
        trial0.t2_onset = 2.345
        trial0.t2_offset = 2.789
        trial0.target1 = 'XOOX'
        trial0.target2 = 'ZERO'
        ## second trial
        trial1 = Mock()
        trial1.phase = 'test'
        trial1.task = 'dual'
        trial1.t2presence = False
        trial1.soa_long = True
        trial1.delay_index = 1
        trial1.t1_index = 1
        trial1.t2_index = 2
        trial1.vis_init = 11
        trial1.t1_trigger = 23
        trial1.t2_trigger = 31
        trial1.task_variant_trigger = 1
        trial1.task_visibility_trigger = 2
        trial1.id_choice = 1
        trial1.id_onset = 4.983
        trial1.id_rt = 2345
        trial1.vis_rating = 3
        trial1.vis_onset = 3.432
        trial1.vis_rt = 3456
        trial1.t1_onset = 1.654
        trial1.t1_offset = 1.987
        trial1.t2_onset = 2.543
        trial1.t2_offset = 2.765
        trial1.target1 = 'OXXO'
        trial1.target2 = 'FIVE'
        self.trials = [trial0, trial1]

    def test_onset(self):
        from experiment.events import format_events
        df = format_events(self.trials)
        assert_array_equal(df.onset, [
            self.trials[0].t1_onset,
            self.trials[0].t2_onset,
            nan,
            self.trials[0].vis_onset,
            self.trials[1].t1_onset,
            self.trials[1].t2_onset,
            self.trials[1].id_onset,
            self.trials[1].vis_onset,
        ])


# onset [to be adjusted from EEG file]
# duration
# sample [to be obtained from EEG file]
# trial_type
# other conditions..
# response_time
# value
# HED
## custom:
# response?
# correct
# stim value (xoox, five)
