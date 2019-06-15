import unittest
import os
import json
import collections
from scheduler.structs.task import Task
from scheduler.scheduler import Scheduler

STN = "data/pstn_two_tasks.json"


class TestBuildPSTN(object):

    def __init__(self):

        # Load the stn as a dictionary
        with open(STN) as json_file:
            pstn_dict = json.load(json_file)

        # Convert the dict to a json string
        pstn_json = json.dumps(pstn_dict)

        self.scheduler = Scheduler('srea', json_temporal_network=pstn_json)

    def test_build_stn(self):
        print("PSTN: \n", self.scheduler.temporal_network)

        print(type(self.scheduler.temporal_network))

        print("Getting GUIDE...")
        alpha, guide_stn = self.scheduler.get_dispatch_graph()
        print("GUIDE")
        print(guide_stn)
        print("Alpha: ", alpha)

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
    test = TestBuildPSTN()
    test.test_build_stn()
