import unittest
import os
import json
import collections
from scheduler.structs.task import Task
from scheduler.scheduler import Scheduler

STN = "data/pstn_two_tasks.json"


class TestBuildPSTN(unittest.TestCase):

    def setUp(self):
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

        completion_time = guide_stn.get_completion_time()
        makespan = guide_stn.get_makespan()
        print("Completion time: ", completion_time)
        print("Makespan: ", makespan)

        self.assertEqual(completion_time, 70)
        self.assertEqual(makespan, 107)

        expected_alpha = 0.023
        self.assertEqual(alpha, expected_alpha)

        constraints = guide_stn.get_constraints()

        for (i, j) in constraints:

            if i == 0 and j == 1:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 37)
                self.assertEqual(upper_bound, 38)
            if i == 0 and j == 2:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 41)
                self.assertEqual(upper_bound, 46)
            if i == 0 and j == 3:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 41)
                self.assertEqual(upper_bound, 52)
            if i == 0 and j == 4:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 92)
                self.assertEqual(upper_bound, 93)
            if i == 0 and j == 5:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 96)
                self.assertEqual(upper_bound, 101)
            if i == 0 and j == 6:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 96)
                self.assertEqual(upper_bound, 107)
            if i == 1 and j == 2:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 0)
                self.assertEqual(upper_bound, 47)
            if i == 2 and j == 3:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 0)
                self.assertEqual(upper_bound, 11)
            if i == 3 and j == 4:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 0)
                self.assertEqual(upper_bound, 61)
            if i == 4 and j == 5:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 0)
                self.assertEqual(upper_bound, 61)
            if i == 5 and j == 6:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 0)
                self.assertEqual(upper_bound, 11)


if __name__ == '__main__':
    unittest.main()
