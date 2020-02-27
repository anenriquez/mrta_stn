import unittest
import json
import logging
import sys
from stn.stp import STP
import os

# A global variable that stores the max float that will be used to deal with infinite edges.
MAX_FLOAT = sys.float_info.max

code_dir = os.path.abspath(os.path.dirname(__file__))
STN = code_dir + "/data/pstn_two_tasks.json"

logger = logging.getLogger()
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestSREA(unittest.TestCase):
    """ Tests the solver Static Robust Execution

    """
    logger = logging.getLogger('stn.test')

    def setUp(self):
        # Load the stn as a dictionary
        with open(STN) as json_file:
            pstn_dict = json.load(json_file)

        # Convert the dict to a json string
        pstn_json = json.dumps(pstn_dict)

        self.stp = STP('srea')
        self.stn = self.stp.get_stn(stn_json=pstn_json)

    def test_build_stn(self):
        self.logger.info("PSTN: \n %s", self.stn)

        self.logger.info("Getting GUIDE...")
        dispatchable_graph = self.stp.solve(self.stn)
        self.logger.info("GUIDE")
        self.logger.info(dispatchable_graph)
        self.logger.info("Risk metric: %s ", dispatchable_graph.risk_metric)

        completion_time = dispatchable_graph.get_completion_time()
        makespan = dispatchable_graph.get_makespan()
        self.logger.info("Completion time: %s ", completion_time)
        self.logger.info("Makespan: %s ", makespan)

        self.assertEqual(completion_time, 163)
        self.assertEqual(makespan, 97)

        expected_risk_metric = 0.0
        self.assertEqual(dispatchable_graph.risk_metric, expected_risk_metric)

        constraints = dispatchable_graph.get_constraints()

        for (i, j) in constraints:

            if i == 0 and j == 1:
                lower_bound = -dispatchable_graph[j][i]['weight']
                upper_bound = dispatchable_graph[i][j]['weight']
                self.assertEqual(lower_bound, 37)
                self.assertEqual(upper_bound, 38)
            if i == 0 and j == 2:
                lower_bound = -dispatchable_graph[j][i]['weight']
                upper_bound = dispatchable_graph[i][j]['weight']
                self.assertEqual(lower_bound, 41)
                self.assertEqual(upper_bound, 47)
            if i == 0 and j == 3:
                lower_bound = -dispatchable_graph[j][i]['weight']
                upper_bound = dispatchable_graph[i][j]['weight']
                self.assertEqual(lower_bound, 42)
                self.assertEqual(upper_bound, 54)
            if i == 0 and j == 4:
                lower_bound = -dispatchable_graph[j][i]['weight']
                upper_bound = dispatchable_graph[i][j]['weight']
                self.assertEqual(lower_bound, 92)
                self.assertEqual(upper_bound, 94)
            if i == 0 and j == 5:
                lower_bound = -dispatchable_graph[j][i]['weight']
                upper_bound = dispatchable_graph[i][j]['weight']
                self.assertEqual(lower_bound, 96)
                self.assertEqual(upper_bound, 102)
            if i == 0 and j == 6:
                lower_bound = -dispatchable_graph[j][i]['weight']
                upper_bound = dispatchable_graph[i][j]['weight']
                self.assertEqual(lower_bound, 97)
                self.assertEqual(upper_bound, 109)
            if i == 1 and j == 2:
                lower_bound = -dispatchable_graph[j][i]['weight']
                upper_bound = dispatchable_graph[i][j]['weight']
                self.assertEqual(lower_bound, 0)
                self.assertEqual(upper_bound, 47)
            if i == 2 and j == 3:
                lower_bound = -dispatchable_graph[j][i]['weight']
                upper_bound = dispatchable_graph[i][j]['weight']
                self.assertEqual(lower_bound, 0)
                self.assertEqual(upper_bound, 61)
            if i == 3 and j == 4:
                lower_bound = -dispatchable_graph[j][i]['weight']
                upper_bound = dispatchable_graph[i][j]['weight']
                self.assertEqual(lower_bound, 0)
                self.assertEqual(upper_bound, 61)
            if i == 4 and j == 5:
                lower_bound = -dispatchable_graph[j][i]['weight']
                upper_bound = dispatchable_graph[i][j]['weight']
                self.assertEqual(lower_bound, 0)
                self.assertEqual(upper_bound, 61)
            if i == 5 and j == 6:
                lower_bound = -dispatchable_graph[j][i]['weight']
                upper_bound = dispatchable_graph[i][j]['weight']
                self.assertEqual(lower_bound, 0)
                self.assertEqual(upper_bound, MAX_FLOAT)


if __name__ == '__main__':
    unittest.main()
