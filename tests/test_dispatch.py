import unittest
import json
import os
import numpy as np
from temporal.networks.stnu import STNU
from temporal.networks.dispatch import Dispatch

STNU_DATA = "data/stnu_two_tasks.json"
MAX_SEED = 2 ** 31 - 1

class TestDispatch(unittest.TestCase):
    def setUp(self):

        my_dir = os.path.dirname(__file__)
        stnu_json = os.path.join(my_dir, STNU_DATA)

        print("my dir:", my_dir)
        print("stnu_json: ", stnu_json)

        with open(stnu_json) as json_file:
            stnu_dict = json.load(json_file)
        self.stnu = STNU.from_dict(stnu_dict)
        self.strategy = "srea"

    def test_consistency(self):
        print("STNU: {}".format(self.stnu))
        random_seed = np.random.randint(MAX_SEED)
        seed_gen = np.random.RandomState(random_seed)
        seed = seed_gen.randint(MAX_SEED)

        dispatch_calculator = Dispatch(self.stnu, seed, self.strategy)
        # Resample the contingent edges.
        # Super important!
        dispatch_calculator.resample_stn()

        print("Getting Guide...")
        alpha, guide_stn = dispatch_calculator.get_guide()
        print("GUIDE")
        print(guide_stn)
        print("Alpha: ", alpha)

        expected_alpha = 0.081
        self.assertEqual(alpha, expected_alpha)

        for (i, j), constraint in sorted(guide_stn.constraints.items()):
            if i == 0 and j == 1:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 38)
                self.assertEqual(upper_bound, 39)
            if i == 0 and j == 2:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 42)
                self.assertEqual(upper_bound, 47)
            if i == 0 and j == 3:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 45)
                self.assertEqual(upper_bound, 52)
            if i == 0 and j == 4:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 91)
                self.assertEqual(upper_bound, 92)
            if i == 0 and j == 5:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 97)
                self.assertEqual(upper_bound, 102)
            if i == 0 and j == 6:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 100)
                self.assertEqual(upper_bound, 107)
            if i == 1 and j == 2:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 6)
                self.assertEqual(upper_bound, 47)
            if i == 2 and j == 3:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 4)
                self.assertEqual(upper_bound, 11)
            if i == 3 and j == 4:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 0)
                self.assertEqual(upper_bound, 49)
            if i == 4 and j == 5:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 8)
                self.assertEqual(upper_bound, 57)
            if i == 5 and j == 6:
                lower_bound = -guide_stn[j][i]['weight']
                upper_bound = guide_stn[i][j]['weight']
                self.assertEqual(lower_bound, 4)
                self.assertEqual(upper_bound, 11)


if __name__ == '__main__':
    unittest.main()
