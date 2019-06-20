import unittest
import os
import json
import collections
import logging
import sys
from scheduler.structs.task import Task
from scheduler.scheduler import Scheduler

STN = "data/stn_two_tasks.json"

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestBuildSTN(unittest.TestCase):
    logger = logging.getLogger('scheduler.test')

    def setUp(self):
        # Load the stn as a dictionary
        with open(STN) as json_file:
            stn_dict = json.load(json_file)

        # Convert the dict to a json string
        stn_json = json.dumps(stn_dict)

        self.scheduler = Scheduler('fpc', json_temporal_network=stn_json)

    def test_build_stn(self):
        self.logger.info("STN: \n %s", self.scheduler.temporal_network)

        metric, minimal_network = self.scheduler.get_dispatch_graph()

        self.logger.info("Minimal STN: \n %s", minimal_network)

        completion_time = minimal_network.get_completion_time()
        makespan = minimal_network.get_makespan()
        self.logger.info("Completion time: %s ", completion_time)
        self.logger.info("Makespan: %s ", makespan)

        self.assertEqual(completion_time, 107)
        self.assertEqual(makespan, 107)


if __name__ == '__main__':
    unittest.main()
