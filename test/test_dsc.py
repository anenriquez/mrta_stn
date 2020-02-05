import unittest
import json
import logging
import sys
from stn.stp import STP
import os

code_dir = os.path.abspath(os.path.dirname(__file__))
STNU = code_dir + "/data/stnu_two_tasks.json"
MAX_FLOAT = sys.float_info.max

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestDSC(unittest.TestCase):
    """ Tests the solver Degree of Strong Controllability

    """
    logger = logging.getLogger('stn.test')

    def setUp(self):
        # Load the stn as a dictionary
        with open(STNU) as json_file:
            stnu_dict = json.load(json_file)

        # Convert the dict to a json string
        stnu_json = json.dumps(stnu_dict)

        self.stp = STP('dsc')
        self.stn = self.stp.get_stn(stn_json=stnu_json)

    def test_build_stn(self):
        self.logger.info("STNU: \n %s", self.stn)

        self.logger.info("Getting Schedule...")
        schedule = self.stp.solve(self.stn)

        self.logger.info("DSC: %s ", schedule.risk_metric)
        self.logger.info("schedule: %s ", schedule)

        completion_time = schedule.get_completion_time()
        makespan = schedule.get_makespan()

        self.logger.info("Completion time: %s ", completion_time)
        self.logger.info("Makespan: %s ", makespan)

        self.assertEqual(completion_time, 61)
        self.assertEqual(makespan, 98)

        expected_risk_metric = 0.0
        self.assertEqual(schedule.risk_metric, expected_risk_metric)

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
