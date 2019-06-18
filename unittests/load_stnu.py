import unittest
import os
import json
import collections
from scheduler.structs.task import Task
from scheduler.scheduler import Scheduler

STNU = "data/stnu_two_tasks.json"


class TestBuildSTNU(object):

    def __init__(self):

        # Load the stn as a dictionary
        with open(STNU) as json_file:
            stnu_dict = json.load(json_file)

        # Convert the dict to a json string
        stnu_json = json.dumps(stnu_dict)

        self.scheduler = Scheduler('dsc_lp', json_temporal_network=stnu_json)

    def test_build_stn(self):
        print("STNU: \n", self.scheduler.get_temporal_network())

        print(type(self.scheduler.temporal_network))

        r = self.scheduler.get_dispatch_graph()
        print(r)


        # metric, minimal_network = self.scheduler.get_dispatch_graph()
        #
        # print("Minimal STN: \n", minimal_network)
        #
        # completion_time = minimal_network.get_completion_time()
        # makespan = minimal_network.get_makespan()
        # print("Completion time: ", completion_time)
        # print("Makespan: ", makespan)
        #
        # self.assertEqual(completion_time, 107)
        # self.assertEqual(makespan, 107)


if __name__ == '__main__':
    # unittest.main()
    test = TestBuildSTNU()
    test.test_build_stn()
