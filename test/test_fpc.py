import unittest
import json
import logging
import sys
from stn.stp import STP
import os

code_dir = os.path.abspath(os.path.dirname(__file__))
STN = code_dir + "/data/stn_two_tasks.json"

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestFPC(unittest.TestCase):
    """ Tests the solver FullPathConsistency

    """
    logger = logging.getLogger('stn.test')

    def setUp(self):
        # Load the stn as a dictionary
        with open(STN) as json_file:
            stn_dict = json.load(json_file)

        # Convert the dict to a json string
        stn_json = json.dumps(stn_dict)

        self.stp = STP('fpc')
        self.stn = self.stp.get_stn(stn_json=stn_json)

    def test_build_stn(self):
        self.logger.info("STN: \n %s", self.stn)

        minimal_network = self.stp.solve(self.stn)

        self.logger.info("Minimal STN: \n %s", minimal_network)

        completion_time = minimal_network.get_completion_time()
        makespan = minimal_network.get_makespan()
        self.logger.info("Completion time: %s ", completion_time)
        self.logger.info("Makespan: %s ", makespan)

        self.assertEqual(completion_time, 157)
        self.assertEqual(makespan, 100)

        constraints = minimal_network.get_constraints()

        for (i, j) in constraints:

            if i == 0 and j == 1:
                lower_bound = -minimal_network[j][i]['weight']
                upper_bound = minimal_network[i][j]['weight']
                self.assertEqual(lower_bound, 35)
                self.assertEqual(upper_bound, 41)
            if i == 0 and j == 2:
                lower_bound = -minimal_network[j][i]['weight']
                upper_bound = minimal_network[i][j]['weight']
                self.assertEqual(lower_bound, 41)
                self.assertEqual(upper_bound, 47)
            if i == 0 and j == 3:
                lower_bound = -minimal_network[j][i]['weight']
                upper_bound = minimal_network[i][j]['weight']
                self.assertEqual(lower_bound, 45)
                self.assertEqual(upper_bound, 51)
            if i == 0 and j == 4:
                lower_bound = -minimal_network[j][i]['weight']
                upper_bound = minimal_network[i][j]['weight']
                self.assertEqual(lower_bound, 90)
                self.assertEqual(upper_bound, 96)
            if i == 0 and j == 5:
                lower_bound = -minimal_network[j][i]['weight']
                upper_bound = minimal_network[i][j]['weight']
                self.assertEqual(lower_bound, 96)
                self.assertEqual(upper_bound, 102)
            if i == 0 and j == 6:
                lower_bound = -minimal_network[j][i]['weight']
                upper_bound = minimal_network[i][j]['weight']
                self.assertEqual(lower_bound, 100)
                self.assertEqual(upper_bound, 106)
            if i == 1 and j == 2:
                lower_bound = -minimal_network[j][i]['weight']
                upper_bound = minimal_network[i][j]['weight']
                self.assertEqual(lower_bound, 6)
                self.assertEqual(upper_bound, 12)
            if i == 2 and j == 3:
                lower_bound = -minimal_network[j][i]['weight']
                upper_bound = minimal_network[i][j]['weight']
                self.assertEqual(lower_bound, 4)
                self.assertEqual(upper_bound, 10)
            if i == 3 and j == 4:
                lower_bound = -minimal_network[j][i]['weight']
                upper_bound = minimal_network[i][j]['weight']
                self.assertEqual(lower_bound, 39)
                self.assertEqual(upper_bound, 51)
            if i == 4 and j == 5:
                lower_bound = -minimal_network[j][i]['weight']
                upper_bound = minimal_network[i][j]['weight']
                self.assertEqual(lower_bound, 6)
                self.assertEqual(upper_bound, 12)
            if i == 5 and j == 6:
                lower_bound = -minimal_network[j][i]['weight']
                upper_bound = minimal_network[i][j]['weight']
                self.assertEqual(lower_bound, 4)
                self.assertEqual(upper_bound, 10)


if __name__ == '__main__':
    unittest.main()