import unittest
import json
import os
import networkx as nx
from src.temporal_networks.stnu import STNU

STNU1 = "data/stnu_two_tasks.json"


class TestSTNUconsistency(unittest.TestCase):
    def setUp(self):

        my_dir = os.path.dirname(__file__)
        stnu_json = os.path.join(my_dir, STNU1)

        print("my dir:", my_dir)
        print("stnu_json: ", stnu_json)

        with open(stnu_json) as json_file:
            stnu_dict = json.load(json_file)
        self.stnu = STNU.from_dict(stnu_dict)

    def test_consistency(self):
        minimal_stnu = nx.floyd_warshall(self.stnu)
        self.assertTrue(self.stnu.is_consistent(minimal_stnu))

        self.stnu.update_edges(minimal_stnu)
        self.stnu.update_time_schedule(minimal_stnu)
        completion_time = self.stnu.get_completion_time()
        makespan = self.stnu.get_makespan()

        self.assertEqual(completion_time, 59)
        self.assertEqual(makespan, 100)


if __name__ == '__main__':
    unittest.main()
