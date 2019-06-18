import unittest
import os
import json
import collections
import sys
from scheduler.structs.task import Task
from scheduler.scheduler import Scheduler

STNU = "data/stnu_two_tasks.json"
MAX_FLOAT = sys.float_info.max


class TestBuildSTNU(unittest.TestCase):

    def setUp(self):

        # Load the stn as a dictionary
        with open(STNU) as json_file:
            stnu_dict = json.load(json_file)

        # Convert the dict to a json string
        stnu_json = json.dumps(stnu_dict)

        self.scheduler = Scheduler('dsc_lp', json_temporal_network=stnu_json)

    def test_build_stn(self):
        print("STNU: \n", self.scheduler.get_temporal_network())

        print(type(self.scheduler.temporal_network))

        print("Getting Schedule...")
        dsc, schedule = self.scheduler.get_dispatch_graph()

        print("DSC: ", dsc)
        print("schedule: ", schedule)

        completion_time = schedule.get_completion_time()
        makespan = schedule.get_makespan()

        print("Completion time: ", completion_time)
        print("Makespan: ", makespan)

        self.assertEqual(completion_time, 69)
        self.assertEqual(makespan, 106)

        expected_dsc = 1.0
        self.assertEqual(dsc, expected_dsc)

        constraints = schedule.get_constraints()

        for (i, j) in constraints:
            if i == 0 and j == 1:
                lower_bound = -schedule[j][i]['weight']
                upper_bound = schedule[i][j]['weight']
                self.assertEqual(lower_bound, 37)
                self.assertEqual(upper_bound, 37)
            if i == 0 and j == 2:
                lower_bound = -schedule[j][i]['weight']
                upper_bound = schedule[i][j]['weight']
                self.assertEqual(lower_bound, 41)
                self.assertEqual(upper_bound, 45)
            if i == 0 and j == 3:
                lower_bound = -schedule[j][i]['weight']
                upper_bound = schedule[i][j]['weight']
                self.assertEqual(lower_bound, 43)
                self.assertEqual(upper_bound, 51)
            if i == 0 and j == 4:
                lower_bound = -schedule[j][i]['weight']
                upper_bound = schedule[i][j]['weight']
                self.assertEqual(lower_bound, 92)
                self.assertEqual(upper_bound, 92)
            if i == 0 and j == 5:
                lower_bound = -schedule[j][i]['weight']
                upper_bound = schedule[i][j]['weight']
                self.assertEqual(lower_bound, 96)
                self.assertEqual(upper_bound, 100)
            if i == 0 and j == 6:
                lower_bound = -schedule[j][i]['weight']
                upper_bound = schedule[i][j]['weight']
                self.assertEqual(lower_bound, 98)
                self.assertEqual(upper_bound, 106)
            if i == 1 and j == 2:
                lower_bound = -schedule[j][i]['weight']
                upper_bound = schedule[i][j]['weight']
                self.assertEqual(lower_bound, 4)
                self.assertEqual(upper_bound, 8)
            if i == 2 and j == 3:
                lower_bound = -schedule[j][i]['weight']
                upper_bound = schedule[i][j]['weight']
                self.assertEqual(lower_bound, 2)
                self.assertEqual(upper_bound, 6)
            if i == 3 and j == 4:
                lower_bound = -schedule[j][i]['weight']
                upper_bound = schedule[i][j]['weight']
                self.assertEqual(lower_bound, 0)
                self.assertEqual(upper_bound, MAX_FLOAT)
            if i == 4 and j == 5:
                lower_bound = -schedule[j][i]['weight']
                upper_bound = schedule[i][j]['weight']
                self.assertEqual(lower_bound, 4)
                self.assertEqual(upper_bound, 8)
            if i == 5 and j == 6:
                lower_bound = -schedule[j][i]['weight']
                upper_bound = schedule[i][j]['weight']
                self.assertEqual(lower_bound, 2)
                self.assertEqual(upper_bound, 6)

if __name__ == '__main__':
    unittest.main()
