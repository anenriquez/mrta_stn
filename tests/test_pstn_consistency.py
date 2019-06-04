import unittest
import json
import os
import numpy as np
from temporal.networks.pstn import PSTN
from temporal.networks.pstn import SchedulerPSTN

PSTN_DATA = "data/pstn_two_tasks.json"
MAX_SEED = 2 ** 31 - 1


class TestPSTNconsistency(unittest.TestCase):
    def setUp(self):

        my_dir = os.path.dirname(__file__)
        pstn_json = os.path.join(my_dir, PSTN_DATA)

        with open(pstn_json) as json_file:
            pstn_dict = json.load(json_file)
        self.pstn = PSTN.from_dict(pstn_dict)

        random_seed = np.random.randint(MAX_SEED)
        seed_gen = np.random.RandomState(random_seed)
        seed = seed_gen.randint(MAX_SEED)
        self.scheduler = SchedulerPSTN(seed)

    def test_consistency(self):
        print("Initial PSTN:\n", self.pstn)
        minimal_pstn = self.pstn.floyd_warshall()
        self.assertTrue(self.pstn.is_consistent(minimal_pstn))

        self.pstn.update_edges(minimal_pstn)

        pstn = self.scheduler.resample_pstn(self.pstn)
        print("Resampled pstn:\n", pstn)

        alpha, schedule = self.scheduler.get_schedule(pstn, "srea")
        print("Schedule: \n", schedule)

        completion_time = self.scheduler.get_completion_time(schedule)
        makespan = self.scheduler.get_makespan(schedule)

        print("Completion time: ", completion_time)
        print("Makespan: ", makespan)

        self.assertEqual(completion_time, 62)
        self.assertEqual(makespan, 100)


if __name__ == '__main__':
    unittest.main()
