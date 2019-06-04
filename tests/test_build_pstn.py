import unittest
import os
import yaml
import collections
import numpy as np
from temporal.networks.pstn import PSTN
from temporal.structs.task import Task
from temporal.networks.pstn import SchedulerPSTN

DATASET = "data/two_tasks.yaml"
MAX_SEED = 2 ** 31 - 1


class TestBuildPSTN(unittest.TestCase):
    def setUp(self):
        self.tasks = list()
        self.scheduled_tasks = list()
        self.pstn = PSTN()

        random_seed = np.random.randint(MAX_SEED)
        seed_gen = np.random.RandomState(random_seed)
        seed = seed_gen.randint(MAX_SEED)
        self.scheduler = SchedulerPSTN(seed)

        my_dir = os.path.dirname(__file__)
        dataset_path = os.path.join(my_dir, DATASET)

        with open(dataset_path, 'r') as file:
            dataset = yaml.safe_load(file)

        ordered_tasks = collections.OrderedDict(sorted(dataset['tasks'].items(), reverse=True))

        for task_id, task in ordered_tasks.items():
            self.tasks.append(Task.from_dict(task))

    def test_build_stn(self):
        self.pstn.build_temporal_network(self.tasks)
        print("STN: \n", self.pstn)
        print("Nodes: ", self.pstn.nodes.data())
        print("Edges: ", self.pstn.edges.data())
        print("Contingent constraints: ", self.pstn.contingent_constraints)

        minimal_stnu = self.pstn.floyd_warshall()
        self.pstn.update_edges(minimal_stnu)

        alpha, schedule = self.scheduler.get_schedule(self.pstn, "srea")
        print("Schedule: \n", schedule)

        completion_time = self.scheduler.get_completion_time(schedule)
        makespan = self.scheduler.get_makespan(schedule)

        print("Completion time: ", completion_time)
        print("Makespan: ", makespan)

        self.assertEqual(completion_time, 62)
        self.assertEqual(makespan, 100)


if __name__ == '__main__':
    unittest.main()
