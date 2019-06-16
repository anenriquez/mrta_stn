import unittest
import os
import json
import collections
from scheduler.structs.task import Task
from scheduler.scheduler import Scheduler

STN = "data/stn_two_tasks.json"


class TestBuildSTN(unittest.TestCase):

    def setUp(self):

        # Load the stn as a dictionary
        with open(STN) as json_file:
            stn_dict = json.load(json_file)

        # Convert the dict to a json string
        stn_json = json.dumps(stn_dict)

        self.scheduler = Scheduler('fpc', json_temporal_network=stn_json)

    def test_build_stn(self):
        print("STN: \n", self.scheduler.temporal_network)

        metric, minimal_network = self.scheduler.get_dispatch_graph()

        print("Minimal STN: \n", minimal_network)

        completion_time = minimal_network.get_completion_time()
        makespan = minimal_network.get_makespan()
        print("Completion time: ", completion_time)
        print("Makespan: ", makespan)

        self.assertEqual(completion_time, 107)
        self.assertEqual(makespan, 107)


if __name__ == '__main__':
    unittest.main()
