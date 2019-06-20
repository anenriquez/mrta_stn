import unittest
import os
import json
import collections
import logging
import sys
from scheduler.structs.task import Task
from scheduler.scheduler import Scheduler

STN = "data/pstn_two_tasks.json"

logger = logging.getLogger()
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestBuildPSTN(unittest.TestCase):
    logger = logging.getLogger('scheduler.test')

    def setUp(self):
        # Load the stn as a dictionary
        with open(STN) as json_file:
            pstn_dict = json.load(json_file)

        # Convert the dict to a json string
        pstn_json = json.dumps(pstn_dict)

        self.scheduler = Scheduler('srea', json_temporal_network=pstn_json)

    def test_build_stn(self):
        self.logger.info("PSTN: \n %s", self.scheduler.temporal_network)


        self.logger.info("Getting GUIDE...")
        alpha, guide_stn = self.scheduler.get_dispatch_graph()
        self.logger.info("GUIDE")
        self.logger.info(guide_stn)
        self.logger.info("Alpha: %s ", alpha)

        completion_time = guide_stn.get_completion_time()
        makespan = guide_stn.get_makespan()
        self.logger.info("Completion time: %s ", completion_time)
        self.logger.info("Makespan: %s ", makespan)

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
