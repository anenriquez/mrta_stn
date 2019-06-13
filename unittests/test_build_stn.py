import unittest
import os
import yaml
import collections
from scheduler.structs.task import Task
from scheduler.scheduler import Scheduler

DATASET = "data/two_tasks.yaml"


class TestBuildSTN(unittest.TestCase):
    def setUp(self):
        tasks = self.get_tasks()
        self.scheduler = Scheduler('fpc')
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
        # print(self.stn.nodes.data())
        # print(self.stn.edges.data())

        metric, minimal_network = self.scheduler.get_dispatch_graph()

        print("Minimal STN: \n", minimal_network)

        completion_time = minimal_network.get_completion_time()
        makespan = minimal_network.get_makespan()
        print("Completion time: ", completion_time)
        print("Makespan: ", makespan)

        self.assertEqual(completion_time, 107)
        self.assertEqual(makespan, 107)


if __name__ == '__main__':
    unittest.main()
