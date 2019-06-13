import unittest
import os
import yaml
import collections
import numpy as np
from scheduler.structs.task import Task
from scheduler.scheduler import Scheduler

DATASET = "data/two_tasks.yaml"


class TestBuildPSTN(unittest.TestCase):
    def setUp(self):
        tasks = self.get_tasks()
        self.scheduler = Scheduler('srea')
        self.scheduler.build_temporal_network(tasks)

    def get_tasks(self):
        my_dir = os.path.dirname(__file__)
        dataset_path = os.path.join(my_dir, DATASET)

        with open(dataset_path, 'r') as file:
            dataset = yaml.safe_load(file)

        tasks = list()
        ordered_tasks = collections.OrderedDict(sorted(dataset['tasks'].items(), reverse=True))

        for task_id, task in ordered_tasks.items():
            tasks.append(Task.from_dict(task))
        return tasks

    def test_build_stn(self):
        print("STN: \n", self.scheduler.temporal_network)
        # print("Nodes: ", self.pstn.nodes.data())
        # print("Edges: ", self.pstn.edges.data())
        # print("Contingent constraints: ", self.pstn.contingent_constraints)

        # minimal_stnu = self.pstn.floyd_warshall()
        # self.pstn.update_edges(minimal_stnu)
        # minimal_network = get_minimal_network(self.pstn)

        alpha, guide = self.scheduler.get_dispatch_graph()
        print("Schedule: \n", guide)

        completion_time = guide.get_completion_time()
        makespan = guide.get_makespan()

        print("Completion time: ", completion_time)
        print("Makespan: ", makespan)

        self.assertEqual(completion_time, 69)
        self.assertEqual(makespan, 107)


if __name__ == '__main__':
    unittest.main()
