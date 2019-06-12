import unittest
import json
import os
from temporal.networks.stn import STN
from temporal.networks.stn import Scheduler

STN_DATA = "data/stn_two_tasks.json"


class TestSTNconsistency(unittest.TestCase):
    def setUp(self):

        my_dir = os.path.dirname(__file__)
        stn_json = os.path.join(my_dir, STN_DATA)

        with open(stn_json) as json_file:
            stn_dict = json.load(json_file)
        self.stn = STN.from_dict(stn_dict)
        self.scheduler = Scheduler()

    def test_consistency(self):
        print("Initial STN: \n", self.stn)
        minimal_stnu = self.stn.floyd_warshall()
        self.assertTrue(self.stn.is_consistent(minimal_stnu))

        self.stn.update_edges(minimal_stnu)

        alpha, schedule = self.scheduler.get_schedule(self.stn, "earliest")
        print("Schedule: \n", schedule)

        completion_time = self.scheduler.get_completion_time(schedule)
        makespan = self.scheduler.get_makespan(schedule)

        print("Completion time: ", completion_time)
        print("Makespan: ", makespan)

        self.assertEqual(completion_time, 100)
        self.assertEqual(makespan, 100)



if __name__ == '__main__':
    unittest.main()
